# ═══════════════════════════════════════════════════════════════
# DOWNLOADER — Video, Music, Batch download using yt-dlp
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations
import os, logging, tempfile, asyncio
from pathlib import Path
from typing import Any
from dataclasses import dataclass

logger = logging.getLogger("nexus.downloader")


@dataclass
class DownloadResult:
    filename: str
    filepath: str
    filesize: int
    format: str
    title: str
    duration: float
    url: str
    status: str  # success, error


class VideoDownloader:
    """Download videos from YouTube, TikTok, Instagram, etc using yt-dlp."""

    def __init__(self, output_dir: str = "data/downloads"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"⬇️ Video Downloader initialized (dir: {output_dir})")

    async def download(self, url: str, format: str = "best", audio_only: bool = False) -> DownloadResult:
        """Download a video/audio from URL."""
        try:
            import yt_dlp

            outtmpl = str(self.output_dir / "%(title)s.%(ext)s")
            ydl_opts = {
                "outtmpl": outtmpl, "quiet": True, "no_warnings": True,
                "merge_output_format": "mp4",
            }

            if audio_only:
                ydl_opts.update({
                    "format": "bestaudio/best",
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3", "preferredquality": "192",
                    }],
                })
            else:
                ydl_opts["format"] = format

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

                if audio_only:
                    filename = Path(filename).with_suffix(".mp3")

                filepath = Path(filename)
                return DownloadResult(
                    filename=filepath.name, filepath=str(filepath),
                    filesize=filepath.stat().st_size if filepath.exists() else 0,
                    format="mp3" if audio_only else info.get("ext", "mp4"),
                    title=info.get("title", ""), duration=info.get("duration", 0),
                    url=url, status="success",
                )

        except Exception as e:
            logger.error(f"❌ Download error: {e}")
            return DownloadResult(
                filename="", filepath="", filesize=0, format="",
                title="", duration=0, url=url, status=f"error: {e}",
            )

    async def download_music(self, url: str) -> DownloadResult:
        return await self.download(url, audio_only=True)

    async def get_info(self, url: str) -> dict:
        """Get video info without downloading."""
        try:
            import yt_dlp
            with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                info = ydl.extract_info(url, download=False)
                return {
                    "title": info.get("title"), "duration": info.get("duration"),
                    "uploader": info.get("uploader"), "view_count": info.get("view_count"),
                    "thumbnail": info.get("thumbnail"),
                    "formats": [
                        {"format_id": f.get("format_id"), "ext": f.get("ext"),
                         "resolution": f.get("resolution"), "filesize": f.get("filesize")}
                        for f in (info.get("formats") or [])[:10]
                    ],
                }
        except Exception as e:
            return {"error": str(e)}

    async def batch_download(self, urls: list[str], audio_only: bool = False) -> list[DownloadResult]:
        """Download multiple URLs."""
        tasks = [self.download(url, audio_only=audio_only) for url in urls]
        return await asyncio.gather(*tasks)
