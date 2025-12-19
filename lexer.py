import re
from enum import Enum
from typing import List, Tuple, Optional

class TokenType(Enum):
    COMMENT = 'COMMENT'
    NUMBER = 'NUMBER'
    STRING = 'STRING'
    IDENTIFIER = 'IDENTIFIER'
    ARRAY_START = '<<'
    ARRAY_END = '>>'
    DICT_START = '{'
    DICT_END = '}'
    ARROW = '->'
    DOT = '.'
    SEMICOLON = ';'
    COMMA = ','
    ASSIGN = ':='
    CONST_START = '?('
    CONST_END = ')'
    EOF = 'EOF'

class Token:
    def __init__(self, type: TokenType, value: str, line: int, column: int):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"Token({self.type}, '{self.value}', {self.line}:{self.column})"

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = self.text[0] if text else None
        
    def advance(self):
        """Перемещаемся к следующему символу"""
        if self.current_char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
            
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None
    
    def skip_whitespace(self):
        """Пропускаем пробельные символы"""
        while self.current_char and self.current_char.isspace():
            self.advance()
    
    def skip_comment(self):
        """Пропускаем однострочный комментарий"""
        while self.current_char and self.current_char != '\n':
            self.advance()
        if self.current_char == '\n':
            self.advance()
    
    def number(self) -> Token:
        """Чтение числа: [1-9][0-9]*"""
        result = ''
        start_col = self.column
        
        # Первая цифра не может быть 0
        if self.current_char and self.current_char in '123456789':
            result += self.current_char
            self.advance()
            
            # Последующие цифры
            while self.current_char and self.current_char.isdigit():
                result += self.current_char
                self.advance()
                
            return Token(TokenType.NUMBER, result, self.line, start_col)
        else:
            raise SyntaxError(f"Ожидалось число в {self.line}:{start_col}")
    
    def identifier(self) -> Token:
        """Чтение идентификатора: [a-zA-Z][a-zA-Z0-9]*"""
        result = ''
        start_col = self.column
        
        if self.current_char and (self.current_char.isalpha() or self.current_char == '_'):
            result += self.current_char
            self.advance()
            
            while self.current_char and (self.current_char.isalnum() or self.current_char == '_'):
                result += self.current_char
                self.advance()
                
            return Token(TokenType.IDENTIFIER, result, self.line, start_col)
        else:
            raise SyntaxError(f"Ожидался идентификатор в {self.line}:{start_col}")
    
    def peek(self, n: int = 1) -> Optional[str]:
        """Заглядываем вперед на n символов"""
        peek_pos = self.pos + n
        if peek_pos < len(self.text):
            return self.text[peek_pos]
        return None
    
    def get_next_token(self) -> Token:
        """Получение следующего токена"""
        while self.current_char is not None:
            # Пропускаем пробелы
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            
            # Комментарии
            if self.current_char == "'":
                self.advance()  # Пропускаем '
                self.skip_comment()
                continue
            
            # Числа
            if self.current_char in '123456789':
                return self.number()
            
            # Идентификаторы
            if self.current_char.isalpha() or self.current_char == '_':
                return self.identifier()
            
            # Многобуквенные операторы
            if self.current_char == '?':
                if self.peek() == '(':
                    start_col = self.column
                    self.advance()  # Пропускаем '?'
                    self.advance()  # Пропускаем '('
                    return Token(TokenType.CONST_START, '?(', self.line, start_col)
            
            if self.current_char == '<':
                if self.peek() == '<':
                    start_col = self.column
                    self.advance()  # Пропускаем первый '<'
                    self.advance()  # Пропускаем второй '<'
                    return Token(TokenType.ARRAY_START, '<<', self.line, start_col)
            
            if self.current_char == '>':
                if self.peek() == '>':
                    start_col = self.column
                    self.advance()  # Пропускаем первый '>'
                    self.advance()  # Пропускаем второй '>'
                    return Token(TokenType.ARRAY_END, '>>', self.line, start_col)
            
            if self.current_char == ':':
                if self.peek() == '=':
                    start_col = self.column
                    self.advance()  # Пропускаем ':'
                    self.advance()  # Пропускаем '='
                    return Token(TokenType.ASSIGN, ':=', self.line, start_col)
            
            if self.current_char == '-':
                if self.peek() == '>':
                    start_col = self.column
                    self.advance()  # Пропускаем '-'
                    self.advance()  # Пропускаем '>'
                    return Token(TokenType.ARROW, '->', self.line, start_col)
            
            # Однобуквенные токены
            start_col = self.column
            char = self.current_char
            
            if char == '{':
                self.advance()
                return Token(TokenType.DICT_START, char, self.line, start_col)
            elif char == '}':
                self.advance()
                return Token(TokenType.DICT_END, char, self.line, start_col)
            elif char == '.':
                self.advance()
                return Token(TokenType.DOT, char, self.line, start_col)
            elif char == ';':
                self.advance()
                return Token(TokenType.SEMICOLON, char, self.line, start_col)
            elif char == ',':
                self.advance()
                return Token(TokenType.COMMA, char, self.line, start_col)
            elif char == ')':
                self.advance()
                return Token(TokenType.CONST_END, char, self.line, start_col)
            else:
                raise SyntaxError(f"Неизвестный символ: '{char}' в {self.line}:{start_col}")
        
        return Token(TokenType.EOF, '', self.line, self.column)
    
    def tokenize(self) -> List[Token]:
        """Получение всех токенов"""
        tokens = []
        while True:
            token = self.get_next_token()
            tokens.append(token)
            if token.type == TokenType.EOF:
                break
        return tokens
