import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QPushButton


class connectsettingsDialog(QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        uic.loadUi('client_connectsettingsDialog.ui', self)

        # Определяем обработчики для событий
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.testconnect_pushButton.clicked.connect(self.testconnect)

    def testconnect(self):
        import socket
        def isOpen(ip, port):
            return
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.connect((ip, int(port)))
                s.shutdown(2)
                return True
            except:
                return False

        print(isOpen(self.ip_addr_lineEdit.text(), self.port_lineEdit.text()))


if __name__ == '__main__':
    class TestMainWindow(QMainWindow):

        def __init__(self):
            super().__init__()
            self.Button1 = QPushButton(text='button1', objectName='button1', clicked=self.openDialog, parent=self)
            self.Button1.setGeometry(1, 1, 50,50)

            self.connectsettingsDialog = connectsettingsDialog(self)

            self.show()

        def openDialog(self):
            self.connectsettingsDialog.show()



    server_app = QApplication(sys.argv)
    mf = TestMainWindow()

    # Запускаем GUI
    server_app.exec_()
