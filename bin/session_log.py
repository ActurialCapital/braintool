#!/usr/bin/env python3
"""Session log: print what just happened, at the only moment anyone cares.

A SessionEnd hook. It reads the transcript that just closed, prints a few lines,
and appends them to inventory/sessions.jsonl for the weekly review to read.

No model call. Everything here is countable - loops, rework, failures, which
skills fired - so this costs nothing, runs instantly, and covers every session
rather than the subset some other tool happened to capture.

The line that matters is `skills`. Seeing "none fired" after a session where you
own twenty of them is the awareness gap made visible while you still care.

Usage:
    python3 bin/session_log.py                     # reads hook JSON on stdin
    python3 bin/session_log.py <transcript.jsonl>  # by hand, for testing
"""
import json, shutil, sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from demand import read_session  # noqa: E402  - the session reader already exists

ROOT = Path(__file__).resolve().parent.parent
LOG = ROOT / "inventory" / "sessions.jsonl"
LABEL = 9

# Colour only when a human is looking. A hook's stdout is often captured, and
# escape codes in a log file are worse than no colour at all.
TTY = sys.stdout.isatty()
DIM, BOLD, WARN, OFF = (("\033[2m", "\033[1m", "\033[33m", "\033[0m")
                        if TTY else ("", "", "", ""))


def width():
    return max(46, min(shutil.get_terminal_size((72, 24)).columns - 2, 78))


def clip(s, n):
    return s if len(s) <= n else s[:n - 1] + "…"


def render(title, rows):
    """A box that survives a narrow terminal and a pipe to a file."""
    w = width()
    inner = w - 2
    out = [f"{DIM}╭{'─' * inner}╮{OFF}",
           f"{DIM}│{OFF} {BOLD}{clip(title, inner - 2):<{inner - 2}}{OFF} {DIM}│{OFF}",
           f"{DIM}├{'─' * (LABEL + 2)}┬{'─' * (inner - LABEL - 3)}┤{OFF}"]
    for label, value, warn in rows:
        v = clip(value, inner - LABEL - 5)
        colour = WARN if warn else ""
        out.append(f"{DIM}│{OFF} {label:<{LABEL}} {DIM}│{OFF} "
                   f"{colour}{v:<{inner - LABEL - 5}}{OFF} {DIM}│{OFF}")
    out.append(f"{DIM}╰{'─' * (LABEL + 2)}┴{'─' * (inner - LABEL - 3)}╯{OFF}")
    return "\n".join(out)


def payload():
    """SessionEnd hands the hook a JSON payload on stdin; argv is for testing.

    `cwd` is the only reliable project name. The transcript lives in a directory
    named by replacing every "/" in the repo path with "-", so a repo whose name
    already contains a hyphen loses everything before it: the last segment of
    `-Users-me-code-my-repo` is "repo".
    """
    if len(sys.argv) > 1:
        return Path(sys.argv[1]), ""
    if sys.stdin.isatty():
        return None, ""
    try:
        raw = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return None, ""
    p = raw.get("transcript_path") or raw.get("transcriptPath")
    return (Path(p) if p else None), raw.get("cwd", "")


def top(counter, n=3):
    return ", ".join(f"{k} ×{v}" for k, v in
                     sorted(counter.items(), key=lambda kv: -kv[1])[:n])


def main():
    f, cwd = payload()
    if not f or not f.is_file():
        return 0                      # nothing to say; never block the exit
    s = read_session(f)
    if not s or s["turns"] < 2:
        return 0                      # a two-line session is not worth a box

    rec = {"day": s["day"] or date.today().isoformat(),
           "session": f.stem, "project": Path(cwd).name if cwd else "?",
           "turns": s["turns"], "errors": s["errors"], "results": s["results"],
           "loops": s["loops"], "rework": s["rework"],
           "skills": sorted(s["skills"]), "opening": s["opening"]}

    rows = []
    if s["loops"]:
        rows.append(("loops", top(s["loops"]), False))
    if s["rework"]:
        rows.append(("rework", top(s["rework"]), False))
    if s["errors"]:
        rows.append(("failed", f"{s['errors']} of {s['results']} tool calls",
                     s["errors"] / max(s["results"], 1) > 0.05))
    # The line worth printing even when it is empty: owning twenty skills and
    # firing none is the finding, and it is invisible anywhere else.
    rows.append(("skills", ", ".join(sorted(s["skills"])) or "none fired",
                 not s["skills"]))

    title = f"braintool · {rec['project']} · {s['turns']} turns"
    print("\n" + render(title, rows))

    # One row per session, not per hook firing. SessionEnd fires on clear and on
    # resume too, so appending blindly wrote 7 rows for 2 sessions - and every
    # ratio the weekly review computes from this file would then be weighted by
    # how often a session was interrupted.
    # ponytail: rewrite the whole file. It is one line per session; if it ever
    # grows past a few thousand, key it by session in a dict and dump once.
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        kept = []
        if LOG.exists():
            for line in LOG.read_text().splitlines():
                try:
                    if json.loads(line).get("session") != rec["session"]:
                        kept.append(line)
                except ValueError:
                    kept.append(line)     # unparseable is still someone's data
        LOG.write_text("\n".join(kept + [json.dumps(rec)]) + "\n")
    except OSError:
        pass                          # a log that cannot write is not an error
    return 0


if __name__ == "__main__":
    sys.exit(main())
