from PyQt5 import uic
import sys

from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import qApp, QMainWindow, QApplication

from server_adduserDialog import adduserDialog
from server_database import ServerStorage


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
        self.adduser_pushButton.clicked.connect(lambda: (self.adduserDialog.exec_(), self.refresh_mainForm()))
        self.deluser_pushButton.clicked.connect(lambda: (self.server.database.remove_user(self.userlist_listview.selectedItems()[0].text()), self.refresh_mainForm()))  #,

        # Создаем подчиненные формы
        self.adduserDialog = adduserDialog(self.server.database)

        self.refresh_mainForm()

        self.show()




    def actionRefresh_triggered(self):
        self.refresh_mainForm()

    def userlist_listview_itemPressed(self):
        current_item = self.userlist_listview.currentItem().text()
        user = self.get_userdata(current_item)
        if not user:
            return
        last_login = user[1]
        # print(last_login.strftime('%d-%m-%y %H:%M:%S'))
        self.lastlogin.setText(last_login.strftime('%d-%m-%y %H:%M:%S'))
        for item in self.server.database.message_history():
            if item[0] == user[0]:
                self.send_message.setText(str(item[2]))
                self.recv_message.setText(str(item[3]))
        # Заполняем таблицу историй входов
        self.fill_historylogin_tableView(user[0])

    def refresh_mainForm(self):
        # print('Press Me')
        self.fill_userlist_listwidget()
        self.fill_activesession_tableView()
        settings = {
            'BindIP': self.server.addr,
            'Port': str(self.server.port),
            'DBPath': self.server.database_unc
        }
        self.fill_settings(settings)

    def fill_userlist_listwidget(self):
        list = []
        # print(database.users_list()[0])
        for user in sorted(self.server.database.users_list()):
            list.append(user[0])
        self.userlist_listview.clear()
        self.userlist_listview.addItems(list)
        self.userlist_listview.setCurrentRow(0)

    def fill_settings(self, settings):
        self.BindIP.setText(settings['BindIP'])
        self.Port.setText(settings['Port'])
        self.DBPath.setText(settings['DBPath'])

    def fill_historylogin_tableView(self, username):
        def gui_create_model():
            list_history_login = self.server.database.login_history(username)
            list = QStandardItemModel()
            header = ['Время логина', 'IP адрес', 'Порт подключения']
            list.setHorizontalHeaderLabels(header)
            for row in list_history_login:
                user, time, ip, port = row
                ip = QStandardItem(ip)
                ip.setEditable(False)
                port = QStandardItem(str(port))
                port.setEditable(False)
                time = QStandardItem(str(time.strftime('%d-%m-%y %H:%M:%S')))
                time.setEditable(False)
                list.appendRow([time, ip, port])
            return list

        self.historylogin_tableView.setModel(gui_create_model())
        self.historylogin_tableView.resizeColumnsToContents()

    def fill_activesession_tableView(self):
        def gui_create_model():
            list_users = self.server.database.active_users_list()
            list = QStandardItemModel()
            list.setHorizontalHeaderLabels(['Имя Клиента', 'IP адрес', 'Порт подключения', 'Время подключения'])
            for row in list_users:
                user, ip, port, time = row
                user = QStandardItem(user)
                user.setEditable(False)
                ip = QStandardItem(ip)
                ip.setEditable(False)
                port = QStandardItem(str(port))
                port.setEditable(False)
                time = QStandardItem(str(time.strftime('%d-%m-%y %H:%M:%S')))
                time.setEditable(False)
                list.appendRow([user, ip, port, time])
            return list

        self.activesession_tableView.setModel(gui_create_model())
        self.activesession_tableView.resizeColumnsToContents()
        self.activesessionnumber.setText(str(len(self.server.database.active_users_list())))

    def get_userdata(self, username):
        for user in self.server.database.users_list():
            if user[0] == username:
                return user


if __name__ == '__main__':
    pass
    # Инициализация базы данных
    db = ServerStorage()

    server_app = QApplication(sys.argv)
    mf = MainForm(db)
    # Запускаем GUI
    server_app.exec_()
    # mf = MainForm() #database

    # app = QtWidgets.QApplication(sys.argv)
    # mainForm = uic.loadUi('server_mainForm.ui')  # 1.ui
    # mainForm.actionRefresh.triggered.connect(actionRefresh_triggered)
    # mainForm.actionExit.triggered.connect(qApp.quit)
    # mainForm.userlist_listview.itemSelectionChanged.connect(userlist_listview_itemPressed)
    # refresh_mainForm()

    # mainForm.show()
    # sys.exit(app.exec_())
