import unittest
from client import *

# Модульные тесты
class TestSplitFunction(unittest.TestCase):
    def setUp(self):
        # Выполнить настройку тестов (если необходимо)
        pass

    @classmethod
    def setUpClass(cls):
        parser = create_parser()
        namespace = parser.parse_args(sys.argv[1:])
        addr = namespace.addr  # 'localhost'
        port = int(namespace.port)
        account_name = 'Alex'

        connect_to_server(addr=addr, port=port)

    @classmethod
    def tearDownClass(cls):
        disconnect_from_server()

    def test_function_presence(self):
        r = execute_command_presence()
        self.assertEqual(r['code'], 200)

if __name__ == '__main__':
    unittest.main()
