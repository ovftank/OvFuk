import sys

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLineEdit,
                             QMainWindow, QMessageBox, QPushButton,
                             QVBoxLayout, QWidget)

from lib import AutoChrome


class Worker(QThread):
    result_signal = pyqtSignal(str)

    def __init__(self, username, password, key_2fa):
        super().__init__()
        self.username = username
        self.password = password
        self.key_2fa = key_2fa

    def run(self):
        chrome = AutoChrome()
        result = chrome.login(self.username, self.password, self.key_2fa)
        self.result_signal.emit(result)


class LoginApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('OvFuk Plus')
        self.setWindowFlags(self.windowFlags() & ~
                            Qt.WindowMaximizeButtonHint)  # type: ignore
        layout = QVBoxLayout()

        self.label_username = QLabel('Tài khoản(UID, Email, SĐT):')
        self.input_username = QLineEdit(self)

        self.label_password = QLabel('Mật khẩu:')
        self.input_password = QLineEdit(self)
        self.input_password.setEchoMode(QLineEdit.Password)

        self.label_2fa = QLabel('2FA Key:')
        self.input_2fa = QLineEdit(self)

        self.button_login = QPushButton('Đăng nhập', self)
        self.button_login.clicked.connect(self.handle_login)

        layout.addWidget(self.label_username)
        layout.addWidget(self.input_username)
        layout.addWidget(self.label_password)
        layout.addWidget(self.input_password)
        layout.addWidget(self.label_2fa)
        layout.addWidget(self.input_2fa)
        layout.addWidget(self.button_login)

        self.setLayout(layout)
        self.resize(300, 200)
        self.show()

    def handle_login(self):
        username = self.input_username.text()
        password = self.input_password.text()
        key_2fa = self.input_2fa.text()

        self.thread: Worker = Worker(username, password, key_2fa)
        self.thread.result_signal.connect(self.handle_result)
        self.thread.start()

    def handle_result(self, result):
        if result == "FAILED":
            QMessageBox.warning(
                self, '???', '???')
        else:
            QMessageBox.information(
                self, 'OK', 'OK')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LoginApp()
    sys.exit(app.exec_())
