import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication


# Класс основного окна
class MainForm(QMainWindow):
    def __init__(self, server):
        super().__init__()
        # Инициализация базы данных
        self.server = server
        # Инициализируем форму
        self.initUI()

    def initUI(self):
        uic.loadUi('server_mainForm.ui', self)
        # Определяем обработчики для событий
        self.actionRefresh.triggered.connect(self.actionRefresh_triggered)
        self.actionExit.triggered.connect(qApp.quit)
        self.userlist_listview.itemSelectionChanged.connect(self.userlist_listview_itemPressed)
        self.refresh_mainForm()

        self.show()

if __name__ == '__main__':
    server_app = QApplication(sys.argv)
    mf = MainForm()
    # Запускаем GUI
    server_app.exec_()
