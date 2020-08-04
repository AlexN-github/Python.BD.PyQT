# Программа сервера для получения приветствия от клиента и отправки ответа
import argparse
import configparser
import json
import logging
import os
import sys
import select
import threading

from PyQt5.QtWidgets import QApplication

from server_mainForm import MainForm
from socket import *

from server_database import ServerStorage


def args(server_addr_default, default_port):
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--addr', default=str(server_addr_default))
    parser.add_argument('-p', '--port', default=str(default_port))
    namespace = parser.parse_args(sys.argv[1:])
    return namespace.addr, namespace.port


# Основной класс сервера
class Server(threading.Thread):
    def __init__(self):

        # Загружаем исходные параментры из конфиг файла
        config = self.config_load()

        # Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию.
        ip_default, port_default = config['SETTINGS']['Listen_Address'], config['SETTINGS']['Default_port']
        listen_address, listen_port = args(ip_default, port_default)

        # База данных сервера
        # Инициализация базы данных
        self.database_unc = 'sqlite:///{0}'.format(config['SETTINGS']['Database_file'])
        self.database = ServerStorage(self.database_unc)

        # Параментры подключения
        self.addr = listen_address
        self.port = int(listen_port)

        # Список подключённых клиентов.
        self.clients = []

        # Список имен и сопоставленных сокетов
        self.names = dict()

        # Очередь запросов на обработку
        self.request_queue = {}

        # Конструктор предка
        super().__init__()

    # Загрузка файла конфигурации
    def config_load(self):
        config = configparser.ConfigParser()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        config.read(f"{dir_path}/{'server.ini'}")
        # Если конфиг файл загружен правильно, запускаемся, иначе конфиг по умолчанию.
        if 'SETTINGS' in config:
            return config
        else:
            config.add_section('SETTINGS')
            config.set('SETTINGS', 'Default_port', '7777')
            config.set('SETTINGS', 'Listen_Address', '')
            config.set('SETTINGS', 'Database_path', '')
            config.set('SETTINGS', 'Database_file', 'server_database.db3')
            return config

    def execute_command_presence(self, client, command):
        result = {}
        client_ip, client_port = client.getpeername()
        # Пишем в БД информацию о логине
        self.database.user_login(command['sender'], client_ip, client_port)
        result['msg'] = 'command `{0}` completed successfully'.format(command['action'])
        result['code'] = 200
        self.sending_responde(client, result)
        return result

    def execute_command_get_contacts(self, client, command):
        result = dict()
        # Пишем в БД информацию о логине
        result['msg'] = 'command `{0}` completed successfully'.format(command['action'])
        result['contact_list'] = self.database.get_contacts(command['sender'])
        result['code'] = 200
        self.sending_responde(client, result)
        return result

    def execute_command_add_contact(self, client, command):
        result = dict()
        self.database.add_contact(command['sender'], command['user'])
        result['msg'] = 'command `{0}` completed successfully'.format(command['action'])
        result['code'] = 200
        self.sending_responde(client, result)
        return result

    def execute_command_del_contact(self, client, command):
        result = dict()
        self.database.del_contact(command['sender'], command['user'])
        result['msg'] = 'command `{0}` completed successfully'.format(command['action'])
        result['code'] = 200
        self.sending_responde(client, result)
        return result

    def execute_command_send_message(self, client, command):
        result = dict()
        result['msg'] = 'command `{0}` completed successfully'.format(command['action'])
        result['code'] = 200
        # Отправляем сообщение получателю
        self.sending_responde(self.names[command['to']], command)
        # Пишем историю в БД
        self.database.process_message(command['sender'], command['to'])
        # Отправляем результат операции отправителю
        self.sending_responde(client, result)
        return result

    def execute_command_broadcast(self, client, command):
        result = dict()
        result['msg'] = 'command `{0}` completed successfully'.format(command['action'])
        result['code'] = 200
        self.sending_message_brodcaste(client, result)
        return result

    def processing_command(self, client):
        def parsing_command(msg):
            command = json.loads(msg)
            return command

        def execute_command(command):
            action = command['action']
            if action == 'presence':
                result = self.execute_command_presence(client, command)
            if action == 'broadcast':
                result = self.execute_command_broadcast(client, command)
            if action == 'get_contacts':
                result = self.execute_command_get_contacts(client, command)
            if action == 'add_contact':
                result = self.execute_command_add_contact(client, command)
            if action == 'del_contact':
                result = self.execute_command_del_contact(client, command)
            if action == 'send_message':
                result = self.execute_command_send_message(client, command)
            elif action == '...':
                pass
            else:
                result = {}
                result['msg'] = 'Invalid command'
                result['code'] = 400
            return result

        print('request', client)
        msg = self.request_queue[client]
        print('msg', msg)
        command = parsing_command(msg)
        if command['sender'] not in self.names.keys():
            self.names[command['sender']] = client

        logger.debug('Принято сообщение: {0}, от клиента: {1}'.format(msg, self.addr))
        logger.info('Принята команда: {0}'.format(command['action']))
        return execute_command(command)

    def sending_responde(self, client, command):
        if 'action' in command.keys() and command['action'] == 'send_message':
            logger.info(
                'Отправляем клиенту {0} msg: {1}'.format(command['to'], command['message']))
        else:
            logger.info(
                'Возвращаем клиенту {0} msg: {1}; code: {2}'.format(client.getpeername(), command['msg'], command['code']))
        # print('Возвращаем клиенту {0} msg: {1}; code: {2}'.format(client.getpeername(), result['msg'], result['code']))
        msg_send = json.dumps(command)
        client.send(msg_send.encode('utf-8'))

    def sending_message_brodcaste(self, client, result):
        logger.info(
            'Возвращаем клиенту {0} msg: {1}; code: {2}'.format(client.getpeername(), result['msg'], result['code']))
        # print('Возвращаем клиенту {0} msg: {1}; code: {2}'.format(client.getpeername(), result['msg'], result['code']))
        msg_send = json.dumps(result)
        for cli in self.clients:
            cli.send(msg_send.encode('utf-8'))
        # client.close()

    def sending_message_unicast(self, client, result):
        # logger.info(
        #    'Возвращаем клиенту {0} msg: {1}; code: {2}'.format(client.getpeername(), result['msg'], result['code']))
        # print('Возвращаем клиенту {0} msg: {1}; code: {2}'.format(client.getpeername(), result['msg'], result['code']))
        msg_send = json.dumps(result)
        for cli in self.clients:
            cli.send(msg_send.encode('utf-8'))
        # client.close()

    def read_requests(self, r_clients):
        """ Чтение запросов из списка клиентов
        """

        for sock in r_clients:
            try:
                data = sock.recv(1024).decode('utf-8')
                self.request_queue[sock] = data
            except:
                print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                logger.info('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
                self.clients.remove(sock)

    def queue_processing(self):
        """ Обрабатываем очередь запросов
        """
        while self.request_queue != {}:
            request = next(iter(self.request_queue))
            self.processing_command(request)
            self.request_queue.pop(request, None)

    def run(self):
        s = socket(AF_INET, SOCK_STREAM)  # Создает сокет TCP
        s.bind((self.addr, self.port))  # Присваивает порт 8888
        s.listen(5)  # Переходит в режим ожидания запросов;
        s.settimeout(0.2)  # Таймаут для операций с сокетом

        # Одновременно обслуживает не более
        # 5 запросов.
        logger.info('Слушаем запросы от клиентов: {0}'.format((self.addr, self.port)))
        # print('Запуск сервера:', (addr, port))
        while True:
            try:
                conn, addr = s.accept()
            except OSError as e:
                pass  # timeout вышел
            else:
                print('Получен запрос на соединение от %s' % str(addr))
                logger.info('Получен запрос на соединение от %s' % str(addr))
                self.clients.append(conn)
            finally:
                wait = 10
                r = []
                w = []
                try:
                    r, w, e = select.select(self.clients, self.clients, [], wait)
                except:
                    pass  # Ничего не делать, если какой-то клиент отключился
                try:
                    self.read_requests(r)
                    if r:
                        print(r)
                        self.queue_processing()
                except Exception as err:
                    result = {}
                    result['msg'] = 'Unexpected error'
                    result['code'] = 500
                    self.sending_responde(conn, result)
                    logger.error('Ошибка обработки запроса клиента {0}: {1}'.format(conn, result['msg']))
                    logger.error(str(err))

    def console_select_input(self):
        # Печатаем справку:
        print_help()

        # Основной цикл сервера:
        while True:
            command = input('Введите комманду: ')
            if command == 'help':
                print_help()
            elif command == 'exit':
                break
            elif command == 'users':
                for user in sorted(self.database.users_list()):
                    print(f'Пользователь {user[0]}, последний вход: {user[1]}')
            elif command == 'connected':
                for user in sorted(self.database.active_users_list()):
                    print(
                        f'Пользователь {user[0]}, подключен: {user[1]}:{user[2]}, время установки соединения: {user[3]}')
            elif command == 'loghist':
                name = input(
                    'Введите имя пользователя для просмотра истории. Для вывода всей истории, просто нажмите Enter: ')
                for user in sorted(self.database.login_history(name)):
                    print(f'Пользователь: {user[0]} время входа: {user[1]}. Вход с: {user[2]}:{user[3]}')
            else:
                print('Команда не распознана.')


def print_help():
    print('Поддерживаемые комманды:')
    print('users - список известных пользователей')
    print('connected - список подключенных пользователей')
    print('loghist - история входов пользователя')
    print('exit - завершение работы сервера.')
    print('help - вывод справки по поддерживаемым командам')


def main():

    # Создание экземпляра класса - сервера.
    server = Server()
    server.daemon = True
    server.start()

    # работем через консоль
    # server.console_select_input()

    # Работаем через GUI
    server_app = QApplication(sys.argv)
    mf = MainForm(server)
    # Запускаем GUI
    server_app.exec_()


try:
    # Инициализируем логирование
    logger = logging.getLogger('app.server')
    logger.info('Программа сервер запущена')

    if __name__ == '__main__':
        main()


#    parser = create_parser()
#    namespace = parser.parse_args(sys.argv[1:])
#    addr = namespace.addr  # 'localhost'
#    port = int(namespace.port)
#    request_queue = {}
#    clients = []

except Exception as err:
    if logger:
        logger.error(err)
    else:
        print(err)
