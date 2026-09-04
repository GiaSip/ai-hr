# Privacy by structure: how ai-hr makes "we don't upload your filenames" a property of the data, not a promise

This document explains the privacy design of [ai-hr](https://github.com/GiaSip/ai-hr) as a
generalizable method: how a tool that scans your disk can make its privacy claim
**structurally verifiable** instead of promised. Every claim below cites a specific line of
the code that backs it, so you can check each one without trusting us.

## The problem: privacy promises are unverifiable by construction

Most tools that touch your files handle privacy with a sentence: *"We never look at your
data."* This kind of promise has a structural weakness, regardless of sincerity:

- **The enforcement point is invisible.** The promise lives in a policy page; the actual
  data flow lives in code the user rarely reads. Nothing connects the two.
- **The model context is a black box.** For AI tools specifically, the risk is not "the
  company will misuse data" but "the data enters the model's context at all." Once a
  filename, path, or file content reaches the context window, no policy can recall it.
- **Promises scale with intent; structure scales with code.** An intent can change on a
  Tuesday. A data schema either contains a field or it does not.

The question worth asking of any tool is therefore not *"do they promise?"* but
**"is the promise enforced by a data shape that can be checked?"**

## The criterion: what makes a claim structural

A privacy claim is structural when three conditions hold:

1. **The claim is a property of the emitted data, not of the operator's behavior.**
   "The output schema has no field that could hold X" is checkable; "we don't upload X"
   is not.
2. **The checking is feasible for an outsider.** The code that produces the output must be
   short enough and dependency-free enough that a third party (or their AI agent) can read
   all of it before trusting it.
3. **The rule survives a capable adversary.** Even an agent that wanted to list your
   directories must have no sanctioned path to do so — the constraint must be written into
   its instructions as a hard rule, not left to its discretion.

## How ai-hr satisfies it

ai-hr scans a computer's file directories and produces a personality verdict from
aggregate statistics. The collector is
[`plugins/ai-hr/scripts/scan.py`](../plugins/ai-hr/scripts/scan.py) — about 120 lines of
pure Python standard library (imports: `json`, `os`, `re`, `sys`, `time`, `collections`,
`datetime`, lines 8–14). No network code, no subprocess, no eval.

**Condition 1 — the output schema carries no name.** The collector's entire output is one
JSON object. Its full shape is the `stats` dict built at [scan.py lines 32–44](../plugins/ai-hr/scripts/scan.py):
file and directory counts, max nesting depth, top-level item count, the ten most common
file extensions, counts of screenshot/versioned/untitled naming patterns, the age of the
oldest untouched file, an eight-week activity histogram, and total size in MB. **There is
no field in this schema that a filename, path, or content snippet could occupy.** This was
confirmed by running the script: the emitted JSON contains exactly these keys and nothing
else ([main()](../plugins/ai-hr/scripts/scan.py) prints one `json.dumps` of it, lines 98–107).

**Condition 2 — an outsider can audit it.** The script is short enough to read in full in
one sitting, which is deliberate. The README asks you not to take our word for it but to
have your own agent audit the code before installing. That instruction is only meaningful
because the code is small.

**Condition 3 — the constraint is a hard rule in the skill, not a hope.** The skill file
([SKILL.md line 27](../plugins/ai-hr/SKILL.md)) states: the *only* permitted way for the agent
to learn anything about the user's filesystem is to run this script; listing directories or
reading filenames by itself is forbidden. Its closing hard rules add that no output may
contain any filename, directory name, path, person, or project name
([SKILL.md line 169](../plugins/ai-hr/SKILL.md)). The script is also strictly read-only: it
calls `os.listdir`, `os.walk`, and `os.stat` (lines 46–47, 55, 83) and never writes,
moves, or deletes anything.

One nuance, stated precisely because it matters: the script *does* read filenames —
transiently, in local memory — to classify them (the screenshot/versioned/untitled regexes
at lines 21–23 and 76–81) and to extract extensions (line 74). The structural guarantee is
about **what crosses the boundary into the model's context**: names are inspected locally
and only counters leave. A filename has nowhere to go, because the schema gives it no field
to travel in.

## Limitations, honestly

- **The guarantee covers the scanner→model boundary only.** The aggregate statistics are
  the product — a persona is deliberately derived from your file-behavior patterns. Coarse
  facts (e.g. how many screenshots you accumulate) can still feel personal. What is
  prevented is identification via names, paths, or contents, not profiling itself.
- **It holds for this exact script.** A modified copy voids it. That is why the audit
  instruction exists: verify the code you actually install, not the idea of it.
- **The root label is a directory basename.** `scan.py` keys the output by the basename of
  each scanned root (lines 104–106). By default these are the standard
  `Desktop` / `Downloads` / `Documents`; if a custom root is passed, its basename appears.
- **Extension lists leak coarse type information** (line 91) — again by design: "mostly
  receives PDFs, rarely produces" is part of the verdict.

The generalizable takeaway: when a privacy claim matters to you, look for the shape of the
data, the length of the code, and the hardness of the rules — and prefer tools where all
three can be checked in one sitting.
