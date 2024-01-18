import ast
from typing import Any, Dict, List


class SimpleCodeVisitor(ast.NodeVisitor):

    imports: List[Any]
    functions: List[Any]
    classes: List[Any]
    variables: List[Any]
    assigned_self_members: List[Any]
    assigned_class_members: List[Any]

    undefined_references: List[ast.Name]

    def __init__(self):
        self.imports = []
        self.functions = []
        self.classes = []
        self.variables = []
        self.assigned_self_members = []
        self.assigned_class_members = []

        self.undefined_references = []

    def visit_Name(self, node: ast.Name):
        self.undefined_references.append(node)

    def visit_Attribute(self, node: ast.Attribute):
        name = ast.Name(
            id=node.attr,
            ctx=node.ctx,
            lineno=node.lineno,
            col_offset=node.col_offset,
            end_lineno=node.end_lineno,
            end_col_offset=node.end_col_offset
        )
        self.undefined_references.append(name)

    def to_json(self) -> Dict[str, Any]:
        return {
            "imports": [],
            "functions": [],
            "classes": [],
            "variables": [],
            "assigned_self_members": [],
            "assigned_class_members": [],
            "undefined_references": [
                {
                    "id": reference.id,
                    "line_number": reference.lineno,
                    "column_number": reference.col_offset,
                }
                for reference in self.undefined_references
            ]
        }
