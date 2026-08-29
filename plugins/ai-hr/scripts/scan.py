#!/usr/bin/env python3
"""desk-persona 采集脚本。

只输出统计特征；输出 schema 里没有文件名/路径字段——隐私是结构保证，不是规则。
只读：本脚本对被扫描目录不做任何写入。
用法：python3 scan.py [root ...]   （缺省扫 ~/Desktop ~/Downloads ~/Documents）
"""
import json
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime, timezone

DEFAULT_ROOTS = ["~/Desktop", "~/Downloads", "~/Documents"]
MAX_FILES = 200_000
MAX_DEPTH = 8
SKIP_DIRS = {"node_modules", ".git", "Library", ".Trash", "venv", ".venv", "__pycache__"}

SCREENSHOT_RE = re.compile(r"(截屏|截图|screenshot|screen ?shot|cleanshot|snipaste)", re.I)
VERSIONED_RE = re.compile(r"(final|定稿|最终|v\d+|副本|copy|\(\d+\))", re.I)
UNTITLED_RE = re.compile(r"(untitled|未命名|新建|无标题)", re.I)


def scan_root(path):
    root = os.path.expanduser(path)
    if not os.path.isdir(root):
        return None
    now = time.time()
    exts = Counter()
    stats = {
        "file_count": 0,
        "dir_count": 0,
        "max_depth": 0,
        "top_level_items": 0,
        "ext_top10": {},
        "screenshot_count": 0,
        "versioned_name_count": 0,
        "untitled_name_count": 0,
        "oldest_untouched_days": 0,
        "weekly_active_files_8w": [0] * 8,
        "total_size_mb": 0,
    }
    try:
        stats["top_level_items"] = len(
            [e for e in os.listdir(root) if not e.startswith(".")]
        )
    except OSError:
        return None
    oldest = now
    base_depth = root.rstrip(os.sep).count(os.sep)
    size_bytes = 0
    done = False
    for dirpath, dirnames, filenames in os.walk(root):
        if done:
            break
        depth = dirpath.rstrip(os.sep).count(os.sep) - base_depth
        if depth >= MAX_DEPTH:
            dirnames[:] = []
        else:
            dirnames[:] = [
                d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")
            ]
        stats["dir_count"] += len(dirnames)
        stats["max_depth"] = max(stats["max_depth"], depth)
        for name in filenames:
            if name.startswith("."):
                continue
            stats["file_count"] += 1
            if stats["file_count"] >= MAX_FILES:
                done = True
                break
            ext = os.path.splitext(name)[1].lower().lstrip(".")
            exts[ext if ext else "无后缀"] += 1
            if SCREENSHOT_RE.search(name):
                stats["screenshot_count"] += 1
            if VERSIONED_RE.search(name):
                stats["versioned_name_count"] += 1
            if UNTITLED_RE.search(name):
                stats["untitled_name_count"] += 1
            try:
                st = os.stat(os.path.join(dirpath, name))
            except OSError:
                continue
            size_bytes += st.st_size
            oldest = min(oldest, st.st_mtime)
            weeks_ago = int((now - st.st_mtime) // (7 * 86400))
            if 0 <= weeks_ago < 8:
                stats["weekly_active_files_8w"][weeks_ago] += 1
    stats["ext_top10"] = dict(exts.most_common(10))
    if stats["file_count"]:
        stats["oldest_untouched_days"] = int((now - oldest) / 86400)
    stats["total_size_mb"] = int(size_bytes / 1_000_000)
    return stats


def main():
    roots = sys.argv[1:] or DEFAULT_ROOTS
    result = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "roots": {},
    }
    for r in roots:
        key = os.path.basename(os.path.expanduser(r).rstrip(os.sep)) or r
        result["roots"][key] = scan_root(r)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
