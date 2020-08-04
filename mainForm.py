from PyQt5 import QtWidgets, uic
import sys
from ..server_database import ServerStorage


def refresh_mainForm():
    print('Press Me')


if __name__ == '__main__':
    # Инициализация базы данных
    database = ServerStorage()
    print(database.users_list())


    app = QtWidgets.QApplication(sys.argv)
    mainForm = uic.loadUi('mainForm.ui')  # 1.ui
    # window.pushButton.clicked.connect(app.quit)
    mainForm.actionRefresh.triggered.connect(refresh_mainForm)

    mainForm.show()
    sys.exit(app.exec_())
