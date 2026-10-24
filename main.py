import sys
import json
import math
import os
from datetime import datetime, timedelta

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton,
    QSpacerItem, QSizePolicy, QDialog, QFormLayout, QDateEdit, QSpinBox,
    QSlider, QGridLayout, QSystemTrayIcon, QMenu, QAction
)
from PyQt5.QtCore import (
    Qt, QPoint, QPointF, QDate, QTimer, QPropertyAnimation, QEasingCurve,
    QVariantAnimation, QAbstractAnimation
)
from PyQt5.QtGui import (
    QFont, QIcon, QPainter, QColor, QBrush, QLinearGradient, QRadialGradient,
    QPainterPath, QPen
)
from PyQt5.QtWidgets import QStyle

CONFIG_FILE = 'config.json'

# 界面缩放默认值，可在设置中调整（80% ~ 200%）
DEFAULT_UI_SCALE = 1.3


def S(v, scale=1.0):
    return int(round(v * scale))


# ---- 主题色 ----
ACCENT = '#8B7CFF'        # 主强调色（紫）
ACCENT_2 = '#4DD8E6'      # 渐变副色（青）
GOLD = '#FFC24B'          # 生日金色
TEXT_MAIN = '#F4F5FC'
TEXT_SUB = '#9EA4C4'


def fmt_big(n):
    """大数字中文化：亿 / 万，其余千分位。"""
    if n >= 100_000_000:
        return f'{n / 100_000_000:.2f} 亿'
    if n >= 1_000_000:
        return f'{n / 10_000:,.0f} 万'
    return f'{n:,}'


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_config(data):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def resource_path(name):
    """兼容 PyInstaller 打包：从临时解包目录读取内置资源。"""
    base = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


def window_qss(scale):
    return f'''
#appBadge {{ color: {ACCENT}; font-size: {S(16, scale)}px; background: transparent; }}
#appTitle {{
    color: {TEXT_MAIN}; font-size: {S(15, scale)}px; font-weight: bold;
    font-family: 'Microsoft YaHei UI';
    background: transparent;
}}
#appSubtitle {{
    color: {TEXT_SUB}; font-size: {S(8, scale)}px; font-weight: 600;
    letter-spacing: {S(3, scale)}px; background: transparent;
}}
#gearBtn {{
    background: transparent; color: {TEXT_SUB}; border: none;
    font-size: {S(17, scale)}px; font-family: 'Segoe UI Symbol', 'Microsoft YaHei UI';
}}
#gearBtn:hover {{ color: {TEXT_MAIN}; }}
#heroNum {{
    color: #FFFFFF; font-size: {S(38, scale)}px; font-weight: bold;
    font-family: 'Segoe UI', 'Microsoft YaHei UI';
    background: transparent;
}}
#heroUnit {{ color: {TEXT_SUB}; font-size: {S(14, scale)}px; padding-bottom: {S(9, scale)}px; background: transparent; }}
#heroCaption {{ color: {TEXT_SUB}; font-size: {S(10, scale)}px; letter-spacing: {S(2, scale)}px; background: transparent; }}
#statCard {{
    background: rgba(255, 255, 255, 20);
    border: 1px solid rgba(255, 255, 255, 30);
    border-radius: {S(12, scale)}px;
}}
#statCard:hover {{
    background: rgba(255, 255, 255, 38);
    border: 1px solid rgba(139, 124, 255, 130);
}}
#statValue {{
    color: #FFFFFF; font-size: {S(17, scale)}px; font-weight: bold;
    font-family: 'Segoe UI', 'Microsoft YaHei UI';
    background: transparent; border: none;
}}
#statCaption {{ color: {TEXT_SUB}; font-size: {S(10, scale)}px; background: transparent; border: none; }}
#divider {{ background: rgba(255, 255, 255, 26); border: none; }}
#sectionHead {{ color: {TEXT_SUB}; font-size: {S(11, scale)}px; letter-spacing: 1px; background: transparent; }}
#birthdayTime {{
    color: {GOLD}; font-size: {S(20, scale)}px; font-weight: bold;
    font-family: 'Segoe UI', 'Microsoft YaHei UI';
    background: transparent;
}}
#progressPct {{
    color: {ACCENT_2}; font-size: {S(12, scale)}px; font-weight: bold;
    font-family: 'Segoe UI';
    background: transparent;
}}
#remainLabel {{ color: {TEXT_MAIN}; font-size: {S(12, scale)}px; background: transparent; }}
'''


def settings_qss(scale):
    return f'''
QDialog {{ background: #202134; }}
QLabel {{ color: #B9BDD3; font-size: {S(12, scale)}px; background: transparent; }}
#sliderValue {{ color: {TEXT_MAIN}; font-size: {S(12, scale)}px; }}
QDateEdit, QSpinBox {{
    background: #2A2B3F; border: 1px solid #3A3B55; border-radius: {S(8, scale)}px;
    padding: {S(5, scale)}px {S(10, scale)}px; color: {TEXT_MAIN}; font-size: {S(13, scale)}px;
    selection-background-color: {ACCENT};
    font-family: 'Segoe UI', 'Microsoft YaHei UI';
}}
QDateEdit:hover, QSpinBox:hover {{ border-color: #55577A; }}
QDateEdit::drop-down {{ background: transparent; border: none; width: {S(20, scale)}px; }}
QDateEdit::down-arrow {{
    image: none; width: 0; height: 0;
    border-left: {S(4, scale)}px solid transparent; border-right: {S(4, scale)}px solid transparent;
    border-top: {S(5, scale)}px solid {TEXT_SUB};
}}
QSpinBox::up-button, QSpinBox::down-button {{ background: transparent; border: none; width: {S(16, scale)}px; }}
QSpinBox::up-arrow {{
    image: none; width: 0; height: 0;
    border-left: {S(4, scale)}px solid transparent; border-right: {S(4, scale)}px solid transparent;
    border-bottom: {S(5, scale)}px solid {TEXT_SUB};
}}
QSpinBox::down-arrow {{
    image: none; width: 0; height: 0;
    border-left: {S(4, scale)}px solid transparent; border-right: {S(4, scale)}px solid transparent;
    border-top: {S(5, scale)}px solid {TEXT_SUB};
}}
QSlider::groove:horizontal {{ height: {S(6, scale)}px; background: #2A2B3F; border-radius: {S(3, scale)}px; }}
QSlider::sub-page:horizontal {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 {ACCENT}, stop:1 {ACCENT_2});
    border-radius: {S(3, scale)}px;
}}
QSlider::handle:horizontal {{
    width: {S(16, scale)}px; height: {S(16, scale)}px; margin: -{S(5, scale)}px 0;
    border-radius: {S(8, scale)}px; background: {TEXT_MAIN};
}}
QSlider::handle:horizontal:hover {{ background: #FFFFFF; }}
QPushButton#primaryBtn {{
    background: {ACCENT}; color: white; border: none; border-radius: {S(8, scale)}px;
    padding: {S(7, scale)}px {S(20, scale)}px; font-size: {S(13, scale)}px; font-weight: 600;
    font-family: 'Microsoft YaHei UI';
}}
QPushButton#primaryBtn:hover {{ background: #9C90FF; }}
QPushButton#ghostBtn {{
    background: transparent; color: #B9BDD3; border: 1px solid #3A3B55;
    border-radius: {S(8, scale)}px; padding: {S(7, scale)}px {S(20, scale)}px; font-size: {S(13, scale)}px;
    font-family: 'Microsoft YaHei UI';
}}
QPushButton#ghostBtn:hover {{ background: #2A2B3F; }}
'''


class StatCard(QWidget):
    """六宫格中的单个统计卡片。"""

    def __init__(self, caption, scale=1.0, parent=None):
        super().__init__(parent)
        self.setObjectName('statCard')
        self.setAttribute(Qt.WA_StyledBackground, True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(S(6, scale), S(12, scale), S(6, scale), S(10, scale))
        layout.setSpacing(S(3, scale))
        self.value_label = QLabel('—')
        self.value_label.setObjectName('statValue')
        self.value_label.setAlignment(Qt.AlignCenter)
        cap = QLabel(caption)
        cap.setObjectName('statCaption')
        cap.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        layout.addWidget(cap)

    def set_value(self, text):
        self.value_label.setText(text)


class LifeProgressBar(QWidget):
    """生命进度条：紫→青渐变填充，数值变化时平滑动画。"""

    def __init__(self, scale=1.0, parent=None):
        super().__init__(parent)
        self.setFixedHeight(S(10, scale))
        self._ratio = 0.0
        self._anim = QVariantAnimation(self)
        self._anim.setDuration(900)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)
        self._anim.valueChanged.connect(self._on_anim)

    def set_ratio(self, ratio, animate=False):
        ratio = max(0.0, min(1.0, ratio))
        if animate and abs(ratio - self._ratio) > 0.002:
            self._anim.stop()
            self._anim.setStartValue(float(self._ratio))
            self._anim.setEndValue(float(ratio))
            self._anim.start()
        else:
            self._anim.stop()
            self._ratio = ratio
            self.update()

    def _on_anim(self, value):
        self._ratio = float(value)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(255, 255, 255, 22))
        painter.drawRoundedRect(0, 0, self.width(), self.height(), self.height() // 2, self.height() // 2)
        w = int(self.width() * self._ratio)
        if w > 0:
            gradient = QLinearGradient(0, 0, self.width(), 0)
            gradient.setColorAt(0.0, QColor(ACCENT))
            gradient.setColorAt(1.0, QColor(ACCENT_2))
            painter.setBrush(QBrush(gradient))
            painter.drawRoundedRect(0, 0, max(w, self.height()), self.height(), self.height() // 2, self.height() // 2)
        painter.end()


class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.setWindowTitle('设置')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.ui_scale = float(config.get('ui_scale', DEFAULT_UI_SCALE))
        self.setFixedWidth(S(340, self.ui_scale) + 20)
        self.config = config
        self.init_ui()

    def init_ui(self):
        s = self.ui_scale
        self.setStyleSheet(settings_qss(s))
        layout = QFormLayout()
        layout.setContentsMargins(S(24, s), S(22, s), S(24, s), S(20, s))
        layout.setSpacing(S(14, s))

        self.birthday_edit = QDateEdit()
        self.birthday_edit.setCalendarPopup(True)
        self.birthday_edit.setDisplayFormat('yyyy-MM-dd')
        birthday = self.config.get('birthday')
        if birthday:
            self.birthday_edit.setDate(QDate.fromString(birthday, 'yyyy-MM-dd'))
        else:
            self.birthday_edit.setDate(QDate.currentDate())
        layout.addRow('阳历生日', self.birthday_edit)

        self.lifetime_spin = QSpinBox()
        self.lifetime_spin.setRange(1, 150)
        self.lifetime_spin.setSuffix(' 岁')
        self.lifetime_spin.setValue(self.config.get('lifetime', 80))
        layout.addRow('假设寿命', self.lifetime_spin)

        # 界面大小：80% ~ 200%
        scale_row = QHBoxLayout()
        scale_row.setSpacing(S(10, s))
        self.scale_slider = QSlider(Qt.Horizontal)
        self.scale_slider.setRange(80, 200)
        self.scale_slider.setValue(int(self.ui_scale * 100))
        self.scale_slider.setSingleStep(5)
        self.scale_slider.setPageStep(20)
        self.scale_value = QLabel(f'{self.scale_slider.value()}%')
        self.scale_value.setObjectName('sliderValue')
        self.scale_value.setFixedWidth(S(36, s))
        self.scale_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.scale_slider.valueChanged.connect(
            lambda v: self.scale_value.setText(f'{v}%'))
        scale_row.addWidget(self.scale_slider)
        scale_row.addWidget(self.scale_value)
        layout.addRow('界面大小', scale_row)

        slider_row = QHBoxLayout()
        slider_row.setSpacing(S(10, s))
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(30, 100)
        self.opacity_slider.setValue(self.config.get('opacity', 85))
        self.opacity_value = QLabel(f"{self.opacity_slider.value()}%")
        self.opacity_value.setObjectName('sliderValue')
        self.opacity_value.setFixedWidth(S(36, s))
        self.opacity_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.opacity_slider.valueChanged.connect(
            lambda v: self.opacity_value.setText(f'{v}%'))
        slider_row.addWidget(self.opacity_slider)
        slider_row.addWidget(self.opacity_value)
        layout.addRow('透明度', slider_row)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(S(10, s))
        btn_row.addStretch()
        cancel_btn = QPushButton('取消')
        cancel_btn.setObjectName('ghostBtn')
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton('保存')
        save_btn.setObjectName('primaryBtn')
        save_btn.setDefault(True)
        save_btn.clicked.connect(self.accept)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addRow(btn_row)

        self.setLayout(layout)

    def get_settings(self):
        return {
            'birthday': self.birthday_edit.date().toString('yyyy-MM-dd'),
            'lifetime': self.lifetime_spin.value(),
            'ui_scale': self.scale_slider.value() / 100,
            'opacity': self.opacity_slider.value()
        }


class LifeCountdownWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.dragging = False
        self.drag_position = QPoint()
        self.config = load_config()
        self.ui_scale = float(self.config.get('ui_scale', DEFAULT_UI_SCALE))
        self._bar_intro = True      # 下一次刷新时进度条播放入场动画
        self._glow_t = 0.0          # 呼吸光晕相位
        self.init_ui()
        self.restore_position()
        self.apply_opacity()
        self.start_timer()
        self.init_tray()
        self._start_glow()
        self.fade_in(450)
        if not self.config.get('birthday'):
            QTimer.singleShot(200, self.open_settings)

    def init_ui(self):
        s = self.ui_scale
        self.setObjectName('LifeWindow')
        self.setWindowTitle('人生')
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setFixedSize(S(380, s) + 4, S(436, s) + 10)
        self.setStyleSheet(window_qss(s))

        root = QVBoxLayout(self)
        root.setContentsMargins(S(22, s), S(16, s), S(22, s), S(18, s))
        root.setSpacing(S(10, s))

        # 顶栏：标志 + 标题 + 设置按钮
        header = QHBoxLayout()
        header.setSpacing(S(6, s))
        badge = QLabel('✦')
        badge.setObjectName('appBadge')
        title_col = QVBoxLayout()
        title_col.setSpacing(0)
        title = QLabel('人生')
        title.setObjectName('appTitle')
        subtitle = QLabel('LIFE · COUNTDOWN')
        subtitle.setObjectName('appSubtitle')
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        header.addWidget(badge)
        header.addSpacing(S(2, s))
        header.addLayout(title_col)
        header.addSpacerItem(QSpacerItem(S(20, s), S(10, s), QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.settings_btn = QPushButton('⚙')
        self.settings_btn.setObjectName('gearBtn')
        self.settings_btn.setFixedSize(S(30, s), S(30, s))
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.clicked.connect(self.open_settings)
        header.addWidget(self.settings_btn)
        root.addLayout(header)

        # 主体：已度过的天数（大数字）
        hero = QHBoxLayout()
        hero.setSpacing(S(6, s))
        hero.addStretch()
        self.hero_num = QLabel('—')
        self.hero_num.setObjectName('heroNum')
        self.hero_unit = QLabel('天')
        self.hero_unit.setObjectName('heroUnit')
        hero.addWidget(self.hero_num, 0, Qt.AlignBottom)
        hero.addWidget(self.hero_unit, 0, Qt.AlignBottom)
        hero.addStretch()
        root.addLayout(hero)
        self.hero_caption = QLabel('已度过的天数')
        self.hero_caption.setObjectName('heroCaption')
        self.hero_caption.setAlignment(Qt.AlignCenter)
        root.addWidget(self.hero_caption)

        root.addSpacing(S(4, s))

        # 六宫格：周岁 / 月 / 周 / 小时 / 分钟 / 秒
        grid = QGridLayout()
        grid.setSpacing(S(8, s))
        self.stat_cards = [StatCard(c, s) for c in ('周岁', '个月', '周', '小时', '分钟', '秒')]
        for i, card in enumerate(self.stat_cards):
            grid.addWidget(card, i // 3, i % 3)
            grid.setColumnStretch(i % 3, 1)
        root.addLayout(grid)

        root.addWidget(self._divider())

        # 下一个生日倒计时
        birthday_head = QLabel('距离下一个生日')
        birthday_head.setObjectName('sectionHead')
        self.birthday_time = QLabel('—')
        self.birthday_time.setObjectName('birthdayTime')
        root.addWidget(birthday_head)
        root.addWidget(self.birthday_time)

        root.addWidget(self._divider())

        # 生命进度 + 剩余寿命
        pct_row = QHBoxLayout()
        progress_title = QLabel('生命进度')
        progress_title.setObjectName('sectionHead')
        self.progress_pct = QLabel('—')
        self.progress_pct.setObjectName('progressPct')
        pct_row.addWidget(progress_title)
        pct_row.addStretch()
        pct_row.addWidget(self.progress_pct)
        root.addLayout(pct_row)
        self.life_bar = LifeProgressBar(s)
        root.addWidget(self.life_bar)
        self.remain_label = QLabel('')
        self.remain_label.setObjectName('remainLabel')
        root.addWidget(self.remain_label)

        root.addStretch()
        self.setLayout(root)

    def _divider(self):
        line = QWidget()
        line.setObjectName('divider')
        line.setFixedHeight(1)
        return line

    def paintEvent(self, event):
        """手绘圆角渐变背景 + 呼吸光晕（顶层窗口的 QSS 背景在半透明模式下不可靠）。"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        radius = S(18, self.ui_scale)
        path.addRoundedRect(0.5, 0.5, self.width() - 1, self.height() - 1, radius, radius)
        gradient = QLinearGradient(0, 0, self.width() * 0.85, self.height())
        gradient.setColorAt(0.0, QColor('#1A1B2F'))
        gradient.setColorAt(0.52, QColor('#1D1E38'))
        gradient.setColorAt(1.0, QColor('#252049'))
        painter.fillPath(path, gradient)
        # 大数字后方的呼吸光晕（4 秒周期，正弦起伏）
        glow = (math.sin(self._glow_t * 2 * math.pi) + 1) / 2
        center = QPointF(self.width() * 0.5, self.height() * 0.17)
        radial = QRadialGradient(center, self.width() * (0.52 + 0.08 * glow))
        radial.setColorAt(0.0, QColor(139, 124, 255, int(18 + 30 * glow)))
        radial.setColorAt(1.0, QColor(139, 124, 255, 0))
        painter.fillPath(path, QBrush(radial))
        painter.setPen(QPen(QColor(255, 255, 255, 26), 1))
        painter.drawPath(path)
        painter.end()

    def _start_glow(self):
        self._glow_timer = QTimer(self)
        self._glow_timer.timeout.connect(self._tick_glow)
        self._glow_timer.start(50)

    def _tick_glow(self):
        if not self.isVisible():
            return
        self._glow_t = (self._glow_t + 0.05 / 4.0) % 1.0
        self.update()

    def fade_in(self, duration=450):
        """窗口淡入显示。"""
        target = float(self.config.get('opacity', 85)) / 100
        self.setWindowOpacity(0.0)
        anim = QPropertyAnimation(self, b'windowOpacity', self)
        anim.setDuration(duration)
        anim.setStartValue(0.0)
        anim.setEndValue(target)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start(QAbstractAnimation.DeleteWhenStopped)

    def _pulse(self, label, color=ACCENT, duration=220):
        """让标签文字从指定颜色闪回白色，制造秒针跳动的动感。"""
        anim = QVariantAnimation(label)
        anim.setDuration(duration)
        anim.setStartValue(QColor(color))
        anim.setEndValue(QColor('#FFFFFF'))
        anim.valueChanged.connect(
            lambda c: label.setStyleSheet(f'color: {c.name()};'))
        anim.finished.connect(lambda: label.setStyleSheet(''))
        anim.start(QAbstractAnimation.DeleteWhenStopped)

    def rebuild_ui(self):
        """界面大小改变后，按新缩放值重建全部界面元素。"""
        self.ui_scale = float(self.config.get('ui_scale', DEFAULT_UI_SCALE))
        old_layout = self.layout()
        if old_layout is not None:
            QWidget().setLayout(old_layout)  # 旧布局连同子控件一并释放
        self.setStyleSheet(window_qss(self.ui_scale))
        self._bar_intro = True
        self.init_ui()
        self.update_life_info()

    def init_tray(self):
        self.tray = QSystemTrayIcon(self)
        icon_path = resource_path('icon.ico')
        if os.path.exists(icon_path):
            self.tray.setIcon(QIcon(icon_path))
        else:
            self.tray.setIcon(QIcon.fromTheme('face-smile') if QIcon.hasThemeIcon('face-smile') else self.style().standardIcon(QStyle.SP_ComputerIcon))
        self.tray.setToolTip('人生')
        menu = QMenu()
        show_action = QAction('显示/隐藏主界面', self)
        show_action.triggered.connect(self.toggle_window)
        quit_action = QAction('退出', self)
        quit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(show_action)
        menu.addSeparator()
        menu.addAction(quit_action)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self.on_tray_activated)
        self.tray.show()

    def toggle_window(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.fade_in(250)

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.toggle_window()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray.showMessage('人生', '程序已最小化到托盘，双击图标可恢复窗口', QSystemTrayIcon.Information, 2000)

    def open_settings(self):
        dlg = SettingsDialog(self.config, self)
        if dlg.exec_() == QDialog.Accepted:
            old_scale = self.ui_scale
            new_settings = dlg.get_settings()
            self.config.update(new_settings)
            save_config(self.config)
            self.apply_opacity()
            self._bar_intro = True  # 寿命调整后进度条重新做动画
            self.update_life_info()
            if abs(float(new_settings.get('ui_scale', old_scale)) - old_scale) > 1e-6:
                self.rebuild_ui()

    def apply_opacity(self):
        opacity = self.config.get('opacity', 85)
        self.setWindowOpacity(opacity / 100)

    def start_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_life_info)
        self.timer.start(1000)
        self.update_life_info()

    def _set_placeholder(self):
        self.hero_num.setText('—')
        self.hero_caption.setText('点击右上角 ⚙ 设置生日')
        for card in self.stat_cards:
            card.set_value('—')
        self.birthday_time.setText('—')
        self.progress_pct.setText('—')
        self.life_bar.set_ratio(0)
        self.remain_label.setText('')

    def update_life_info(self):
        birthday_str = self.config.get('birthday')
        lifetime = self.config.get('lifetime', 80)
        if not birthday_str:
            self._set_placeholder()
            return
        try:
            birthday = datetime.strptime(birthday_str, '%Y-%m-%d')
        except ValueError:
            self._set_placeholder()
            self.hero_caption.setText('生日格式错误，请在设置中修改')
            return

        now = datetime.now()
        delta = now - birthday
        total_seconds = int(delta.total_seconds())
        years = now.year - birthday.year - ((now.month, now.day) < (birthday.month, birthday.day))
        months = (now.year - birthday.year) * 12 + (now.month - birthday.month) - (1 if now.day < birthday.day else 0)
        weeks = delta.days // 7

        self.hero_caption.setText('已度过的天数')
        self.hero_num.setText(f'{delta.days:,}')
        values = (
            str(years), str(months), f'{weeks:,}',
            fmt_big(total_seconds // 3600),
            fmt_big(total_seconds // 60),
            fmt_big(total_seconds),
        )
        for card, text in zip(self.stat_cards, values):
            card.set_value(text)
        if self.isVisible():
            self._pulse(self.stat_cards[5].value_label)  # 秒数每秒闪动

        # 下一个生日（2 月 29 日生日按平年落到 2 月 28 日）
        next_birthday_year = now.year if (now.month, now.day) < (birthday.month, birthday.day) else now.year + 1
        try:
            next_birthday = birthday.replace(year=next_birthday_year)
        except ValueError:
            next_birthday = birthday.replace(year=next_birthday_year, day=28)
        until_next = next_birthday - now
        if until_next.total_seconds() < 0:
            until_next = timedelta(0)
        days_left, rest = until_next.days, until_next.seconds
        hours_left, rest = divmod(rest, 3600)
        minutes_left, seconds_left = divmod(rest, 60)
        self.birthday_time.setText(f'{days_left} 天 {hours_left:02d}:{minutes_left:02d}:{seconds_left:02d}')

        # 生命进度与剩余寿命（同样处理 2 月 29 日）
        try:
            end_date = birthday.replace(year=birthday.year + lifetime)
        except ValueError:
            end_date = birthday.replace(year=birthday.year + lifetime, day=28)
        total_span = (end_date - birthday).total_seconds()
        ratio = total_seconds / total_span if total_span > 0 else 1.0
        self.life_bar.set_ratio(ratio, animate=self._bar_intro)
        self._bar_intro = False
        self.progress_pct.setText(f'{ratio * 100:.1f}%')
        remain = end_date - now
        if remain.total_seconds() < 0:
            remain = timedelta(0)
        remain_years = remain.days // 365
        remain_days = remain.days % 365
        remain_hours = remain.seconds // 3600
        self.remain_label.setText(f'预计剩余   约 {remain_years} 年 {remain_days} 天 {remain_hours:02d} 小时')

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.save_position()
            event.accept()

    def save_position(self):
        pos = self.pos()
        self.config['window_pos'] = {'x': pos.x(), 'y': pos.y()}
        save_config(self.config)

    def restore_position(self):
        pos = self.config.get('window_pos')
        if pos:
            self.move(pos['x'], pos['y'])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LifeCountdownWindow()
    window.show()
    sys.exit(app.exec_())
