"""Simple media downloader: paste a link, get an .mp4 or .mp3 back.

Uses yt-dlp (supports YouTube, Vimeo, X/Twitter, Instagram, SoundCloud and ~1,800 other sites)
and ffmpeg for merging/converting.
"""
import shutil
import tempfile
import threading
import time
import webbrowser
from pathlib import Path
from urllib.parse import quote

from flask import Flask, Response, jsonify, render_template, request
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

app = Flask(__name__)

VIDEO_QUALITIES = {"best": None, "1080": 1080, "720": 720, "480": 480, "360": 360}
AUDIO_BITRATES = {"320", "192", "128"}
PORT = 5000


def find_ffmpeg() -> str | None:
    """Use the system ffmpeg if there is one, otherwise the copy bundled with imageio-ffmpeg."""
    system = shutil.which("ffmpeg")
    if system:
        return system
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


FFMPEG = find_ffmpeg()

# Each download gets its own folder inside the project's downloads/ dir.
WORK_ROOT = Path(__file__).parent / "downloads"
WORK_ROOT.mkdir(exist_ok=True)
STALE_AFTER = 15 * 60  # seconds


def sweep_old_jobs() -> None:
    """Backup cleanup: remove any job folder in downloads/ older than STALE_AFTER."""
    cutoff = time.time() - STALE_AFTER
    for d in WORK_ROOT.glob("job_*"):
        if d.is_dir() and d.stat().st_mtime < cutoff:
            shutil.rmtree(d, ignore_errors=True)


def build_options(fmt: str, quality: str, out_dir: str) -> dict:
    opts = {
        "outtmpl": f"{out_dir}/%(title).150B.%(ext)s",
        "noplaylist": True,          # a playlist link downloads just the one video
        "ffmpeg_location": FFMPEG,
        "noprogress": True,
        "quiet": True,
        "no_warnings": True,
        "restrictfilenames": False,
    }
    if fmt == "mp3":
        bitrate = quality if quality in AUDIO_BITRATES else "192"
        opts.update(
            format="bestaudio/best",
            postprocessors=[{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": bitrate,
            }],
        )
    else:
        height = VIDEO_QUALITIES.get(quality)
        cap = f"[height<={height}]" if height else ""
        # Prefer H.264 + AAC so the .mp4 plays everywhere (QuickTime, iPhone, Windows).
        opts.update(
            format=(
                f"bv*{cap}[vcodec^=avc1]+ba[acodec^=mp4a]/"
                f"bv*{cap}+ba/b{cap}/b"
            ),
            merge_output_format="mp4",
            postprocessors=[{"key": "FFmpegVideoRemuxer", "preferedformat": "mp4"}],
        )
    return opts


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/info")
def info():
    url = (request.json or {}).get("url", "").strip()
    if not url:
        return jsonify(error="Paste a link first."), 400
    try:
        with YoutubeDL({"quiet": True, "no_warnings": True, "noplaylist": True}) as ydl:
            meta = ydl.extract_info(url, download=False)
    except DownloadError as e:
        return jsonify(error=clean_error(e)), 400
    return jsonify(
        title=meta.get("title"),
        thumbnail=meta.get("thumbnail"),
        duration=meta.get("duration"),
        uploader=meta.get("uploader") or meta.get("channel"),
        site=meta.get("extractor_key"),
    )


@app.post("/api/download")
def download():
    data = request.json or {}
    url = data.get("url", "").strip()
    fmt = data.get("format", "mp4")
    quality = str(data.get("quality", "best"))
    if not url:
        return jsonify(error="Paste a link first."), 400
    if fmt not in {"mp4", "mp3"}:
        return jsonify(error="Format must be mp4 or mp3."), 400

    sweep_old_jobs()
    work_dir = tempfile.mkdtemp(prefix="job_", dir=WORK_ROOT)
    try:
        with YoutubeDL(build_options(fmt, quality, work_dir)) as ydl:
            ydl.download([url])
        files = [p for p in Path(work_dir).iterdir() if p.suffix == f".{fmt}"]
        if not files:
            raise DownloadError("Nothing was produced — the site may not offer this format.")
        path = files[0]
    except DownloadError as e:
        shutil.rmtree(work_dir, ignore_errors=True)
        return jsonify(error=clean_error(e)), 400

    def stream():
        # Send the file in chunks, then delete the job folder once it has gone out.
        try:
            with open(path, "rb") as f:
                while chunk := f.read(1024 * 1024):
                    yield chunk
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)

    ascii_name = path.name.encode("ascii", "ignore").decode().replace('"', "") or f"download.{fmt}"
    return Response(
        stream(),
        mimetype="audio/mpeg" if fmt == "mp3" else "video/mp4",
        headers={
            "Content-Length": str(path.stat().st_size),
            "Content-Disposition": (
                f"attachment; filename=\"{ascii_name}\"; filename*=UTF-8''{quote(path.name)}"
            ),
        },
    )


def clean_error(e: Exception) -> str:
    msg = str(e).replace("ERROR: ", "")
    if "Unsupported URL" in msg:
        return "That site isn't supported, or the link isn't a video page."
    if "Sign in" in msg or "login" in msg.lower():
        return "This video needs a login (private, age-restricted or members-only)."
    return msg[:300]


if __name__ == "__main__":
    if not FFMPEG:
        print("WARNING: ffmpeg not found - run: pip install -r requirements.txt")
    url = f"http://127.0.0.1:{PORT}"
    print(f"\nVideo downloader is running at {url}\nClose this window to stop it.\n")
    threading.Timer(1.0, webbrowser.open, args=[url]).start()
    app.run(host="127.0.0.1", port=PORT, debug=False)
