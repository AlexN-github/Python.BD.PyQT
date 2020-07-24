# Программа клиента, запрашивающего текущее время
import log.client_log_config
import argparse
import json
from socket import *
import sys
import time
from common.variables import *
import logging


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', default='')
    parser.add_argument('-a', '--addr', default='localhost')
    parser.add_argument('-p', '--port', default=str(default_port))
    return parser


# Основной класс клиента
class Client:
    def __init__(self, listen_address, listen_port, client_name):

        # Параментры подключения
        self.addr = listen_address
        self.port = int(listen_port)

        # Имя клиента
        self.account_name = client_name

    def execute_command_presence(self):
        logger.info('Выполняем команду: `presence`')
        # print('Выполняем команду: `presence`')
        command = {
            'action': 'presence',
            'time': int(time.time()),
            'type': 'status',
            'user': {
                'account_name': '',
                'status': 'Yep, I am here!'
            }
        }
        timestamp = int(time.time())
        command['time'] = timestamp
        command['account_name'] = self.account_name
        result = self.execute_command(command)
        print(result)

        return result

    def execute_command_broadcast(self):
        logger.info('Выполняем команду: `broadcast`')
        # print('Выполняем команду: `broadcast`')
        command = {
            'action': 'broadcast',
            'time': int(time.time()),
            'type': 'status',
            'user': {
                'account_name': '',
                'status': 'Yep, I am here!'
            }
        }
        timestamp = int(time.time())
        command['time'] = timestamp
        command['account_name'] = self.account_name
        result = self.execute_command(command)
        print(result)

        return result


    def waiting_messages(self):
        def parsing_recv(msg):
            respond = json.loads(msg)
            return respond

        data = sock.recv(block_transfer_size)
        msg_recv = data.decode('utf-8')
        result = parsing_recv(msg_recv)
        logger.info('Сообщение от сервера: {0}; Code: {1}'.format(result['msg'], result['code']))
        print(result)
        #print('Сообщение от сервера: {0}; Code: {1}'.format(result['msg'], result['code']))
        return result


    def connect_to_server(self):
        global sock
        logger.info('Устанавливаем соединение: {0}'.format((self.addr, self.port)))
        # print('Устанавливаем соединение:', (addr, port))
        sock = socket(AF_INET, SOCK_STREAM)  # Создать сокет TCP
        sock.connect((self.addr, self.port))  # Соединиться с сервером


    def disconnect_from_server(self):
        logger.info('Отключаемся от сервера {0}'.format((self.addr, self.port)))
        # print('Отключаемся от сервера', (addr, port))
        sock.close()


    def execute_command(self, msg):
        def parsing_recv(msg):
            respond = json.loads(msg)
            return respond

        msg_send = json.dumps(msg)
        print(msg_send)
        sock.send(msg_send.encode('utf-8'))
        data = sock.recv(block_transfer_size)
        msg_recv = data.decode('utf-8')
        result = parsing_recv(msg_recv)
        logger.info('Сообщение от сервера: {0}; Code: {1}'.format(result['msg'], result['code']))
        # print('Сообщение от сервера: {0}; Code: {1}'.format(result['msg'], result['code']))
        return result


    def mainloop(self):
        try:
            self.connect_to_server()
            while True:
                print('*' * 30)
                inputuser = input(
                    'Отправить клиенту команду PRESENCE (1) \r\nОтправить клиенту команду BROADCAST (2) \r\nЖдем входящие сообшения (3) \r\nОтключиться от сервера и выйти (q)')
                if inputuser == '1':
                    self.execute_command_presence()
                if inputuser == '2':
                    self.execute_command_broadcast()
                if inputuser == '3':
                    self.waiting_messages()
                elif inputuser == 'q':
                    break

            # disconnect_from_server()
        except Exception as err:
            logger.error(err)


def main():

    # Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию.
    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])

    # Создание экземпляра класса - клиента.
    client = Client(namespace.addr, namespace.port, namespace.name)
    client.mainloop()


#parser = create_parser()
#namespace = parser.parse_args(sys.argv[1:])
#client_name = namespace.name
#print(client_name)
#addr = namespace.addr  # 'localhost'
#port = int(namespace.port)
#account_name = 'Alex'

try:
    # Инициализируем логирование
    logger = logging.getLogger('app.client')
    logger.info('Программа клиент запущена')

    if __name__ == '__main__':
        main()


except Exception as err:
    if logger:
        logger.error(err)
    else:
        print(err)


