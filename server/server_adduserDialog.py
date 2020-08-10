import binascii
import hashlib
import os
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QPushButton, QMessageBox
from server.server_database import ServerStorage

class adduserDialog(QDialog):

    def __init__(self, database):
        super().__init__()
        self.initUI()
        self.database = database
        self.messages = QMessageBox()

    def initUI(self):
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'server_adduserDialog.ui'), self)

        # Определяем обработчики для событий
        self.accept_pushButton.clicked.connect(self.save_data)
        self.cancel_pushButton.clicked.connect(self.reject)

    def save_data(self):
        """
        Метод проверки правильности ввода и сохранения в базу нового пользователя.
        """
        if not self.username_lineEdit.text():
            self.messages.critical(
                self, 'Ошибка', 'Не указано имя пользователя.')
            return
        elif self.pwd_lineEdit.text() != self.pwd2_lineEdit.text():
            self.messages.critical(
                self, 'Ошибка', 'Введённые пароли не совпадают.')
            return
        elif self.database.check_user(self.username_lineEdit.text()):
            self.messages.critical(
                self, 'Ошибка', 'Пользователь уже существует.')
            return
        else:
            # Генерируем хэш пароля, в качестве соли будем использовать логин в
            # нижнем регистре.
            passwd_bytes = self.pwd_lineEdit.text().encode('utf-8')
            salt = self.username_lineEdit.text().lower().encode('utf-8')
            passwd_hash = hashlib.pbkdf2_hmac('sha512', passwd_bytes, salt, 10000)
            self.database.add_user(self.username_lineEdit.text(), binascii.hexlify(passwd_hash))
            self.messages.information(
                self, 'Успех', 'Пользователь успешно зарегистрирован.')
            # Рассылаем клиентам сообщение о необходимости обновить справичники
            self.close()


if __name__ == '__main__':
    class TestMainWindow(QMainWindow):

        def __init__(self):
            super().__init__()
            self.Button1 = QPushButton(text='button1', objectName='button1', clicked=self.openDialog, parent=self)
            self.Button1.setGeometry(1, 1, 50,50)

            self.adduserDialog = adduserDialog(database)

            self.show()

        def openDialog(self):
            self.adduserDialog.show()


    database = ServerStorage('sqlite:///server_base.db3')
    server_app = QApplication(sys.argv)
    mf = TestMainWindow()

    # Запускаем GUI
    server_app.exec_()
