# Video downloader

A small local web app: paste a link, download it as an MP4 video or MP3 audio file.

Built with Flask and [yt-dlp](https://github.com/yt-dlp/yt-dlp), with ffmpeg doing the conversion.

## Run it

You need Python 3.10+ and [ffmpeg](https://ffmpeg.org/download.html) installed.

```bash
pip install -r requirements.txt
```

```bash
python app.py
```

Then open http://127.0.0.1:5000.

## Notes

- If downloads from a site stop working, update yt-dlp: `pip install -U yt-dlp`.
- A playlist link downloads only the single video.
- The app listens on your own machine only. It has no login or rate limiting, so don't expose it to the internet as is.
- Only download content you own or have permission to save.
