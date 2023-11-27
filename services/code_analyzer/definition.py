from dataclasses import dataclass
from typing import Any, List, Set, Dict
import ast


@dataclass
class Definition:

    id: str
    nodes: List[ast.AST]
    references: Set[ast.AST]
    is_builtin: bool

    def to_json(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "defined_at": [
                {
                    "start_line_number": node.lineno if node else None,
                    "start_column_number": node.col_offset if node else None,
                    "end_line_number": node.end_lineno if node else None,
                    "end_column_number": node.end_col_offset if node else None
                }
                for node in self.nodes
            ],
            "references": [
                {
                    "start_line_number": reference.lineno,
                    "start_column_number": reference.col_offset,
                    "end_line_number": reference.end_lineno,
                    "end_column_number": reference.end_col_offset
                }
                for reference in self.references
            ],
            "is_builtin": self.is_builtin
        }
