#!/usr/bin/env python3
"""
YouTube Transcript Extractor

Usage:
    python3 fetch_transcript.py VIDEO_ID [--output DIR] [--format txt|json|timestamps] [--proxy PROXY_URL]

Fetches transcripts from YouTube videos using youtube_transcript_api.
Saves to the specified output directory (default: ./data/).

Requirements: pip install youtube_transcript_api

If YouTube blocks your IP (too many requests), use --proxy with a proxy URL.
"""

import argparse
import os
import sys

def fetch_transcript(video_id: str, proxy_config=None) -> list:
    """Fetch transcript for a YouTube video. Returns list of snippet objects."""
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api.proxies import ProxyConfig
    
    ytt_api = YouTubeTranscriptApi(
        proxy_config=proxy_config
    )
    try:
        transcript = ytt_api.fetch(video_id)
        return transcript
    except Exception as e:
        print(f"Error fetching transcript for {video_id}: {e}", file=sys.stderr)
        # Try listing available transcripts instead
        try:
            transcript_list = ytt_api.list(video_id)
            print("Available transcripts:", file=sys.stderr)
            for t in transcript_list:
                print(f"  - {t.language} ({t.language_code})"
                      f"{' [generated]' if t.is_generated else ' [manual]'}"
                      f"{' [translatable]' if t.is_translatable else ''}", file=sys.stderr)
        except Exception:
            print("No transcripts available for this video.", file=sys.stderr)
        sys.exit(1)


def save_transcript(transcript, video_id: str, output_dir: str, fmt: str):
    """Save transcript in the specified format."""
    os.makedirs(output_dir, exist_ok=True)
    
    full_text = ' '.join([snippet.text for snippet in transcript])
    
    if fmt == "txt":
        path = os.path.join(output_dir, f"{video_id}.txt")
        with open(path, "w") as f:
            f.write(full_text)
        print(f"Saved plain text: {path} ({len(full_text)} chars)")
    
    elif fmt == "timestamps":
        path = os.path.join(output_dir, f"{video_id}_timestamps.txt")
        with open(path, "w") as f:
            for snippet in transcript:
                start = snippet.start
                duration = snippet.duration
                text = snippet.text
                f.write(f"[{start:.1f}s - {start+duration:.1f}s] {text}\n")
        print(f"Saved with timestamps: {path} ({len(transcript)} segments)")
    
    elif fmt == "json":
        import json
        path = os.path.join(output_dir, f"{video_id}.json")
        data = []
        for snippet in transcript:
            data.append({
                "text": snippet.text,
                "start": snippet.start,
                "duration": snippet.duration,
            })
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Saved as JSON: {path} ({len(data)} segments)")


def list_transcripts(video_id: str, proxy_config=None):
    """List available transcripts for a video."""
    from youtube_transcript_api import YouTubeTranscriptApi
    ytt_api = YouTubeTranscriptApi(proxy_config=proxy_config)
    try:
        transcript_list = ytt_api.list(video_id)
        print(f"Available transcripts for {video_id}:")
        for t in transcript_list:
            print(f"  - {t.language} ({t.language_code})"
                  f"{' [generated]' if t.is_generated else ' [manual]'}"
                  f"{' [translatable]' if t.is_translatable else ''}")
    except Exception as e:
        print(f"Cannot list transcripts for {video_id}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Fetch YouTube video transcripts")
    parser.add_argument("video_id", help="YouTube video ID (11 chars from URL)")
    parser.add_argument("--output", "-o", default="./data", help="Output directory")
    parser.add_argument("--format", "-f", choices=["txt", "json", "timestamps"],
                       default="txt", help="Output format")
    parser.add_argument("--list", action="store_true", help="List available transcripts only")
    parser.add_argument("--proxy", help="Proxy URL for IP-blocked requests "
                       "(e.g., http://user:pass@host:port)")
    
    args = parser.parse_args()
    
    # Configure proxy if provided
    proxy_config = None
    if args.proxy:
        from youtube_transcript_api.proxies import ProxyConfig
        from youtube_transcript_api.proxies import ProxyType
        proxy_config = ProxyConfig(
            http_proxy=args.proxy,
            https_proxy=args.proxy,
            proxy_type=ProxyType.HTTP
        )
    
    if args.list:
        list_transcripts(args.video_id, proxy_config)
        return
    
    transcript = fetch_transcript(args.video_id, proxy_config)
    save_transcript(transcript, args.video_id, args.output, args.format)


if __name__ == "__main__":
    main()
