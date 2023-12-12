from code_visitor import CodeVisitor
from metric_calculator import MetricCalculator
from typing import Any, Dict
from code_snippet import CodeSnippet


class CodeAnalyzer:

    code_snippet: CodeSnippet
    code_visitor: CodeVisitor
    metric_calculator: MetricCalculator

    def __init__(self, code_snippet: CodeSnippet):
        self.code_snippet = code_snippet
        self.code_visitor = None
        self.metric_calculator = None

    def analyze(self):
        self.code_visitor = CodeVisitor()
        self.code_visitor.visit(self.code_snippet.tree)
        self.metric_calculator = MetricCalculator(self.code_snippet)
        self.metric_calculator.calculate()

    def to_json(self) -> Dict[str, Any]:
        return {
            "error": None,
            "analysis": self.code_visitor.to_json(),
            "metrics": self.metric_calculator.to_json()
        }


if __name__ == "__main__":
    import json
    with open("services/code_analyzer/test.py") as f:
        code = f.read()
    analyzer = CodeAnalyzer(code)
    analyzer.analyze()
    print(json.dumps(analyzer.to_json()))
