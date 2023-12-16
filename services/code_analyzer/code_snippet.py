import ast
from dataclasses import dataclass


@dataclass
class CodeSnippet:
    code: str
    tree: ast.Module
    start_line: int
    end_line: int

    def to_json(self):
        return {
            "code": self.code,
            "start_line": self.start_line,
            "end_line": self.end_line
        }
