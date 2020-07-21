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
    parser.add_argument('-a', '--addr', default='localhost')
    parser.add_argument('-p', '--port', default=str(default_port))

    return parser


def execute_command_presence():
    logger.info('Выполняем команду: `presence`')
    # print('Выполняем команду: `presence`')
    command = {
        'action': 'presence',
        'time': int(time.time()),
        'type': 'status',
        'user': {
            'account_name': account_name,
            'status': 'Yep, I am here!'
        }
    }
    timestamp = int(time.time())
    command['time'] = timestamp
    command['account_name'] = 'Alex'
    result = execute_command(command)
    print(result)

    return result

def execute_command_broadcast():
    logger.info('Выполняем команду: `broadcast`')
    # print('Выполняем команду: `broadcast`')
    command = {
        'action': 'broadcast',
        'time': int(time.time()),
        'type': 'status',
        'user': {
            'account_name': account_name,
            'status': 'Yep, I am here!'
        }
    }
    timestamp = int(time.time())
    command['time'] = timestamp
    command['account_name'] = 'Alex'
    result = execute_command(command)
    print(result)

    return result


def waiting_messages():
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


def connect_to_server(addr, port):
    global sock
    logger.info('Устанавливаем соединение: {0}'.format((addr, port)))
    # print('Устанавливаем соединение:', (addr, port))
    sock = socket(AF_INET, SOCK_STREAM)  # Создать сокет TCP
    sock.connect((addr, port))  # Соединиться с сервером


def disconnect_from_server():
    logger.info('Отключаемся от сервера {0}'.format((addr, port)))
    # print('Отключаемся от сервера', (addr, port))
    sock.close()


def execute_command(msg):
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


logger = logging.getLogger('app.client')
logger.info('Программа клиент запущена')
parser = create_parser()
namespace = parser.parse_args(sys.argv[1:])
addr = namespace.addr  # 'localhost'
port = int(namespace.port)
account_name = 'Alex'

try:
    connect_to_server(addr=addr, port=port)
    while True:
        print('*'*30)
        inputuser = input('Отправить клиенту команду PRESENCE (1) \r\nОтправить клиенту команду BROADCAST (2) \r\nЖдем входящие сообшения (3) \r\nОтключиться от сервера и выйти (q)')
        if inputuser == '1':
            execute_command_presence()
        if inputuser == '2':
            execute_command_broadcast()
        if inputuser == '3':
            waiting_messages()
        elif inputuser == 'q':
            break

    #disconnect_from_server()
except Exception as err:
    logger.error(err)
