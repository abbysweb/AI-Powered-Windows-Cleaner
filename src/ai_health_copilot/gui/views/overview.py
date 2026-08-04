import platform
from datetime import datetime, timezone

import psutil
import pyqtgraph as pg
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


def _fmt_size(b: int) -> str:
    if b >= 1024**3:
        return f"{b / 1024**3:.1f} GB"
    if b >= 1024**2:
        return f"{b / 1024**2:.1f} MB"
    if b >= 1024:
        return f"{b / 1024:.1f} KB"
    return f"{b} B"


def _compute_health() -> int:
    """Simple 0-100 health score based on CPU / RAM / Disk pressure."""
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    try:
        disk = psutil.disk_usage("C:\\").percent
    except OSError:
        disk = 0.0
    penalty = (cpu / 100) * 20 + (ram / 100) * 40 + (disk / 100) * 40
    return max(0, int(100 - penalty))


class MetricTile(QFrame):
    """A compact status tile: icon + label + big value + subtitle."""

    def __init__(
        self,
        icon: str,
        title: str,
        value: str,
        subtitle: str,
        accent: str = "#2196F3",
        parent=None,
    ):
        super().__init__(parent)
        self._accent = accent
        self.setStyleSheet(
            f"QFrame {{ background-color: rgba(255,255,255,0.75); border-radius: 12px; "
            f"border: 1px solid rgba(0,0,0,0.08); border-top: 3px solid {accent}; }}"
        )
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(18)
        shadow.setColor(QColor(0, 0, 0, 25))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        top = QHBoxLayout()
        lbl_icon = QLabel(icon)
        lbl_icon.setStyleSheet("font-size: 20px; background: transparent; border: none;")
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("font-size: 12px; color: #777; font-weight: 600; background: transparent; border: none;")
        top.addWidget(lbl_icon)
        top.addWidget(lbl_title)
        top.addStretch()
        layout.addLayout(top)

        self.lbl_value = QLabel(value)
        self.lbl_value.setStyleSheet(
            f"font-size: 28px; font-weight: bold; color: {accent}; background: transparent; border: none;"
        )
        layout.addWidget(self.lbl_value)

        self.lbl_sub = QLabel(subtitle)
        self.lbl_sub.setStyleSheet("font-size: 11px; color: #999; background: transparent; border: none;")
        layout.addWidget(self.lbl_sub)

    def update_value(self, value: str, subtitle: str = "") -> None:
        self.lbl_value.setText(value)
        if subtitle:
            self.lbl_sub.setText(subtitle)


class OverviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        # Refresh live metrics every 3 s
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh_metrics)
        self._timer.start(3000)

    # ── UI ────────────────────────────────────────────────────────────────────
    def setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 24, 30, 24)
        root.setSpacing(20)

        # ── Top header ───────────────────────────────────────────────────────
        header_row = QHBoxLayout()
        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: #1A1A1A;")
        header_row.addWidget(title)
        header_row.addStretch()

        self.lbl_time = QLabel()
        self.lbl_time.setStyleSheet("font-size: 13px; color: #888;")
        self._update_clock()
        clock_timer = QTimer(self)
        clock_timer.timeout.connect(self._update_clock)
        clock_timer.start(60000)
        header_row.addWidget(self.lbl_time)
        root.addLayout(header_row)

        lbl_host = QLabel(
            f"Host: {platform.node()}  ·  OS: {platform.system()} {platform.release()}"
        )
        lbl_host.setStyleSheet("font-size: 12px; color: #999;")
        root.addWidget(lbl_host)

        # ── Row 1: Metric tiles ───────────────────────────────────────────────
        tiles_row = QHBoxLayout()
        tiles_row.setSpacing(16)

        cpu = psutil.cpu_count(logical=True) or 0
        ram = psutil.virtual_memory()
        boot = datetime.fromtimestamp(psutil.boot_time(), tz=timezone.utc)
        uptime_h = int((datetime.now(tz=timezone.utc) - boot).total_seconds() // 3600)

        self.tile_cpu = MetricTile(
            "🖥", "CPU Usage", f"{psutil.cpu_percent(interval=None):.0f}%",
            f"{cpu} logical cores", "#2196F3",
        )
        self.tile_ram = MetricTile(
            "🧠", "RAM Usage", f"{ram.percent:.0f}%",
            f"{_fmt_size(ram.used)} / {_fmt_size(ram.total)}", "#9C27B0",
        )
        self.tile_uptime = MetricTile(
            "⏱", "Uptime", f"{uptime_h}h",
            boot.strftime("Booted %b %d, %H:%M"), "#FF9800",
        )
        score = _compute_health()
        score_color = "#4CAF50" if score >= 80 else ("#FF9800" if score >= 60 else "#F44336")
        self.tile_health = MetricTile(
            "❤️", "Health Score", f"{score}",
            "Real-time system score", score_color,
        )

        for tile in (self.tile_cpu, self.tile_ram, self.tile_uptime, self.tile_health):
            tiles_row.addWidget(tile)
        root.addLayout(tiles_row)

        # ── Row 2: Disk chart + Quick Actions ────────────────────────────────
        mid_row = QHBoxLayout()
        mid_row.setSpacing(16)

        # Disk bar chart
        disk_card = self._make_card("💾  Disk Usage by Drive")
        disk_layout = disk_card.layout()
        assert disk_layout is not None

        self.disk_plot = pg.PlotWidget()
        self.disk_plot.setBackground("transparent")
        self.disk_plot.setMouseEnabled(x=False, y=False)
        self.disk_plot.showGrid(y=True, alpha=0.15)
        self.disk_plot.setMinimumHeight(180)
        self._populate_disk_chart()
        disk_layout.addWidget(self.disk_plot)
        mid_row.addWidget(disk_card, 3)

        # Quick Actions card
        actions_card = self._make_card("⚡  Quick Actions")
        actions_raw = actions_card.layout()
        assert actions_raw is not None
        from PySide6.QtWidgets import QVBoxLayout as _QVBox
        actions_vl = _QVBox() if not isinstance(actions_raw, QVBoxLayout) else actions_raw

        self.btn_scan = QPushButton("\u25b6  Start Deep Scan")
        self.btn_clean = QPushButton("\U0001f9f9  Quick Clean")
        self.btn_scan.setStyleSheet(
            "QPushButton { padding: 13px; font-size: 14px; background-color: #2196F3; "
            "color: white; border-radius: 8px; font-weight: bold; border: none; }"
            "QPushButton:hover { background-color: #1976D2; }"
            "QPushButton:pressed { background-color: #0D47A1; }"
        )
        self.btn_clean.setStyleSheet(
            "QPushButton { padding: 13px; font-size: 14px; background-color: #FF9800; "
            "color: white; border-radius: 8px; font-weight: bold; border: none; }"
            "QPushButton:hover { background-color: #F57C00; }"
            "QPushButton:pressed { background-color: #E65100; }"
        )
        self.btn_scan.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clean.setCursor(Qt.CursorShape.PointingHandCursor)
        actions_vl.addWidget(self.btn_scan)
        actions_vl.addSpacing(8)
        actions_vl.addWidget(self.btn_clean)
        actions_vl.addStretch()

        # Top processes label
        lbl_procs_title = QLabel("\U0001f525  Top CPU Processes")
        lbl_procs_title.setStyleSheet(
            "font-size: 13px; font-weight: bold; color: #555; background: transparent; border: none; margin-top: 8px;"
        )
        actions_vl.addWidget(lbl_procs_title)

        procs = sorted(
            psutil.process_iter(["name", "cpu_percent"]),
            key=lambda p: p.info.get("cpu_percent") or 0,  # type: ignore[index]
            reverse=True,
        )[:4]
        for proc in procs:
            name = (proc.info.get("name") or "Unknown")[:22]  # type: ignore[index]
            cpu_p = proc.info.get("cpu_percent") or 0.0  # type: ignore[index]
            row = QLabel(f"  {name}  \u2014  {cpu_p:.1f}%")
            row.setStyleSheet("font-size: 12px; color: #666; background: transparent; border: none;")
            actions_vl.addWidget(row)

        mid_row.addWidget(actions_card, 2)
        root.addLayout(mid_row)

        # ── Row 3: Storage summary tiles ──────────────────────────────────────
        disk_tiles_row = QHBoxLayout()
        disk_tiles_row.setSpacing(16)

        for part in psutil.disk_partitions(all=False)[:4]:
            try:
                usage = psutil.disk_usage(part.mountpoint)
                tile = MetricTile(
                    "📁",
                    part.device.replace(":\\", ":"),
                    f"{usage.percent:.0f}% used",
                    f"{_fmt_size(usage.used)} / {_fmt_size(usage.total)}",
                    "#F44336" if usage.percent > 85 else ("#FF9800" if usage.percent > 70 else "#4CAF50"),
                )
                disk_tiles_row.addWidget(tile)
            except OSError:
                continue

        disk_tiles_row.addStretch()
        root.addLayout(disk_tiles_row)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _make_card(self, title: str) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            "QFrame { background-color: rgba(255,255,255,0.75); border-radius: 12px; "
            "border: 1px solid rgba(0,0,0,0.08); }"
        )
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(18)
        shadow.setColor(QColor(0, 0, 0, 22))
        shadow.setOffset(0, 4)
        card.setGraphicsEffect(shadow)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(8)

        lbl = QLabel(title)
        lbl.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #444; border: none; background: transparent;"
        )
        layout.addWidget(lbl)
        return card

    def _populate_disk_chart(self) -> None:
        self.disk_plot.clear()
        self.disk_plot.hideAxis("bottom")
        axis = self.disk_plot.getAxis("left")
        axis.setLabel("GB")
        axis.setTextPen(pg.mkPen("#888"))

        used_vals, free_vals, labels, x_vals = [], [], [], []
        for i, part in enumerate(psutil.disk_partitions(all=False)):
            try:
                usage = psutil.disk_usage(part.mountpoint)
                used_gb = usage.used / 1024**3
                free_gb = usage.free / 1024**3
                used_vals.append(used_gb)
                free_vals.append(free_gb)
                labels.append(part.device.replace(":\\", ":"))
                x_vals.append(float(i))
            except OSError:
                continue

        if not x_vals:
            return

        used_bars = pg.BarGraphItem(
            x=x_vals, height=used_vals, width=0.4,
            brush=pg.mkBrush("#2196F3"), pen=pg.mkPen(None),
        )
        free_bars = pg.BarGraphItem(
            x=[x + 0.42 for x in x_vals], height=free_vals, width=0.4,
            brush=pg.mkBrush("#4CAF50"), pen=pg.mkPen(None),
        )
        self.disk_plot.addItem(used_bars)
        self.disk_plot.addItem(free_bars)

        # Legend
        legend = self.disk_plot.addLegend(offset=(10, 5))
        legend.addItem(pg.BarGraphItem(x=[], height=[], width=0.4, brush="#2196F3"), "Used")
        legend.addItem(pg.BarGraphItem(x=[], height=[], width=0.4, brush="#4CAF50"), "Free")

        bottom_axis = pg.AxisItem("bottom")
        bottom_axis.setTicks([list(zip(x_vals, labels))])
        self.disk_plot.setAxisItems({"bottom": bottom_axis})
        bottom_axis.setTextPen(pg.mkPen("#888"))

    def _update_clock(self) -> None:
        now = datetime.now(tz=timezone.utc).astimezone()  # local time
        self.lbl_time.setText(now.strftime("%A, %d %B %Y  %H:%M"))

    def _refresh_metrics(self) -> None:
        """Update live tiles every 3 seconds."""
        cpu_p = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory()
        score = _compute_health()
        score_color = "#4CAF50" if score >= 80 else ("#FF9800" if score >= 60 else "#F44336")

        self.tile_cpu.update_value(f"{cpu_p:.0f}%")
        self.tile_ram.update_value(
            f"{ram.percent:.0f}%",
            f"{_fmt_size(ram.used)} / {_fmt_size(ram.total)}",
        )
        self.tile_health.update_value(f"{score}")
        self.tile_health.lbl_value.setStyleSheet(
            f"font-size: 28px; font-weight: bold; color: {score_color}; background: transparent; border: none;"
        )
