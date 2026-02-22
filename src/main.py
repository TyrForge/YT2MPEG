#!/usr/bin/env python3

import sys
import os
import re
import platform
from pathlib import Path

IS_WINDOWS = platform.system() == "Windows"

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QCheckBox, QFileDialog,
    QScrollArea, QFrame, QProgressBar, QMessageBox, QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal, QObject, QTimer
from PySide6.QtGui import QColor, QPalette, QFont, QClipboard

try:
    import yt_dlp
except ImportError:
    app = QApplication(sys.argv)
    QMessageBox.critical(None, "Missing dependency",
        "yt-dlp is not installed.\n\nRun:  pip install yt-dlp")
    sys.exit(1)


# ─── Constants ────────────────────────────────────────────────────────────────

def _default_music_dir():
    if IS_WINDOWS:
        # Use Windows Music library if available, fallback to ~/Music
        music = os.environ.get("USERPROFILE", str(Path.home()))
        return str(Path(music) / "Music")
    return str(Path.home() / "Music")

DEFAULT_MUSIC_DIR = _default_music_dir()

AUDIO_FORMATS = [
    ("MP3  -  most compatible",    "mp3"),
    ("Opus  -  best size/quality", "opus"),
    ("FLAC  -  lossless",          "flac"),
    ("M4A  -  Apple devices",      "m4a"),
    ("WAV  -  uncompressed",       "wav"),
    ("MP4  -  Video Format",       "mp4"),
]

ORGANIZE_MODES = [
    ("Artist / Album / Track", "artist_album"),
    ("Artist / Track",         "artist"),
    ("Flat (no subfolders)",   "flat"),
]

C = {
    "bg":      "#0d0d0d",
    "surface": "#161616",
    "surf2":   "#1e1e1e",
    "border":  "#2a2a2a",
    "accent":  "#c8f04a",
    "accent2": "#4af0c8",
    "text":    "#e8e8e8",
    "muted":   "#666666",
    "danger":  "#f05a4a",
}

STYLESHEET = f"""
QWidget {{
    background: transparent;
    color: {C['text']};
    font-family: 'Segoe UI', 'SF Pro Display', system-ui, sans-serif;
    font-size: 13px;
}}
QMainWindow, #root {{ background: {C['bg']}; }}
#sidebar {{ background: {C['surface']}; border-right: 1px solid {C['border']}; }}
#header  {{ background: {C['surface']}; border-bottom: 1px solid {C['border']}; }}
#footer  {{ background: {C['surface']}; border-top: 1px solid {C['border']}; }}

QLabel {{ background: transparent; }}
#section {{
    color: {C['muted']}; font-size: 10px;
    font-family: 'Courier New', monospace; letter-spacing: 2px;
}}
#muted  {{ color: {C['muted']}; font-size: 11px; }}
#code   {{
    background: {C['surf2']}; border: 1px solid {C['border']};
    border-radius: 6px; color: {C['accent']};
    font-family: 'Courier New', monospace; font-size: 11px;
    padding: 8px 12px;
}}

QLineEdit {{
    background: {C['surf2']}; border: 1px solid {C['border']};
    border-radius: 7px; color: {C['text']};
    padding: 9px 13px;
    font-family: 'Courier New', monospace; font-size: 12px;
    selection-background-color: {C['accent']}; selection-color: #000;
}}
QLineEdit:focus {{ border: 1px solid {C['accent']}; }}

QComboBox {{
    background: {C['surf2']}; border: 1px solid {C['border']};
    border-radius: 7px; color: {C['text']};
    padding: 9px 13px; font-size: 12px;
}}
QComboBox:focus, QComboBox:on {{ border: 1px solid {C['accent']}; }}
QComboBox::drop-down {{ border: none; width: 28px; }}
QComboBox::down-arrow {{
    border-left: 4px solid transparent; border-right: 4px solid transparent;
    border-top: 5px solid {C['muted']}; width: 0; height: 0; margin-right: 10px;
}}
QComboBox QAbstractItemView {{
    background: {C['surf2']}; border: 1px solid {C['border']};
    color: {C['text']}; selection-background-color: {C['accent']};
    selection-color: #000; padding: 4px;
}}

QPushButton {{
    background: {C['surf2']}; border: 1px solid {C['border']};
    border-radius: 7px; color: {C['muted']};
    padding: 9px 18px; font-family: 'Courier New', monospace;
    font-size: 12px; font-weight: bold; letter-spacing: 0.5px;
}}
QPushButton:hover {{ border: 1px solid {C['accent']}; color: {C['accent']}; }}
QPushButton:pressed {{ background: #222; }}
QPushButton:disabled {{ background: {C['surface']}; border: 1px solid {C['border']}; color: {C['border']}; }}

#accent {{ background: {C['accent']}; border: none; color: #0d0d0d; padding: 10px 22px; }}
#accent:hover {{ background: #d4f55a; }}
#accent:disabled {{ background: {C['border']}; color: {C['muted']}; }}

#download {{
    background: {C['accent']}; border: none; color: #0d0d0d;
    font-size: 14px; font-weight: bold; padding: 13px 32px;
    border-radius: 10px; letter-spacing: 0.5px;
}}
#download:hover {{ background: #d4f55a; }}
#download:disabled {{ background: {C['border']}; color: {C['muted']}; }}

#danger {{ background: transparent; border: 1px solid {C['danger']}; color: {C['danger']}; }}
#danger:hover {{ background: {C['danger']}; color: white; }}

QCheckBox {{ color: {C['text']}; spacing: 8px; font-size: 13px; }}
QCheckBox::indicator {{
    width: 18px; height: 18px;
    border: 1px solid {C['border']}; border-radius: 5px;
    background: {C['surf2']};
}}
QCheckBox::indicator:checked {{
    background: {C['accent']}; border: 1px solid {C['accent']};
}}
QCheckBox::indicator:hover {{ border: 1px solid {C['accent']}; }}

QScrollArea {{ border: none; background: transparent; }}
QScrollBar:vertical {{
    background: {C['surface']}; width: 6px; border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {C['border']}; border-radius: 3px; min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background: {C['muted']}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

QProgressBar {{
    background: {C['border']}; border: none;
    border-radius: 3px; max-height: 4px; text-align: center; font-size: 0px;
}}
QProgressBar::chunk {{ background: {C['accent2']}; border-radius: 3px; }}
QProgressBar[done="true"]::chunk {{ background: {C['accent']}; }}

#sep {{ background: {C['border']}; max-height: 1px; min-height: 1px; }}

#qitem           {{ background: {C['surf2']}; border: 1px solid {C['border']};     border-radius: 10px; }}
#qitem_dl        {{ background: {C['surf2']}; border: 1px solid {C['accent2']};    border-radius: 10px; }}
#qitem_done      {{ background: {C['surf2']}; border: 1px solid {C['accent']};     border-radius: 10px; }}
#qitem_error     {{ background: {C['surf2']}; border: 1px solid {C['danger']};     border-radius: 10px; }}
"""


# ─── Download Worker ──────────────────────────────────────────────────────────

class DownloadWorker(QObject):
    progress = Signal(str, float, str)
    finished = Signal(str)
    error    = Signal(str, str)

    def __init__(self, item_id, url, opts):
        super().__init__()
        self.item_id = item_id
        self.url     = url
        self.opts    = opts
        self._abort  = False

    def abort(self):
        self._abort = True

    def run(self):
        me = self

        def hook(d):
            if me._abort:
                raise yt_dlp.utils.DownloadError("Aborted")
            if d['status'] == 'downloading':
                try:
                    pct = float(d.get('_percent_str', '0%').strip().rstrip('%'))
                except ValueError:
                    pct = 0.0
                speed = d.get('_speed_str', '').strip()
                eta   = d.get('_eta_str', '').strip()
                txt = f"Downloading…  {speed}" + (f"  ETA {eta}" if eta else "")
                me.progress.emit(me.item_id, pct * 0.85, txt)
            elif d['status'] == 'finished':
                me.progress.emit(me.item_id, 90.0, "Converting & embedding metadata…")

        opts = {**self.opts, 'quiet': True, 'no_warnings': True,
                'progress_hooks': [hook]}
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                ydl.download([self.url])
            me.progress.emit(me.item_id, 100.0, "Done!")
            me.finished.emit(me.item_id)
        except Exception as e:
            if not me._abort:
                me.error.emit(me.item_id, str(e)[:120])


class DownloadThread(QThread):
    def __init__(self, worker):
        super().__init__()
        self.worker = worker
        self.worker.moveToThread(self)

    def run(self):
        self.worker.run()


# ─── Queue Item ───────────────────────────────────────────────────────────────

class QueueItem(QFrame):
    remove_requested = Signal(str)

    ICONS   = {"queued": "⏳", "downloading": "↓", "done": "✓", "error": "✗"}
    COLORS  = {"queued": C["muted"], "downloading": C["accent2"], "done": C["accent"], "error": C["danger"]}
    NAMES   = {"queued": "qitem", "downloading": "qitem_dl", "done": "qitem_done", "error": "qitem_error"}

    def __init__(self, item_id, url, parent=None):
        super().__init__(parent)
        self.item_id = item_id
        self.url = url
        self.status = "queued"
        self.setObjectName("qitem")
        self.setFixedHeight(90)
        self._build()

    def _build(self):
        row = QHBoxLayout(self)
        row.setContentsMargins(14, 12, 14, 12)
        row.setSpacing(12)

        self.icon = QLabel("⏳")
        self.icon.setFixedWidth(24)
        self.icon.setAlignment(Qt.AlignCenter)
        f = QFont(); f.setPointSize(16)
        self.icon.setFont(f)
        row.addWidget(self.icon)

        col = QVBoxLayout()
        col.setSpacing(3)

        short = self.url if len(self.url) <= 72 else self.url[:69] + "..."
        self.url_lbl = QLabel(short)
        self.url_lbl.setObjectName("muted")
        self.url_lbl.setFont(QFont("Courier New", 10))
        col.addWidget(self.url_lbl)

        self.status_lbl = QLabel("Queued")
        col.addWidget(self.status_lbl)

        self.bar = QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setValue(0)
        self.bar.setVisible(False)
        col.addWidget(self.bar)

        row.addLayout(col, stretch=1)

        rm = QPushButton("✕")
        rm.setFixedSize(28, 28)
        rm.setCursor(Qt.PointingHandCursor)
        rm.setToolTip("Remove")
        rm.clicked.connect(lambda: self.remove_requested.emit(self.item_id))
        row.addWidget(rm)

    def set_status(self, status, text, pct=0.0):
        self.status = status
        self.setObjectName(self.NAMES.get(status, "qitem"))
        self.style().unpolish(self); self.style().polish(self)

        self.icon.setText(self.ICONS.get(status, "?"))
        self.status_lbl.setText(text)
        self.status_lbl.setStyleSheet(f"color: {self.COLORS.get(status, C['text'])};")

        if status == "downloading":
            self.bar.setVisible(True)
            self.bar.setValue(int(pct))
            self.bar.setProperty("done", False)
        elif status == "done":
            self.bar.setVisible(True)
            self.bar.setValue(100)
            self.bar.setProperty("done", True)
        else:
            self.bar.setVisible(False)

        self.bar.style().unpolish(self.bar); self.bar.style().polish(self.bar)


# ─── Main Window ──────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YT2MPEG")
        self.setMinimumSize(880, 600)
        self.resize(1040, 680)
        self._items:   dict[str, QueueItem]     = {}
        self._threads: dict[str, DownloadThread] = {}
        self._counter  = 0
        self._running  = False
        self._pending  = 0
        self._build()
        self.setAcceptDrops(True)

    def _build(self):
        root = QWidget(); root.setObjectName("root")
        self.setCentralWidget(root)
        vbox = QVBoxLayout(root)
        vbox.setContentsMargins(0, 0, 0, 0); vbox.setSpacing(0)
        vbox.addWidget(self._mk_header())

        body_w = QWidget()
        body = QHBoxLayout(body_w)
        body.setContentsMargins(0, 0, 0, 0); body.setSpacing(0)
        body.addWidget(self._mk_sidebar())
        body.addWidget(self._mk_content(), stretch=1)
        vbox.addWidget(body_w, stretch=1)

    # ── Header ────────────────────────────────────────────────────────────────
    def _mk_header(self):
        h = QWidget(); h.setObjectName("header"); h.setFixedHeight(64)
        row = QHBoxLayout(h); row.setContentsMargins(24, 0, 24, 0); row.setSpacing(14)

        logo = QLabel("🎵")
        logo.setFixedSize(38, 38); logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet(f"background:{C['accent']}; border-radius:9px; font-size:18px;")
        row.addWidget(logo)

        col = QVBoxLayout(); col.setSpacing(1)
        t = QLabel("YT2MPEG")
        t.setStyleSheet("font-size:18px; font-weight:700;")
        col.addWidget(t)
        s = QLabel("yt-dlp · YT2MPEG"); s.setObjectName("muted")
        col.addWidget(s)
        row.addLayout(col)
        row.addStretch()

        badge = QLabel("PERSONAL USE ONLY")
        badge.setStyleSheet(
            f"background:#1a2a0a; border:1px solid {C['accent']}; color:{C['accent']};"
            "font-family:'Courier New'; font-size:10px; padding:4px 12px;"
            "border-radius:4px; letter-spacing:1px;")
        row.addWidget(badge)
        return h

    # ── Sidebar ───────────────────────────────────────────────────────────────
    def _mk_sidebar(self):
        sb = QWidget(); sb.setObjectName("sidebar"); sb.setFixedWidth(295)
        v = QVBoxLayout(sb); v.setContentsMargins(22, 22, 22, 22); v.setSpacing(0)

        v.addWidget(self._lbl("OUTPUT"))
        v.addSpacing(8)
        v.addWidget(self._field_lbl("Media folder"))
        v.addSpacing(5)

        row = QHBoxLayout(); row.setSpacing(6)
        self.folder_input = QLineEdit(DEFAULT_MUSIC_DIR)
        self.folder_input.setPlaceholderText("~/Music")
        self.folder_input.textChanged.connect(self._update_cmd)
        row.addWidget(self.folder_input)
        br = QPushButton("…"); br.setFixedWidth(36)
        br.setCursor(Qt.PointingHandCursor)
        br.clicked.connect(self._browse)
        row.addWidget(br)
        v.addLayout(row)

        v.addSpacing(20); v.addWidget(self._sep()); v.addSpacing(20)

        v.addWidget(self._lbl("MEDIA"))
        v.addSpacing(8)
        v.addWidget(self._field_lbl("Format"))
        v.addSpacing(5)
        self.fmt_combo = QComboBox()
        for lbl, val in AUDIO_FORMATS: self.fmt_combo.addItem(lbl, val)
        self.fmt_combo.currentIndexChanged.connect(self._update_cmd)
        v.addWidget(self.fmt_combo)

        v.addSpacing(12)
        v.addWidget(self._field_lbl("Folder structure"))
        v.addSpacing(5)
        self.org_combo = QComboBox()
        for lbl, val in ORGANIZE_MODES: self.org_combo.addItem(lbl, val)
        self.org_combo.currentIndexChanged.connect(self._update_cmd)
        v.addWidget(self.org_combo)

        v.addSpacing(20); v.addWidget(self._sep()); v.addSpacing(20)

        v.addWidget(self._lbl("METADATA"))
        v.addSpacing(10)
        self.chk_thumb = QCheckBox("Embed cover art"); self.chk_thumb.setChecked(True)
        self.chk_thumb.stateChanged.connect(self._update_cmd)
        v.addWidget(self.chk_thumb)
        sub1 = QLabel("Downloads & embeds album thumbnail"); sub1.setObjectName("muted")
        sub1.setContentsMargins(26,0,0,0); v.addWidget(sub1)

        v.addSpacing(12)
        self.chk_meta = QCheckBox("Embed metadata tags"); self.chk_meta.setChecked(True)
        self.chk_meta.stateChanged.connect(self._update_cmd)
        v.addWidget(self.chk_meta)
        sub2 = QLabel("Artist, album, year, track number"); sub2.setObjectName("muted")
        sub2.setContentsMargins(26,0,0,0); v.addWidget(sub2)

        v.addSpacing(20); v.addWidget(self._sep()); v.addSpacing(20)

        if IS_WINDOWS:
            setup_cmd = (
                "pip install yt-dlp PySide6<br>"
                "# Download ffmpeg from ffmpeg.org<br>"
                "# and add it to your PATH")
        else:
            setup_cmd = (
                "pip install yt-dlp PySide6<br>"
                "sudo apt install ffmpeg")
        hint = QLabel(
            "<b style='color:#888'>Setup</b><br>"
            f"<code style='color:{C['accent']};font-size:11px'>"
            f"{setup_cmd}</code>")
        hint.setStyleSheet("color:#555; font-size:11px; line-height:1.6;")
        hint.setWordWrap(True)
        v.addWidget(hint)
        v.addStretch()
        return sb

    # ── Content ───────────────────────────────────────────────────────────────
    def _mk_content(self):
        w = QWidget()
        v = QVBoxLayout(w); v.setContentsMargins(0,0,0,0); v.setSpacing(0)

        # URL bar
        url_bar = QWidget()
        ub = QVBoxLayout(url_bar); ub.setContentsMargins(26,20,26,20); ub.setSpacing(10)
        ub.addWidget(self._lbl("DOWNLOAD QUEUE"))
        row = QHBoxLayout(); row.setSpacing(10)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(
            "Paste YouTube / SoundCloud / Bandcamp URL…  (or drag & drop)")
        self.url_input.setFixedHeight(42)
        self.url_input.returnPressed.connect(self._add_url)
        row.addWidget(self.url_input)
        add_btn = QPushButton("ADD"); add_btn.setObjectName("accent")
        add_btn.setFixedHeight(42); add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._add_url)
        row.addWidget(add_btn)
        ub.addLayout(row)
        hint = QLabel("Supports single tracks, full playlists, albums, and channels.")
        hint.setObjectName("muted"); ub.addWidget(hint)
        v.addWidget(url_bar)
        v.addWidget(self._sep())

        # Queue scroll
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.q_widget = QWidget()
        self.q_layout = QVBoxLayout(self.q_widget)
        self.q_layout.setContentsMargins(26,16,26,16)
        self.q_layout.setSpacing(10)
        self.q_layout.setAlignment(Qt.AlignTop)

        self.empty_lbl = QLabel(
            f"<div style='text-align:center;color:{C['muted']}'>"
            "<div style='font-size:48px;margin-bottom:12px'>📭</div>"
            "<div style='font-family:Courier New;font-size:13px'>No URLs in queue yet</div>"
            "<div style='font-size:12px;margin-top:6px'>"
            "Paste a URL above or drag &amp; drop links here</div></div>")
        self.empty_lbl.setAlignment(Qt.AlignCenter)
        self.empty_lbl.setMinimumHeight(200)
        self.q_layout.addWidget(self.empty_lbl)

        self.scroll.setWidget(self.q_widget)
        v.addWidget(self.scroll, stretch=1)
        v.addWidget(self._sep())

        # Command preview
        cmd_w = QWidget()
        cmd_l = QVBoxLayout(cmd_w); cmd_l.setContentsMargins(26,14,26,14); cmd_l.setSpacing(6)
        ch = QHBoxLayout()
        ch.addWidget(self._lbl("EQUIVALENT CLI COMMAND"))
        ch.addStretch()
        cp = QPushButton("COPY"); cp.setFixedHeight(26)
        cp.setCursor(Qt.PointingHandCursor)
        cp.clicked.connect(self._copy_cmd)
        ch.addWidget(cp)
        cmd_l.addLayout(ch)
        self.cmd_lbl = QLabel("python main.py  # (add URLs above)")
        self.cmd_lbl.setObjectName("code"); self.cmd_lbl.setWordWrap(True)
        cmd_l.addWidget(self.cmd_lbl)
        v.addWidget(cmd_w)
        v.addWidget(self._sep())

        # Footer
        ft = QWidget(); ft.setObjectName("footer")
        fl = QHBoxLayout(ft); fl.setContentsMargins(26,14,26,14); fl.setSpacing(12)
        self.dl_btn = QPushButton("⬇  Download")
        self.dl_btn.setObjectName("download"); self.dl_btn.setFixedHeight(48)
        self.dl_btn.setCursor(Qt.PointingHandCursor); self.dl_btn.setEnabled(False)
        self.dl_btn.clicked.connect(self._start)
        fl.addWidget(self.dl_btn)

        self.clr_done_btn = QPushButton("Clear finished")
        self.clr_done_btn.setFixedHeight(40); self.clr_done_btn.setCursor(Qt.PointingHandCursor)
        self.clr_done_btn.setVisible(False); self.clr_done_btn.clicked.connect(self._clear_done)
        fl.addWidget(self.clr_done_btn)

        self.clr_all_btn = QPushButton("Clear all"); self.clr_all_btn.setObjectName("danger")
        self.clr_all_btn.setFixedHeight(40); self.clr_all_btn.setCursor(Qt.PointingHandCursor)
        self.clr_all_btn.setVisible(False); self.clr_all_btn.clicked.connect(self._clear_all)
        fl.addWidget(self.clr_all_btn)

        fl.addStretch()
        self.status_lbl = QLabel("idle")
        self.status_lbl.setStyleSheet(
            f"color:{C['muted']}; font-family:'Courier New'; font-size:11px;")
        fl.addWidget(self.status_lbl)
        v.addWidget(ft)
        return w

    # ── UI helpers ────────────────────────────────────────────────────────────
    def _lbl(self, t):
        l = QLabel(t); l.setObjectName("section"); return l

    def _field_lbl(self, t):
        l = QLabel(t); l.setStyleSheet("color:#bbb; font-size:13px; font-weight:500;")
        return l

    def _sep(self):
        f = QFrame(); f.setObjectName("sep"); f.setFrameShape(QFrame.HLine); return f

    # ── Actions ───────────────────────────────────────────────────────────────
    def _browse(self):
        current = os.path.expanduser(self.folder_input.text() or DEFAULT_MUSIC_DIR)
        d = QFileDialog.getExistingDirectory(self, "Select Media Folder", current)
        if d: self.folder_input.setText(d)

    def _add_url(self):
        raw = self.url_input.text().strip()
        if not raw: return
        if not raw.startswith(("http://", "https://")):
            self.url_input.setStyleSheet(f"border:1px solid {C['danger']};")
            QTimer.singleShot(1500, lambda: self.url_input.setStyleSheet(""))
            return
        self._counter += 1
        iid = f"item_{self._counter}"
        item = QueueItem(iid, raw)
        item.remove_requested.connect(self._remove)
        self._items[iid] = item
        self.q_layout.addWidget(item)
        self.url_input.clear()
        self._update_cmd(); self._update_state()

    def _remove(self, iid):
        if iid in self._items:
            w = self._items.pop(iid)
            self.q_layout.removeWidget(w); w.deleteLater()
        if iid in self._threads:
            self._threads[iid].worker.abort()
        self._update_cmd(); self._update_state()

    def _clear_done(self):
        for iid in [i for i, w in self._items.items() if w.status in ("done","error")]:
            self._remove(iid)

    def _clear_all(self):
        for iid in list(self._items): self._remove(iid)

    def _update_cmd(self):
        parts = ["python main.py"]
        folder = self.folder_input.text().strip()
        if folder and folder != DEFAULT_MUSIC_DIR:
            # Quote paths properly — on Windows backslashes need quoting too
            parts.append(f'--dir "{folder}"')
        fmt = self.fmt_combo.currentData()
        if fmt != "mp3": parts.append(f"--format {fmt}")
        org = self.org_combo.currentData()
        if org != "artist_album": parts.append(f"--organize {org}")
        if not self.chk_thumb.isChecked(): parts.append("--no-thumbnail")
        if not self.chk_meta.isChecked():  parts.append("--no-metadata")
        urls = [w.url for w in self._items.values()]
        for u in urls: parts.append(f'"{u}"')
        sep = " ^\n  " if IS_WINDOWS else " \\\n  "
        cmd = sep.join(parts) if urls else "python main.py  # (add URLs)"
        self.cmd_lbl.setText(cmd)

    def _copy_cmd(self):
        QApplication.clipboard().setText(self.cmd_lbl.text())

    def _update_state(self):
        items = list(self._items.values())
        has_q  = any(i.status == "queued" for i in items)
        has_dn = any(i.status in ("done","error") for i in items)
        q_cnt  = sum(1 for i in items if i.status == "queued")
        dn_cnt = sum(1 for i in items if i.status == "done")

        self.dl_btn.setEnabled(has_q and not self._running)
        self.clr_done_btn.setVisible(has_dn)
        self.clr_all_btn.setVisible(bool(items) and not self._running)
        self.empty_lbl.setVisible(not items)

        if self._running:
            self.dl_btn.setText("⏳  Downloading…")
            self.status_lbl.setText("downloading")
            self.status_lbl.setStyleSheet(
                f"color:{C['accent']}; font-family:'Courier New'; font-size:11px;")
        else:
            self.dl_btn.setText(f"⬇  Download ({q_cnt})" if q_cnt else "⬇  Download")
            parts = []
            if dn_cnt: parts.append(f"{dn_cnt} done")
            if q_cnt:  parts.append(f"{q_cnt} queued")
            self.status_lbl.setText("  ·  ".join(parts) or "idle")
            self.status_lbl.setStyleSheet(
                f"color:{C['muted']}; font-family:'Courier New'; font-size:11px;")

    # ── yt-dlp opts ───────────────────────────────────────────────────────────
    def _get_opts(self):
        base  = os.path.expanduser(self.folder_input.text() or DEFAULT_MUSIC_DIR)
        fmt   = self.fmt_combo.currentData()
        org   = self.org_combo.currentData()
        thumb = self.chk_thumb.isChecked()
        meta  = self.chk_meta.isChecked()

        is_video = fmt == "mp4"

        # Use Path for cross-platform path joining
        templates = {
            "artist_album": str(Path(base) / "%(artist,uploader)s"
                                            / "%(album,playlist_title,NA)s"
                                            / "%(title)s.%(ext)s"),
            "artist":       str(Path(base) / "%(artist,uploader)s"
                                            / "%(title)s.%(ext)s"),
            "flat":         str(Path(base) / "%(title)s.%(ext)s"),
        }

        if is_video:
            pp = [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}]
            if meta: pp.append({"key": "FFmpegMetadata", "add_metadata": True})
        else:
            pp = [{"key": "FFmpegExtractAudio", "preferredcodec": fmt, "preferredquality": "0"}]
            if meta:  pp.append({"key": "FFmpegMetadata", "add_metadata": True})
            if thumb: pp.append({"key": "EmbedThumbnail", "already_have_thumbnail": False})

        os.makedirs(base, exist_ok=True)
        return {
            "format":           "bestvideo+bestaudio/best" if is_video else "bestaudio/best",
            "outtmpl":          templates.get(org, templates["artist_album"]),
            "postprocessors":   pp,
            "writethumbnail":   thumb and not is_video,
            "embedthumbnail":   thumb and not is_video,
            "addmetadata":      meta,
            "ignoreerrors":     True,
            "trim_filenames":   200,
            # Windows-safe: restrict characters in output filenames
            "windowsfilenames": IS_WINDOWS,
        }

    # ── Download ──────────────────────────────────────────────────────────────
    def _start(self):
        queued = [(iid, w) for iid, w in self._items.items() if w.status == "queued"]
        if not queued: return
        self._running = True
        self._pending = len(queued)
        self._update_state()
        opts = self._get_opts()

        for iid, item in queued:
            item.set_status("downloading", "Starting…", 0)
            worker = DownloadWorker(iid, item.url, opts)
            worker.progress.connect(self._on_prog)
            worker.finished.connect(self._on_done)
            worker.error.connect(self._on_err)
            t = DownloadThread(worker)
            self._threads[iid] = t
            t.start()

    def _on_prog(self, iid, pct, txt):
        if iid in self._items:
            self._items[iid].set_status("downloading", txt, pct)

    def _on_done(self, iid):
        if iid in self._items:
            self._items[iid].set_status("done", "Done! ✓", 100)
        self._thread_done(iid)

    def _on_err(self, iid, msg):
        if iid in self._items:
            self._items[iid].set_status("error", f"Error: {msg}")
        self._thread_done(iid)

    def _thread_done(self, iid):
        if iid in self._threads:
            self._threads[iid].quit()
            self._threads[iid].wait()
            del self._threads[iid]
        self._pending -= 1
        if self._pending <= 0:
            self._running = False
            self._update_state()

    # ── Drag & drop ───────────────────────────────────────────────────────────
    def dragEnterEvent(self, e):
        if e.mimeData().hasText() or e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e):
        if e.mimeData().hasUrls():
            for u in e.mimeData().urls():
                self.url_input.setText(u.toString()); self._add_url()
        elif e.mimeData().hasText():
            self.url_input.setText(e.mimeData().text().strip()); self._add_url()


# ─── Entry point ──────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("YT2MPEG")

    pal = QPalette()
    for role, hex_col in [
        (QPalette.Window,        C["bg"]),
        (QPalette.WindowText,    C["text"]),
        (QPalette.Base,          C["surf2"]),
        (QPalette.AlternateBase, C["surface"]),
        (QPalette.Text,          C["text"]),
        (QPalette.Button,        C["surf2"]),
        (QPalette.ButtonText,    C["text"]),
        (QPalette.Highlight,     C["accent"]),
        (QPalette.HighlightedText, "#000000"),
    ]:
        pal.setColor(role, QColor(hex_col))
    app.setPalette(pal)
    app.setStyleSheet(STYLESHEET)

    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
