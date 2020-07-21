"""
Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться
доступность сетевых узлов. Аргументом функции является список, в котором каждый
сетевой узел должен быть представлен именем хоста или ip-адресом. В функции необходимо
перебирать ip-адреса и проверять их доступность с выводом соответствующего
сообщения («Узел доступен», «Узел недоступен»). При этом ip-адрес сетевого узла должен
создаваться с помощью функции ip_address()
"""
import subprocess
import platform
import socket
import ipaddress

def host_ping(address_list):
    def ping_ip(ip):
        try:
            output = subprocess.check_output('ping -{} 1 {}'.format('n' if platform.system().lower(
            ) == 'windows' else 'c', ip), shell=True, universal_newlines=True, encoding='866')
            if 'unreachable' in output or 'Заданный узел недоступен' in output:
                return False
            else:
                return True
        except Exception:
            return False

    for each in address_list:
        ipaddr = ipaddress.ip_address(socket.gethostbyname(each))
        if ping_ip(str(ipaddr)):
            print(f'{str(ipaddr)} is available')
        else:
            print(f'{str(ipaddr)} is not available')


address_list = ['8.8.8.8', '8.8.4.4', '1.2.3.4', '192.168.0.3', 'localhost']
host_ping(address_list)
