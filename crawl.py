import base64
import json
import re
import sys
import webbrowser
from binascii import crc_hqx

from PyQt5.QtCore import QBuffer, QIODevice, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFontDatabase, QIcon, QImage, QPixmap
from PyQt5.QtMultimedia import QSound
from PyQt5.QtWidgets import (QApplication, QCheckBox, QFileDialog, QHBoxLayout,
                             QLabel, QLineEdit, QMessageBox, QPushButton,
                             QSpinBox, QVBoxLayout, QWidget)

from lib import AutoChrome, gen_text


def validate_proxy(proxy):
    pattern = r'^[^:]+:\d+$'
    return re.match(pattern, proxy) is not None


def base64_to_pixmap(base64_str):
    image_data = base64.b64decode(base64_str)
    buffer = QBuffer()
    buffer.setData(image_data)
    buffer.open(QIODevice.ReadOnly)  # type: ignore
    image = QImage()
    image.loadFromData(buffer.data())
    pixmap = QPixmap.fromImage(image)
    return pixmap


def main():
    app = QApplication(sys.argv)
    font_db = QFontDatabase()
    font_db.addApplicationFont('fonts/VNF-Comic Sans.ttf')

    class Worker(QThread):
        result_signal = pyqtSignal(str)

        def __init__(self, username, password, key_2fa, proxy, load_image, load_css, headless, keyword, page_number):
            super().__init__()
            self.username = username
            self.password = password
            self.key_2fa = key_2fa
            self.proxy = proxy
            self.load_image = load_image
            self.load_css = load_css
            self.headless = headless
            self.keyword = keyword
            self.page_number = page_number

        def run(self):
            if self.username == '' or self.password == '' or self.key_2fa == '':
                self.result_signal.emit(
                    '{"status": "ERROR", "message": "Chưa điền đủ thông tin đăng nhập"}')
                return
            elif self.keyword == '':
                self.result_signal.emit(
                    '{"status": "ERROR", "message": "Vui lòng nhập từ khoá"}')
                return
            if self.proxy != '' and not validate_proxy(self.proxy):
                self.result_signal.emit(
                    '{"status": "ERROR", "message": "Proxy không hợp lệ"}')
                return
            try:
                chrome = AutoChrome(
                    self.load_image,
                    self.load_css,
                    self.headless,
                    self.proxy
                )
            except Exception as e:
                self.result_signal.emit(
                    '{"status": "ERROR", "message": "' + str(e) + '"}')
                return
            status = chrome.login(self.username, self.password, self.key_2fa)
            if status != 'SUCCESS':
                self.result_signal.emit(
                    '{"status": "ERROR", "message": "Thông tin tài khoản không hợp lệ"}')
                return
            try:
                result = chrome.search_group(self.keyword, self.page_number)
                if "SUCCESS" in result:
                    number = result.split('|')[1]
                    self.result_signal.emit(
                        '{"status": "SUCCESS", "message": "Lấy được + ' + f'{number}' + ' Group!"}')
                else:
                    self.result_signal.emit(
                        '{"status": "ERROR", "message": "Lỗi không xác định"}')
            except Exception as e:
                self.result_signal.emit(
                    '{"status": "ERROR", "message": "' + str(e) + '"}')

    class OvFuk(QWidget):
        def __init__(self):
            super().__init__()
            self.sound = QSound('./media/tuturu.wav')
            self.initUI()

        def initUI(self):
            icon_pixmap = base64_to_pixmap(base64_icon)
            icon = QIcon(icon_pixmap)
            self.setWindowIcon(icon)
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
            self.keyword_label = QLabel('🔒 Nhập từ khoá:')
            self.keyword = QLineEdit(self)
            self.keyword.setPlaceholderText(
                'Nhập vào từ khoá cần tìm(VD: Nhà Hàng, Quán Hát,...)')
            self.page_label = QLabel('📄 Số trang cần lấy:')
            self.page_number = QSpinBox(self)
            self.page_number.setMinimum(1)
            self.page_number.setToolTip('Số lần ấn xem thêm')
            self.button_login = QPushButton('🚀 Chạy', self)
            self.button_login.clicked.connect(self.handle_login)

            config_layout.addWidget(self.proxy_label)
            config_layout.addSpacing(5)
            config_layout.addWidget(self.proxy)
            config_layout.addSpacing(5)
            config_layout.addLayout(check_box_layout)
            config_layout.addSpacing(5)
            config_layout.addWidget(self.keyword_label)
            config_layout.addSpacing(5)
            config_layout.addWidget(self.keyword)
            config_layout.addSpacing(5)
            config_layout.addWidget(self.page_label)
            config_layout.addSpacing(5)
            config_layout.addWidget(self.page_number)
            config_layout.addSpacing(5)
            main_layout = QVBoxLayout()
            main_layout.addItem(layout_1)
            main_layout.addItem(layout_2)
            main_layout.addItem(config_layout)
            main_layout.addWidget(self.button_login)
            self.setLayout(main_layout)
            self.apply_stylesheet("style.qss")
            self.setFixedSize(self.sizeHint())
            self.show()

        def apply_stylesheet(self, filename):
            try:
                with open(filename, "r") as file:
                    stylesheet = file.read()
                    self.setStyleSheet(stylesheet)
            except FileNotFoundError:
                print(f"Stylesheet file '{filename}' not found.")

        def handle_login(self):
            username = self.input_username.text()
            password = self.input_password.text()
            key_2fa = self.input_2fa.text()
            proxy = self.proxy.text()
            load_image = self.load_image.isChecked()
            load_css = self.load_css.isChecked()
            hide_chrome = self.hide_chrome.isChecked()
            keyword = self.keyword.text()
            page_number = self.page_number.value()
            self.thread: Worker = Worker(
                username, password, key_2fa, proxy, load_image, load_css, hide_chrome, keyword, page_number)
            self.thread.result_signal.connect(self.handle_result)
            self.thread.start()

        def handle_result(self, result):
            try:
                result_dict = json.loads(result)
                status = result_dict.get("status")
                message = result_dict.get("message")

                if status == "ERROR":
                    QMessageBox.critical(self, "Lỗi", message)
                else:
                    QMessageBox.information(
                        self, "Thành công", "Hoạt động đã hoàn tất thành công")
            except json.JSONDecodeError:
                QMessageBox.critical(
                    self, "Lỗi", "Dữ liệu trả về không hợp lệ")

        def select_images(self):
            options = QFileDialog.Options()
            options |= QFileDialog.ReadOnly

            file_dialog = QFileDialog(self)
            file_dialog.setFileMode(QFileDialog.ExistingFiles)
            file_dialog.setNameFilter("Images (*.png *.jpg *.bmp)")
            file_dialog.setViewMode(QFileDialog.List)
            file_dialog.setOptions(options)

            if file_dialog.exec_():
                self.image_paths = file_dialog.selectedFiles()
                if len(self.image_paths) > 3:
                    QMessageBox.warning(
                        self, "Cảnh báo", "Bạn chỉ có thể chọn tối đa 3 hình ảnh.")
                    self.image_paths = self.image_paths[:3]
                else:
                    self.sound.play()
                    QMessageBox.about(
                        self, "Thông báo", f"Đã chọn {len(self.image_paths)} hình ảnh.")
            print(self.image_paths)

    window = OvFuk()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()