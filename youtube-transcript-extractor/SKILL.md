---
name: youtube-transcript-extractor
description: "Fetch and save YouTube video transcripts using the youtube_transcript_api Python library. Use when Codex needs to extract spoken content, captions, or subtitles from YouTube videos for analysis, summarization, or reference material. Supports fetching transcripts from multiple languages, listing available transcripts, and saving in plain text, JSON, or timestamped formats."
---

# YouTube Transcript Extractor

Fetch transcripts/captions from YouTube videos using `youtube_transcript_api`.

## Prerequisites

Ensure the dependency is installed:

```bash
pip install youtube_transcript_api
```

If running in the Codex workspace Python:

```bash
/Users/shivam94/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pip install youtube_transcript_api
```

## Usage

### Fetch a transcript (plain text — default)

```bash
python3 scripts/fetch_transcript.py VIDEO_ID --output data/
```

### Fetch with timestamps

```bash
python3 scripts/fetch_transcript.py VIDEO_ID --output data/ --format timestamps
```

### Fetch as JSON

```bash
python3 scripts/fetch_transcript.py VIDEO_ID --output data/ --format json
```

### List available transcripts for a video (before fetching)

```bash
python3 scripts/fetch_transcript.py VIDEO_ID --list
```

### Fetch from the workspace Python

```bash
/Users/shivam94/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 scripts/fetch_transcript.py VIDEO_ID --output data/
```

## Output Formats

| Format | File | Content |
|---|---|---|
| `txt` | `data/VIDEO_ID.txt` | Plain concatenated text, space-separated |
| `timestamps` | `data/VIDEO_ID_timestamps.txt` | Each line: `[start - end] text` |
| `json` | `data/VIDEO_ID.json` | JSON array of `{text, start, duration}` objects |

## When Transcripts Are Not Available

Some videos have subtitles disabled. The script will detect this and attempt to list any available transcripts. Common reasons for failure:

- Uploader disabled captions/subtitles
- Auto-generated captions not yet processed by YouTube
- Video is private/unlisted with restricted access
- Region-locked content

In these cases, the script exits with an error message and lists any alternatives.

## Video ID Extraction

Extract the video ID from a YouTube URL:

| URL | Video ID |
|---|---|
| `https://www.youtube.com/watch?v=DGUgpyniLsk` | `DGUgpyniLsk` |
| `https://youtu.be/VJo5vIxWawM` | `VJo5vIxWawM` |
| `https://www.youtube.com/watch?v=TdwB8pzxfqE&t=30s` | `TdwB8pzxfqE` |

## Multiple Video Batch Script

For fetching transcripts from multiple videos at once, either call the script in a loop:

```bash
for vid in ID1 ID2 ID3; do
    python3 scripts/fetch_transcript.py "$vid" --output data/
done
```

## Integration with Other Skills

This skill pairs well with:
- **`$humanizer`** — Rewrite transcript text into natural prose
- **`$html-effectiveness`** — Create interactive transcript viewers
- **`$cognitive-apprenticeship`** — Analyze transcript content for learning

## Error Handling

- If the API times out (YouTube blocking), retry after a few seconds
- Some videos only have auto-generated captions — these are still fetched but may contain transcription errors
- For videos without English captions, use `--list` first to check available languages, then pass the correct language code

## Reference

- API docs: `youtube_transcript_api` on PyPI
- YouTube video IDs are 11 characters (letters, digits, underscore, hyphen)
