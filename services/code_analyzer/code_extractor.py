import ast
from typing import List
from code_snippet import CodeSnippet


class CodeExtractor:

    _lines: List[str]
    _code_snippets: List[CodeSnippet]

    @property
    def code_snippets(self) -> List[CodeSnippet]:
        return self._code_snippets

    def __init__(self, text: str):
        self._lines = text.split("\n")
        self._code_snippets = []

    def _is_candidate(self, start: int, end: int) -> bool:
        return (
            len(self._lines[end - 1].strip())
            and any(
                not line.strip().startswith("#")
                for line in self._lines[start:end]
            )
        )

    def extract(self):
        start = 0
        while start < len(self._lines):
            if len(self._lines[start].strip()) == 0:
                start += 1
                continue
            for end in range(len(self._lines) - 1, start, -1):
                if not self._is_candidate(start, end):
                    continue
                if len(snippet := "\n".join(self._lines[start:end])) == 0:
                    continue
                try:
                    tree = ast.parse(snippet)
                except (SyntaxError, ValueError):
                    continue  # no valid code snippet, just continue
                else:
                    self._code_snippets.append(
                        CodeSnippet(
                            code=snippet,
                            tree=tree,
                            start_line=start,
                            end_line=end - 1,
                        )
                    )
                    start = end
                    break
            else:
                start += 1
