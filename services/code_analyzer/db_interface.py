import requests
import os
from code_snippet import CodeSnippet
from code_analyzer import CodeAnalyzer


class DbInterface:

    DB_INTERFACE_PORT: int = os.environ.get('DB_INTERFACE_INTERNAL_PORT')
    DB_INTERFACE_URL: str = f"http://db_interface:{DB_INTERFACE_PORT}"

    @classmethod
    def get_prediction(cls, prediction_id: str):
        response = requests.get(
            f"{cls.DB_INTERFACE_URL}/predictions/{prediction_id}"
        )
        return response.json()

    @classmethod
    def get_code_snippet(cls, code_snippet_id: str):
        response = requests.get(
            f"{cls.DB_INTERFACE_URL}/code_snippets/{code_snippet_id}"
        )
        return response.json()

    @classmethod
    def post_code_snippet(
        cls,
        code: str,
        start_line: int,
        end_line: int,
        prediction: str
    ):
        response = requests.post(
            f"{cls.DB_INTERFACE_URL}/code_snippets",
            json={
                "code": code,
                "start_line": start_line,
                "end_line": end_line,
                "prediction": prediction
            }
        )
        return response.json()

    @classmethod
    def post_symbol_reference(
        cls,
        symbol: str,
        start_line: int,
        end_line: int,
        start_column: int,
        end_column: int,
        code_snippet: str
    ):
        response = requests.post(
            f"{cls.DB_INTERFACE_URL}/symbol_references",
            json={
                "symbol": symbol,
                "start_line": start_line,
                "end_line": end_line,
                "start_column": start_column,
                "end_column": end_column,
                "code_snippet": code_snippet
            }
        )
        return response.json()

    @classmethod
    def persist_code_snippet(
        cls, code_snippet: CodeSnippet, analyzer: CodeAnalyzer, prediction: str
    ) -> str:
        code_snippet = cls.post_code_snippet(
            code=code_snippet.code,
            start_line=code_snippet.start_line,
            end_line=code_snippet.end_line,
            prediction=prediction
        )

        for reference in analyzer.code_visitor.references:
            cls.post_symbol_reference(
                symbol=reference.id,
                start_line=reference.lineno,
                end_line=reference.end_lineno,
                start_column=reference.col_offset,
                end_column=reference.end_col_offset,
                code_snippet=code_snippet['id']
            )

        return code_snippet['id']
