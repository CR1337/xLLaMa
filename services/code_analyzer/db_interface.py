import requests
import os
from code_snippet import CodeSnippet
from code_analyzer import CodeAnalyzer
from itertools import product
from typing import Any, Dict, List


class DbInterface:

    DB_INTERFACE_PORT: int = os.environ.get('DB_INTERFACE_INTERNAL_PORT')
    DB_INTERFACE_URL: str = f"http://db_interface:{DB_INTERFACE_PORT}"

    @classmethod
    def symbol_definition_type_by_name(cls, name: str) -> Dict[str, Any]:
        return requests.get(
            f"{cls.DB_INTERFACE_URL}/symbol_definition_types/by_name/{name}"
        ).json()

    @classmethod
    def get_prediction(cls, prediction_id: str):
        response = requests.get(
            f"{cls.DB_INTERFACE_URL}/predictions/{prediction_id}"
        )
        return response.json()

    @classmethod
    def post_code_snippet(
        cls,
        code: str,
        start_line_number: int,
        end_line_number: int,
        raw_loc: int,
        raw_lloc: int,
        raw_sloc: int,
        raw_comments: int,
        raw_multi: int,
        raw_single_comments: int,
        raw_blank: int,
        halstead_h1: int,
        halstead_h2: int,
        halstead_N1: int,
        halstead_N2: int,
        halstead_length: float,
        halstead_volume: float,
        halstead_difficulty: float,
        halstead_effort: float,
        halstead_time: float,
        halstead_bugs: float,
        cyclomatic_complexity_score: float,
        cyclomatic_complexity_rank: str,
        maintainability_index_score: float,
        maintainability_index_rank: str,
        prediction: str
    ):
        response = requests.post(
            f"{cls.DB_INTERFACE_URL}/code_snippets",
            json={
                "code": code,
                "start_line_number": start_line_number,
                "end_line_number": end_line_number,
                "raw_loc": raw_loc,
                "raw_lloc": raw_lloc,
                "raw_sloc": raw_sloc,
                "raw_comments": raw_comments,
                "raw_multi": raw_multi,
                "raw_single_comments": raw_single_comments,
                "raw_blank": raw_blank,
                "halstead_h1": halstead_h1,
                "halstead_h2": halstead_h2,
                "halstead_N1": halstead_N1,
                "halstead_N2": halstead_N2,
                "halstead_length": halstead_length,
                "halstead_volume": halstead_volume,
                "halstead_difficulty": halstead_difficulty,
                "halstead_effort": halstead_effort,
                "halstead_time": halstead_time,
                "halstead_bugs": halstead_bugs,
                "cyclomatic_complexity_score": cyclomatic_complexity_score,
                "cyclomatic_complexity_rank": cyclomatic_complexity_rank,
                "maintainability_index_score": maintainability_index_score,
                "maintainability_index_rank": maintainability_index_rank,
                "prediction": prediction
            }
        )
        return response.json()

    @classmethod
    def post_undefined_symbol_reference(
        cls,
        symbol: str,
        start_line: int,
        end_line: int,
        start_column: int,
        end_column: int,
        code_snippet: str
    ):
        response = requests.post(
            f"{cls.DB_INTERFACE_URL}/undefined_symbol_references",
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
    def post_symbol_definition(
        cls,
        symbol: str,
        start_line: int,
        end_line: int,
        start_column: int,
        end_column: int,
        is_builtin: bool,
        code_snippet: str,
        symbol_definition_type: str
    ):
        response = requests.post(
            f"{cls.DB_INTERFACE_URL}/symbol_definitions",
            json={
                "symbol": symbol,
                "start_line": start_line,
                "end_line": end_line,
                "start_column": start_column,
                "end_column": end_column,
                "is_builtin": is_builtin,
                "code_snippet": code_snippet,
                "symbol_definition_type": symbol_definition_type
            }
        )
        return response.json()

    @classmethod
    def post_symbol_reference(
        cls,
        start_line: int,
        end_line: int,
        start_column: int,
        end_column: int
    ):
        response = requests.post(
            f"{cls.DB_INTERFACE_URL}/symbol_references",
            json={
                "start_line": start_line,
                "end_line": end_line,
                "start_column": start_column,
                "end_column": end_column,
            }
        )
        return response.json()

    @classmethod
    def post_symbol_definition_reference(
        cls,
        symbol_definition: str,
        symbol_reference: str
    ):
        response = requests.post(
            f"{cls.DB_INTERFACE_URL}/symbol_definition_references",
            json={
                "symbol_definition": symbol_definition,
                "symbol_reference": symbol_reference
            }
        )
        return response.json()

    @classmethod
    def persist_code_snippet(
        cls, code_snippet: CodeSnippet, analyzer: CodeAnalyzer, prediction: str
    ) -> str:
        code_snippet = cls.post_code_snippet(
            code=code_snippet.code,
            start_line_number=code_snippet.start_line_number,
            end_line_number=code_snippet.end_line_number,
            raw_loc=analyzer.metric_calculator.raw_report.loc,
            raw_lloc=analyzer.metric_calculator.raw_report.lloc,
            raw_sloc=analyzer.metric_calculator.raw_report.sloc,
            raw_comments=analyzer.metric_calculator.raw_report.comments,
            raw_multi=analyzer.metric_calculator.raw_report.multi,
            raw_single_comments=(
                analyzer.metric_calculator.raw_report.single_comments
            ),
            raw_blank=analyzer.metric_calculator.raw_report.blank,
            halstead_h1=analyzer.metric_calculator.halstead_report.h1,
            halstead_h2=analyzer.metric_calculator.halstead_report.h2,
            halstead_N1=analyzer.metric_calculator.halstead_report.N1,
            halstead_N2=analyzer.metric_calculator.halstead_report.N2,
            halstead_length=analyzer.metric_calculator.halstead_report.length,
            halstead_volume=analyzer.metric_calculator.halstead_report.volume,
            halstead_difficulty=(
                analyzer.metric_calculator.halstead_report.difficulty
            ),
            halstead_effort=analyzer.metric_calculator.halstead_report.effort,
            halstead_time=analyzer.metric_calculator.halstead_report.time,
            halstead_bugs=analyzer.metric_calculator.halstead_report.bugs,
            cyclomatic_complexity_score=(
                analyzer.metric_calculator.cyclometic_complexity
            ),
            cyclomatic_complexity_rank=(
                analyzer.metric_calculator.cyclometic_complexity_rank
            ),
            maintainability_index_score=(
                analyzer.metric_calculator.maintainability_index
            ),
            maintainability_index_rank=(
                analyzer.metric_calculator.maintainability_index_rank
            ),
            prediction=prediction
        )

        for undefined_reference in analyzer.code_visitor.undefined_references:
            cls.post_undefined_symbol_reference(
                symbol=undefined_reference.id,
                start_line=undefined_reference.lineno,
                end_line=undefined_reference.end_lineno,
                start_column=undefined_reference.column,
                end_column=undefined_reference.end_col_offset,
                code_snippet=code_snippet['id']
            )

        for definition_list, definition_type_name in (
            (analyzer.code_visitor.imports, "import"),
            (analyzer.code_visitor.functions, "function"),
            (analyzer.code_visitor.classes, "class"),
            (analyzer.code_visitor.variables, "variable")
            (analyzer.code_visitor.assigned_self_members, "self_assignment"),
            (analyzer.code_visitor.assigned_class_members, "cls_assignment")
        ):
            symbol_definition_type = cls.symbol_definition_type_by_name(
                definition_type_name
            )
            for definition in definition_list:
                symbol_definitions = [
                    cls.post_symbol_definition(
                        symbol=definition.id,
                        start_line=node.lineno,
                        end_line=node.end_lineno,
                        start_column=node.col_offset,
                        end_column=node.end_col_offset,
                        is_builtin=definition.is_builtin,
                        code_snippet=code_snippet['id'],
                        symbol_definition_type=symbol_definition_type['id']
                    )
                    for node in definition.nodes
                ]
                symbol_references = [
                    cls.post_symbol_reference(
                        start_line=reference.lineno,
                        end_line=reference.end_lineno,
                        start_column=reference.col_offset,
                        end_column=reference.end_col_offset,
                    )
                    for reference in definition.references
                ]
                for symbol_definition, symbol_reference in product(
                    symbol_definitions, symbol_references
                ):
                    cls.post_symbol_definition_reference(
                        symbol_definition=symbol_definition['id'],
                        symbol_reference=symbol_reference['id']
                    )

        return code_snippet['id']
