import sys
import webbrowser
from tabnanny import check
from unittest import result

from flask import config
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QCheckBox, QHBoxLayout, QLabel,
                             QLineEdit, QMessageBox, QPushButton, QTextEdit,
                             QVBoxLayout, QWidget)

from lib import AutoChrome, gen_text


class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)  # type: ignore
        self.setToolTip('Click để lấy API')

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:  # type: ignore
            self.clicked.emit()
            webbrowser.open('https://aistudio.google.com/app/apikey?hl=vi')
        super().mousePressEvent(event)


class Worker(QThread):
    result_signal = pyqtSignal(str)

    def __init__(self, username, password, key_2fa, proxy, load_image, load_css, headless, api_gemini, content):
        super().__init__()
        self.username = username
        self.password = password
        self.key_2fa = key_2fa
        self.proxy = proxy
        self.load_image = load_image
        self.load_css = load_css
        self.headless = headless
        self.api_gemini = api_gemini
        self.content = content

    def run(self):
        chrome = AutoChrome(
            self.load_image,
            self.load_css,
            self.headless,
            self.proxy
        )
        chrome.login(self.username, self.password, self.key_2fa)
        content = gen_text(self.api_gemini, self.content)
        with open('group_id.txt', 'r') as f:
            for line in f:
                chrome.post_status(content, line)


class OvFuk(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('OvFuk')
        self.setWindowFlags(self.windowFlags() & ~
                            Qt.WindowMaximizeButtonHint)  # type: ignore
        layout_1 = QHBoxLayout()
        username_layout = QVBoxLayout()
        self.label_username = QLabel('🕵️‍♂️ Tài khoản:')
        self.input_username = QLineEdit(self)
        self.input_username.setToolTip('UID, Email, SĐT')
        self.input_username.setPlaceholderText('UID, Email, SĐT')
        username_layout.addWidget(self.label_username)
        username_layout.addSpacing(5)
        username_layout.addWidget(self.input_username)

        self.label_password = QLabel('🔒 Mật khẩu:')
        self.input_password = QLineEdit(self)
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setPlaceholderText('Nhập mật khẩu')
        self.input_password.setToolTip('Mật khẩu Facebook')
        password_layout = QVBoxLayout()
        password_layout.addWidget(self.label_password)
        password_layout.addSpacing(5)
        password_layout.addWidget(self.input_password)
        layout_1.addLayout(username_layout)
        layout_1.addSpacing(8)
        layout_1.addLayout(password_layout)

        layout_2 = QVBoxLayout()
        two_fa_layout = QHBoxLayout()
        self.label_2fa = QLabel('🔑 2FA Key:')
        self.input_2fa = QLineEdit(self)
        self.input_2fa.setPlaceholderText(
            'Key 2FA (dạng: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX)')
        self.input_2fa.setToolTip('Không phải dạng code 6-8 đâu nha!')

        two_fa_layout.addWidget(self.label_2fa)
        two_fa_layout.addSpacing(5)
        two_fa_layout.addWidget(self.input_2fa)

        layout_2.addLayout(two_fa_layout)

        config_layout = QVBoxLayout()
        self.proxy_label = QLabel('🌐 Proxy:')
        self.proxy = QLineEdit(self)
        self.proxy.setPlaceholderText('Proxy dạng IP:PORT')
        self.proxy.setToolTip('VD: 192.168.1.1:8080')

        self.load_image = QCheckBox('Load Hình Ảnh 📷', self)
        self.load_image.setToolTip(
            'Bật load hình ảnh')
        self.load_css = QCheckBox('Load CSS 🖌️', self)
        self.load_css.setToolTip(
            'Bật load CSS')
        self.hide_chrome = QCheckBox('Ẩn Chrome 🐱‍💻', self)
        self.hide_chrome.setToolTip(
            'Kích hoạt chế độ chạy nền (Nhẹ hơn, có thể sẽ bị lỗi không mong muốn)')
        check_box_layout = QHBoxLayout()
        check_box_layout.addWidget(self.load_image)
        check_box_layout.addSpacing(5)
        check_box_layout.addWidget(self.load_css)
        check_box_layout.addSpacing(5)
        check_box_layout.addWidget(self.hide_chrome)
        self.api_key_label = ClickableLabel('🔒 API Gemini:')
        self.api_key = QLineEdit(self)
        self.api_key.setPlaceholderText(
            'Click vào tiêu đề để lấy API')
        self.content_label = QLabel("📝 Nội dung bài đăng: ")
        self.content = QTextEdit(self)
        self.content.setAcceptRichText(False)

        self.button_login = QPushButton('🚀 Chạy', self)
        self.button_login.clicked.connect(self.handle_login)

        config_layout.addWidget(self.proxy_label)
        config_layout.addSpacing(5)
        config_layout.addWidget(self.proxy)
        config_layout.addSpacing(5)
        config_layout.addLayout(check_box_layout)
        config_layout.addSpacing(5)
        config_layout.addWidget(self.api_key_label)
        config_layout.addSpacing(5)
        config_layout.addWidget(self.api_key)
        config_layout.addSpacing(5)
        config_layout.addWidget(self.content_label)
        config_layout.addSpacing(5)
        config_layout.addWidget(self.content)
        config_layout.addSpacing(5)
        self.button_reload = QPushButton('Reload Stylesheet', self)
        self.button_reload.clicked.connect(self.reload_stylesheet)
        main_layout = QVBoxLayout()
        main_layout.addItem(layout_1)
        main_layout.addItem(layout_2)
        main_layout.addItem(config_layout)
        main_layout.addWidget(self.button_login)
        main_layout.addWidget(self.button_reload)
        self.setLayout(main_layout)
        self.apply_stylesheet("style.qss")
        self.show()

    def apply_stylesheet(self, filename):
        try:
            with open(filename, "r") as file:
                stylesheet = file.read()
                self.setStyleSheet(stylesheet)
        except FileNotFoundError:
            print(f"Stylesheet file '{filename}' not found.")

    def reload_stylesheet(self):
        self.apply_stylesheet("style.qss")

    def handle_login(self):
        username = self.input_username.text()
        password = self.input_password.text()
        key_2fa = self.input_2fa.text()
        proxy = self.proxy.text()
        load_image = self.load_image.isChecked()
        load_css = self.load_css.isChecked()
        hide_chrome = self.hide_chrome.isChecked()
        api_gemini = self.api_key.text()
        content = self.content.toPlainText()

        self.thread: Worker = Worker(
            username, password, key_2fa, proxy, load_image, load_css, hide_chrome, api_gemini, content)
        self.thread.result_signal.connect(self.handle_result)
        self.thread.start()

    def handle_result(self, result):
        QMessageBox.information(self, 'Chạy hoàn tất', result)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = OvFuk()
    sys.exit(app.exec_())
