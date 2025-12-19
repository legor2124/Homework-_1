import unittest
from converter import ConfigConverter

class TestConfigConverter(unittest.TestCase):
    def setUp(self):
        self.converter = ConfigConverter()
    
    def test_numbers(self):
        """Тест чисел"""
        source = "123"
        result = self.converter.convert_string(source)
        self.assertIn('_result = 123', result)
    
    def test_array(self):
        """Тест массивов"""
        source = "<< 1, 2, 3, 4, 5 >>"
        result = self.converter.convert_string(source)
        self.assertIn('_result = [1, 2, 3, 4, 5]', result)
    
    def test_empty_array(self):
        """Тест пустого массива"""
        source = "<< >>"
        result = self.converter.convert_string(source)
        self.assertIn('_result = []', result)
    
    def test_dict(self):
        """Тест словарей"""
        source = "{ key1 -> 123. key2 -> 456 }"
        result = self.converter.convert_string(source)
        self.assertIn('key1 = 123', result)
        self.assertIn('key2 = 456', result)
    
    def test_nested_dict(self):
        """Тест вложенных словарей"""
        source = "{ server -> { port -> 8080. host -> \"localhost\" } }"
        result = self.converter.convert_string(source)
        self.assertIn('[server]', result)
        self.assertIn('port = 8080', result)
        self.assertIn('host = "localhost"', result)
    
    def test_const_declaration(self):
        """Тест объявления констант"""
        source = """
        max_connections := 1000;
        timeout := 30;
        { server -> { max_connections -> ?(max_connections). timeout -> ?(timeout) } }
        """
        result = self.converter.convert_string(source)
        self.assertIn('max_connections = 1000', result)
        self.assertIn('timeout = 30', result)
    
    def test_const_reference(self):
        """Тест ссылок на константы"""
        source = """
        base_port := 8000;
        offset := 80;
        { server -> { port -> ?(base_port). test_port -> << ?(base_port), ?(offset) >> } }
        """
        result = self.converter.convert_string(source)
        self.assertIn('port = 8000', result)
        self.assertIn('test_port = [8000, 80]', result)
    
    def test_complex_nested(self):
        """Тест сложных вложенных структур"""
        source = """
        {
            app -> {
                name -> "MyApp".
                version -> << 1, 0, 0 >>.
                settings -> {
                    debug -> true.
                    features -> << "auth", "api", "logging" >>
                }
            }.
            
            database -> {
                connections -> {
                    main -> { host -> "db1". port -> 5432 }.
                    replica -> { host -> "db2". port -> 5433 }
                }
            }
        }
        """
        result = self.converter.convert_string(source)
        
        # Проверяем различные части вывода
        self.assertIn('[app]', result)
        self.assertIn('name = "MyApp"', result)
        self.assertIn('version = [1, 0, 0]', result)
        self.assertIn('[app.settings]', result)
        self.assertIn('debug = true', result)
        self.assertIn('features = ["auth", "api", "logging"]', result)
        self.assertIn('[database.connections.main]', result)
        self.assertIn('host = "db1"', result)
        self.assertIn('port = 5432', result)
    
    def test_error_undefined_constant(self):
        """Тест ошибки неопределенной константы"""
        source = "{ key -> ?(undefined_constant) }"
        with self.assertRaises(NameError):
            self.converter.convert_string(source)
    
    def test_error_syntax(self):
        """Тест синтаксической ошибки"""
        source = "{ key -> }"  # Неправильный синтаксис
        with self.assertRaises(SyntaxError):
            self.converter.convert_string(source)
    
    def test_array_in_dict(self):
        """Тест массива в словаре"""
        source = "{ servers -> << \"server1\", \"server2\", \"server3\" >> }"
        result = self.converter.convert_string(source)
        self.assertIn('servers = ["server1", "server2", "server3"]', result)
    
    def test_dict_in_array(self):
        """Тест словаря в массиве"""
        source = "<< { name -> \"item1\". value -> 100 }, { name -> \"item2\". value -> 200 } >>"
        result = self.converter.convert_string(source)
        self.assertIn('_result = [{ name = "item1", value = 100 }, { name = "item2", value = 200 }]', result)

if __name__ == '__main__':
    unittest.main()
