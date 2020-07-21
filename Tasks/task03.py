"""
Написать функцию host_range_ping_tab(), возможности которой основаны на функции
из примера 2. Но в данном случае результат должен быть итоговым по всем ip-адресам,
представленным в табличном формате (использовать модуль tabulate). Таблица должна
состоять из двух колонок и выглядеть примерно так:
Reachable
-------------
10.0.0.1
10.0.0.2
Unreachable
-------------
10.0.0.3
10.0.0.4
"""

import subprocess
import platform
import socket
import ipaddress
import tabulate

def host_ping(address_list):
    def ping_ip(ip):
        try:
            output = subprocess.check_output("ping -{} 1 {}".format('n' if platform.system().lower(
            ) == "windows" else 'c', ip), shell=True, universal_newlines=True, encoding='866')
            if 'unreachable' in output or 'Заданный узел недоступен' in output:
                return False
            else:
                return True
        except Exception:
            return False

    res = {}
    res['Reachable'] = []
    res['UnReachable'] = []
    for each in address_list:
        each = str(each)
        ipaddr = ipaddress.ip_address(socket.gethostbyname(each))

        if ping_ip(str(ipaddr)):
            res['Reachable'].append(str(ipaddr))
        else:
            res['UnReachable'].append(str(ipaddr))
    return(res)

def host_range_ping_tab(range):
    subnet = ipaddress.ip_network(range)
    address_list = list(subnet.hosts())
    list_res = host_ping(address_list)
    print(tabulate.tabulate(list_res, headers='keys', tablefmt='grid'))
    return()


range = '192.168.0.0/29'
host_range_ping_tab(range)
