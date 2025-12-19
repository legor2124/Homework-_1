from typing import Dict, List, Any, Union
from lexer import Token, TokenType, Lexer

class ASTNode:
    pass

class NumberNode(ASTNode):
    def __init__(self, value: int):
        self.value = value
    
    def __repr__(self):
        return f"Number({self.value})"

class IdentifierNode(ASTNode):
    def __init__(self, name: str):
        self.name = name
    
    def __repr__(self):
        return f"Identifier({self.name})"

class ArrayNode(ASTNode):
    def __init__(self, elements: List[ASTNode]):
        self.elements = elements
    
    def __repr__(self):
        return f"Array({self.elements})"

class DictEntryNode(ASTNode):
    def __init__(self, key: str, value: ASTNode):
        self.key = key
        self.value = value
    
    def __repr__(self):
        return f"DictEntry({self.key} -> {self.value})"

class DictNode(ASTNode):
    def __init__(self, entries: List[DictEntryNode]):
        self.entries = entries
    
    def __repr__(self):
        return f"Dict({self.entries})"

class ConstDeclarationNode(ASTNode):
    def __init__(self, name: str, value: ASTNode):
        self.name = name
        self.value = value
    
    def __repr__(self):
        return f"Const({self.name} := {self.value})"

class ConstReferenceNode(ASTNode):
    def __init__(self, name: str):
        self.name = name
    
    def __repr__(self):
        return f"ConstRef(?(self.name))"

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0]
        self.constants: Dict[str, Any] = {}
    
    def eat(self, token_type: TokenType):
        """Потребление токена ожидаемого типа"""
        if self.current_token.type == token_type:
            self.pos += 1
            if self.pos < len(self.tokens):
                self.current_token = self.tokens[self.pos]
        else:
            raise SyntaxError(
                f"Ожидался {token_type}, получен {self.current_token.type} "
                f"в {self.current_token.line}:{self.current_token.column}"
            )
    
    def parse(self) -> List[ASTNode]:
        """Основной метод парсинга"""
        nodes = []
        
        while self.current_token.type != TokenType.EOF:
            # Проверяем, является ли это объявлением константы
            if (self.current_token.type == TokenType.IDENTIFIER and 
                self.pos + 1 < len(self.tokens) and 
                self.tokens[self.pos + 1].type == TokenType.ASSIGN):
                
                nodes.append(self.parse_const_declaration())
            else:
                nodes.append(self.parse_value())
        
        return nodes
    
    def parse_const_declaration(self) -> ConstDeclarationNode:
        """Парсинг объявления константы: имя := значение;"""
        name_token = self.current_token
        self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.ASSIGN)
        
        value = self.parse_value()
        self.eat(TokenType.SEMICOLON)
        
        return ConstDeclarationNode(name_token.value, value)
    
    def parse_value(self) -> ASTNode:
        """Парсинг значения: число | массив | словарь | ссылка на константу"""
        token = self.current_token
        
        if token.type == TokenType.NUMBER:
            return self.parse_number()
        elif token.type == TokenType.CONST_START:
            return self.parse_const_reference()
        elif token.type == TokenType.ARRAY_START:
            return self.parse_array()
        elif token.type == TokenType.DICT_START:
            return self.parse_dict()
        else:
            raise SyntaxError(
                f"Ожидалось значение, получен {token.type} "
                f"в {token.line}:{token.column}"
            )
    
    def parse_number(self) -> NumberNode:
        """Парсинг числа"""
        token = self.current_token
        self.eat(TokenType.NUMBER)
        return NumberNode(int(token.value))
    
    def parse_const_reference(self) -> ConstReferenceNode:
        """Парсинг ссылки на константу: ?(имя)"""
        self.eat(TokenType.CONST_START)  # ?(
        
        if self.current_token.type != TokenType.IDENTIFIER:
            raise SyntaxError(
                f"Ожидался идентификатор, получен {self.current_token.type} "
                f"в {self.current_token.line}:{self.current_token.column}"
            )
        
        name_token = self.current_token
        self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.CONST_END)  # )
        
        return ConstReferenceNode(name_token.value)
    
    def parse_array(self) -> ArrayNode:
        """Парсинг массива: << значение, значение, ... >>"""
        self.eat(TokenType.ARRAY_START)  # <<
        
        elements = []
        if self.current_token.type != TokenType.ARRAY_END:
            elements.append(self.parse_value())
            
            while self.current_token.type == TokenType.COMMA:
                self.eat(TokenType.COMMA)
                elements.append(self.parse_value())
        
        self.eat(TokenType.ARRAY_END)  # >>
        return ArrayNode(elements)
    
    def parse_dict(self) -> DictNode:
        """Парсинг словаря: { имя -> значение. имя -> значение. ... }"""
        self.eat(TokenType.DICT_START)  # {
        
        entries = []
        if self.current_token.type != TokenType.DICT_END:
            entries.append(self.parse_dict_entry())
            
            while self.current_token.type == TokenType.DOT:
                self.eat(TokenType.DOT)
                entries.append(self.parse_dict_entry())
        
        self.eat(TokenType.DICT_END)  # }
        return DictNode(entries)
    
    def parse_dict_entry(self) -> DictEntryNode:
        """Парсинг записи словаря: имя -> значение"""
        if self.current_token.type != TokenType.IDENTIFIER:
            raise SyntaxError(
                f"Ожидался идентификатор, получен {self.current_token.type} "
                f"в {self.current_token.line}:{self.current_token.column}"
            )
        
        key_token = self.current_token
        self.eat(TokenType.IDENTIFIER)
        self.eat(TokenType.ARROW)
        
        value = self.parse_value()
        return DictEntryNode(key_token.value, value)
