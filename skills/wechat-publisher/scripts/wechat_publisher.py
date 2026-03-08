#!/usr/bin/env python3
"""WeChat Publisher - Publish Markdown articles to WeChat Official Accounts.

Subcommands:
    status          Check all accounts' connection status
    publish         Publish article(s) to an account
    themes          List available CSS themes
    import-plugin   Import config from Obsidian plugin
    add-account     Add a new account
    remove-account  Remove an account
    test            Test connection to an account
    update-account  Update account fields
"""

import argparse
import json
import os
import re
import sys
import time
import mimetypes
from pathlib import Path
from io import BytesIO

import requests
import markdown as md_lib
from PIL import Image
from premailer import transform as premailer_transform

# ==================== Constants ====================

CONFIG_PATH = os.path.expanduser("~/.claude/wechat-publisher-config.json")
VAULT_ROOT = "/Users/relax/Library/Mobile Documents/com~apple~CloudDocs/Obsidian2025"
WECHAT_API = "https://api.weixin.qq.com/cgi-bin"

ERROR_CODES = {
    -1: "微信系统繁忙，请稍后重试",
    40001: "access_token 无效或已过期",
    40002: "grant_type 不合法",
    40003: "AppID 不合法",
    40004: "媒体类型不合法",
    40007: "图片格式不支持（仅 JPG/PNG）",
    40009: "图片大小超限（最大 2MB）",
    40035: "文章标题过长（最多 64 字符）",
    40036: "内容标题缺失",
    41001: "缺少 access_token",
    42001: "access_token 已过期",
    43002: "需要 POST 请求",
    45009: "接口调用频率超限",
    45064: "创建草稿频率超限",
    48001: "API 无权限，请确认已获取相关接口权限",
    50002: "用户受限，建议检查公众号状态",
}

DEFAULT_CSS = """\
.note-to-mp {
    max-width: 677px; margin: 0 auto;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 15px; color: #333; line-height: 1.75;
    word-wrap: break-word; word-break: break-word;
}
.note-to-mp h1 { font-size: 20px; font-weight: bold; color: #333; margin: 1.2em 0 1em; }
.note-to-mp h2 { font-size: 18px; font-weight: bold; color: #333; margin: 1.2em 0 1em; }
.note-to-mp h3 { font-size: 17px; font-weight: bold; color: #333; margin: 1.2em 0 1em; }
.note-to-mp h4, .note-to-mp h5, .note-to-mp h6 { font-size: 16px; font-weight: bold; color: #333; margin: 1.2em 0 1em; }
.note-to-mp p { margin: 1em 0; line-height: 1.75; }
.note-to-mp img { max-width: 100%; height: auto; display: block; margin: 1em auto; }
.note-to-mp blockquote { border-left: 4px solid #d0d0d0; padding: 12px 20px; color: #666; margin: 1em 0; background-color: #f7f7f7; }
.note-to-mp code { font-family: Menlo, Monaco, Consolas, monospace; font-size: 14px; padding: 2px 4px; background-color: #f6f8fa; border-radius: 3px; }
.note-to-mp .code-section { margin: 1em 0; padding: 16px; background-color: #f6f8fa; border-radius: 6px; overflow-x: auto; }
.note-to-mp .code-section pre { margin: 0; padding: 0; background: transparent; border: none; }
.note-to-mp .code-section code { background: transparent; padding: 0; }
.note-to-mp table { width: 100%; border-collapse: collapse; margin: 1em 0; }
.note-to-mp th, .note-to-mp td { padding: 8px 12px; border: 1px solid #ddd; }
.note-to-mp th { background-color: #f6f8fa; font-weight: bold; }
.note-to-mp strong { font-weight: bold; color: #333; }
.note-to-mp em { font-style: italic; }
.note-to-mp a { color: #576b95; text-decoration: none; }
.note-to-mp ul, .note-to-mp ol { margin: 1em 0; padding-left: 2em; }
.note-to-mp li { margin: 0.5em 0; line-height: 1.75; }
.note-to-mp hr { border: none; border-top: 1px solid #ddd; margin: 2em 0; }
"""


# ==================== Config ====================

def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {
            "accounts": [],
            "publishHistory": [],
            "excludeFrontmatter": True,
            "themesFolder": os.path.join(VAULT_ROOT, "📌 20-素材/203-Settings/2033-CSS"),
            "defaultTheme": "默认",
        }
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config):
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


# ==================== Proxy ====================

def get_session(proxy_config=None):
    session = requests.Session()
    session.trust_env = False  # Prevent system VPN/proxy from bypassing SOCKS
    if proxy_config:
        ptype = proxy_config.get("type", "http").lower()
        host = proxy_config["host"]
        port = proxy_config["port"]
        user = proxy_config.get("username", "")
        pwd = proxy_config.get("password", "")
        auth = f"{user}:{pwd}@" if user and pwd else ""

        if ptype == "socks5":
            url = f"socks5h://{auth}{host}:{port}"
        elif ptype == "https":
            url = f"https://{auth}{host}:{port}"
        else:
            url = f"http://{auth}{host}:{port}"

        session.proxies = {"http": url, "https": url}
    return session


# ==================== IP Detection ====================

IP_CHECK_URLS = [
    "http://myip.ipip.net",
    "http://ip-api.com/json",
    "http://httpbin.org/ip",
    "http://ifconfig.me/ip",
]


def _extract_ip(text):
    """Extract first IPv4 address from text."""
    m = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", text)
    return m.group(0) if m else None


def detect_exit_ip(proxy_config=None):
    """Detect exit IP and measure latency. Returns (ip, latency_ms) or (None, None)."""
    session = get_session(proxy_config)
    for url in IP_CHECK_URLS:
        try:
            t0 = time.time()
            resp = session.get(url, timeout=15)
            latency_ms = int((time.time() - t0) * 1000)
            ctype = resp.headers.get("content-type", "")
            if "json" in ctype or url.endswith("/json") or "httpbin" in url:
                data = resp.json()
                ip = data.get("origin", "").split(",")[0].strip() or data.get("ip") or data.get("query")
            else:
                ip = _extract_ip(resp.text)
            if ip:
                return ip, latency_ms
        except Exception:
            continue
    return None, None


def verify_proxy_active(proxy_config):
    """Verify that proxy is actually routing traffic (exit IP differs from direct IP)."""
    direct_ip, _ = detect_exit_ip(None)
    proxy_ip, latency = detect_exit_ip(proxy_config)
    if not proxy_ip:
        return None, None, False
    routed = (direct_ip != proxy_ip) if direct_ip else True
    return proxy_ip, latency, routed


# ==================== WeChat API ====================

def wechat_error(data):
    errcode = data.get("errcode", -1)
    errmsg = ERROR_CODES.get(errcode, data.get("errmsg", "未知错误"))
    return errcode, errmsg


def get_access_token(appid, appsecret, proxy_config=None):
    session = get_session(proxy_config)
    params = {"grant_type": "client_credential", "appid": appid, "secret": appsecret}
    resp = session.get(f"{WECHAT_API}/token", params=params, timeout=30)
    data = resp.json()
    if "access_token" in data:
        return data["access_token"], data.get("expires_in", 7200)
    code, msg = wechat_error(data)
    raise Exception(f"获取 token 失败 [{code}]: {msg}")


def upload_content_image(image_data, filename, access_token, proxy_config=None):
    """Upload image for article body content. Returns WeChat URL."""
    session = get_session(proxy_config)
    files = {"media": (filename, image_data, "application/octet-stream")}
    resp = session.post(
        f"{WECHAT_API}/media/uploadimg",
        params={"access_token": access_token},
        files=files,
        timeout=60,
    )
    data = resp.json()
    if "url" in data:
        return data["url"]
    code, msg = wechat_error(data)
    raise Exception(f"上传图片失败 [{code}]: {msg}")


def upload_cover_image(image_data, filename, access_token, proxy_config=None):
    """Upload image as permanent material for cover. Returns media_id."""
    session = get_session(proxy_config)
    files = {"media": (filename, image_data, "application/octet-stream")}
    resp = session.post(
        f"{WECHAT_API}/material/add_material",
        params={"access_token": access_token, "type": "image"},
        files=files,
        timeout=60,
    )
    data = resp.json()
    if "media_id" in data:
        return data["media_id"]
    code, msg = wechat_error(data)
    raise Exception(f"上传封面失败 [{code}]: {msg}")


def create_draft(articles, access_token, proxy_config=None):
    """Create a draft. articles = list of article dicts."""
    session = get_session(proxy_config)
    # Must use ensure_ascii=False so Chinese chars are sent as UTF-8,
    # not \uXXXX escapes (WeChat API treats escapes as literal text)
    payload = json.dumps({"articles": articles}, ensure_ascii=False).encode("utf-8")
    resp = session.post(
        f"{WECHAT_API}/draft/add",
        params={"access_token": access_token},
        data=payload,
        headers={"Content-Type": "application/json"},
        timeout=60,
    )
    data = resp.json()
    if "media_id" in data:
        return data["media_id"]
    code, msg = wechat_error(data)
    raise Exception(f"创建草稿失败 [{code}]: {msg}")


# ==================== Token Management ====================

def ensure_token(account, config):
    """Refresh token if expired. Mutates account and saves config."""
    now_ms = int(time.time() * 1000)
    if account.get("accessToken") and now_ms < account.get("tokenExpireTime", 0):
        return account["accessToken"]

    token, expires_in = get_access_token(
        account["appid"], account["appsecret"], account.get("proxyConfig")
    )
    account["accessToken"] = token
    account["tokenExpireTime"] = now_ms + expires_in * 1000
    account["status"] = "online"
    account["lastCheckTime"] = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())

    # Persist
    for acc in config["accounts"]:
        if acc["id"] == account["id"]:
            acc.update(account)
            break
    save_config(config)
    return token


# ==================== Image Processing ====================

def compress_image(image_data, max_kb=1024):
    """Compress image to fit within max_kb. Returns bytes."""
    img = Image.open(BytesIO(image_data))
    if img.mode in ("RGBA", "P", "LA"):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        if "A" in img.mode:
            bg.paste(img, mask=img.split()[-1])
        else:
            bg.paste(img)
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")

    for quality in range(90, 5, -10):
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=quality, optimize=True)
        if buf.tell() <= max_kb * 1024:
            return buf.getvalue()

    # Resize if still too large
    while True:
        w, h = img.size
        img = img.resize((w * 3 // 4, h * 3 // 4), Image.LANCZOS)
        buf = BytesIO()
        img.save(buf, format="JPEG", quality=50, optimize=True)
        if buf.tell() <= max_kb * 1024:
            return buf.getvalue()


# ==================== Markdown Processing ====================

def strip_frontmatter(content):
    if content.startswith("---"):
        m = re.match(r"^---\s*\n.*?\n---\s*\n", content, re.DOTALL)
        if m:
            return content[m.end():]
    return content


def find_file_in_vault(filename, vault_root):
    """Find file by name in vault, skipping hidden dirs."""
    direct = os.path.join(vault_root, filename)
    if os.path.exists(direct):
        return direct
    basename = os.path.basename(filename)
    for root, dirs, files in os.walk(vault_root):
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        if basename in files:
            return os.path.join(root, basename)
    return None


def extract_images(content, vault_root):
    """Find all image references. Returns list of (original_match, file_path)."""
    images = []
    seen = set()
    # Obsidian wikilinks: ![[image.png]] or ![[image.png|alt]]
    for m in re.finditer(r"!\[\[([^\]|]+)(?:\|[^\]]*)?\]\]", content):
        ref = m.group(0)
        fname = m.group(1).strip()
        fpath = find_file_in_vault(fname, vault_root)
        if fpath and fpath not in seen:
            images.append((ref, fpath))
            seen.add(fpath)
    # Standard markdown: ![alt](path)
    for m in re.finditer(r"!\[([^\]]*)\]\(([^)]+)\)", content):
        ref = m.group(0)
        path = m.group(2).strip()
        if path.startswith("http"):
            continue
        fpath = os.path.join(vault_root, path) if not os.path.isabs(path) else path
        if os.path.exists(fpath) and fpath not in seen:
            images.append((ref, fpath))
            seen.add(fpath)
    return images


def markdown_to_html(content):
    """Convert markdown to WeChat-compatible HTML."""
    extensions = ["fenced_code", "tables", "nl2br", "sane_lists"]
    html = md_lib.markdown(content, extensions=extensions)

    # Wrap fenced code blocks in code-section div (matches plugin's marked.js output)
    html = re.sub(
        r"<pre><code(?:\s+class=\"language-(\w+)\")?>",
        lambda m: f'<section class="code-section {m.group(1) or ""}"><pre><code>',
        html,
    )
    html = html.replace("</code></pre>", "</code></pre></section>")

    # Wrap everything in note-to-mp root
    html = f'<section class="note-to-mp">{html}</section>'
    return html


# ==================== CSS Theme ====================

def load_css_theme(theme_name, themes_folder, account_name=None):
    """Load CSS theme. Auto-detect by account name if possible."""

    # Auto-detect: find theme file containing 【accountName】
    if account_name and themes_folder and os.path.isdir(themes_folder):
        for f in os.listdir(themes_folder):
            if f.endswith(".bak"):
                continue
            if f"【{account_name}】" in f:
                return _read_css_from_file(os.path.join(themes_folder, f))

    if not theme_name or theme_name == "默认":
        return DEFAULT_CSS

    if not themes_folder or not os.path.isdir(themes_folder):
        return DEFAULT_CSS

    # Match by theme name substring
    for f in sorted(os.listdir(themes_folder)):
        if f.endswith(".bak"):
            continue
        name_no_ext = os.path.splitext(f)[0]
        if theme_name in name_no_ext or name_no_ext == theme_name:
            return _read_css_from_file(os.path.join(themes_folder, f))

    print(f"[WARN] Theme '{theme_name}' not found, using default", file=sys.stderr)
    return DEFAULT_CSS


def _read_css_from_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    if filepath.endswith(".css"):
        return content
    # Extract CSS from markdown code block
    m = re.search(r"```(?:css|CSS)\s*\n(.*?)```", content, re.DOTALL)
    return m.group(1) if m else DEFAULT_CSS


def apply_css_inline(html, css_content):
    """Apply CSS by converting to inline styles (WeChat requirement)."""
    full = f"<html><head><style>{css_content}</style></head><body>{html}</body></html>"
    result = premailer_transform(
        full,
        remove_classes=False,
        keep_style_tags=False,
        strip_important=False,
        cssutils_logging_level="CRITICAL",
    )
    m = re.search(r"<body>(.*?)</body>", result, re.DOTALL)
    return m.group(1).strip() if m else html


# ==================== Publishing Pipeline ====================

def publish_article(account, article_path, config, theme_name=None, cover_path=None):
    """Publish one article to one account. Returns result dict."""
    vault_root = VAULT_ROOT
    result = {"status": "failed", "message": "", "article": article_path}

    try:
        # 1. Token
        proxy = account.get("proxyConfig")

        # 1a. Verify proxy is actually routing if configured
        if proxy:
            proxy_ip, _, routed = verify_proxy_active(proxy)
            if not proxy_ip:
                raise Exception(f"代理无法连接: {proxy['host']}:{proxy['port']}")
            if not routed:
                raise Exception(f"代理未生效！出口 IP ({proxy_ip}) 与本机相同，流量未经代理转发")
            print(f"  [PROXY] 已确认代理生效，出口 IP: {proxy_ip}", file=sys.stderr)

        token = ensure_token(account, config)

        # 2. Read file
        fpath = article_path if os.path.isabs(article_path) else os.path.join(vault_root, article_path)
        if not os.path.exists(fpath):
            raise Exception(f"文件不存在: {fpath}")
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        # 3. Strip frontmatter
        if config.get("excludeFrontmatter", True):
            content = strip_frontmatter(content)

        # 4. Title: first H1 or filename (strip date_style_ prefix)
        title_m = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if title_m:
            title = title_m.group(1).strip()
        else:
            stem = Path(fpath).stem
            # Strip "2026-02-21_oMel_" style prefix from filename
            stem_m = re.match(r"\d{4}-\d{2}-\d{2}_[^_]+_(.+)$", stem)
            title = stem_m.group(1) if stem_m else stem
        # WeChat API title limit: 64 characters
        if len(title) > 64:
            title = title[:63] + "…"

        # 5. Upload images and replace references
        images = extract_images(content, vault_root)
        first_img_data = None

        for orig_ref, img_path in images:
            with open(img_path, "rb") as f:
                img_data = f.read()

            if first_img_data is None:
                first_img_data = (img_data, os.path.basename(img_path))

            # Compress if > 1MB
            if len(img_data) > 1024 * 1024:
                img_data = compress_image(img_data, max_kb=1024)

            img_name = os.path.basename(img_path)
            wx_url = upload_content_image(img_data, img_name, token, proxy)
            content = content.replace(orig_ref, f"![]({wx_url})")
            print(f"  [IMG] {img_name} -> uploaded", file=sys.stderr)

        # 6. Cover image
        thumb_media_id = None
        if cover_path and os.path.exists(cover_path):
            with open(cover_path, "rb") as f:
                cdata = f.read()
            if len(cdata) > 1024 * 1024:
                cdata = compress_image(cdata, max_kb=1024)
            thumb_media_id = upload_cover_image(cdata, os.path.basename(cover_path), token, proxy)
            print(f"  [COVER] custom cover uploaded", file=sys.stderr)
        elif first_img_data:
            cdata, cname = first_img_data
            if len(cdata) > 1024 * 1024:
                cdata = compress_image(cdata, max_kb=1024)
            thumb_media_id = upload_cover_image(cdata, cname, token, proxy)
            print(f"  [COVER] first image as cover", file=sys.stderr)

        # 7. Markdown -> HTML
        html = markdown_to_html(content)

        # 8. CSS theme (auto-detect by account name, or use specified)
        themes_folder = config.get("themesFolder", "")
        if themes_folder and not os.path.isabs(themes_folder):
            themes_folder = os.path.join(vault_root, themes_folder)
        css = load_css_theme(theme_name, themes_folder, account.get("name"))
        html = apply_css_inline(html, css)

        # 9. Create draft
        article_data = {
            "title": title,
            "content": html,
            "content_source_url": "",
            "need_open_comment": 0,
            "only_fans_can_comment": 0,
        }
        if thumb_media_id:
            article_data["thumb_media_id"] = thumb_media_id

        media_id = create_draft([article_data], token, proxy)

        result["status"] = "success"
        result["message"] = f"草稿创建成功"
        result["media_id"] = media_id
        result["title"] = title

    except Exception as e:
        result["message"] = str(e)

    return result


# ==================== Commands ====================

def cmd_status(_args):
    config = load_config()
    accounts = config.get("accounts", [])
    if not accounts:
        print(json.dumps({"accounts": [], "message": "未配置账号"}, ensure_ascii=False))
        return

    # Detect direct IP once (for proxy verification)
    print("[检测] 获取本机 IP...", file=sys.stderr)
    direct_ip, _ = detect_exit_ip(None)
    if direct_ip:
        print(f"  本机 IP: {direct_ip}", file=sys.stderr)

    results = []
    for acc in accounts:
        print(f"[检测] {acc['name']}...", file=sys.stderr)
        pc = acc.get("proxyConfig")

        # 1. Detect exit IP and latency
        if pc:
            proxy_str = f"{pc['type']}://{pc['host']}:{pc['port']}"
            exit_ip, latency_ms = detect_exit_ip(pc)
            proxy_routed = (exit_ip != direct_ip) if (exit_ip and direct_ip) else None
        else:
            proxy_str = "直连"
            exit_ip = direct_ip
            latency_ms = None
            proxy_routed = None  # N/A for direct

        # 2. Test WeChat API connection
        wechat_ok = False
        wechat_msg = ""
        try:
            ensure_token(acc, config)
            wechat_ok = True
            wechat_msg = "已连接"
        except Exception as e:
            wechat_msg = str(e)
            acc["status"] = "error"

        # 3. Auto-detect theme
        themes_folder = config.get("themesFolder", "")
        if themes_folder and not os.path.isabs(themes_folder):
            themes_folder = os.path.join(VAULT_ROOT, themes_folder)
        detected_theme = "默认"
        if themes_folder and os.path.isdir(themes_folder):
            for f in os.listdir(themes_folder):
                if f.endswith(".bak"):
                    continue
                if f"【{acc['name']}】" in f:
                    detected_theme = os.path.splitext(f)[0]
                    break

        results.append({
            "id": acc["id"],
            "style": acc.get("style", ""),
            "name": acc["name"],
            "theme": detected_theme,
            "proxy": proxy_str,
            "exit_ip": exit_ip,
            "latency_ms": latency_ms,
            "proxy_routed": proxy_routed,  # True=traffic goes through proxy, False=proxy leaked, None=direct/unknown
            "wechat_connected": wechat_ok,
            "status_message": wechat_msg,
        })

    save_config(config)
    print(json.dumps({"direct_ip": direct_ip, "accounts": results}, ensure_ascii=False, indent=2))


def cmd_publish(args):
    config = load_config()
    account = None
    for acc in config["accounts"]:
        if acc["name"] == args.account or acc["id"] == args.account:
            account = acc
            break
    if not account:
        print(json.dumps({"status": "error", "message": f"账号 '{args.account}' 未找到"}, ensure_ascii=False))
        sys.exit(1)

    theme = args.theme  # None = auto-detect by account name
    results = []

    for article_path in args.articles:
        print(f"\n[发布] {os.path.basename(article_path)} -> {account['name']}", file=sys.stderr)
        r = publish_article(account, article_path, config, theme, args.cover)
        results.append(r)
        icon = "✅" if r["status"] == "success" else "❌"
        print(f"  {icon} {r['message']}", file=sys.stderr)

        # Rate limiting: wait between articles
        if len(args.articles) > 1:
            time.sleep(2)

    success = sum(1 for r in results if r["status"] == "success")
    failed = len(results) - success

    # Record history
    for r in results:
        config["publishHistory"].insert(0, {
            "time": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
            "articleTitle": r.get("title", os.path.basename(r["article"])),
            "accountId": account["id"],
            "accountName": account["name"],
            "status": r["status"],
            "message": r["message"],
        })
    config["publishHistory"] = config["publishHistory"][:100]
    save_config(config)

    print(json.dumps({
        "account": account["name"],
        "total": len(results),
        "success": success,
        "failed": failed,
        "results": results,
    }, ensure_ascii=False, indent=2))


def cmd_themes(_args):
    config = load_config()
    tf = config.get("themesFolder", "")
    if tf and not os.path.isabs(tf):
        tf = os.path.join(VAULT_ROOT, tf)

    themes = [{"name": "默认", "file": "(built-in)", "accounts": []}]
    if tf and os.path.isdir(tf):
        for f in sorted(os.listdir(tf)):
            if f.endswith(".bak"):
                continue
            if not (f.endswith(".md") or f.endswith(".css")):
                continue
            name = os.path.splitext(f)[0]
            # Extract account names from 【...】
            accs = re.findall(r"【([^】]+)】", f)
            themes.append({"name": name, "file": f, "accounts": accs})

    print(json.dumps({"themes": themes, "folder": tf}, ensure_ascii=False, indent=2))


def cmd_import_plugin(_args):
    plugin_path = os.path.join(VAULT_ROOT, ".obsidian/plugins/wechat-publisher/data.json")
    if not os.path.exists(plugin_path):
        print(json.dumps({"status": "error", "message": "插件 data.json 不存在"}, ensure_ascii=False))
        sys.exit(1)

    with open(plugin_path, "r", encoding="utf-8") as f:
        pdata = json.load(f)

    config = load_config()
    imported = 0
    for acc in pdata.get("accounts", []):
        if any(a["id"] == acc["id"] for a in config["accounts"]):
            continue
        config["accounts"].append({
            "id": acc["id"],
            "name": acc["name"],
            "style": acc.get("style", ""),
            "appid": acc["appid"],
            "appsecret": acc["appsecret"],
            "proxyConfig": acc.get("proxyConfig"),
            "accessToken": acc.get("accessToken", ""),
            "tokenExpireTime": acc.get("tokenExpireTime", 0),
            "status": acc.get("status", "unknown"),
            "lastCheckTime": acc.get("lastCheckTime", ""),
        })
        imported += 1

    # Import settings
    tf = pdata.get("themesFolder", "")
    if tf and not os.path.isabs(tf):
        tf = os.path.join(VAULT_ROOT, tf)
    config["themesFolder"] = tf or config.get("themesFolder", "")
    config["defaultTheme"] = pdata.get("defaultTheme", config.get("defaultTheme", "默认"))
    config["excludeFrontmatter"] = pdata.get("excludeFrontmatter", True)

    save_config(config)
    print(json.dumps({
        "status": "success",
        "imported": imported,
        "total": len(config["accounts"]),
        "accounts": [a["name"] for a in config["accounts"]],
    }, ensure_ascii=False, indent=2))


def cmd_add_account(args):
    config = load_config()
    account = {
        "id": f"account-{int(time.time() * 1000)}",
        "name": args.name,
        "style": getattr(args, "style", "") or "",
        "appid": args.appid,
        "appsecret": args.appsecret,
        "accessToken": "",
        "tokenExpireTime": 0,
        "status": "unknown",
        "lastCheckTime": "",
    }
    if args.proxy_type:
        account["proxyConfig"] = {
            "type": args.proxy_type,
            "host": args.proxy_host,
            "port": int(args.proxy_port),
        }
        if args.proxy_user:
            account["proxyConfig"]["username"] = args.proxy_user
        if args.proxy_pass:
            account["proxyConfig"]["password"] = args.proxy_pass

    config["accounts"].append(account)
    save_config(config)
    print(json.dumps({"status": "success", "account": account["name"]}, ensure_ascii=False, indent=2))


def cmd_remove_account(args):
    config = load_config()
    before = len(config["accounts"])
    config["accounts"] = [
        a for a in config["accounts"] if a["name"] != args.name and a["id"] != args.name
    ]
    removed = before - len(config["accounts"])
    save_config(config)
    print(json.dumps({"status": "success", "removed": removed}, ensure_ascii=False, indent=2))


def cmd_test(args):
    config = load_config()
    account = None
    for acc in config["accounts"]:
        if acc["name"] == args.account or acc["id"] == args.account:
            account = acc
            break
    if not account:
        print(json.dumps({"status": "error", "message": f"账号 '{args.account}' 未找到"}, ensure_ascii=False))
        sys.exit(1)

    try:
        token, expires_in = get_access_token(
            account["appid"], account["appsecret"], account.get("proxyConfig")
        )
        print(json.dumps({
            "status": "success",
            "account": account["name"],
            "message": "连接成功",
            "expires_in": expires_in,
        }, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "account": account["name"],
            "message": str(e),
        }, ensure_ascii=False, indent=2))


def cmd_update_account(args):
    config = load_config()
    account = None
    for acc in config["accounts"]:
        if acc["name"] == args.account or acc["id"] == args.account:
            account = acc
            break
    if not account:
        print(json.dumps({"status": "error", "message": f"账号 '{args.account}' 未找到"}, ensure_ascii=False))
        sys.exit(1)

    if args.new_name:
        account["name"] = args.new_name
    if hasattr(args, "style") and args.style is not None:
        account["style"] = args.style
    if args.appid:
        account["appid"] = args.appid
    if args.appsecret:
        account["appsecret"] = args.appsecret
    if args.proxy_type:
        account["proxyConfig"] = {
            "type": args.proxy_type,
            "host": args.proxy_host,
            "port": int(args.proxy_port),
        }
        if args.proxy_user:
            account["proxyConfig"]["username"] = args.proxy_user
        if args.proxy_pass:
            account["proxyConfig"]["password"] = args.proxy_pass
    if args.clear_proxy:
        account.pop("proxyConfig", None)

    # Reset token so it gets refreshed
    account["accessToken"] = ""
    account["tokenExpireTime"] = 0
    save_config(config)
    print(json.dumps({"status": "success", "account": account["name"]}, ensure_ascii=False, indent=2))


# ==================== Main ====================

def main():
    p = argparse.ArgumentParser(description="WeChat Publisher")
    sub = p.add_subparsers(dest="command")

    sub.add_parser("status")

    pub = sub.add_parser("publish")
    pub.add_argument("account", help="Account name or ID")
    pub.add_argument("articles", nargs="+", help="Article file paths")
    pub.add_argument("--theme", help="CSS theme name (auto-detect if omitted)")
    pub.add_argument("--cover", help="Cover image path")

    sub.add_parser("themes")
    sub.add_parser("import-plugin")

    add = sub.add_parser("add-account")
    add.add_argument("--name", required=True)
    add.add_argument("--style", help="Writing style name")
    add.add_argument("--appid", required=True)
    add.add_argument("--appsecret", required=True)
    add.add_argument("--proxy-type", choices=["socks5", "http", "https"])
    add.add_argument("--proxy-host")
    add.add_argument("--proxy-port")
    add.add_argument("--proxy-user")
    add.add_argument("--proxy-pass")

    rm = sub.add_parser("remove-account")
    rm.add_argument("name")

    t = sub.add_parser("test")
    t.add_argument("account")

    upd = sub.add_parser("update-account")
    upd.add_argument("account")
    upd.add_argument("--new-name")
    upd.add_argument("--style", help="Writing style name")
    upd.add_argument("--appid")
    upd.add_argument("--appsecret")
    upd.add_argument("--proxy-type", choices=["socks5", "http", "https"])
    upd.add_argument("--proxy-host")
    upd.add_argument("--proxy-port")
    upd.add_argument("--proxy-user")
    upd.add_argument("--proxy-pass")
    upd.add_argument("--clear-proxy", action="store_true")

    args = p.parse_args()
    cmds = {
        "status": cmd_status,
        "publish": cmd_publish,
        "themes": cmd_themes,
        "import-plugin": cmd_import_plugin,
        "add-account": cmd_add_account,
        "remove-account": cmd_remove_account,
        "test": cmd_test,
        "update-account": cmd_update_account,
    }
    fn = cmds.get(args.command)
    if fn:
        fn(args)
    else:
        p.print_help()


if __name__ == "__main__":
    main()
