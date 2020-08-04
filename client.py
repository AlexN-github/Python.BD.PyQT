# Программа клиента, запрашивающего текущее время
# Программа клиента, запрашивающего текущее время
import log.client_log_config
import argparse
import json
from socket import *
import sys
import time
from common.variables import *
import logging
import threading


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name', default='test1')
    parser.add_argument('-a', '--addr', default='localhost')
    parser.add_argument('-p', '--port', default=str(default_port))
    return parser


# Основной класс клиента
class Client(threading.Thread):
    def __init__(self, listen_address, listen_port, client_name):

        # Параментры подключения
        self.addr = listen_address
        self.port = int(listen_port)

        # Имя клиента
        self.account_name = client_name

        # Прием сообщений в фоне
        self.background_receive = True

        # Конструктор предка
        super().__init__()

    def execute_command_presence(self):
        logger.info('Выполняем команду: `presence`')
        # print('Выполняем команду: `presence`')
        command = {
            'action': 'presence',
            'time': int(time.time()),
            'type': 'status',
            'sender': self.account_name
        }
        result = self.execute_command(command)
        return result

    def execute_command_get_contacts(self):
        logger.info('Выполняем команду: `get_contacts`')
        # print('Выполняем команду: `get_contacts`')
        command = {
            'action': 'get_contacts',
            'time': int(time.time()),
            'sender': self.account_name
        }
        result = self.execute_command(command)
        #print(result['contact_list'])
        return result['contact_list']

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
        #print(result['contact_list'])
        return result

    def execute_command_del_contact(self, username):
        logger.info('Выполняем команду: `add_contact`')
        # print('Выполняем команду: `add_contact`')
        command = {
            'action': 'del_contact',
            'time': int(time.time()),
            'sender': self.account_name,
            'user': username
        }
        result = self.execute_command(command)
        #print(result['contact_list'])
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
            logger.info(
                'Принято сообщение от клиента {0} msg: {1}'.format(result['sender'], result['message']))
        else:
            logger.info(
                'Сообщение от сервера: {0}; Code: {1}'.format(result['msg'], result['code']))

        #print(result)
        #print('Сообщение от сервера: {0}; Code: {1}'.format(result['msg'], result['code']))
        return result


    def connect_to_server(self):
        #global sock
        logger.info('Устанавливаем соединение: {0}'.format((self.addr, self.port)))
        # print('Устанавливаем соединение:', (addr, port))
        self.sock = socket(AF_INET, SOCK_STREAM)  # Создать сокет TCP
        self.sock.connect((self.addr, self.port))  # Соединиться с сервером
        self.sock.settimeout(0.2)  # Таймаут для операций с сокетом



    def disconnect_from_server(self):
        logger.info('Отключаемся от сервера {0}'.format((self.addr, self.port)))
        # print('Отключаемся от сервера', (addr, port))
        self.sock.close()


    def execute_command(self, msg):
        def parsing_recv(msg):
            respond = json.loads(msg)
            return respond

        msg_send = json.dumps(msg)
        #print(msg_send)
        result = {}
        try:
            self.pause_background_receive(False)
            time.sleep(0.3)
            self.sock.send(msg_send.encode('utf-8'))
            #print(result)
            result = self.receive_messages()
        except OSError as e:
            pass  # timeout вышел
        finally:
            self.pause_background_receive(True)

        #data = sock.recv(block_transfer_size)
        #msg_recv = data.decode('utf-8')
        #result = parsing_recv(msg_recv)
        #logger.info('Сообщение от сервера: {0}; Code: {1}'.format(result['msg'], result['code']))
        # print('Сообщение от сервера: {0}; Code: {1}'.format(result['msg'], result['code']))
        return result

    def pause_background_receive(self, pause):
        self.background_receive = pause

    def run(self):
        try:
            self.connect_to_server()
            #self.background_receive = False
            while True:
                if self.background_receive:
                    #logger.info('читаем из бек ресив')
                    try:
                        res = self.receive_messages()
                        print(res)
                        logger.info('res=', res)
                    except OSError as e:
                        pass  # timeout вышел
                    #print('background_receive=', self.background_receive)
                else:
                    #print('background_receive=', self.background_receive)
                    #logger.info('Ставим на паузу бэк ресив')
                    #time.sleep(1)
                    pass

            # disconnect_from_server()
        except Exception as err:
            logger.error(err)


def print_help():
    print('*' * 30)
    print('Отправить серверу команду PRESENCE (1)')
    print('Отправить команду BROADCAST (2)')
    print('Отправить cерверу команду GET_CONTACTS (3)')
    print('Отправить cерверу команду ADD_CONTACT (4)')
    print('Отправить cерверу команду DEL_CONTACT (5)')
    print('Отправить сообщение получателю SEND_MESSAGE (6)')
    print('Отключиться от сервера и выйти (q)')

def main():

    # Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию.
    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])

    # Создание экземпляра класса - клиента.
    client = Client(namespace.addr, namespace.port, namespace.name)
    client.daemon = True
    client.start()
    #client.mainloop()

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


