# bird CLI Reference

## Installation

```bash
# npm
npm install -g @steipete/bird

# Homebrew (macOS)
brew install steipete/tap/bird
```

## Authentication

bird uses cookie-based authentication from your browser. Supported sources:
- Chrome (default)
- Firefox: `--firefox-profile <name>`
- Safari (requires permissions)
- Manual: `--auth-token <token>` or `TWITTER_AUTH_TOKEN` env var

Verify: `bird whoami`

## Commands Used by This Skill

### bird trending

```
bird trending [options]
```

Fetch AI-curated news and trending topics from Explore tabs.

| Option | Description |
|--------|-------------|
| `-n, --count <number>` | Number of items (default: 10) |
| `--ai-only` | Show only AI-curated news |
| `--with-tweets` | Include related tweets per item |
| `--tweets-per-item <n>` | Tweets per news item (default: 5) |
| `--for-you` | For You tab only |
| `--news-only` | News tab only |
| `--sports` | Sports tab only |
| `--entertainment` | Entertainment tab only |
| `--trending-only` | Trending tab only |
| `--json` | Output as JSON |

### bird search

```
bird search [options] <query>
```

Search for tweets.

| Option | Description |
|--------|-------------|
| `-n, --count <number>` | Number of tweets (default: 10) |
| `--all` | Fetch all results (paged) |
| `--max-pages <number>` | Stop after N pages with --all |
| `--json` | Output as JSON |

### bird user-tweets

```
bird user-tweets [options] <handle>
```

Get tweets from a user's profile timeline.

| Option | Description |
|--------|-------------|
| `-n, --count <number>` | Number of tweets (default: 20) |
| `--max-pages <number>` | Stop after N pages (max: 10) |
| `--json` | Output as JSON |

## JSON Output Schema

### Trending Item

```json
{
  "id": "twitter://trending/...",
  "headline": "Topic Title",
  "category": "AI · News",
  "timeAgo": "9 hours ago",
  "postCount": 12000,
  "description": "Optional description",
  "url": "twitter://...",
  "tweets": [ /* Tweet objects */ ]
}
```

### Tweet Object

```json
{
  "id": "2022155359377347022",
  "text": "Tweet text content...",
  "createdAt": "Fri Feb 13 03:46:22 +0000 2026",
  "replyCount": 0,
  "retweetCount": 417,
  "likeCount": 1200,
  "conversationId": "2022155359377347022",
  "author": {
    "username": "handle",
    "name": "Display Name"
  },
  "authorId": "12345",
  "media": [
    {
      "type": "photo",
      "url": "https://pbs.twimg.com/...",
      "width": 640,
      "height": 800
    }
  ]
}
```

## Advanced Search Operators

| Operator | Example | Description |
|----------|---------|-------------|
| `from:` | `from:elonmusk` | Tweets from user |
| `to:` | `to:elonmusk` | Replies to user |
| `""` | `"exact phrase"` | Exact match |
| `#` | `#AI` | Hashtag |
| `min_faves:` | `min_faves:100` | Min likes |
| `min_retweets:` | `min_retweets:50` | Min retweets |
| `lang:` | `lang:en` | Language filter |
| `since:` | `since:2026-01-01` | Date range start |
| `until:` | `until:2026-02-01` | Date range end |
| `filter:` | `filter:media` | Has media |
| `OR` | `AI OR ML` | Either term |
