import reflex as rx
import asyncio
import json
import logging
import re
import os
import signal
from datetime import datetime
from pathlib import Path
from typing import TypedDict


class FormatData(TypedDict):
    format_id: str
    ext: str
    resolution: str
    vcodec: str
    acodec: str
    filesize: str
    format_note: str


def parse_subtitle_text(content: str, fmt: str) -> str:
    lines = content.split("""
""")
    clean_lines = []
    if fmt == "vtt":
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if (
                line.startswith("WEBVTT")
                or line.startswith("Kind:")
                or line.startswith("Language:")
            ):
                continue
            if "-->" in line:
                continue
            line = re.sub("<[^>]+>", "", line)
            if line and (not clean_lines or clean_lines[-1] != line):
                clean_lines.append(line)
    elif fmt == "srt":
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.isdigit():
                continue
            if "-->" in line:
                continue
            if line and (not clean_lines or clean_lines[-1] != line):
                clean_lines.append(line)
    else:
        return content
    return """
""".join(clean_lines)


class YTState(rx.State):
    url: str = ""
    is_loading: bool = False
    error_message: str = ""
    video_title: str = ""
    channel: str = ""
    duration: str = ""
    view_count: str = ""
    upload_date: str = ""
    thumbnail_url: str = ""
    description: str = ""
    formats: list[FormatData] = []
    subtitles: list[str] = []
    auto_captions: list[str] = []
    is_playlist: bool = False
    playlist_title: str = ""
    playlist_count: int = 0
    raw_output: str = ""
    active_tab: str = "Metadata"
    show_full_description: bool = False
    selected_preset: str = "best"
    custom_format_id: str = ""
    is_downloading: bool = False
    download_progress: float = 0.0
    download_speed: str = ""
    download_eta: str = ""
    download_size: str = ""
    download_status: str = ""
    download_log: list[str] = []
    download_process_pid: int = 0
    download_history: list[dict] = []
    subtitle_write_subs: bool = False
    subtitle_write_auto_subs: bool = False
    subtitle_langs: str = "en"
    subtitle_format: str = "srt"
    playlist_entries: list[dict] = []
    playlist_start: int = 1
    playlist_end: int = 0
    is_playlist_loading: bool = False
    lyrics_content: str = ""
    lyrics_source: str = ""
    is_fetching_lyrics: bool = False
    show_language_picker: bool = False
    selected_subtitle_lang: str = "en"
    show_available_langs: bool = False
    show_advanced_subtitle_options: bool = False

    @rx.event
    def set_tab(self, tab: str):
        self.active_tab = tab

    @rx.event
    def toggle_description(self):
        self.show_full_description = not self.show_full_description

    @rx.event
    def set_preset(self, value: str):
        self.selected_preset = value

    @rx.event
    def set_custom_format(self, value: str):
        self.custom_format_id = value

    @rx.event
    def set_subtitle_write_subs(self, val: bool):
        self.subtitle_write_subs = val

    @rx.event
    def set_subtitle_write_auto_subs(self, val: bool):
        self.subtitle_write_auto_subs = val

    @rx.event
    def set_subtitle_langs(self, val: str):
        self.subtitle_langs = val

    @rx.event
    def set_subtitle_format(self, val: str):
        self.subtitle_format = val

    @rx.event
    def set_playlist_start(self, val: str):
        try:
            self.playlist_start = int(val)
        except ValueError:
            pass

    @rx.event
    def set_playlist_end(self, val: str):
        try:
            self.playlist_end = int(val)
        except ValueError:
            pass

    @rx.event
    def clear_log(self):
        self.download_log = []

    @rx.event
    def toggle_language_picker(self):
        self.show_language_picker = not self.show_language_picker

    @rx.event
    def set_selected_subtitle_lang(self, lang: str):
        self.selected_subtitle_lang = lang

    @rx.event
    def toggle_available_langs(self):
        self.show_available_langs = not self.show_available_langs

    @rx.event
    def toggle_advanced_subtitle_options(self):
        self.show_advanced_subtitle_options = not self.show_advanced_subtitle_options

    @rx.event
    def clear_lyrics(self):
        self.lyrics_content = ""
        self.lyrics_source = ""

    @rx.event
    def copy_lyrics(self):
        return [
            rx.set_clipboard(self.lyrics_content),
            rx.toast("Lyrics copied to clipboard!", duration=3000),
        ]

    @rx.event(background=True)
    async def fetch_auto_lyrics(self):
        async with self:
            self.is_fetching_lyrics = True
            self.lyrics_content = ""
            self.lyrics_source = "Auto-generated (en)"
        content = await self._fetch_subtitles_helper("auto", "en")
        async with self:
            if content:
                self.lyrics_content = content
            else:
                self.lyrics_content = "Failed to fetch auto-generated lyrics."
            self.is_fetching_lyrics = False

    @rx.event(background=True)
    async def fetch_manual_lyrics(self):
        async with self:
            self.is_fetching_lyrics = True
            self.lyrics_content = ""
            lang = "en"
            if "en" not in self.subtitles and self.subtitles:
                lang = self.subtitles[0]
            self.lyrics_source = f"Manual ({lang})"
        content = await self._fetch_subtitles_helper("manual", lang)
        async with self:
            if content:
                self.lyrics_content = content
            else:
                self.lyrics_content = "Failed to fetch manual lyrics."
            self.is_fetching_lyrics = False

    @rx.event(background=True)
    async def fetch_lyrics_by_lang(self, lang: str):
        async with self:
            self.is_fetching_lyrics = True
            self.lyrics_content = ""
            sub_type = "auto"
            if lang in self.subtitles:
                sub_type = "manual"
            self.lyrics_source = (
                f"{('Manual' if sub_type == 'manual' else 'Auto-generated')} ({lang})"
            )
        content = await self._fetch_subtitles_helper(sub_type, lang)
        async with self:
            if content:
                self.lyrics_content = content
            else:
                self.lyrics_content = f"Failed to fetch lyrics for {lang}."
            self.is_fetching_lyrics = False

    async def _fetch_subtitles_helper(self, sub_type: str, lang: str):
        import glob, os, asyncio

        tmp_dir = "/tmp/yt-subs"
        os.makedirs(tmp_dir, exist_ok=True)
        for f in glob.glob(f"{tmp_dir}/*"):
            try:
                os.remove(f)
            except:
                logging.exception("Unexpected error")
        cmd = ["yt-dlp", "--skip-download", "-o", f"{tmp_dir}/%(id)s"]
        if sub_type == "auto":
            cmd.extend(["--write-auto-subs"])
        else:
            cmd.extend(["--write-subs"])
        cmd.extend(["--sub-langs", lang, "--sub-format", "vtt", self.url])
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        await proc.wait()
        sub_files = glob.glob(f"{tmp_dir}/*.vtt")
        if sub_files:
            with open(sub_files[0], "r", encoding="utf-8") as f:
                content = f.read()
            return parse_subtitle_text(content, "vtt")
        return None

    @rx.event
    def start_download(self):
        if not self.url or self.is_downloading:
            return
        yield YTState.run_download

    @rx.event
    def start_playlist_download(self):
        if not self.url or self.is_downloading:
            return
        yield YTState.run_playlist_download

    @rx.event
    def cancel_download(self):
        if self.is_downloading and self.download_process_pid > 0:
            try:
                os.kill(self.download_process_pid, signal.SIGTERM)
            except Exception as e:
                logging.exception(
                    f"Failed to kill process {self.download_process_pid}: {e}"
                )
            self.download_status = "Cancelled"
            self.is_downloading = False

    @rx.event(background=True)
    async def run_download(self):
        async with self:
            self.is_downloading = True
            self.download_progress = 0.0
            self.download_speed = ""
            self.download_eta = ""
            self.download_size = ""
            self.download_status = "Preparing..."
            self.download_log = []
            preset = self.selected_preset
            format_str = "bestvideo+bestaudio/best"
            is_mp3 = False
            if preset == "audio_m4a":
                format_str = "bestaudio[ext=m4a]/bestaudio"
            elif preset == "audio_mp3":
                format_str = "bestaudio"
                is_mp3 = True
            elif preset == "720p":
                format_str = "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]"
            elif preset == "480p":
                format_str = "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]"
            elif preset == "360p":
                format_str = "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360]"
            elif preset == "custom" and self.custom_format_id:
                format_str = self.custom_format_id
            dl_dir = Path("/tmp/yt-dlp-downloads")
            dl_dir.mkdir(parents=True, exist_ok=True)
            cmd = [
                "yt-dlp",
                "--newline",
                "-f",
                format_str,
                "-o",
                f"{dl_dir}/%(title)s.%(ext)s",
            ]
            if is_mp3:
                cmd.extend(["--extract-audio", "--audio-format", "mp3"])
            if self.subtitle_write_subs:
                cmd.append("--write-subs")
            if self.subtitle_write_auto_subs:
                cmd.append("--write-auto-subs")
            if self.subtitle_langs:
                cmd.extend(["--sub-langs", self.subtitle_langs])
            if self.subtitle_format:
                cmd.extend(["--sub-format", self.subtitle_format])
            cmd.append(self.url)
            self.download_log.append(f"> {' '.join(cmd)}")
            self.download_status = "Downloading..."
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
            )
            async with self:
                self.download_process_pid = proc.pid
            prog_pattern = re.compile(
                "\\[download\\]\\s+(\\d+\\.?\\d*)%\\s+of\\s+~?\\s*(\\S+)\\s+at\\s+(\\S+)\\s+ETA\\s+(\\S+)"
            )
            while True:
                line_bytes = await proc.stdout.readline()
                if not line_bytes:
                    break
                line = line_bytes.decode("utf-8", errors="replace").strip()
                if not line:
                    continue
                async with self:
                    self.download_log.append(line)
                    if len(self.download_log) > 500:
                        self.download_log = self.download_log[-500:]
                    if "[Merger]" in line:
                        self.download_status = "Merging..."
                    elif "[ExtractAudio]" in line:
                        self.download_status = "Extracting Audio..."
                    match = prog_pattern.search(line)
                    if match:
                        self.download_progress = float(match.group(1))
                        self.download_size = match.group(2)
                        self.download_speed = match.group(3)
                        self.download_eta = match.group(4)
            await proc.wait()
            async with self:
                if self.download_status == "Cancelled":
                    pass
                elif proc.returncode == 0:
                    self.download_status = "Complete!"
                    self.download_progress = 100.0
                    self.download_history.insert(
                        0,
                        {
                            "title": self.video_title,
                            "format": preset,
                            "status": "Complete",
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "filesize": self.download_size,
                        },
                    )
                else:
                    self.download_status = "Error"
                    self.download_history.insert(
                        0,
                        {
                            "title": self.video_title,
                            "format": preset,
                            "status": "Error",
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "filesize": "",
                        },
                    )
        except Exception as e:
            logging.exception("Download failed")
            async with self:
                self.download_status = "Error"
                self.download_log.append(f"Error: {str(e)}")
        finally:
            async with self:
                self.is_downloading = False
                self.download_process_pid = 0

    @rx.event(background=True)
    async def run_playlist_download(self):
        async with self:
            self.is_downloading = True
            self.download_progress = 0.0
            self.download_speed = ""
            self.download_eta = ""
            self.download_size = ""
            self.download_status = "Preparing Playlist..."
            self.download_log = []
            preset = self.selected_preset
            format_str = "bestvideo+bestaudio/best"
            is_mp3 = False
            if preset == "audio_m4a":
                format_str = "bestaudio[ext=m4a]/bestaudio"
            elif preset == "audio_mp3":
                format_str = "bestaudio"
                is_mp3 = True
            elif preset == "720p":
                format_str = "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720]"
            elif preset == "480p":
                format_str = "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480]"
            elif preset == "360p":
                format_str = "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360]"
            elif preset == "custom" and self.custom_format_id:
                format_str = self.custom_format_id
            dl_dir = Path("/tmp/yt-dlp-downloads")
            dl_dir.mkdir(parents=True, exist_ok=True)
            cmd = [
                "yt-dlp",
                "--newline",
                "-f",
                format_str,
                "-o",
                f"{dl_dir}/%(playlist_index)s - %(title)s.%(ext)s",
            ]
            if self.playlist_end > 0:
                cmd.extend(
                    ["--playlist-items", f"{self.playlist_start}:{self.playlist_end}"]
                )
            else:
                cmd.extend(["--playlist-items", f"{self.playlist_start}:"])
            if is_mp3:
                cmd.extend(["--extract-audio", "--audio-format", "mp3"])
            if self.subtitle_write_subs:
                cmd.append("--write-subs")
            if self.subtitle_write_auto_subs:
                cmd.append("--write-auto-subs")
            if self.subtitle_langs:
                cmd.extend(["--sub-langs", self.subtitle_langs])
            if self.subtitle_format:
                cmd.extend(["--sub-format", self.subtitle_format])
            cmd.append(self.url)
            self.download_log.append(f"> {' '.join(cmd)}")
            self.download_status = "Downloading Playlist..."
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
            )
            async with self:
                self.download_process_pid = proc.pid
            prog_pattern = re.compile(
                "\\[download\\]\\s+(\\d+\\.?\\d*)%\\s+of\\s+~?\\s*(\\S+)\\s+at\\s+(\\S+)\\s+ETA\\s+(\\S+)"
            )
            while True:
                line_bytes = await proc.stdout.readline()
                if not line_bytes:
                    break
                line = line_bytes.decode("utf-8", errors="replace").strip()
                if not line:
                    continue
                async with self:
                    self.download_log.append(line)
                    if len(self.download_log) > 500:
                        self.download_log = self.download_log[-500:]
                    if "[Merger]" in line:
                        self.download_status = "Merging..."
                    elif "[ExtractAudio]" in line:
                        self.download_status = "Extracting Audio..."
                    match = prog_pattern.search(line)
                    if match:
                        self.download_progress = float(match.group(1))
                        self.download_size = match.group(2)
                        self.download_speed = match.group(3)
                        self.download_eta = match.group(4)
            await proc.wait()
            async with self:
                if self.download_status == "Cancelled":
                    pass
                elif proc.returncode == 0:
                    self.download_status = "Complete!"
                    self.download_progress = 100.0
                    self.download_history.insert(
                        0,
                        {
                            "title": self.playlist_title or "Playlist Download",
                            "format": preset,
                            "status": "Complete",
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "filesize": self.download_size,
                        },
                    )
                else:
                    self.download_status = "Error"
                    self.download_history.insert(
                        0,
                        {
                            "title": self.playlist_title or "Playlist Download",
                            "format": preset,
                            "status": "Error",
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "filesize": "",
                        },
                    )
        except Exception as e:
            logging.exception("Playlist download failed")
            async with self:
                self.download_status = "Error"
                self.download_log.append(f"Error: {str(e)}")
        finally:
            async with self:
                self.is_downloading = False
                self.download_process_pid = 0

    @rx.event
    def handle_submit(self, form_data: dict):
        url = form_data.get("url", "").strip()
        if not url:
            self.error_message = "Please enter a valid URL."
            return
        self.error_message = ""
        self.url = url
        yield YTState.process_url(url)

    @rx.event(background=True)
    async def process_url(self, url: str):
        async with self:
            self.is_loading = True
            self.error_message = ""
            self.video_title = ""
            self.formats = []
            self.raw_output = ""
            self.thumbnail_url = ""
            self.lyrics_content = ""
            self.lyrics_source = ""
            self.show_language_picker = False
            self.active_tab = "Metadata"
        try:
            proc = await asyncio.create_subprocess_exec(
                "yt-dlp",
                "--dump-json",
                "--no-download",
                url,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode != 0:
                async with self:
                    self.error_message = f"yt-dlp error: {stderr.decode()[:500]}"
                    self.is_loading = False
                return
            data = json.loads(stdout.decode())
            async with self:
                self.raw_output = json.dumps(data, indent=2)
                self.video_title = data.get("title", "Unknown Title")
                self.channel = data.get("channel", "Unknown Channel")
                dur_sec = data.get("duration", 0)
                if dur_sec:
                    m, s = divmod(dur_sec, 60)
                    h, m = divmod(m, 60)
                    if h > 0:
                        self.duration = f"{h}:{m:02d}:{s:02d}"
                    else:
                        self.duration = f"{m}:{s:02d}"
                else:
                    self.duration = "N/A"
                views = data.get("view_count", 0)
                self.view_count = f"{views:,}" if views else "N/A"
                udate = data.get("upload_date", "")
                if udate and len(udate) == 8:
                    self.upload_date = f"{udate[:4]}-{udate[4:6]}-{udate[6:]}"
                else:
                    self.upload_date = udate or "N/A"
                self.thumbnail_url = data.get("thumbnail", "")
                self.description = data.get("description", "")
                raw_formats = data.get("formats", [])
                processed_formats = []
                for fmt in raw_formats:
                    ext = fmt.get("ext", "")
                    if (
                        ext in ["mhtml"]
                        or "storyboard" in fmt.get("format_note", "").lower()
                    ):
                        continue
                    width = fmt.get("width")
                    height = fmt.get("height")
                    if width and height:
                        res = f"{width}x{height}"
                        res_val = width * height
                    else:
                        res = "audio only"
                        res_val = 0
                    fs = fmt.get("filesize") or fmt.get("filesize_approx") or 0
                    if fs > 1024**3:
                        fs_str = f"{fs / 1024**3:.2f} GB"
                    elif fs > 1024**2:
                        fs_str = f"{fs / 1024**2:.2f} MB"
                    elif fs > 1024:
                        fs_str = f"{fs / 1024:.2f} KB"
                    elif fs > 0:
                        fs_str = f"{fs} B"
                    else:
                        fs_str = "N/A"
                    processed_formats.append(
                        {
                            "format_id": str(fmt.get("format_id", "")),
                            "ext": ext,
                            "resolution": res,
                            "vcodec": fmt.get("vcodec", "none"),
                            "acodec": fmt.get("acodec", "none"),
                            "filesize": fs_str,
                            "format_note": fmt.get("format_note", ""),
                            "_res_val": res_val,
                        }
                    )
                processed_formats.sort(key=lambda x: x["_res_val"], reverse=True)
                self.formats = [
                    {k: v for k, v in f.items() if k != "_res_val"}
                    for f in processed_formats
                ]
                self.subtitles = list(data.get("subtitles", {}).keys())
                self.auto_captions = list(data.get("automatic_captions", {}).keys())
                if data.get("_type") == "playlist" or "entries" in data:
                    self.is_playlist = True
                    self.playlist_title = data.get("title", "Unknown Playlist")
                    self.playlist_count = data.get("playlist_count") or len(
                        data.get("entries", [])
                    )
                    self.is_loading = False
                    yield YTState.fetch_playlist_entries
                else:
                    self.is_playlist = False
                    self.is_loading = False
        except Exception as e:
            logging.exception(f"Error fetching URL: {e}")
            async with self:
                self.error_message = f"An unexpected error occurred while fetching."
                self.is_loading = False

    @rx.event(background=True)
    async def fetch_playlist_entries(self):
        async with self:
            self.is_playlist_loading = True
            self.playlist_entries = []
        try:
            proc = await asyncio.create_subprocess_exec(
                "yt-dlp",
                "--flat-playlist",
                "--dump-json",
                self.url,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            while True:
                line_bytes = await proc.stdout.readline()
                if not line_bytes:
                    break
                line = line_bytes.decode("utf-8", errors="replace").strip()
                if not line:
                    continue
                try:
                    entry_data = json.loads(line)
                    async with self:
                        idx = (
                            entry_data.get("playlist_index")
                            or len(self.playlist_entries) + 1
                        )
                        dur_sec = entry_data.get("duration", 0)
                        if dur_sec:
                            m, s = divmod(dur_sec, 60)
                            h, m = divmod(m, 60)
                            duration = (
                                f"{h}:{m:02d}:{s:02d}" if h > 0 else f"{m}:{s:02d}"
                            )
                        else:
                            duration = "N/A"
                        self.playlist_entries.append(
                            {
                                "index": idx,
                                "title": entry_data.get("title", "Unknown Title"),
                                "url": entry_data.get("url", ""),
                                "duration": duration,
                                "uploader": entry_data.get("uploader", "Unknown"),
                            }
                        )
                except Exception as e:
                    logging.exception(f"Error parsing playlist entry: {e}")
            await proc.wait()
        except Exception as e:
            logging.exception(f"Error fetching playlist entries: {e}")
        finally:
            async with self:
                self.is_playlist_loading = False