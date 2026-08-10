#!/usr/bin/env python3
"""Demand: which sessions are worth reading, from the transcripts reconcile reads.

reconcile.py answers SUPPLY - what is installed, does anything call it. This is
the other half, and it is deliberately NOT the answer. Counting words cannot see
a situation: twenty turns of back-and-forth are one problem, "any ideas why this
fails" is debugging and not brainstorming, and the strongest signal there is -
you gave up and did it by hand - leaves no keyword at all.

So this script REDUCES. It scores every session on things a machine can see
without interpreting anything (loops, rework, failures, whether any skill fired)
and hands back a shortlist. An agent reads that shortlist and judges what was
actually happening. Deterministic funnel, probabilistic verdict.

The counts below are a sampling frame, never a finding. Intent probes count
SESSIONS, not turns - counting turns inflated one brainstorm into twenty.

Output stays local: it quotes the opening line of sampled sessions so a reviewer
can pick which to read, and that is your raw prompt text. inventory/ is
gitignored for exactly this reason.

Usage:
    python3 bin/demand.py                 # all history
    python3 bin/demand.py --days 30       # recent window
    python3 bin/demand.py --sample 20     # sessions to shortlist
"""
import argparse, re, sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

CL = Path.home() / ".claude"
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "inventory" / "demand.md"

# ponytail: same regex-over-lines trick as reconcile.py - 20x faster than
# json.loads on ~1GB of transcript. Upgrade only if a field stops being greppable.
RE_DAY = re.compile(r'"timestamp"\s*:\s*"(\d{4}-\d{2}-\d{2})')
RE_CMD = re.compile(r'"command"\s*:\s*"((?:[^"\\]|\\.)*)"')
RE_FILE = re.compile(r'"file_path"\s*:\s*"((?:[^"\\]|\\.)*)"')
RE_ERR = re.compile(r'"is_error"\s*:\s*true')
RE_TOOL = re.compile(r'"name"\s*:\s*"([A-Za-z_][A-Za-z0-9_]*)"\s*,\s*"input"')
RE_SKILL = re.compile(r'"skill"\s*:\s*"([a-zA-Z0-9_:.-]+)"')
# A tool RESULT is also a user-role line. Matching intent words against the whole
# line counted grep output as if you had typed it - 18x inflation on the first
# run. Only a string `content` is something you actually wrote.
RE_USER_TEXT = re.compile(r'"role"\s*:\s*"user"\s*,\s*"content"\s*:\s*'
                          r'"((?:[^"\\]|\\.)*)"')
RE_INJECTED = re.compile(r"<[a-z][a-z-]*>.*?</[a-z][a-z-]*>|<[a-z][a-z-]*>\s*$")

# Getting somewhere is not doing something. Skipped, never counted.
NAVIGATION = {"cd", "export", "source", ".", "set", "unset", "true", ":", "pushd",
              "popd", "clear"}

# Binaries whose first word says nothing - the subcommand is the intent.
TWO_WORD = {"git", "gh", "npm", "pnpm", "yarn", "bun", "uv", "uvx", "pip",
            "pip3", "python", "python3", "docker", "kubectl", "cargo", "go",
            "brew", "make", "poetry", "supabase", "vercel", "aws", "terraform"}

# Triage only. These words decide which sessions get READ, and nothing else.
# Every one of them is wrong often: "options" is usually a CLI flag, and half of
# real brainstorming never uses any of them.
INTENT = {
    "plan":       r"\b(plan|roadmap|phases?|break (this|it) down)\b",
    "brainstorm": r"\b(brainstorm|ideas?|options?|alternatives?)\b",
    "debug":      r"\b(debug|why is|not working|broken|failing|traceback)\b",
    "review":     r"\b(review|audit|check (this|the)|look over)\b",
    "explain":    r"\b(explain|what does|how does|understand)\b",
    "cleanup":    r"\b(clean ?up|refactor|simplify|remove|delete)\b",
    "test":       r"\b(tests?|pytest|failing test|coverage)\b",
}
INTENT_RX = {k: re.compile(v, re.I) for k, v in INTENT.items()}


def segment(seg: str) -> str:
    """One command segment reduced to its intent. Never an argument or a path."""
    parts = [p for p in seg.split("|")[0].split() if "=" not in p.split("/")[0]]
    if not parts:
        return ""
    head = Path(parts[0]).name
    if head in ("sudo", "time", "nohup", "env") and len(parts) > 1:
        parts, head = parts[1:], Path(parts[1]).name
    if head in TWO_WORD and len(parts) > 1 and not parts[1].startswith("-"):
        sub = Path(parts[1]).name
        # bin/reconcile.py -> reconcile.py: the script IS the intent, its path is not.
        return f"{head} {sub}"
    return head


def verb(cmd: str) -> str:
    """The intent of a whole command line.

    `cd repo && pytest` is a pytest intent, so navigation and env setup are
    skipped rather than counted - reading them literally put `cd` at the top of
    the first run with 8751 hits, which measures nothing.

    ponytail: returns ONE verb for a chain. `build && test` is filed as a build.
    Split into a list if chained commands ever matter more than they cost.
    """
    for seg in re.split(r"&&|\|\||;", cmd.strip().strip("()")):
        v = segment(seg.strip())
        if v and v not in NAVIGATION:
            return v
    return ""


def read_session(f: Path):
    """Everything measurable about one session, without interpreting any of it.

    Reads whole files and filters by session afterwards. Filtering line by line
    looked cheaper and silently let 2394 sessions through a 30-day window,
    because one stray in-window timestamp reopened the whole file.
    """
    s = dict(path=f, day="", turns=0, opening="", verbs=Counter(), edits=Counter(),
             errors=0, results=0, skills=set(), intents=set())
    try:
        fh = open(f, errors="replace")
    except OSError:
        return None
    with fh:
        for line in fh:
            m = RE_DAY.search(line)
            if m and not s["day"]:
                # First timestamp = when the session started. NOT max(): a tool
                # result quoting a date would move the session to that date.
                s["day"] = m.group(1)

            if '"name":"Bash"' in line or '"name": "Bash"' in line:
                for c in RE_CMD.findall(line):
                    v = verb(c)
                    if v:
                        s["verbs"][v] += 1
                        last_verb = v
            if RE_TOOL.search(line) and ('"Edit"' in line or '"Write"' in line):
                for p in RE_FILE.findall(line):
                    s["edits"][Path(p).name] += 1
            if '"tool_result"' in line:
                s["results"] += 1
                if RE_ERR.search(line):
                    s["errors"] += 1
            s["skills"].update(RE_SKILL.findall(line))

            m = RE_USER_TEXT.search(line)
            if m:
                s["turns"] += 1
                # Hooks and reminders are injected into your turn. Not your words.
                text = RE_INJECTED.sub(" ", m.group(1)).strip()
                # Escaped newlines survive the strip and look like content.
                # Require real words, or the preview is a column of "\n \n".
                if not s["opening"] and len(re.findall(r"[A-Za-z]{3}", text)) > 3:
                    s["opening"] = re.sub(r"\\n|\s+", " ", text)[:110]
                for k, rx in INTENT_RX.items():
                    if rx.search(text):
                        s["intents"].add(k)
    s["loops"] = {v: n for v, n in s["verbs"].items() if n >= 3}
    s["rework"] = {p: n for p, n in s["edits"].items() if n >= 3}
    # Keep talk-only sessions. Dropping them for having no commands threw away
    # 17k turns on the first run - and a session that is all conversation is
    # exactly where planning and brainstorming happen.
    return s if (s["verbs"] or s["edits"] or s["turns"]) else None


def score(s):
    """How likely is this session to repay reading?

    Weights are a guess, deliberately: they only decide reading ORDER, and a
    wrong order costs one wasted read. Rework counts double because a file
    edited four times is a fix that did not land, which is the thing churn
    measures at repo scale. A session where no skill fired scores higher only
    because the interesting question is what you did INSTEAD.
    """
    return (2 * len(s["rework"]) + len(s["loops"]) + min(s["errors"], 10)
            + (2 if not s["skills"] else 0))


def scan(since: str):
    out = []
    for f in (CL / "projects").rglob("*.jsonl"):
        s = read_session(f)
        if s and s["day"] >= since:
            out.append(s)
    return out


def table(rows, headers, align=None):
    sep = align or ["---"] * len(headers)
    return (["| " + " | ".join(headers) + " |", "|" + "|".join(sep) + "|"]
            + ["| " + " | ".join(str(c) for c in r) + " |" for r in rows])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=0, help="only the last N days")
    ap.add_argument("--top", type=int, default=20, help="rows per count table")
    ap.add_argument("--sample", type=int, default=20, help="sessions to shortlist")
    a = ap.parse_args()

    since = (date.today() - timedelta(days=a.days)).isoformat() if a.days else ""
    ss = scan(since)
    if not ss:
        print("no sessions in window — nothing to measure", file=sys.stderr)
        return 1

    verbs, err_by_verb, rework, intents, loops = (Counter() for _ in range(5))
    for s in ss:
        verbs.update(s["verbs"])
        rework.update(s["rework"])
        loops.update(s["loops"])
        intents.update(s["intents"])
    turns = sum(s["turns"] for s in ss)
    errors = sum(s["errors"] for s in ss)
    results = sum(s["results"] for s in ss)
    unserved = [s for s in ss if not s["skills"]]
    rate = 100 * errors / results if results else 0
    window = f"last {a.days} days" if a.days else "all history"

    body = [
        "---", f"verified_at: {date.today().isoformat()}", "---", "",
        "# Demand", "",
        f"{len(ss)} sessions, {turns} turns you typed, {window}. "
        f"{errors}/{results} tool results errored ({rate:.1f}%). "
        f"{len(unserved)} sessions ({100*len(unserved)//len(ss)}%) invoked no "
        "skill at all.", "",
        "**Nothing below is a finding.** These counts pick which sessions are "
        "worth reading; the reading is where the answer is. A count cannot tell "
        "one problem from twenty turns about it, and cannot see you giving up "
        "and doing it by hand.", "",
        "## Read these", "",
        "Ranked by rework, loops, failures, and whether any skill fired. Open "
        "them and judge what was actually happening.", "",
    ]
    body += table(
        [(s["day"], s["turns"], len(s["rework"]), len(s["loops"]), s["errors"],
          ", ".join(sorted(s["skills"])[:2]) or "—",
          (s["opening"] or "—").replace("|", "\\|"),
          f"`{s['path']}`")
         for s in sorted(ss, key=score, reverse=True)[:a.sample]],
        ["Day", "Turns", "Rework", "Loops", "Errors", "Skills fired",
         "Opened with", "Session"])

    body += ["", "## Counts (triage only)", "",
             "`Loop sessions` is the honest column: a verb run 3+ times in ONE "
             "session is a loop you were stuck in, not a habit.", ""]
    body += table([(v, n, loops.get(v, 0)) for v, n in verbs.most_common(a.top)],
                  ["Verb", "Runs", "Loop sessions"])

    body += ["", "### Rework", "",
             "Files edited 3+ times in one session — the change did not land.", ""]
    rw = rework.most_common(a.top)
    body += table(rw, ["File", "Sessions"]) if rw else ["_none._"]

    body += ["", "### Intent probes", "",
             f"Sessions out of {len(ss)} where you used the words. **Wrong "
             "often** — `options` is usually a CLI flag, and half of real "
             "brainstorming uses none of these words. Sampling frame, not "
             "evidence.", ""]
    body += table(intents.most_common(), ["Intent", "Sessions"])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(body) + "\n")
    print(f"{len(ss)} sessions, {turns} turns, {errors}/{results} errored "
          f"({rate:.1f}%), {len(unserved)} with no skill invoked")
    print(f"wrote {OUT.relative_to(ROOT)} — {a.sample} sessions shortlisted for "
          "reading")
    return 0


if __name__ == "__main__":
    sys.exit(main())
