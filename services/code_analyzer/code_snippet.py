import ast
from dataclasses import dataclass


@dataclass
class CodeSnippet:
    code: str
    tree: ast.Module
    start_line_number: int
    end_line_number: int

    def to_json(self):
        return {
            "code": self.code,
            "start_line_number": self.start_line_number,
            "end_line_number": self.end_line_number,
        }
