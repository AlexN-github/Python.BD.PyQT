"""
Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона.
Меняться должен только последний октет каждого адреса. По результатам проверки
должно выводиться соответствующее сообщение.
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
        each = str(each)
        ipaddr = ipaddress.ip_address(socket.gethostbyname(each))
        if ping_ip(str(ipaddr)):
            print(f'{str(ipaddr)} is available')
        else:
            print(f'{str(ipaddr)} is not available')

def host_range_ping(range):
    subnet = ipaddress.ip_network(range)
    address_list = list(subnet.hosts())
    host_ping(address_list)
    return()


range = '192.168.0.0/29'
host_range_ping(range)
