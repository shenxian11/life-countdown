import sys
import json
import os
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy,
    QDialog, QFormLayout, QDateEdit, QSpinBox, QSlider, QDialogButtonBox, QSystemTrayIcon, QMenu, QAction
)
from PyQt5.QtCore import Qt, QPoint, QDate, QTimer, QSize
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QStyle

CONFIG_FILE = 'config.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_config(data):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f)

class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.setWindowTitle('设置')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setFixedSize(320, 220)
        self.config = config
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet('background: white;')
        layout = QFormLayout()
        # 生日
        self.birthday_edit = QDateEdit(self)
        self.birthday_edit.setCalendarPopup(True)
        self.birthday_edit.setStyleSheet('background: white; color: #222;')
        birthday = self.config.get('birthday')
        if birthday:
            self.birthday_edit.setDate(QDate.fromString(birthday, 'yyyy-MM-dd'))
        else:
            self.birthday_edit.setDate(QDate.currentDate())
        layout.addRow('阳历生日：', self.birthday_edit)
        # 寿命
        self.lifetime_spin = QSpinBox(self)
        self.lifetime_spin.setRange(1, 150)
        self.lifetime_spin.setSuffix(' 岁')
        self.lifetime_spin.setValue(self.config.get('lifetime', 80))
        self.lifetime_spin.setStyleSheet('background: white; color: #222;')
        layout.addRow('假设寿命：', self.lifetime_spin)
        # 透明度
        self.opacity_slider = QSlider(Qt.Horizontal, self)
        self.opacity_slider.setRange(30, 100)
        self.opacity_slider.setValue(self.config.get('opacity', 85))
        self.opacity_slider.setStyleSheet('background: white;')
        layout.addRow('悬浮窗透明度：', self.opacity_slider)
        # 按钮
        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel, self)
        self.button_box.setStyleSheet('background: white;')
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addRow(self.button_box)
        self.setLayout(layout)

    def get_settings(self):
        return {
            'birthday': self.birthday_edit.date().toString('yyyy-MM-dd'),
            'lifetime': self.lifetime_spin.value(),
            'opacity': self.opacity_slider.value()
        }

class LifeCountdownWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.dragging = False
        self.drag_position = QPoint()
        self.config = load_config()
        self.init_ui()
        self.restore_position()
        self.apply_opacity()
        self.start_timer()
        self.init_tray()

    def init_ui(self):
        self.setWindowTitle('人生')
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setGeometry(100, 100, 360, 350)
        self.setStyleSheet('background: rgba(30, 30, 30, 0.85); border-radius: 16px;')
        # 顶部栏（标题+设置按钮）
        top_layout = QHBoxLayout()
        title = QLabel('人生')
        title.setFont(QFont('微软雅黑', 16, QFont.Bold))
        title.setStyleSheet('color: #FFD700; background: transparent;')
        top_layout.addWidget(title)
        top_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.settings_btn = QPushButton('⚙️')
        self.settings_btn.setFixedSize(32, 32)
        self.settings_btn.setStyleSheet('''
            QPushButton {
                background: transparent;
                color: #FFD700;
                font-size: 18px;
                border: none;
            }
            QPushButton:hover {
                color: #FFFFFF;
            }
        ''')
        self.settings_btn.clicked.connect(self.open_settings)
        top_layout.addWidget(self.settings_btn)
        top_layout.setContentsMargins(8, 8, 8, 0)
        # 寿命信息区
        self.age_label = QLabel()
        self.week_label = QLabel()
        self.month_label = QLabel()
        self.day_label = QLabel()
        self.hour_label = QLabel()
        self.minute_label = QLabel()
        self.second_label = QLabel()
        for label in [self.age_label, self.week_label, self.month_label, self.day_label, self.hour_label, self.minute_label, self.second_label]:
            label.setFont(QFont('微软雅黑', 13))
            label.setStyleSheet('color: #FFFFFF; background: transparent; padding: 2px;')
            label.setAlignment(Qt.AlignLeft)
        # 下一个生日倒计时
        self.next_birthday_label = QLabel('下一个生日距今还有：')
        self.next_birthday_time_label = QLabel()
        self.next_birthday_label.setFont(QFont('微软雅黑', 12, QFont.Bold))
        self.next_birthday_label.setStyleSheet('color: #FFD700; background: transparent; margin-top: 10px;')
        self.next_birthday_time_label.setFont(QFont('微软雅黑', 13))
        self.next_birthday_time_label.setStyleSheet('color: #00FFCC; background: transparent;')
        # 剩余寿命显示
        self.remain_label = QLabel()
        self.remain_label.setFont(QFont('微软雅黑', 13, QFont.Bold))
        self.remain_label.setStyleSheet('color: #FF6666; background: transparent; margin-top: 10px;')
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addSpacing(8)
        main_layout.addWidget(self.age_label)
        main_layout.addWidget(self.week_label)
        main_layout.addWidget(self.month_label)
        main_layout.addWidget(self.day_label)
        main_layout.addWidget(self.hour_label)
        main_layout.addWidget(self.minute_label)
        main_layout.addWidget(self.second_label)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.next_birthday_label)
        main_layout.addWidget(self.next_birthday_time_label)
        main_layout.addWidget(self.remain_label)
        main_layout.addStretch()
        main_layout.setContentsMargins(18, 8, 18, 18)
        self.setLayout(main_layout)

    def init_tray(self):
        self.tray = QSystemTrayIcon(self)
        # 使用自定义图标或默认图标
        icon_path = 'icon.ico'
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
            new_settings = dlg.get_settings()
            self.config.update(new_settings)
            save_config(self.config)
            self.apply_opacity()  # 确保透明度立即生效
            self.update_life_info()  # 立即刷新寿命信息

    def apply_opacity(self):
        opacity = self.config.get('opacity', 85)
        self.setWindowOpacity(opacity / 100)

    def start_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_life_info)
        self.timer.start(1000)
        self.update_life_info()

    def update_life_info(self):
        birthday_str = self.config.get('birthday')
        lifetime = self.config.get('lifetime', 80)
        if not birthday_str:
            self.age_label.setText('请在设置中填写生日')
            self.week_label.setText('')
            self.month_label.setText('')
            self.day_label.setText('')
            self.hour_label.setText('')
            self.minute_label.setText('')
            self.second_label.setText('')
            self.next_birthday_time_label.setText('')
            if hasattr(self, 'remain_label'):
                self.remain_label.setText('')
            return
        try:
            birthday = datetime.strptime(birthday_str, '%Y-%m-%d')
        except Exception:
            self.age_label.setText('生日格式错误')
            return
        now = datetime.now()
        # 年龄
        years = now.year - birthday.year - ((now.month, now.day) < (birthday.month, birthday.day))
        # 周龄、月龄、日龄、小时、分钟、秒
        delta = now - birthday
        weeks = delta.days // 7
        months = (now.year - birthday.year) * 12 + (now.month - birthday.month) - (1 if now.day < birthday.day else 0)
        days = delta.days
        hours = int(delta.total_seconds() // 3600)
        minutes = int(delta.total_seconds() // 60)
        seconds = int(delta.total_seconds())
        self.age_label.setText(f'你已经 {years} 周岁 ...')
        self.week_label.setText(f'活了 {weeks} 周')
        self.month_label.setText(f'活了 {months} 月')
        self.day_label.setText(f'活了 {days} 日')
        self.hour_label.setText(f'活了 {hours} 小时')
        self.minute_label.setText(f'活了 {minutes} 分钟')
        self.second_label.setText(f'活了 {seconds} 秒钟')
        # 下一个生日
        next_birthday_year = now.year if (now.month, now.day) < (birthday.month, birthday.day) else now.year + 1
        next_birthday = birthday.replace(year=next_birthday_year)
        until_next = next_birthday - now
        if until_next.total_seconds() < 0:
            until_next = timedelta(0)
        days_left = until_next.days
        hours_left = until_next.seconds // 3600
        minutes_left = (until_next.seconds % 3600) // 60
        seconds_left = until_next.seconds % 60
        self.next_birthday_time_label.setText(f'{days_left} 天 {hours_left} 小时 {minutes_left} 分 {seconds_left} 秒')
        # 剩余寿命（只显示年、天、小时）
        end_date = birthday.replace(year=birthday.year + lifetime)
        remain = end_date - now
        if remain.total_seconds() < 0:
            remain = timedelta(0)
        remain_years = remain.days // 365
        remain_days = remain.days % 365
        remain_hours = remain.seconds // 3600
        self.remain_label.setText(f'大概寿命：{remain_years} 年 {remain_days} 天 {remain_hours} 小时')
        # 大概剩余天数
        if not hasattr(self, 'remain_days_label'):
            self.remain_days_label = QLabel()
            self.remain_days_label.setFont(QFont('微软雅黑', 13, QFont.Bold))
            self.remain_days_label.setStyleSheet('color: #FFCC00; background: transparent; margin-top: 2px;')
            # 插入到主布局中，紧跟在 remain_label 后
            layout = self.layout()
            idx = layout.indexOf(self.remain_label)
            layout.insertWidget(idx + 1, self.remain_days_label)
        self.remain_days_label.setText(f'剩余天数：{remain.days} 天')

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