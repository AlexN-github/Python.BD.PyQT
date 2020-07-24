import subprocess

process = []

while True:
    action = input('Выберите действие: \nq - выход \ns - запустить сервер и клиенты \nx - закрыть все окна\n>>')
    if action == 'q':
        break
    elif action == 's':
        clients_count = int(input('Введите количество тестовых клиентов для запуска: '))
        # Запускаем сервер!
        process.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))
        # Запускаем клиентов:
        for i in range(clients_count):
            process.append(subprocess.Popen('python client.py -n test{0}'.format(i + 1), creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif action == 'x':
        while process:
            process.pop().kill()