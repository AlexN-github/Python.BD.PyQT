#import datetime
import os
import sys
from datetime import datetime

from PyQt5 import uic
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QHBoxLayout, QTextEdit, QMessageBox, qApp

# Класс основного окна
from client.client_AuthDialog import AuthDialog
from client.client_usersSelectDialog import usersSelectDialog
from client.client_connectsettingsDialog import connectsettingsDialog
from common.utils import get_current_fullpath


class MainForm(QMainWindow):
    def __init__(self, client):
        super().__init__()
        # Инициализация базы данных
        self.client = client
        self.client.set_external_output_logMessage(self.write_footerLog_textEdit) # (lambda: print('123'))
        #self.client.set_external_output_ReceiveMessage(self.write_ReceiveMessage_textEdit) # (lambda: print('123'))

        #Подписываемся на события CLIENT
        self.client.message_receive.connect(self.write_ReceiveMessage_textEdit)
        #self.client.unauthorized_access.connect(self.auth)

        # Инициализируем форму
        self.initUI()

        self.AuthDialog = AuthDialog(self)

        # Инициируем подключение к серверу
        self.client.connect_to_server()
        while True:
            res = self.client.execute_command_presence()
            if res['code'] == 200:
                break
            if res['code'] == 403:
                self.auth()

        #Прописываем заголовок окна
        self.setWindowTitle('{0} - {1}'.format(self.windowTitle(), self.client.account_name))

        # Создаем подчиненные формы
        #self.usersSelectDialog = usersSelectDialog(self)
        self.usersSelectDialog = usersSelectDialog(self)
        self.connectsettingsDialog = connectsettingsDialog(self)

        # Заполняем список контактов
        self.fill_contactlist_listWidget()

    def initUI(self):
        # Инициируем главную форму
        uic.loadUi(os.path.join(os.path.dirname(__file__), 'client_mainForm.ui'), self)

        # Определяем обработчики для событий
        self.addcontact_pushButton.clicked.connect(self.addcontact_pushButton_clicked)
        self.delcontact_pushButton.clicked.connect(self.delcontact_pushButton_clicked)
        self.sendmessage_pushButton.clicked.connect(self.sendmessage_pushButton_clicked)
        self.contactlist_listWidget.doubleClicked.connect(self.contactlist_listWidget_doubleClicked)
        self.correspondence_tabWidget.tabCloseRequested.connect(lambda index: self.correspondence_tabWidget.widget(index).deleteLater())
        self.actionExit.triggered.connect(qApp.quit)
        self.actionСonnect.triggered.connect(lambda: self.connectsettingsDialog.exec_())
        self.actionAuth.triggered.connect(self.auth)

        self.show()

    def write_footerLog_textEdit(self, text_message):
        log_message = '{0}::{1}'.format(datetime.now().strftime('%d-%m-%y %H:%M:%S'), text_message)
        print(log_message)
        self.footerLog_textEdit.append(log_message)

    def write_ReceiveMessage_textEdit(self, sender, message):
        textEdit = self.findChild(QObject, '{0}_textEdit'.format(sender))
        if not textEdit:
            self.__insert_new_tab(sender)
        textEdit = self.findChild(QObject, '{0}_textEdit'.format(sender))
        textEdit.append(message)

    def auth(self):
        self.AuthDialog.login_lineEdit.setText(self.client.account_name)
        self.AuthDialog.pwd_lineEdit.setText(self.client.password)
        res = self.AuthDialog.exec_()
        if res:
            self.client.account_name = self.AuthDialog.login_lineEdit.text()
            self.client.password = self.AuthDialog.pwd_lineEdit.text()

    def addcontact_pushButton_clicked(self):
        def select_new_contact(lu):
            self.usersSelectDialog.fill_users_tableView(lu)
            res = self.usersSelectDialog.exec_()
            if res:
                selected_row = self.usersSelectDialog.users_tableView.selectionModel().selectedRows()[0]
                return selected_row.data()
            else:
                return None

        lu = self.client.execute_command_get_allUsers()
        #lu = [
        #    ('test1', datetime(2020, 8, 5, 12, 1, 35, 603531)),
        #    ('test2', datetime(2020, 8, 5, 12, 2, 35, 603531)),
        #    ('test3', datetime(2020, 8, 5, 12, 3, 35, 603531)),
        #    ('test4', datetime(2020, 8, 5, 12, 4, 35, 603531)),
        #]
        new_contact = select_new_contact(lu)
        if new_contact:
            # Добавляем в список формы
            for index in range(self.contactlist_listWidget.count()):
                if self.contactlist_listWidget.item(index).text() == new_contact:
                    return
            else:
                # Добавляем только если нет такого в списке
                self.contactlist_listWidget.addItem(new_contact)
                # Отправляем запрос серверу на добавление
                self.client.execute_command_add_contact(new_contact)

    def delcontact_pushButton_clicked(self):
        def remove_select_contact():
            listItems = self.contactlist_listWidget.selectedItems()
            if not listItems:
                return
            for item in listItems:
                buttonReply = QMessageBox.question(self, 'Удаление контакта',
                                                   'Вы действительно хотите удалить контакт `{0}` из списка контактов?'.format(item.text()),
                                                   QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if buttonReply == QMessageBox.Yes:
                    # Удаляем контакт из списка формы
                    self.contactlist_listWidget.takeItem(self.contactlist_listWidget.row(item))
                    tab = self.findChild(QObject, '{0}_tab'.format(item.text()))
                    if tab:
                        tab.deleteLater()
                    # Отправляем запрос серверу на удаление
                    self.client.execute_command_del_contact(item.text())

        remove_select_contact()



        print('Hello')

    def sendmessage_pushButton_clicked(self):
        if not self.correspondence_tabWidget.currentWidget():
            QMessageBox.question(self, 'Сообщение',
                                 'Для отправки сообщения необходимо выбрать контакт. Выберите контакт в списке контактов и нажмите на нем два раза',
                                 QMessageBox.Yes, QMessageBox.Yes)
            return
        sendmessage = self.sendmessage_textEdit.toPlainText()
        current_contact_tab = self.correspondence_tabWidget.currentWidget().objectName().replace('_tab', '')
        self.client.execute_command_send_message(current_contact_tab, sendmessage)
        #print(current_contact_tab)
        editText = self.findChild(QObject, '{0}_textEdit'.format(current_contact_tab))

        message = 'Исходящее сообщение {0}\n{1}'.format(datetime.now().strftime('%d-%m-%y %H:%M:%S'), sendmessage)
        editText.append(message)
        self.sendmessage_textEdit.clear()
        print('Hello')

    def __insert_new_tab(self, contact):
        search_tab = self.findChild(QObject, '{0}_tab'.format(contact))
        if search_tab:
            self.correspondence_tabWidget.setCurrentWidget(search_tab)
        else:
            number_new_tab = self.correspondence_tabWidget.count()
            self.correspondence_tabWidget.insertTab(number_new_tab, QWidget(), contact)
            new_tab = self.correspondence_tabWidget.widget(number_new_tab)
            new_tab.setObjectName('{0}_tab'.format(contact))
            text_edit = QTextEdit('', self)
            name_widget = '{0}_textEdit'.format(contact)
            text_edit.setObjectName(name_widget)
            text_edit.setReadOnly(True)
            #print(self.findChild(QObject, 'contact3_textEdit'))
            hbox = QHBoxLayout()
            hbox.addWidget(text_edit)
            new_tab.setLayout(hbox)
            self.correspondence_tabWidget.setCurrentWidget(new_tab)

    def contactlist_listWidget_doubleClicked(self):
        selected_contact = self.contactlist_listWidget.currentItem().text()
        self.__insert_new_tab(selected_contact)

        #print('Hello')

    def fill_contactlist_listWidget(self):
        list_contact = self.client.execute_command_get_contacts()
        #print('Hello')
        #list_contact = ['contact1', 'contact2', 'contact3']
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
