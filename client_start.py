# Программа клиента
import binascii
import hashlib
import hmac
from datetime import datetime
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication
import argparse
import json
from socket import *
import sys
import time
from client.client_mainForm import MainForm
from common.variables import *
import logging
from log.client_log_config import logger


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', default='')
    parser.add_argument('-a', '--addr', default='localhost')
    parser.add_argument('-p', '--port', default=str(default_port))
    return parser


# Основной класс клиента
class Client(QtCore.QThread):
    # Создаем сигнал прихода нового сообщения
    message_receive = QtCore.pyqtSignal(object, object)

    def __init__(self, listen_address, listen_port, client_name):

        # Параментры подключения
        self.addr = listen_address
        self.port = int(listen_port)

        # Имя клиента
        self.account_name = client_name
        # Пароль для тестирования
        self.password = '123456'

        # Прием сообщений в фоне
        self.background_receive = True

        # Инициализация свойств
        self.random_str = None

        # Конструктор предка
        super().__init__()

    def set_external_output_logMessage(self, f):
        global ext_output
        ext_output = f

    def set_external_output_ReceiveMessage(self, f):
        global output_ReceiveMessage
        output_ReceiveMessage = f

    def execute_command_presence(self):
        def get_client_digest():
            # Запускаем процедуру авторизации
            if self.random_str is None:
                return None
            # Получаем хэш пароля
            passwd_bytes = self.password.encode('utf-8')
            salt = self.account_name.lower().encode('utf-8')
            passwd_hash = hashlib.pbkdf2_hmac('sha512', passwd_bytes, salt, 10000)
            passwd_hash_string = binascii.hexlify(passwd_hash)
            hash = hmac.new(passwd_hash_string, self.random_str.encode('utf-8'), 'MD5')
            digest = hash.digest()
            client_digest = binascii.b2a_base64(digest).decode('ascii')
            # logger.debug('random_str= {0}'.format(self.random_str))
            # logger.degub('passwd_hash_string= {0}'.format(passwd_hash_string))

            return client_digest

        logger.info('Выполняем команду: `presence`')
        ext_output('Выполняем команду: `presence`')
        # print('Выполняем команду: `presence`')
        command = {
            'action': 'presence',
            'time': int(time.time()),
            'type': 'status',
            'sender': self.account_name,
            'data': get_client_digest()
        }
        result = self.execute_command(command)
        return result

    def execute_command_get_contacts(self):
        logger.info('Выполняем команду: `get_contacts`')
        ext_output('Выполняем команду: `get_contacts`')
        # print('Выполняем команду: `get_contacts`')
        command = {
            'action': 'get_contacts',
            'time': int(time.time()),
            'sender': self.account_name
        }
        result = self.execute_command(command)
        logger.debug(result)
        return result['contact_list']

    def execute_command_get_allUsers(self):
        message = 'Выполняем команду: `get_allUsers`'
        logger.info(message)
        ext_output(message)
        # print('Выполняем команду: `get_allUsers`')
        command = {
            'action': 'get_allUsers',
            'time': int(time.time()),
            'sender': self.account_name
        }
        result = self.execute_command(command)
        return result['allUsers_list']

    def execute_command_add_contact(self, username):
        logger.info('Выполняем команду: `add_contact`')
        # print('Выполняем команду: `add_contact`')
        command = {
            'action': 'add_contact',
            'time': int(time.time()),
            'sender': self.account_name,
            'user': username
        }
        result = self.execute_command(command)
        return result

    def execute_command_del_contact(self, username):
        logger.info('Выполняем команду: `del_contact`')
        ext_output('Выполняем команду: `del_contact`')
        # print('Выполняем команду: `del_contact`')
        command = {
            'action': 'del_contact',
            'time': int(time.time()),
            'sender': self.account_name,
            'user': username
        }
        result = self.execute_command(command)
        return result

    def execute_command_send_message(self, username, message):
        logger.info('Выполняем команду: `send_message`')
        # print('Выполняем команду: `send_message`')
        command = {
            'action': 'send_message',
            'time': int(time.time()),
            'sender': self.account_name,
            'to': username,
            'message': message
        }
        result = self.execute_command(command)
        # print(result['contact_list'])
        return result

    def execute_command_broadcast(self):
        logger.info('Выполняем команду: `broadcast`')
        ext_output('Выполняем команду: `broadcast`')
        # print('Выполняем команду: `broadcast`')
        command = {
            'action': 'broadcast',
            'time': int(time.time()),
            'type': 'status',
            'sender': self.account_name
        }
        result = self.execute_command(command)
        print(result)

        return result

    def receive_messages(self):
        def parsing_recv(msg):
            respond = json.loads(msg)
            return respond

        data = self.sock.recv(block_transfer_size)
        msg_recv = data.decode('utf-8')
        result = parsing_recv(msg_recv)
        if 'action' in result.keys() and result['action'] == 'send_message':
            message = 'Принято сообщение от клиента {0} msg: {1}'.format(result['sender'], result['message'])
            logger.info(message)
            ext_output(message)
        else:
            message = 'Сообщение от сервера: {0}; Code: {1}'.format(result['msg'], result['code'])
            logger.info(message)
            ext_output(message)

        return result

    def connect_to_server(self):
        message = 'Устанавливаем соединение: {0}'.format((self.addr, self.port))
        logger.info(message)
        ext_output(message)
        # print('Устанавливаем соединение:', (addr, port))
        try:
            self.sock = socket(AF_INET, SOCK_STREAM)  # Создать сокет TCP
            self.sock.connect((self.addr, self.port))  # Соединиться с сервером
            self.sock.settimeout(0.2)  # Таймаут для операций с сокетом

            self.daemon = True
            self.start()
            message = 'Подключение к серверу успешно'
            logger.info(message)
            ext_output(message)
        except Exception as err:
            if logger:
                message = 'Подключение не успешно: {0}'.format((self.addr, self.port))
                logger.error(message)
                logger.debug(err)
                ext_output(message)
                ext_output(str(err))
                return False
            else:
                print(err)

        return

    def disconnect_from_server(self):
        message = 'Отключаемся от сервера {0}'.format((self.addr, self.port))
        logger.info(message)
        ext_output(message)
        # print('Отключаемся от сервера', (addr, port))
        self.sock.close()

    def execute_command(self, msg):
        def parsing_recv(msg):
            respond = json.loads(msg)
            return respond

        msg_send = json.dumps(msg)
        result = {}
        try:
            self.pause_background_receive(False)
            time.sleep(0.3)
            self.sock.send(msg_send.encode('utf-8'))
            # print(result)
            # Даем время на ответ серверу 30сек, иначе таймаут
            start_time = datetime.now()
            timeout_sec = 30
            while True:
                try:
                    if (datetime.now() - start_time).seconds > timeout_sec:
                        break
                    result = self.receive_messages()
                    break
                except OSError as e:
                    # logger.info('Продолжаем ожидать ответ')
                    pass
        finally:
            self.pause_background_receive(True)

        if result['code'] == 403:
            # если пришел ответ от сервера 403, то выполняем авторизацию
            logger.critical(f'Запрос неавторизован.')
            if not msg['data'] is None:
                logging.critical('Запрос авторизации не выполнен. Неверное имя пользователя или пароль')
                return result
                # raise ServerError('Запрос неавторизован')

            self.random_str = result['data']
            result = self.execute_command_presence()
            pass

        return result

    def pause_background_receive(self, pause):
        self.background_receive = pause

    def run(self):
        try:
            # self.background_receive = False
            while True:
                if self.background_receive:
                    # logger.info('читаем из бек ресив')
                    try:
                        res = self.receive_messages()
                        print(res)
                        # logger.info('Принято сообщение через приемник res= {0}'.format(res))
                        if res['action'] == 'send_message':
                            message = 'Входящее сообщение {0}\n{1}'.format(datetime.now().strftime('%d-%m-%y %H:%M:%S'), res['message'])
                            self.message_receive.emit(res['sender'], message)

                    except OSError as e:
                        pass  # timeout вышел
                    # print('background_receive=', self.background_receive)
                else:
                    # print('background_receive=', self.background_receive)
                    # logger.info('Ставим на паузу бэк ресив')
                    # time.sleep(1)
                    pass

            # disconnect_from_server()
        except Exception as err:
            logger.error('Соединение с сервером было разорвано: {0}'.format(str(err)))
            ext_output('Соединение с сервером было разорвано.')


def print_help():
    print('*' * 30)
    print('Отправить серверу команду PRESENCE (1)')
    print('Отправить команду BROADCAST (2)')
    print('Отправить cерверу команду GET_CONTACTS (3)')
    print('Отправить cерверу команду ADD_CONTACT (4)')
    print('Отправить cерверу команду DEL_CONTACT (5)')
    print('Отправить сообщение получателю SEND_MESSAGE (6)')
    print('Отключиться от сервера и выйти (q)')

def console_select_input(client):
    while True:
        print_help()
        inputuser = input()
        if inputuser == '1':
            res = client.execute_command_presence()
            print(res)
        if inputuser == '2':
            res = client.execute_command_broadcast()
            print(res)
        if inputuser == '3':
            contact_list = client.execute_command_get_contacts()
            print('Список контактов: {0}'.format(contact_list))
        if inputuser == '4':
            inputuser = input('Введите имя пользователя для добавления в контакты\n\r')
            client.execute_command_add_contact(inputuser)
        if inputuser == '5':
            inputuser = input('Введите имя пользователя для удаления из контактов\n\r')
            client.execute_command_del_contact(inputuser)
        if inputuser == '6':
            username = input('Введите имя получателя\n\r')
            message = input('Введите текст сообщения\n\r')
            client.execute_command_send_message(username, message)
        elif inputuser == 'q':
            break


def main():

    # Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию.
    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])

    # Создание экземпляра класса - клиента.
    client = Client(namespace.addr, namespace.port, namespace.name)

    # Консольная версия управления
    # console_select_input(client)

    server_app = QApplication(sys.argv)
    mf = MainForm(client)
    # Запускаем GUI
    server_app.exec_()


try:
    # Инициализируем логирование
    message = 'Программа клиент запущена'
    logger.info(message)

    if __name__ == '__main__':
        main()


except Exception as err:
    if logger:
        logger.error(err)
    else:
        print(err)


