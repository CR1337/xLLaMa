import radon.raw as radon_raw
import radon.metrics as radon_metrics
import radon.complexity as radon_complexity
import ast
from typing import Any, Dict


class MetricCalculator:

    code: str
    tree: ast.Module

    raw_report: radon_raw.Module
    halstead_report: radon_metrics.HalsteadReport
    cyclometic_complexity: float
    maintainability_index: float

    def __init__(self, code: str, tree: ast.Module):
        self.tree = tree
        self.code = code

        self.raw_report = None
        self.halstead_report = None
        self.complexity_visitor = None
        self.maintainability_index = None

    def calculate(self):
        self.raw_report = radon_raw.analyze(self.code)
        self.halstead_report = radon_metrics.h_visit_ast(self.tree).total
        self.cyclometic_complexity = radon_complexity.average_complexity(
            radon_complexity.cc_visit_ast(self.tree)
        )
        self.maintainability_index = radon_metrics.mi_compute(
            self.halstead_report.volume,
            self.cyclometic_complexity,
            self.raw_report.sloc,
            self.raw_report.comments
        )

    def to_json(self) -> Dict[str, Any]:
        return {
            'raw': {
                'loc': self.raw_report.loc,
                'lloc': self.raw_report.lloc,
                'sloc': self.raw_report.sloc,
                'comments': self.raw_report.comments,
                'multi': self.raw_report.multi,
                'single_comments': self.raw_report.single_comments,
                'blank': self.raw_report.blank
            },
            'halstead': {
                'h1': self.halstead_report.h1,
                'h2': self.halstead_report.h2,
                'N1': self.halstead_report.N1,
                'N2': self.halstead_report.N2,
                'calculated_length': self.halstead_report.calculated_length,
                'volume': self.halstead_report.volume,
                'difficulty': self.halstead_report.difficulty,
                'effort': self.halstead_report.effort,
                'time': self.halstead_report.time,
                'bugs': self.halstead_report.bugs
            },
            'cyclomatic_complexity': {
                'score': self.cyclometic_complexity,
                'rank': radon_complexity.cc_rank(
                    self.cyclometic_complexity
                ),
            },
            'maintainability_index': {
                'score': self.maintainability_index,
                'rank': radon_metrics.mi_rank(self.maintainability_index)
            }
        }
