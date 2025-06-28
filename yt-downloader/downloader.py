from pytube import YouTube, Playlist
from urllib.parse import urlparse, parse_qs, urlunparse

def clean_url(url):
    """Remove query parameters like ?si=... from YouTube URL."""
    parsed = urlparse(url)
    return urlunparse(parsed._replace(query=""))

def download_video(url, resolution='720p', download_subs=False):
    url = clean_url(url)
    print(f"[DEBUG] Cleaned URL: {url}")
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(res=resolution, progressive=True).first()
        if stream:
            print(f"[INFO] Downloading: {yt.title}")
            stream.download()
        else:
            print(f"[ERROR] No stream found for resolution: {resolution}")
        if download_subs and yt.captions:
            caption = yt.captions.get_by_language_code('en')
            if caption:
                with open(f"{yt.title}.srt", "w", encoding='utf-8') as f:
                    f.write(caption.generate_srt_captions())
    except Exception as e:
        print(f"[ERROR] Failed to download video: {e}")

def download_playlist(url, resolution='720p', download_subs=False):
    url = clean_url(url)
    try:
        pl = Playlist(url)
        print(f"[DEBUG] Playlist title: {pl.title}")
        print(f"[DEBUG] Found {len(pl.video_urls)} videos.")
        
        if not pl.video_urls:
            print("[WARNING] No videos found in the playlist.")
            return

        for video_url in pl.video_urls:
            print(f"[DEBUG] Downloading from playlist: {video_url}")
            download_video(video_url, resolution, download_subs)
    except Exception as e:
        print(f"[ERROR] Playlist download failed: {e}")
