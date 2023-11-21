import ast
from code_visitor import CodeVisitor
from metric_calculator import MetricCalculator
from typing import Any, Dict, List
from scope import Definition


class CodeAnalyzer:

    code: str
    code_visitor: CodeVisitor
    metric_calculator: MetricCalculator

    value_error: bool
    syntax_error: bool
    error_line_number: int | None
    error_column_number: int | None

    def __init__(self, code: str):
        self.code = code
        self.code_visitor = None
        self.metric_calculator = None

        self.value_error = False
        self.syntax_error = False
        self.error_line_number = None
        self.error_column_number = None

    def analyze(self):
        try:
            tree = ast.parse(self.code)
        except SyntaxError as ex:
            self.syntax_error = True
            self.error_line_number = ex.lineno
            self.error_column_number = ex.offset
        except ValueError:
            self.value_error = True
        else:
            self.code_visitor = CodeVisitor()
            self.code_visitor.visit(tree)
            self.metric_calculator = MetricCalculator(self.code, tree)
            self.metric_calculator.calculate()

    def _definition_list_to_json(
        self, definitions: list[Definition]
    ) -> List[Dict[str, Any]]:
        return [
            {
                "id": definition.id_,
                "start_line_number": (
                    definition.node.lineno if definition.node else None
                ),
                "start_column_number": (
                    definition.node.col_offset if definition.node else None
                ),
                "end_line_number": (
                    definition.node.end_lineno if definition.node else None
                ),
                "end_column_number": (
                    definition.node.end_col_offset
                    if definition.node
                    else None
                ),
                "references": [
                    {
                        "line_number": reference.lineno,
                        "column_number": reference.col_offset,
                    }
                    for reference in definition.references
                ],
            }
            for definition in definitions
        ]

    def to_json(self) -> Dict[str, Any]:
        if self.code_visitor is None:
            return {}
        elif self.syntax_error:
            return {
                "error": "systax_error",
                "error_line_number": self.error_line_number,
                "error_column_number": self.error_column_number,
            }
        elif self.value_error:
            return {"error": "value_error"}
        else:
            return {
                "error": None,
                "analysis": self.code_visitor.to_json(),
                "metrics": self.metric_calculator.to_json()
            }


if __name__ == "__main__":
    with open("test.py") as f:
        code = f.read()
    analyzer = CodeAnalyzer(code)
    analyzer.analyze()
    print(analyzer.to_json())
