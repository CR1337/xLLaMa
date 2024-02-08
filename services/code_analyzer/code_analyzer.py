from code_snippet import CodeSnippet
from code_analyzer.code_visitor import CodeVisitor


class CodeAnalyzer:

    code_snippet: CodeSnippet
    code_visitor: CodeVisitor

    def __init__(self, code_snippet: CodeSnippet):
        self.code_snippet = code_snippet
        self.code_visitor = None

    def analyze(self):
        self.code_visitor = CodeVisitor()
        self.code_visitor.visit(self.code_snippet.tree)
