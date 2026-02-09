from tree_sitter import Node

def error_format(node: Node) -> str:
    start_line = node.start_point[0] + 1
    start_column = node.start_point[1] + 1
    end_line = node.end_point[0] + 1
    end_column = node.end_point[1] + 1
    if start_line == end_line and start_column == end_column:
        return f"\nline:{start_line} column:{start_column}"
    elif start_line == end_line:
        return f"\nline:{start_line} columns:{start_column}-{end_column}"
    else:
        return f"\nfrom line:{start_line} column:{start_column}\nto line:{end_line} column:{end_column}"

# def node_to_location_string(node: Node, include_text: bool = False) -> str:
#     """
#     Преобразует Node в строку с указанием местоположения.
    
#     Args:
#         node: Узел tree_sitter
#         include_text: Если True, включает текст узла в результат
    
#     Returns:
#         Строка формата: "строка:столбец" или "строка:столбец-конечная_строка:конечный_столбец"
#     """
#     if not node:
#         return "Неверный узел"
    
#     # Получаем начальную позицию
#     start_line, start_column = node.start_point
#     # Получаем конечную позицию
#     end_line, end_column = node.end_point
    
#     # Преобразуем в человекочитаемый формат (индексация с 1)
#     start_line += 1
#     start_column += 1
#     end_line += 1
#     end_column += 1
    
#     result = f"строка {start_line}, столбец {start_column}"
    
#     # Если узел занимает несколько строк, добавляем конечную позицию
#     if start_line != end_line or start_column != end_column:
#         result += f" - строка {end_line}, столбец {end_column}"
    
#     # Если нужно включить текст узла
#     if include_text and hasattr(node, 'text'):
#         # Убираем лишние пробелы и переносы для компактности
#         text_preview = node.text.decode('utf-8') if isinstance(node.text, bytes) else str(node.text)
#         text_preview = text_preview.strip().replace('\n', ' ')
#         if len(text_preview) > 50:
#             text_preview = text_preview[:47] + "..."
#         result += f" | текст: '{text_preview}'"
    
#     return result


# def node_to_compact_string(node: Node) -> str:
#     """
#     Компактное представление местоположения узла.
    
#     Returns:
#         Строка формата: "L{line}:{col}" или "L{start_line}:{start_col}-L{end_line}:{end_col}"
#     """
#     if not node:
#         return "Invalid node"
    
#     start_line, start_column = node.start_point
#     end_line, end_column = node.end_point
    
#     # Преобразуем в человекочитаемый формат
#     start_line += 1
#     start_column += 1
#     end_line += 1
#     end_column += 1
    
#     if start_line == end_line and start_column == end_column:
#         return f"L{start_line}:{start_column}"
#     elif start_line == end_line:
#         return f"L{start_line}:{start_column}-{end_column}"
#     else:
#         return f"L{start_line}:{start_column}-L{end_line}:{end_column}"


# # Пример использования:
# def print_node_info(node: Node, source_code: Optional[bytes] = None):
#     """
#     Печатает подробную информацию об узле.
    
#     Args:
#         node: Узел tree_sitter
#         source_code: Исходный код (опционально, для получения текста)
#     """
#     if not node:
#         print("Неверный узел")
#         return
    
#     print("=" * 50)
#     print(f"Тип узла: {node.type}")
#     print(f"Местоположение: {node_to_location_string(node)}")
#     print(f"Компактный формат: {node_to_compact_string(node)}")
    
#     # Получаем текст узла
#     if source_code:
#         text = node.text.decode('utf-8') if isinstance(node.text, bytes) else str(node.text)
#         print(f"Текст узла ({len(text)} символов):")
#         print("-" * 30)
#         print(repr(text[:200]) + ("..." if len(text) > 200 else ""))
#         print("-" * 30)
    
#     print(f"Количество детей: {node.child_count}")
#     print("=" * 50)


# # Пример использования в реальном коде:
# def process_ast_node(node: Node, indent: int = 0):
#     """
#     Рекурсивная обработка AST с выводом местоположения узлов.
#     """
#     indent_str = "  " * indent
#     location = node_to_compact_string(node)
#     print(f"{indent_str}[{location}] {node.type}")
    
#     for child in node.children:
#         process_ast_node(child, indent + 1)


# Пример для демонстрации работы:
# if __name__ == "__main__":
#     # Создаем тестовый узел (в реальности он будет получен от tree-sitter)
#     class MockNode:
#         def __init__(self, start_line, start_col, end_line, end_col, text=None, type="test"):
#             self.start_point = (start_line, start_col)
#             self.end_point = (end_line, end_col)
#             self.text = text.encode() if text else b"test text"
#             self.type = type
#             self._child_count = 0
        
#         @property
#         def child_count(self):
#             return self._child_count
    
#     # Тестируем на mock-узлах
#     print("Тест 1: Узел на одной строке")
#     node1 = MockNode(0, 0, 0, 10, "print('Hello')")
#     print(node_to_location_string(node1))
#     print(node_to_location_string(node1, include_text=True))
#     print()
    
#     print("Тест 2: Узел на нескольких строках")
#     node2 = MockNode(0, 0, 2, 5, "def func():\n    pass\n    return")
#     print(node_to_location_string(node2))
#     print(node_to_compact_string(node2))
#     print()
    
#     print("Тест 3: Компактный формат")
#     node3 = MockNode(9, 3, 9, 15)  # 10 строка, 4 столбец
#     print(f"Компактно: {node_to_compact_string(node3)}")
