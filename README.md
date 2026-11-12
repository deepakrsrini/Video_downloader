# Video downloader

A small local web app: paste a link, download it as an MP4 video or MP3 audio file.

Built with Flask and [yt-dlp](https://github.com/yt-dlp/yt-dlp), with ffmpeg doing the conversion.

## Run it

You need [Python](https://www.python.org/downloads/) installed (on Windows, tick "Add python.exe to PATH" in the installer). Nothing else.

1. Download this repo: green **Code** button, then **Download ZIP**, and unzip it.
2. Double-click the launcher:
   - Windows: `start.bat`
   - macOS: `start.command`
   - Linux: `./start.sh`

The first run takes about a minute to set itself up. After that it starts in a few seconds and opens the page in your browser. Close the launcher window to stop it.

## Notes

- The launcher updates yt-dlp each time it starts, which fixes most cases of a site suddenly not working.
- A playlist link downloads only the single video.
- The app listens on your own machine only. It has no login or rate limiting, so don't expose it to the internet as is.
- Only download content you own or have permission to save.
