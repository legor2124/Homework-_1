import tomlkit
from typing import Any, Dict
from datetime import datetime

class TOMLGenerator:
    def __init__(self):
        self.doc = tomlkit.document()
        self.doc.add(tomlkit.comment(f"Generated from custom config language on {datetime.now().isoformat()}"))
    
    def add_value(self, key: str, value: Any, parent=None):
        """Добавление значения в документ TOML"""
        if parent is None:
            parent = self.doc
        
        # Обработка вложенных ключей (разделенных точкой)
        if '.' in key:
            parts = key.split('.')
            current = parent
            
            for i, part in enumerate(parts[:-1]):
                if part not in current:
                    current[part] = tomlkit.table()
                current = current[part]
            
            self._set_value(current, parts[-1], value)
        else:
            self._set_value(parent, key, value)
    
    def _set_value(self, container, key: str, value: Any):
        """Установка значения с правильным типом TOML"""
        if isinstance(value, dict):
            # Вложенная таблица
            table = tomlkit.table()
            for sub_key, sub_value in value.items():
                self._set_value(table, sub_key, sub_value)
            container[key] = table
        elif isinstance(value, list):
            # Массив
            container[key] = self._convert_list(value)
        elif isinstance(value, bool):
            container[key] = value
        elif isinstance(value, int):
            container[key] = value
        elif isinstance(value, float):
            container[key] = value
        elif isinstance(value, str):
            container[key] = value
        else:
            container[key] = str(value)
    
    def _convert_list(self, lst: list) -> list:
        """Конвертация списка с поддержкой вложенных структур"""
        result = []
        for item in lst:
            if isinstance(item, dict):
                table = tomlkit.inline_table()
                for key, value in item.items():
                    self._set_value(table, key, value)
                result.append(table)
            elif isinstance(item, list):
                result.append(self._convert_list(item))
            else:
                result.append(item)
        return result
    
    def generate(self, data: Dict[str, Any]) -> str:
        """Генерация TOML из словаря данных"""
        for key, value in data.items():
            if key != '_result':  # Специальное поле для результатов
                self.add_value(key, value)
        
        return tomlkit.dumps(self.doc)
    
    def generate_from_nodes(self, nodes, evaluator):
        """Генерация TOML непосредственно из AST узлов"""
        data = evaluator.evaluate_all(nodes)
        return self.generate(data)
