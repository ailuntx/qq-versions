# qq-versions

自动采集 QQ Linux 版公开下载信息，并通过 GitHub Actions 发布版本归档。

## 数据文件

`versions.json` 记录 Linux 版历史版本。每个版本包含：

- `version`: 官方配置中的版本号
- `released`: 官方配置中的更新时间
- `packages`: 按架构和包格式分组的下载信息
- `config_url`: 本次采集使用的官方配置脚本

QQ Linux 官网会按访问地区/CDN 返回不同版本。`latest` 表示当前已知最高版本，`last_seen` 表示最近一次采集环境看到的版本。

当前支持的 Linux 包：

- `x86_64`: `deb`、`rpm`、`appimage`
- `arm64`: `deb`、`rpm`、`appimage`
- `loongarch64`: `deb`
- `mips64el`: `deb`，如果官方配置继续提供

## 本地运行

```bash
python -m unittest discover -s tests
python scripts/track.py --check
python scripts/track.py --update
```

需要下载安装包并计算 `sha256` 时：

```bash
python scripts/track.py --check --update --download
```

## 自动发布

`.github/workflows/track.yml` 每 6 小时检查一次。发现新版本后会：

1. 更新 `versions.json`
2. 下载官方 Linux 安装包并计算 `sha256`
3. 提交数据文件
4. 创建 GitHub Release 并上传安装包

## 相关项目

- Windows: <https://github.com/PRO-2684/qqnt-version-history>
- 官方 Linux 页面: <https://im.qq.com/linuxqq/index.shtml>
- 官方新版入口: <https://im.qq.com/index/#/linux>

安装包版权归腾讯所有。本项目仅保存公开元数据和自动发布流程。
