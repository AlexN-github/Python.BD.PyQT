# Программа сервера для получения приветствия от клиента и отправки ответа
import logging
import select

import log.server_log_config
import argparse
import json
from socket import *
import sys

from common.variables import *


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--addr', default=str(server_addr_default))
    parser.add_argument('-p', '--port', default=str(default_port))

    return parser


def execute_command_presence(client, command):
    result = {}
    result['msg'] = 'command `{0}` completed successfully'.format(command['action'])
    result['code'] = 200
    sending_responde(client, result)
    return result

def execute_command_broadcast(client, command):
    result = {}
    result['msg'] = 'command `{0}` completed successfully'.format(command['action'])
    result['code'] = 200
    sending_responde_brodcaste(client, result)
    return result

def processing_command(request):
    def parsing_command(msg):
        command = json.loads(msg)
        return command

    def execute_command(command):
        action = command['action']
        if action == 'presence':
            result = execute_command_presence(request, command)
        if action == 'broadcast':
            result = execute_command_broadcast(request, command)
        elif action == '...':
            pass
        else:
            result = {}
            result['msg'] = 'Invalid command'
            result['code'] = 400
        return result

    print('request', request)
    msg = request_queue[request]#request.recv(block_transfer_size).decode('utf-8')
    print('msg', msg)
    #addr = request.raddr
    command = parsing_command(msg)
    logger.debug('Принято сообщение: {0}, от клиента: {1}'.format(msg, addr))
    logger.info('Принята команда: {0}'.format(command['action']))
    return execute_command(command)


def sending_responde(client, result):
    logger.info(
        'Возвращаем клиенту {0} msg: {1}; code: {2}'.format(client.getpeername(), result['msg'], result['code']))
    # print('Возвращаем клиенту {0} msg: {1}; code: {2}'.format(client.getpeername(), result['msg'], result['code']))
    msg_send = json.dumps(result)
    client.send(msg_send.encode('utf-8'))
    #client.close()

def sending_responde_brodcaste(client, result):
    logger.info(
        'Возвращаем клиенту {0} msg: {1}; code: {2}'.format(client.getpeername(), result['msg'], result['code']))
    # print('Возвращаем клиенту {0} msg: {1}; code: {2}'.format(client.getpeername(), result['msg'], result['code']))
    msg_send = json.dumps(result)
    for cli in clients:
        cli.send(msg_send.encode('utf-8'))
    #client.close()


def read_requests(r_clients):
    """ Чтение запросов из списка клиентов
    """

    for sock in r_clients:
        try:
            data = sock.recv(1024).decode('utf-8')
            request_queue[sock] = data
        except:
            print('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
            logger.info('Клиент {} {} отключился'.format(sock.fileno(), sock.getpeername()))
            clients.remove(sock)

    #return responses


def queue_processing():
    """ Обрабатываем очередь запросов
    """
    while request_queue != {}:
        request = next(iter(request_queue)) #request_queue[list(request_queue.items())[0]]
        processing_command(request)
        request_queue.pop(request, None)
        #del request_queue[request]

def mainloop(addr, port):
    s = socket(AF_INET, SOCK_STREAM)  # Создает сокет TCP
    s.bind((addr, port))  # Присваивает порт 8888
    s.listen(5)  # Переходит в режим ожидания запросов;
    s.settimeout(0.2)  # Таймаут для операций с сокетом

    # Одновременно обслуживает не более
    # 5 запросов.
    logger.info('Слушаем запросы от клиентов: {0}'.format((addr, port)))
    # print('Запуск сервера:', (addr, port))
    while True:
        try:
            conn, addr = s.accept()
        except OSError as e:
            pass  # timeout вышел
        else:
            print("Получен запрос на соединение от %s" % str(addr))
            logger.info('Получен запрос на соединение от %s' % str(addr))
            clients.append(conn)
        finally:
            wait = 10
            r = []
            w = []
            try:
                r, w, e = select.select(clients, clients, [], wait)
            except:
                pass  # Ничего не делать, если какой-то клиент отключился
            try:
                read_requests(r)
                if r:
                    print(r)
                    queue_processing()
                #result = processing_command(conn, addr)
                #sending_responde(conn, result)
            except Exception:
                result = {}
                result['msg'] = 'Unexpected error'
                result['code'] = 500
                sending_responde(conn, result)
                logger.error('Ошибка обработки запроса клиента {0}: {1}'.format(conn, result['msg']))


logger = logging.getLogger('app.server')
logger.info('Программа сервер запущена')

try:
    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])
    addr = namespace.addr  # 'localhost'
    port = int(namespace.port)
    request_queue = {}
    clients = []
    mainloop(addr, port)
except Exception as err:
    logger.error(err)
