# AI HR Department（AI 人事部）

> After AI takes over, what job will you be assigned?

[简体中文](README.zh-CN.md)

This skill scans your file directories, then — in the name of the "AI HR Department" — issues you a **Human Placement Notice**: which of 16 types you are, and the evidence behind the verdict.

You get back a vertical card image you can post straight to social media.

> **Note on language:** the verdict, the 16 role names and the card are all written in Chinese. The skill is built for a Chinese-speaking audience. Everything below describes how it works; the output itself will not be in English.

## The premise

**The tidier you are, the easier you are to replace.**

The moment you organize your work into something clean and legible, you have already done the hardest part of the job for the AI. Conversely: directories with chaotic naming, runaway nesting, and structure only you can parse — those the AI cannot learn.

So in this system, **mess is a moat**.

## Privacy: structural, not promised

This is the most important thing about this project, and the reason it can be open source.

The collector — [`plugins/ai-hr/scripts/scan.py`](plugins/ai-hr/scripts/scan.py) — is ~120 lines of pure Python standard library. **You can read all of it.** The JSON it emits **has no field that holds a filename**; only counts, file extensions, and fixed enum keys.

Which means: this is not "we promise not to look at your filenames." It is that **the model never gets the chance to see one**. Privacy here is a property of the output schema, not a pledge in a policy page.

The skill file also hard-codes the rule: the only permitted way to learn anything about your filesystem is this script — listing directories directly is forbidden.

The script is read-only. It never writes, moves, or deletes anything.

The full argument — why privacy promises fail, what makes one structurally checkable, and how this repo satisfies it, with line-level citations into `scan.py` — is in [docs/privacy-by-structure.md](docs/privacy-by-structure.md).

### Don't take our word for it — have your agent audit it

`scan.py` is short enough that any competent agent can read all of it before installing. When we ran the install through WorkBuddy, it audited the code unprompted and reported back: three read-only calls (`os.listdir` / `os.walk` / `os.stat`), no writes, no network requests, no `subprocess` / `eval` / `exec`; the skill file contains no prompt injection and no exfiltration instructions. Its own phrasing for the schema finding was that privacy here is *structural, not a promise*.

Ask yours to do the same before you install. That is the point of keeping the collector this small.

## Install

Requires [WorkBuddy](https://www.workbuddy.cn/) or another desktop agent compatible with the OpenClaw skill format.

**Simplest way — just ask your agent to do it.** Paste this:

> 请帮我安装一下这个项目 https://github.com/GiaSip/ai-hr ，然后帮我试一下

That is verbatim the message we tested with. The agent read the repo, audited the code on its own initiative, installed the skill, and ran it — one message, no menus, no marketplace dialog.

**Or register it as a plugin marketplace** (this is what gets you update notifications): open WorkBuddy's *add marketplace* dialog and enter `GiaSip/ai-hr` — the full URL works too — then install the `ai-hr` plugin.

Either way, trigger it with:

> 给我的电脑画个像

No runtime setup needed — WorkBuddy ships with its own Python.

## The 16 types

Four binary axes, combined into 16 types, each with a four-letter code:

| Axis | Meaning |
|---|---|
| **R / C** | Structure: regular ↔ chaotic |
| **M / K** | Output: maker ↔ keeper |
| **S / B** | Rhythm: steady ↔ bursty |
| **A / F** | Time: deep archive ↔ travelling light |

For example **RMBA**「节点爆破手」(*Deadline Detonator*): dormant for weeks, then at every deadline pulls templates out of the archive and assembles something immaculate — a plant that flowers only three days before the due date.

Four of the sixteen are marked rare. Rarity is defined by **contradictory trait combinations**, not by an extreme value on any single axis.

## On the tone

The verdicts are meant to sting. Social sharing runs on a little offense — something too gentle gives nobody a reason to repost it.

But there is a line: **it judges how you pile up files, never who you are.** Nothing about appearance, gender, region, or income. The goal is that you laugh, swear once, screenshot it, and post it — not that you actually feel bad.

Every verdict is framed as a *pre-assessment*: it reflects what a future AI would want in a hire, not a judgment of who you are today.

## License

MIT
