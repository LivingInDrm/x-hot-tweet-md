---
name: x-hot-tweet-md
description: "Fetch hot/trending tweets from X.com (Twitter) using the bird CLI tool and generate well-formatted Markdown documents with optional auto-translation. This skill should be used when the user asks to get trending topics, search tweets by keyword/topic, or fetch tweets from a specific user account on X/Twitter and wants the results as Markdown. Supports automatic translation to Chinese or other languages. Triggers on mentions of X/Twitter trending, hot tweets, tweet collection, tweet-to-markdown, or bird CLI usage."
---

# X Hot Tweet to Markdown

Fetch tweets from X.com via the `bird` CLI and convert them to structured Markdown documents containing tweet content, author info, engagement metrics, hashtags, and original links. Supports automatic translation via `--translate` flag.

## Prerequisites

- **bird CLI** must be installed (`npm install -g @steipete/bird` or `brew install steipete/tap/bird`)
- bird must be authenticated (cookies from Chrome/Firefox/Safari, or `TWITTER_AUTH_TOKEN` env var)
- Verify setup by running `bird whoami`
- **For translation**: `pip install deep-translator` (optional, only needed when using `--translate`)

## Supported Modes

| Mode | bird Command | Description |
|------|-------------|-------------|
| **Trending** | `bird trending` | Fetch trending topics and AI-curated news from Explore tabs |
| **Search** | `bird search "<query>"` | Search tweets by keyword, hashtag, or advanced query |
| **User** | `bird user-tweets <handle>` | Fetch recent tweets from a specific user |

## Workflow

### 1. Trending Topics

To fetch trending topics and generate Markdown:

```bash
bird trending --json -n <count> --with-tweets --tweets-per-item <n> 2>&1 | python3 <skill_path>/scripts/bird2md.py trending -o <output_file>
```

Options for `bird trending`:
- `--for-you` / `--news-only` / `--sports` / `--entertainment` / `--trending-only` - filter by tab
- `--ai-only` - show only AI-curated news items
- `--with-tweets` - include related tweets for each trending item
- `--tweets-per-item <n>` - number of tweets per item (default: 5)
- `-n <count>` - number of items (default: 10)

### 2. Search Tweets

To search tweets by keyword and generate Markdown:

```bash
bird search "<query>" --json -n <count> 2>&1 | python3 <skill_path>/scripts/bird2md.py search --query "<query>" -o <output_file>
```

Advanced search query syntax (same as X.com web):
- `from:username` - tweets from a specific user
- `to:username` - replies to a specific user
- `"exact phrase"` - exact phrase match
- `#hashtag` - tweets with specific hashtag
- `min_faves:100` - minimum likes
- `min_retweets:50` - minimum retweets
- `lang:en` - filter by language
- Combine with AND/OR operators

### 3. User Tweets

To fetch a user's tweets and generate Markdown:

```bash
bird user-tweets <handle> --json -n <count> 2>&1 | python3 <skill_path>/scripts/bird2md.py user --handle <handle> -o <output_file>
```

### bird2md.py Script Reference

The converter script at `scripts/bird2md.py` accepts:

| Argument | Description |
|----------|-------------|
| `mode` | Required. One of: `trending`, `search`, `user` |
| `-f, --file` | Read JSON from file instead of stdin |
| `-o, --output` | Write Markdown to file (default: stdout) |
| `--query` | Search query string (for search mode title) |
| `--handle` | Twitter handle (for user mode title) |
| `--title` | Custom document title |
| `--translate LANG` | Auto-translate content to target language (e.g., `zh-CN`, `ja`, `ko`) |

Input can be piped from bird CLI or read from a saved JSON file.

### Translation

Append `--translate zh-CN` to any command to auto-translate content to Chinese. All bird2md.py modes support this flag:

```bash
bird trending --json -n 10 --with-tweets 2>&1 | python3 <skill_path>/scripts/bird2md.py trending --translate zh-CN -o trending.md
bird search "AI" --json -n 10 2>&1 | python3 <skill_path>/scripts/bird2md.py search --query "AI" --translate zh-CN -o search.md
bird user-tweets @elonmusk --json -n 10 2>&1 | python3 <skill_path>/scripts/bird2md.py user --handle elonmusk --translate zh-CN -o user.md
```

Translation behavior:
- Trending headlines and descriptions are translated (original shown below)
- Tweet text shows original first, then `[译]` translated version
- Content already in the target language is auto-detected and skipped
- Supported languages: `zh-CN` (Chinese), `ja` (Japanese), `ko` (Korean), `fr`, `de`, `es`, and all Google Translate languages
- Requires `deep-translator` package (`pip install deep-translator`)

### Output Format

The generated Markdown includes for each tweet:
- **Author**: display name and @handle with profile link
- **Content**: full tweet text
- **Engagement**: likes, retweets, replies counts
- **Hashtags**: extracted from tweet text
- **Timestamp**: formatted publish time (UTC)
- **Link**: direct link to original tweet on X.com

## Important Notes

- bird CLI is **read-only safe**. Do NOT use it for posting, retweeting, or liking (account suspension risk).
- The `--json` flag is required for all bird commands when piping to bird2md.py.
- Filter stderr warnings (cookie messages) by piping through `2>&1` - the script handles this automatically.
- For large result sets, use `--all --max-pages <n>` on search, or increase `-n` count.
