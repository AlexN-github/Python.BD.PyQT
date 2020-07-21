# logging - стандартный модуль для организации логирования
import logging
import logging.handlers

# Можно выполнить более расширенную настройку логирования.
# Создаем объект-логгер с именем app.main:
logger = logging.getLogger('app.server')

# Создаем объект форматирования:
formatter = logging.Formatter('%(asctime)s %(levelname)s %(module)s %(message)s')

# Создаем файловый обработчик логирования (можно задать кодировку):
fh = logging.handlers.TimedRotatingFileHandler('log/server.log', encoding='utf-8', interval=1, when='D')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

# Добавляем в логгер новый обработчик событий и устанавливаем уровень логирования
logger.addHandler(fh)
logger.setLevel(logging.DEBUG)
