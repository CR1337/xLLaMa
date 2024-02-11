import ast
from typing import List


class CodeVisitor(ast.NodeVisitor):
    """
    This visitor extracts all identifiers from a python module.
    """

    _references: List[ast.Name]

    @property
    def references(self) -> List[ast.Name]:
        return self._references

    def __init__(self):
        self._references = []

    def visit_Name(self, node: ast.Name):
        self._references.append(node)

    def visit_Attribute(self, node: ast.Attribute):
        name = ast.Name(
            id=node.attr,
            ctx=node.ctx,
            lineno=node.lineno,
            col_offset=node.col_offset,
            end_lineno=node.end_lineno,
            end_col_offset=node.end_col_offset
        )
        self._references.append(name)
