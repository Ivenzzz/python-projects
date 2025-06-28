import tkinter as tk
from downloader import download_video, download_playlist

def start_download():
    url = url_entry.get()
    quality = quality_var.get()
    is_playlist = playlist_var.get()
    download_subs = subs_var.get()
    
    if is_playlist:
        download_playlist(url, quality, download_subs)
    else:
        download_video(url, quality, download_subs)

root = tk.Tk()
root.title("YouTube Downloader")

tk.Label(root, text="URL:").pack()
url_entry = tk.Entry(root, width=50)
url_entry.pack()

quality_var = tk.StringVar(value='720p')
tk.Label(root, text="Quality:").pack()
tk.OptionMenu(root, quality_var, '144p', '360p', '480p', '720p', '1080p').pack()

playlist_var = tk.BooleanVar()
tk.Checkbutton(root, text="Is Playlist", variable=playlist_var).pack()

subs_var = tk.BooleanVar()
tk.Checkbutton(root, text="Download Subtitles", variable=subs_var).pack()

tk.Button(root, text="Download", command=start_download).pack()

root.mainloop()
