#!/usr/bin/env python3
import json
import sys
import re
from pathlib import Path
import os

# 要去掉的参数（完全匹配）
REMOVE_FLAGS = {
    "arm-openbmc-linux-gnueabi-g++",
    "-marm",
    "-fstack-protector-strong",
    "-O2",
    "-Wformat",
    "-Wformat-security",
    "-Wno-psabi",
    "-Wuninitialized",
    "-fcanon-prefix-map",
    "-MD",
    "-MQ",
    "-MF",
    "-o",
    "-c",
    "-g",
    "-Werror",
    "-Winvalid-pch",
    "-fPIC",
    "-pipe",
    "-fvisibility-inlines-hidden"
}

# 要去掉的参数（前缀匹配）
REMOVE_PREFIXES = [
    "-mcpu=",
    "-D_FORTIFY_SOURCE=",
    "--sysroot",
    "-I../",
    "-flto=",
    "-fdiagnostics-color=",
    "-D_GLIBCXX_ASSERTIONS=",
    "-fdebug-prefix-map=",
    "-fmacro-prefix-map=",
    "src/",
    "../",
    "-Werror="
]

# 保留的前缀（例如 -D 和 -I 要保留）
# KEEP_PREFIXES = [
#     "-DBOOST", "-std=", "-Wall", "-Wextra", "-Wpedantic", "-O", "-g"
# ]


def should_keep(arg):
    """判断这个编译参数是否保留"""
    # if any(arg.startswith(prefix) for prefix in KEEP_PREFIXES):
    #     return True
    if any(arg.startswith(prefix) for prefix in REMOVE_PREFIXES):
        return False
    if arg in REMOVE_FLAGS:
        return False
    return True


def clean_command(command):
    """清理不适合 clangd 的参数"""
    # args = re.findall(r'(?:[^\s"\'\\]+|"(?:\\.|[^"])*"|\'(?:\\.|[^\'])*\')+', command)
    args = command.split(" ")
    cleaned = ["g++"]
    skip_next = False

    for i, arg in enumerate(args):
        if should_keep(arg):
            cleaned.append(arg)
        # if skip_next:
        #     skip_next = False
        #     continue

        # if arg in REMOVE_FLAGS:
        #     # 如果参数后面还有值，比如 -o output.o
        #     if i + 1 < len(args) and not args[i + 1].startswith("-"):
        #         skip_next = True
        #     continue

        # if any(arg.startswith(prefix) for prefix in REMOVE_PREFIXES):
        #     continue

        # cleaned.append(arg)

    return " ".join(cleaned)


def process_compile_commands(path):
    """修改 compile_commands.json"""
    with open(path, "r") as f:
        data = json.load(f)

    current_dir = os.getcwd()

    for entry in data:
        old_cmd = entry["command"]
        print(old_cmd)
        if "output" in entry:
            del entry["output"]

        entry["directory"] = current_dir
        entry["command"] = clean_command(old_cmd)

    backup_path = path.with_suffix(".json.bak")
    path.rename(backup_path)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

    print(f"✅ 已修正: {path}")
    print(f"📦 备份原文件: {backup_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python format-clangd-cfg.py /path/to/compile_commands.json")
        sys.exit(1)

    json_path = Path(sys.argv[1])
    if not json_path.is_file():
        print(f"❌ 找不到文件: {json_path}")
        sys.exit(1)

    process_compile_commands(json_path)
