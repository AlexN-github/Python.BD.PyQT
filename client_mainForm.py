import sys

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget


# Класс основного окна
class MainForm(QMainWindow):
    def __init__(self):
        super().__init__()
        # Инициализация базы данных
        #self.server = server
        # Инициализируем форму
        self.initUI()

    def initUI(self):
        uic.loadUi('client_mainForm.ui', self)

        self.fill_contactlist_listWidget()
        # Определяем обработчики для событий
        self.addcontact_pushButton.clicked.connect(self.addcontact_pushButton_clicked)
        self.delcontact_pushButton.clicked.connect(self.delcontact_pushButton_clicked)
        self.sendmessage_pushButton.clicked.connect(self.sendmessage_pushButton_clicked)
        self.contactlist_listWidget.doubleClicked.connect(self.contactlist_listWidget_doubleClicked)
        #self.actionRefresh.triggered.connect(self.actionRefresh_triggered)
        #self.actionExit.triggered.connect(qApp.quit)
        #self.userlist_listview.itemSelectionChanged.connect(self.userlist_listview_itemPressed)
        #self.refresh_mainForm()

        self.show()

    def addcontact_pushButton_clicked(self):
        print('Hello')

    def delcontact_pushButton_clicked(self):
        def removeSel():
            listItems = self.contactlist_listWidget.selectedItems()
            if not listItems: return
            for item in listItems:
                self.contactlist_listWidget.takeItem(self.contactlist_listWidget.row(item))
        removeSel()
        print('Hello')

    def sendmessage_pushButton_clicked(self):
        sendmessage = self.sendmessage_textEdit.toPlainText()
        self.correspondence_Tab1_textEdit.append(sendmessage)
        print('Hello')

    def contactlist_listWidget_doubleClicked(self):
        selected_contact = self.contactlist_listWidget.currentItem().text()
        self.correspondence_tabWidget.insertTab(self.correspondence_tabWidget.count(), QWidget(), selected_contact)
        print('Hello')

    def fill_contactlist_listWidget(self):
        print('Hello')
        list_contact = ['contact1', 'contact2', 'contact3']
        # print(database.users_list()[0])
        #for user in sorted(self.server.database.users_list()):
        #    list.append(user[0])
        self.contactlist_listWidget.clear()
        self.contactlist_listWidget.addItems(list_contact)
        self.contactlist_listWidget.setCurrentRow(0)



if __name__ == '__main__':
    server_app = QApplication(sys.argv)
    mf = MainForm()
    # Запускаем GUI
    server_app.exec_()
