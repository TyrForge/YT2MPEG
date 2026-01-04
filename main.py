import tkinter as tk
from tkinter import messagebox, filedialog
from yt_dlp import YoutubeDL
import threading
import os


def choose_folder():
    folder = filedialog.askdirectory()
    if folder:
        output_dir.set(folder)

def start_download():
    threading.Thread(target=download, daemon=True).start()


def download():
    url = url_entry.get().strip()
    format_choice = format_var.get()
    folder = output_dir.get()

    if not url:
        messagebox.showerror("Error", "Please enter a YouTube URL")
        return
    
    if not folder:
        messagebox.showerror("Error", "Please choose an output folder")
        return

    download_btn.config(state="disabled")
    outtmpl = os.path.join(folder, "%(title)s.%(ext)s")

    if format_choice == "MP3":
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': outtmpl,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'quiet': True,
        }
    else: 
        ydl_opts = {
            'format': 'bv*[vcodec^=avc1]+ba[acodec^=mp4a]/b[ext=mp4]',
            'outtmpl': outtmpl,
            'merge_output_format': 'mp4',
            'quiet': True,
        }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        messagebox.showinfo("Success", f"{format_choice} download complete!")
    except Exception as e:
        messagebox.showerror("Error", f"Download failed:\n{e}")
    finally:
        download_btn.config(state="normal")

root = tk.Tk()
root.title("YouTube Downloader")

tk.Label(root, text="YouTube URL:").pack(pady=5)
url_entry = tk.Entry(root, width=55)
url_entry.pack(padx=10, pady=5)

format_var = tk.StringVar(value="MP3")
tk.Label(root, text="Format:").pack(pady=5)
tk.OptionMenu(root, format_var, "MP3", "MP4").pack()

output_dir = tk.StringVar()
tk.Label(root, text="Output Folder:").pack(pady=4)

folder_frame = tk.Frame(root)
folder_frame.pack(padx=10)

tk.Entry(folder_frame, textvariable=output_dir, width=45).pack(side="left", padx=5)
tk.Button(folder_frame, text="Browse...", command=choose_folder).pack(side="left")

download_btn = tk.Button(root, text="Download", command=start_download)
download_btn.pack(pady=12)

root.mainloop()