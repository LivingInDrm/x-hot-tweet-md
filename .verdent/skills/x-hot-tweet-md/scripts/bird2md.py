#!/usr/bin/env python3
"""
bird2md - Convert bird CLI JSON output to formatted Markdown.

Supports three modes:
  1. trending  - Convert trending/news JSON to Markdown
  2. search    - Convert search results JSON to Markdown
  3. user      - Convert user-tweets JSON to Markdown

Usage:
  bird trending --json -n 20 --with-tweets | python3 bird2md.py trending
  bird search "AI" --json -n 20 | python3 bird2md.py search --query "AI"
  bird user-tweets @elonmusk --json -n 20 | python3 bird2md.py user --handle elonmusk
  python3 bird2md.py trending -f trending.json
  python3 bird2md.py trending -f trending.json -o output.md
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

WARN_PREFIX = "\u26a0"
INFO_PREFIX = "\u2139"

_translator = None


def init_translator(target_lang: str):
    global _translator
    try:
        from deep_translator import GoogleTranslator
        _translator = GoogleTranslator(source="auto", target=target_lang)
    except ImportError:
        print("Error: deep-translator not installed. Run: pip install deep-translator", file=sys.stderr)
        sys.exit(1)


def _already_in_target_lang(text: str) -> bool:
    if not _translator:
        return False
    target = _translator.target
    if target.startswith("zh"):
        ratio = len(re.findall(r"[\u4e00-\u9fff]", text)) / max(len(text), 1)
        return ratio > 0.3
    if target == "ja":
        ratio = len(re.findall(r"[\u3040-\u30ff]", text)) / max(len(text), 1)
        return ratio > 0.15
    if target == "ko":
        ratio = len(re.findall(r"[\uac00-\ud7af]", text)) / max(len(text), 1)
        return ratio > 0.3
    return False


_translate_cache: dict[str, str] = {}


def translate_text(text: str) -> str:
    if not _translator or not text or not text.strip():
        return ""
    cleaned = re.sub(r"https?://\S+", "", text).strip()
    cleaned = re.sub(r"@[A-Za-z0-9_]+", "", cleaned).strip()
    if not cleaned:
        return ""
    if _already_in_target_lang(cleaned):
        return ""
    if cleaned in _translate_cache:
        return _translate_cache[cleaned]
    try:
        result = _translator.translate(cleaned)
        _translate_cache[cleaned] = result or ""
        return result or ""
    except Exception as e:
        print(f"Translation warning: {e}", file=sys.stderr)
        _translate_cache[cleaned] = ""
        return ""


def parse_twitter_date(date_str: str) -> str:
    try:
        dt = datetime.strptime(date_str, "%a %b %d %H:%M:%S %z %Y")
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except (ValueError, TypeError):
        return date_str or "N/A"


def format_count(count) -> str:
    if count is None:
        return "0"
    try:
        n = int(count)
    except (ValueError, TypeError):
        return "0"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def tweet_url(author_username: str, tweet_id: str) -> str:
    return f"https://x.com/{author_username}/status/{tweet_id}"


def render_tweet_block(tweet: dict, indent: str = "") -> list[str]:
    lines = []
    author = tweet.get("author", {})
    username = author.get("username", "unknown")
    name = author.get("name", username)
    text = tweet.get("text", "").strip()
    created = parse_twitter_date(tweet.get("createdAt", ""))
    likes = format_count(tweet.get("likeCount", 0))
    retweets = format_count(tweet.get("retweetCount", 0))
    replies = format_count(tweet.get("replyCount", 0))
    tid = tweet.get("id", "")
    url = tweet_url(username, tid)

    hashtags = re.findall(r"#\w+", text)

    lines.append(f"{indent}> **{name}** ([@{username}](https://x.com/{username})) - {created}")
    lines.append(f"{indent}>")
    for tline in text.split("\n"):
        lines.append(f"{indent}> {tline}")
    translated = translate_text(text)
    if translated:
        lines.append(f"{indent}>")
        lines.append(f"{indent}> **[译]** {translated}")
    lines.append(f"{indent}>")
    stats = f"{indent}> Likes: **{likes}** | Retweets: **{retweets}** | Replies: **{replies}**"
    lines.append(stats)
    if hashtags:
        lines.append(f"{indent}> Tags: {' '.join(hashtags)}")
    lines.append(f"{indent}>")
    lines.append(f"{indent}> [View original]({url})")
    lines.append("")
    return lines


def render_trending(data: list[dict], title: str = None) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = []
    lines.append(f"# {title or 'X/Twitter Trending'}")
    lines.append("")
    lines.append(f"> Generated at {now}")
    lines.append("")
    lines.append("---")
    lines.append("")

    for i, item in enumerate(data, 1):
        headline = item.get("headline", "Unknown")
        category = item.get("category", "")
        time_ago = item.get("timeAgo", "")
        post_count = item.get("postCount")
        description = item.get("description", "")

        headline_zh = translate_text(headline)
        if headline_zh and headline_zh != headline:
            lines.append(f"## {i}. {headline_zh}")
            lines.append(f"_{headline}_")
        else:
            lines.append(f"## {i}. {headline}")
        lines.append("")

        meta_parts = []
        if category:
            meta_parts.append(f"**Category:** {category}")
        if time_ago:
            meta_parts.append(f"**Time:** {time_ago}")
        if post_count:
            meta_parts.append(f"**Posts:** {format_count(post_count)}")
        if meta_parts:
            lines.append(" | ".join(meta_parts))
            lines.append("")

        if description:
            desc_zh = translate_text(description)
            if desc_zh and desc_zh != description:
                lines.append(f"_{desc_zh}_ ({description})")
            else:
                lines.append(f"_{description}_")
            lines.append("")

        tweets = item.get("tweets", [])
        if tweets:
            lines.append("### Related Tweets")
            lines.append("")
            for t in tweets:
                lines.extend(render_tweet_block(t))

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def render_search(data: list[dict], query: str = "") -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = []
    title = f'X/Twitter Search: "{query}"' if query else "X/Twitter Search Results"
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"> Generated at {now} | Results: {len(data)}")
    lines.append("")
    lines.append("---")
    lines.append("")

    for i, tweet in enumerate(data, 1):
        author = tweet.get("author", {})
        name = author.get("name", "unknown")
        username = author.get("username", "unknown")
        lines.append(f"### {i}. {name} (@{username})")
        lines.append("")
        lines.extend(render_tweet_block(tweet))
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def render_user_tweets(data: list[dict], handle: str = "") -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = []
    if handle:
        display_handle = handle if handle.startswith("@") else f"@{handle}"
    else:
        first_author = data[0].get("author", {}) if data else {}
        display_handle = f"@{first_author.get('username', 'unknown')}"
        handle = first_author.get("username", "unknown")

    lines.append(f"# {display_handle} - Recent Tweets")
    lines.append("")
    lines.append(f"> Generated at {now} | Tweets: {len(data)}")
    lines.append("")
    lines.append("---")
    lines.append("")

    for i, tweet in enumerate(data, 1):
        created = parse_twitter_date(tweet.get("createdAt", ""))
        lines.append(f"### {i}. [{created}]")
        lines.append("")
        lines.extend(render_tweet_block(tweet))
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Convert bird CLI JSON output to Markdown"
    )
    parser.add_argument(
        "mode",
        choices=["trending", "search", "user"],
        help="Conversion mode",
    )
    parser.add_argument(
        "-f", "--file",
        help="Read JSON from file instead of stdin",
    )
    parser.add_argument(
        "-o", "--output",
        help="Write Markdown to file instead of stdout",
    )
    parser.add_argument(
        "--query",
        default="",
        help="Search query (for search mode title)",
    )
    parser.add_argument(
        "--handle",
        default="",
        help="Twitter handle (for user mode title)",
    )
    parser.add_argument(
        "--title",
        default="",
        help="Custom title for the Markdown document",
    )
    parser.add_argument(
        "--translate",
        default="",
        metavar="LANG",
        help="Translate content to target language (e.g., zh-CN, ja, ko). Requires deep-translator.",
    )

    args = parser.parse_args()

    if args.translate:
        init_translator(args.translate)

    try:
        if args.file:
            with open(args.file, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            raw = sys.stdin.read()
            raw_lines = raw.strip().split("\n")
            json_lines = [
                l for l in raw_lines
                if not l.startswith(WARN_PREFIX) and not l.startswith(INFO_PREFIX)
            ]
            data = json.loads("\n".join(json_lines))
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input - {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: File not found - {args.file}", file=sys.stderr)
        sys.exit(1)

    if not isinstance(data, list):
        print(f"Error: Expected JSON array, got {type(data).__name__}", file=sys.stderr)
        sys.exit(1)

    if not data:
        print("Warning: No data returned", file=sys.stderr)

    if args.mode == "trending":
        md = render_trending(data, title=args.title or None)
    elif args.mode == "search":
        md = render_search(data, query=args.query)
    else:
        md = render_user_tweets(data, handle=args.handle)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(md, encoding="utf-8")
        print(f"Written to {args.output}", file=sys.stderr)
    else:
        print(md)


if __name__ == "__main__":
    main()
