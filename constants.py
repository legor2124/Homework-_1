from typing import Dict, Any, Union
from parser import *

class ConstantEvaluator:
    def __init__(self):
        self.constants: Dict[str, Any] = {}
        self.visited: set = set()
    
    def evaluate_node(self, node: ASTNode) -> Any:
        """Рекурсивное вычисление значения узла AST"""
        if isinstance(node, NumberNode):
            return node.value
        
        elif isinstance(node, ConstReferenceNode):
            return self.evaluate_constant_reference(node.name)
        
        elif isinstance(node, ArrayNode):
            return [self.evaluate_node(element) for element in node.elements]
        
        elif isinstance(node, DictNode):
            result = {}
            for entry in node.entries:
                result[entry.key] = self.evaluate_node(entry.value)
            return result
        
        elif isinstance(node, ConstDeclarationNode):
            # Вычисляем значение константы
            value = self.evaluate_node(node.value)
            self.constants[node.name] = value
            return None  # Объявления констант не возвращают значения
        
        else:
            raise ValueError(f"Неизвестный тип узла: {type(node)}")
    
    def evaluate_constant_reference(self, name: str) -> Any:
        """Вычисление ссылки на константу с проверкой циклов"""
        if name in self.visited:
            raise RuntimeError(f"Циклическая зависимость констант: {name}")
        
        if name not in self.constants:
            raise NameError(f"Неопределенная константа: {name}")
        
        self.visited.add(name)
        try:
            value = self.constants[name]
            # Если значение ещё не вычислено (если это AST узел)
            if isinstance(value, ASTNode):
                value = self.evaluate_node(value)
                self.constants[name] = value
            return value
        finally:
            self.visited.remove(name)
    
    def evaluate_all(self, nodes: List[ASTNode]) -> Dict[str, Any]:
        """Вычисление всех узлов и возврат конечных значений"""
        # Сначала обрабатываем объявления констант
        for node in nodes:
            if isinstance(node, ConstDeclarationNode):
                self.evaluate_node(node)
        
        # Затем вычисляем все остальные значения
        results = {}
        for node in nodes:
            if not isinstance(node, ConstDeclarationNode):
                # Для словарей собираем все пары ключ-значение
                if isinstance(node, DictNode):
                    for entry in node.entries:
                        results[entry.key] = self.evaluate_node(entry.value)
                else:
                    # Для остальных узлов (если они есть на верхнем уровне)
                    value = self.evaluate_node(node)
                    if value is not None:
                        results['_result'] = value
        
        return results
