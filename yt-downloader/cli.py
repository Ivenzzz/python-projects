import argparse
from downloader import download_video, download_playlist

def main():
    parser = argparse.ArgumentParser(description="YouTube Downloader")
    parser.add_argument('url', help='YouTube video or playlist URL')
    parser.add_argument('--playlist', action='store_true', help='Indicates if URL is a playlist')
    parser.add_argument('--quality', default='720p', help='Video quality (e.g., 720p, 1080p)')
    parser.add_argument('--subs', action='store_true', help='Download subtitles if available')
    args = parser.parse_args()

    if args.playlist:
        download_playlist(args.url, args.quality, args.subs)
    else:
        download_video(args.url, args.quality, args.subs)

if __name__ == '__main__':
    main()
