import sys
from pathlib import Path
from typing import Optional
from lexer import Lexer
from parser import Parser
from constants import ConstantEvaluator
from toml_generator import TOMLGenerator

class ConfigConverter:
    def __init__(self):
        self.lexer = None
        self.parser = None
        self.evaluator = ConstantEvaluator()
        self.generator = TOMLGenerator()
    
    def convert_file(self, input_path: Path) -> str:
        """Конвертация файла из учебного языка в TOML"""
        try:
            # Чтение исходного файла
            with open(input_path, 'r', encoding='utf-8') as f:
                source = f.read()
            
            # Лексический анализ
            self.lexer = Lexer(source)
            tokens = self.lexer.tokenize()
            
            # Синтаксический анализ
            self.parser = Parser(tokens)
            ast_nodes = self.parser.parse()
            
            # Вычисление констант и генерация TOML
            toml_output = self.generator.generate_from_nodes(ast_nodes, self.evaluator)
            
            return toml_output
            
        except FileNotFoundError:
            print(f"Ошибка: файл {input_path} не найден", file=sys.stderr)
            sys.exit(1)
        except SyntaxError as e:
            print(f"Синтаксическая ошибка: {e}", file=sys.stderr)
            sys.exit(1)
        except NameError as e:
            print(f"Ошибка имени: {e}", file=sys.stderr)
            sys.exit(1)
        except RuntimeError as e:
            print(f"Ошибка времени выполнения: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Неожиданная ошибка: {e}", file=sys.stderr)
            sys.exit(1)
    
    def convert_string(self, source: str) -> str:
        """Конвертация строки из учебного языка в TOML"""
        try:
            # Лексический анализ
            self.lexer = Lexer(source)
            tokens = self.lexer.tokenize()
            
            # Синтаксический анализ
            self.parser = Parser(tokens)
            ast_nodes = self.parser.parse()
            
            # Вычисление констант и генерация TOML
            toml_output = self.generator.generate_from_nodes(ast_nodes, self.evaluator)
            
            return toml_output
            
        except Exception as e:
            raise ValueError(f"Ошибка конвертации: {e}")
