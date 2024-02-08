import ast
from dataclasses import dataclass


@dataclass
class CodeSnippet:
    code: str
    tree: ast.Module
    start_line: int
    end_line: int
