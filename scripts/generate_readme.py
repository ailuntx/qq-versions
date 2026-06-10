#!/usr/bin/env python3
"""Generate README.md from versions.json."""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import quote


REPO = "ailuntx/qq-versions"
PRODUCT = "QQ Linux"
OFFICIAL_URL = "https://im.qq.com/linuxqq/index.shtml"
ARCH_COLUMNS = ["x86_64", "arm64", "loongarch64", "mips64el"]
PACKAGE_ORDER = ["deb", "rpm", "AppImage", "appimage"]


def version_key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in re.findall(r"\d+", version))


def release_url(version: str) -> str:
    return f"https://github.com/{REPO}/releases/tag/{quote(version)}"


def asset_url(version: str, file_name: str) -> str:
    return f"https://github.com/{REPO}/releases/download/{quote(version)}/{quote(file_name)}"


def display_date(value: str | None) -> str:
    if not value:
        return "unknown"
    if value.endswith("T00:00:00+00:00"):
        return value[:10]
    return value.replace("T", " ").replace("+00:00", " UTC")


def arch_links(version: str, packages: dict, arch: str) -> str:
    by_type = packages.get(arch)
    if not by_type:
        return "-"
    links = []
    for package_type in PACKAGE_ORDER:
        info = by_type.get(package_type)
        if not info:
            continue
        label = "AppImage" if package_type.lower() == "appimage" else package_type
        url = asset_url(version, info["file"]) if info.get("file") else info["url"]
        links.append(f"[{label}]({url})")
    return " / ".join(links) if links else "-"


def version_rows(data: dict) -> str:
    versions = sorted(data["versions"], key=lambda item: version_key(item["version"]), reverse=True)
    header = ["版本", "官方发布时间", "Release", *ARCH_COLUMNS]
    lines = ["| " + " | ".join(header) + " |", "| " + " | ".join(["---"] * len(header)) + " |"]
    for item in versions:
        version = item["version"]
        row = [
            version,
            display_date(item.get("released")),
            f"[Release]({release_url(version)})",
            *[arch_links(version, item["packages"], arch) for arch in ARCH_COLUMNS],
        ]
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def main() -> None:
    data = json.loads(Path("versions.json").read_text(encoding="utf-8"))
    readme = f"""# {PRODUCT} Versions

[![Track](https://github.com/{REPO}/actions/workflows/track.yml/badge.svg)](https://github.com/{REPO}/actions/workflows/track.yml)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/{REPO}/total)
![GitHub Downloads (all assets, latest release)](https://img.shields.io/github/downloads/{REPO}/latest/total)

QQ Linux 版安装包归档。安装包来自腾讯官方公开下载地址，Release 中保留归档副本和 SHA256。

## 版本表

{version_rows(data)}

官方页面：<{OFFICIAL_URL}>

> QQ Linux 官网会按访问地区/CDN 返回不同版本。本仓库的 `latest` 表示当前已知最高版本；旧版本可能只有官方链接或 Release 记录，没有完整归档资产。

## 校验信息

每个 Release 的说明里包含文件大小和 SHA256。也可以查看 [`versions.json`](versions.json) 获取完整元数据。

## 自动更新

仓库每天自动检查一次官方 Linux 版本。发现新版本时会下载官方安装包、计算 SHA256、更新 `versions.json`，并创建 GitHub Release。

相同版本不会重复下载。只有手动运行 workflow 并填写 `version` 时，才会重新下载该版本并覆盖上传 Release 资产。

## 相关项目

- Windows: <https://github.com/PRO-2684/qqnt-version-history>
- 官方新版入口: <https://im.qq.com/index/#/linux>
- Telegram @QQUpdates: <https://t.me/QQUpdates>
- Winget `Tencent.QQ.NT`: <https://github.com/microsoft/winget-pkgs>

安装包版权归腾讯所有。本项目仅用于公开版本归档。
"""
    Path("README.md").write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    main()
