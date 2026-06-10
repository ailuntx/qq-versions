#!/usr/bin/env python3
"""Track QQ Linux release metadata."""

from __future__ import annotations

import argparse
import datetime as dt
import email.utils
import hashlib
import json
import os
import re
import shutil
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


PRODUCT = "QQ Linux"
SOURCE_URL = "https://im.qq.com/linuxqq/index.shtml"
DEFAULT_CONFIG_URL = "https://cdn-go.cn/qq-web/im.qq.com_new/latest/rainbow/linuxConfig.js"
DEFAULT_TIMEOUT = 30
CONFIG_URL_RE = re.compile(r'var\s+rainbowConfigUrl\s*=\s*"([^"]+)"')
CONFIG_JSON_RE = re.compile(r"var\s+params\s*=\s*(\{.*?\});", re.DOTALL)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def fetch_text(url: str, timeout: int = DEFAULT_TIMEOUT) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; version-tracker/1.0)",
            "Accept": "text/html,application/javascript,*/*;q=0.8",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def request_headers(url: str, timeout: int = DEFAULT_TIMEOUT) -> dict[str, str]:
    def failed(exc: BaseException) -> dict[str, str]:
        return {
            "url": url,
            "status": "",
            "error": str(exc),
        }

    req = urllib.request.Request(
        url,
        method="HEAD",
        headers={"User-Agent": "Mozilla/5.0 (compatible; version-tracker/1.0)"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return {
                "url": response.geturl(),
                "status": str(response.status),
                **{k.lower(): v for k, v in response.headers.items()},
            }
    except urllib.error.HTTPError as exc:
        if exc.code not in {403, 405}:
            return {
                "url": url,
                "status": str(exc.code),
                "error": str(exc.reason),
                **{k.lower(): v for k, v in exc.headers.items()},
            }
    except (urllib.error.URLError, OSError) as exc:
        return failed(exc)

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; version-tracker/1.0)",
            "Range": "bytes=0-0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return {
                "url": response.geturl(),
                "status": str(response.status),
                **{k.lower(): v for k, v in response.headers.items()},
            }
    except urllib.error.HTTPError as exc:
        return {
            "url": url,
            "status": str(exc.code),
            "error": str(exc.reason),
            **{k.lower(): v for k, v in exc.headers.items()},
        }
    except (urllib.error.URLError, OSError) as exc:
        return failed(exc)


def parse_http_date(value: str | None) -> str | None:
    if not value:
        return None
    parsed = email.utils.parsedate_to_datetime(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc).replace(microsecond=0).isoformat()


def resolve_url(url: str) -> str:
    if url.startswith("//"):
        return "https:" + url
    return urllib.parse.urljoin(SOURCE_URL, url)


def determine_config_url(page: str) -> str:
    match = CONFIG_URL_RE.search(page)
    if not match:
        return DEFAULT_CONFIG_URL
    return resolve_url(match.group(1))


def parse_config(config_js: str) -> dict[str, Any]:
    match = CONFIG_JSON_RE.search(config_js)
    if not match:
        raise RuntimeError("Could not find QQ Linux config JSON")
    config = json.loads(match.group(1))
    packages: dict[str, dict[str, dict[str, Any]]] = {}

    for arch, key in (
        ("x86_64", "x64DownloadUrl"),
        ("arm64", "armDownloadUrl"),
    ):
        urls = config.get(key) or {}
        for package_type in ("deb", "rpm", "appimage"):
            url = urls.get(package_type)
            if url:
                packages.setdefault(arch, {})[package_type] = {"url": url}

    loongarch = config.get("loongarchDownloadUrl")
    if loongarch:
        packages.setdefault("loongarch64", {})["deb"] = {"url": loongarch}

    mips = config.get("mipsDownloadUrl")
    if mips:
        packages.setdefault("mips64el", {})["deb"] = {"url": mips}

    if not config.get("version"):
        raise RuntimeError("Could not find QQ Linux version in config")
    if not packages:
        raise RuntimeError("Could not find QQ Linux package URLs in config")

    released = config.get("updateDate")
    if released and re.fullmatch(r"\d{4}-\d{2}-\d{2}", released):
        released = released + "T00:00:00+00:00"

    return {
        "version": config["version"],
        "released": released,
        "packages": packages,
    }


def enrich_package_metadata(release: dict[str, Any], timeout: int) -> dict[str, Any]:
    for by_type in release["packages"].values():
        for info in by_type.values():
            headers = request_headers(info["url"], timeout=timeout)
            content_length = headers.get("content-length")
            info.update(
                {
                    "url": headers.get("url", info["url"]),
                    "status": int(headers["status"]) if headers.get("status", "").isdigit() else None,
                    "size": int(content_length) if content_length and content_length.isdigit() else None,
                    "last_modified": parse_http_date(headers.get("last-modified")),
                    "etag": headers.get("etag"),
                    "md5": headers.get("x-cos-meta-md5"),
                    "sha256": None,
                    "error": headers.get("error"),
                }
            )
    return release


def load_versions(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {
            "schema": 1,
            "product": PRODUCT,
            "source": SOURCE_URL,
            "updated_at": None,
            "latest": None,
            "versions": [],
        }
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def known_versions(data: dict[str, Any]) -> set[str]:
    return {entry["version"] for entry in data.get("versions", [])}


def find_version(data: dict[str, Any], version: str) -> dict[str, Any] | None:
    for entry in data.get("versions", []):
        if entry["version"] == version:
            return entry
    return None


def version_key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in re.findall(r"\d+", version))


def upsert_release(data: dict[str, Any], release: dict[str, Any]) -> dict[str, Any]:
    versions = [entry for entry in data.get("versions", []) if entry["version"] != release["version"]]
    versions.append(release)
    versions.sort(key=lambda entry: (entry.get("released") or "", entry["version"]))
    latest = max(versions, key=lambda entry: version_key(entry["version"]))["version"]
    data.update(
        {
            "schema": 1,
            "product": PRODUCT,
            "source": SOURCE_URL,
            "updated_at": utc_now(),
            "latest": latest,
            "last_seen": release["version"],
            "versions": versions,
        }
    )
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def set_output(key: str, value: str) -> None:
    print(f"{key}={value}")
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as fh:
            fh.write(f"{key}={value}\n")


def filename_from_url(url: str) -> str:
    return urllib.parse.urlparse(url).path.rsplit("/", 1)[-1]


def human_size(size: int | None) -> str:
    if size is None:
        return "unknown"
    return f"{size / 1024 / 1024:.1f} MiB ({size} bytes)"


def download_file(url: str, directory: Path, timeout: int) -> tuple[Path, int, str]:
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / filename_from_url(url)
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (compatible; version-tracker/1.0)"},
    )
    digest = hashlib.sha256()
    size = 0
    with urllib.request.urlopen(req, timeout=timeout) as response, target.open("wb") as fh:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            fh.write(chunk)
            digest.update(chunk)
            size += len(chunk)
    return target, size, digest.hexdigest()


def download_release_assets(release: dict[str, Any], directory: Path, timeout: int) -> None:
    if directory.exists():
        shutil.rmtree(directory)
    for by_type in release["packages"].values():
        for info in by_type.values():
            try:
                path, size, sha256 = download_file(info["url"], directory, timeout)
            except urllib.error.URLError as exc:
                info["download_error"] = str(exc.reason)
                continue
            info["file"] = path.name
            info["size"] = size
            info["size_human"] = human_size(size)
            info["sha256"] = sha256


def release_notes(release: dict[str, Any]) -> str:
    lines = [
        "## Version Info",
        f"- Product: `{PRODUCT}`",
        f"- Version: `{release['version']}`",
        f"- Released: `{release.get('released') or 'unknown'}`",
        "",
        "## Assets",
        "| Architecture | Package | File | Size | SHA256 | Official URL |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]
    for arch, by_type in sorted(release["packages"].items()):
        for package_type, info in sorted(by_type.items()):
            file_name = info.get("file") or filename_from_url(info["url"])
            sha256 = info.get("sha256") or "unknown"
            size = human_size(info.get("size"))
            if info.get("download_error"):
                file_name = f"{file_name} (download failed: {info['download_error']})"
            lines.append(
                f"| {arch} | {package_type} | `{file_name}` | {size} | "
                f"`{sha256}` | [official]({info['url']}) |"
            )
    lines.append("")
    return "\n".join(lines)


def get_current_release(timeout: int) -> dict[str, Any]:
    page = fetch_text(SOURCE_URL, timeout=timeout)
    config_url = determine_config_url(page)
    release = parse_config(fetch_text(config_url, timeout=timeout))
    release["config_url"] = config_url
    return enrich_package_metadata(release, timeout)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--versions", type=Path, default=Path("versions.json"))
    parser.add_argument("--latest", type=Path, default=Path("latest.json"))
    parser.add_argument("--release-notes", type=Path, default=Path("release-notes.md"))
    parser.add_argument("--download-dir", type=Path, default=Path("downloads"))
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    parser.add_argument("--version", help="Use an existing version from versions.json instead of live metadata")
    parser.add_argument("--check", action="store_true", help="Fetch current metadata and set changed output")
    parser.add_argument("--update", action="store_true", help="Update versions.json from --latest or live metadata")
    parser.add_argument("--download", action="store_true", help="Download release assets and compute sha256")
    args = parser.parse_args(argv)

    if not args.check and not args.update:
        parser.error("choose --check and/or --update")

    data = load_versions(args.versions)
    release: dict[str, Any]

    if args.version:
        release = find_version(data, args.version)
        if not release:
            raise RuntimeError(f"Version {args.version} not found in {args.versions}")
        set_output("changed", "true")
        set_output("version", release["version"])
        set_output("tag", release["version"])
    elif args.check:
        release = get_current_release(args.timeout)
        write_json(args.latest, release)
        changed = release["version"] not in known_versions(data)
        set_output("changed", "true" if changed else "false")
        set_output("version", release["version"])
        set_output("tag", release["version"])
        if not args.update:
            return 0
    elif args.latest.exists():
        release = json.loads(args.latest.read_text(encoding="utf-8"))
    else:
        release = get_current_release(args.timeout)

    if args.download:
        download_release_assets(release, args.download_dir, args.timeout)

    data = upsert_release(data, release)
    write_json(args.versions, data)
    args.release_notes.write_text(release_notes(release), encoding="utf-8")
    set_output("version", release["version"])
    set_output("tag", release["version"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
