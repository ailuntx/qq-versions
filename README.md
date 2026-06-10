# QQ Linux Versions

[![Track](https://github.com/ailuntx/qq-versions/actions/workflows/track.yml/badge.svg)](https://github.com/ailuntx/qq-versions/actions/workflows/track.yml)
![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/ailuntx/qq-versions/total)
![GitHub Downloads (all assets, latest release)](https://img.shields.io/github/downloads/ailuntx/qq-versions/latest/total)

QQ Linux 版安装包归档。安装包来自腾讯官方公开下载地址，Release 中保留归档副本和 SHA256。

## 版本表

| 版本 | 官方发布时间 | Release | x86_64 | arm64 | loongarch64 | mips64el |
| --- | --- | --- | --- | --- | --- | --- |
| 3.2.29 | 2026-05-28 | [Release](https://github.com/ailuntx/qq-versions/releases/tag/3.2.29) | [deb](https://github.com/ailuntx/qq-versions/releases/download/3.2.29/QQ_3.2.29_260528_amd64_01.deb) / [rpm](https://github.com/ailuntx/qq-versions/releases/download/3.2.29/QQ_3.2.29_260528_x86_64_01.rpm) / [AppImage](https://github.com/ailuntx/qq-versions/releases/download/3.2.29/QQ_3.2.29_260528_x86_64_01.AppImage) | [deb](https://github.com/ailuntx/qq-versions/releases/download/3.2.29/QQ_3.2.29_260528_arm64_01.deb) / [rpm](https://github.com/ailuntx/qq-versions/releases/download/3.2.29/QQ_3.2.29_260528_aarch64_01.rpm) / [AppImage](https://github.com/ailuntx/qq-versions/releases/download/3.2.29/QQ_3.2.29_260528_arm64_01.AppImage) | [deb](https://github.com/ailuntx/qq-versions/releases/download/3.2.29/QQ_3.2.29_260528_loongarch64_01.deb) | [deb](https://github.com/ailuntx/qq-versions/releases/download/3.2.29/QQ_3.2.29_260528_mips64el_01.deb) |
| 3.2.22 | 2025-12-03 | [Release](https://github.com/ailuntx/qq-versions/releases/tag/3.2.22) | [deb](https://dldir1v6.qq.com/qqfile/qq/QQNT/Linux/QQ_3.2.22_251203_amd64_01.deb) / [rpm](https://dldir1v6.qq.com/qqfile/qq/QQNT/Linux/QQ_3.2.22_251203_x86_64_01.rpm) / [AppImage](https://dldir1v6.qq.com/qqfile/qq/QQNT/Linux/QQ_3.2.22_251203_x86_64_01.AppImage) | [deb](https://dldir1v6.qq.com/qqfile/qq/QQNT/Linux/QQ_3.2.22_251203_arm64_01.deb) / [rpm](https://dldir1v6.qq.com/qqfile/qq/QQNT/Linux/QQ_3.2.22_251203_aarch64_01.rpm) / [AppImage](https://dldir1v6.qq.com/qqfile/qq/QQNT/Linux/QQ_3.2.22_251203_arm64_01.AppImage) | [deb](https://dldir1v6.qq.com/qqfile/qq/QQNT/Linux/QQ_3.2.22_251203_loongarch64_01.deb) | [deb](https://dldir1v6.qq.com/qqfile/qq/QQNT/Linux/QQ_3.2.22_251203_mips64el_01.deb) |

官方页面：<https://im.qq.com/linuxqq/index.shtml>

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
