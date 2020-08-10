import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QApplication, QPushButton, QMainWindow


class AuthDialog(QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        uic.loadUi('client_AuthDialog.ui', self)

        # Определяем обработчики для событий
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)



if __name__ == '__main__':
    class TestMainWindow(QMainWindow):

        def __init__(self):
            super().__init__()
            self.Button1 = QPushButton(text='button1', objectName='button1', clicked=self.openDialog, parent=self)
            self.Button1.setGeometry(1, 1, 50,50)

            self.AuthDialog = AuthDialog(self)

            self.show()

        def openDialog(self):
            self.AuthDialog.show()



    server_app = QApplication(sys.argv)
    mf = TestMainWindow()

    # Запускаем GUI
    server_app.exec_()
