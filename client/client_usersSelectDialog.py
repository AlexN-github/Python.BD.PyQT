import sys
import datetime
from PyQt5 import uic
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QDialog, QMainWindow, QApplication, QPushButton


class usersSelectDialog(QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        uic.loadUi('client_usersSelectDialog.ui', self)

        # Определяем обработчики для событий
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.users_tableView.doubleClicked.connect(self.accept)  #lambda: self.accept()

    def fill_users_tableView(self, list_users):
        list = QStandardItemModel()
        list.setHorizontalHeaderLabels(['Имя Клиента', 'Время подключения'])
        for row in list_users:
            user, time = row
            user = QStandardItem(user)
            user.setEditable(False)
            time = QStandardItem(time)
            time.setEditable(False)
            list.appendRow([user, time])
        self.users_tableView.setModel(list)
        self.users_tableView.resizeColumnsToContents()


#'name', 'last_login'

if __name__ == '__main__':
    class TestMainWindow(QMainWindow):

        def __init__(self):
            super().__init__()
            self.Button1 = QPushButton(text='button1', objectName='button1', clicked=self.openDialog1, parent=self)
            self.Button1.setGeometry(1, 1, 50,50)
            self.Button2 = QPushButton(text='button2', objectName='button2', clicked=self.openDialog2, parent=self)
            self.Button2.setGeometry(1, 60, 50,50)
            self.usersSelectDialog = usersSelectDialog(self)

            self.show()
            #self.openDialog()

        def openDialog1(self):
            def select_new_contact(lu):
                self.usersSelectDialog.fill_users_tableView(lu)
                res = self.usersSelectDialog.exec_()
                if res:
                    selected_row = self.usersSelectDialog.users_tableView.selectionModel().selectedRows()[0]
                    number_row = self.usersSelectDialog.users_tableView.selectionModel().selectedRows()[0].row()
                    return selected_row.data()
                else:
                    return None

            lu = [
                ('test1', datetime.datetime(2020, 8, 5, 12, 1, 35, 603531)),
                ('test2', datetime.datetime(2020, 8, 5, 12, 2, 35, 603531)),
                ('test3', datetime.datetime(2020, 8, 5, 12, 3, 35, 603531)),
                ('test4', datetime.datetime(2020, 8, 5, 12, 4, 35, 603531)),
            ]

            print(select_new_contact(lu))


        def openDialog2(self):
            lu = [
                ('test11', datetime.datetime(2020, 8, 5, 12, 1, 35, 603531)),
                ('test22', datetime.datetime(2020, 8, 5, 12, 2, 35, 603531)),
                ('test33', datetime.datetime(2020, 8, 5, 12, 3, 35, 603531)),
                ('test44', datetime.datetime(2020, 8, 5, 12, 4, 35, 603531)),
            ]
            self.usersSelectDialog.fill_users_tableView(lu)
            res = self.usersSelectDialog.exec_()
            if res:
                print('Ok')
            else:
                print('No')
            #print(self.usersSelectDialog.Accepted)
            #print(res)

    server_app = QApplication(sys.argv)
    mf = TestMainWindow()
    #mf.clicked.connect(mf.refreshopenDialog())
    # Запускаем GUI

    server_app.exec_()
