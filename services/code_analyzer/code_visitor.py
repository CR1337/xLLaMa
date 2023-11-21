from __future__ import annotations
import ast
from stack import Stack
from scope import Definition, Scope
from typing import Any, Dict, List


# TODO: handle `self`
# FIXME: multiple copies of references


class CodeVisitor(ast.NodeVisitor):

    scopes: Stack
    inside_attribute: bool

    imports: List[Definition]
    functions: List[Definition]
    classes: List[Definition]
    variables: List[Definition]

    undefined_references: List[ast.Name]

    def __init__(self):
        self.scopes = Stack()
        self.scopes.push(Scope.create_builtin_scope())
        self.inside_attribute = False

        self.imports = []
        self.functions = []
        self.classes = []
        self.variables = []

        self.undefined_references = []

    def _visit_sub_scope(self, node: ast.AST):
        scope = Scope(node, self.scopes.peek())
        self.scopes.peek().add_child(scope)
        self.scopes.push(scope)
        self.generic_visit(node)
        self.scopes.peek().handle_possibly_defined_variables()
        self.scopes.peek().handle_used_references()
        self.imports.extend(self.scopes.peek().imported_names)
        self.functions.extend(self.scopes.peek().defined_functions)
        self.classes.extend(self.scopes.peek().defined_classes)
        self.variables.extend(self.scopes.peek().defined_variables)
        self.undefined_references.extend(
            self.scopes.peek().undefined_references
        )
        self.scopes.pop()

    def visit_Module(self, node: ast.Module):
        self._visit_sub_scope(node)

    def _visit_attribute_or_name(self, node: ast.Attribute | ast.Name):
        if isinstance(node, ast.Attribute):
            self.scopes.peek().add_used_reference(node.value)
        elif isinstance(node, ast.Name):
            self.scopes.peek().add_used_reference(node)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        self.scopes.peek().add_defined_class(node.name, node)
        for base in node.bases:
            self._visit_attribute_or_name(base)
        for decorator in node.decorator_list:
            self._visit_attribute_or_name(decorator)
        self._visit_sub_scope(node)

    def _visit_functiondef(self, node: ast.FunctionDef | ast.AsyncFunctionDef):
        self.scopes.peek().add_defined_function(node.name, node)
        for decorator in node.decorator_list:
            self._visit_attribute_or_name(decorator)
        all_args = (
            node.args.args + node.args.kwonlyargs + node.args.posonlyargs
        )
        if node.args.vararg:
            all_args.append(node.args.vararg)
        if node.args.kwarg:
            all_args.append(node.args.kwarg)
        for arg in all_args:
            self.scopes.peek().add_defined_variable(arg.arg, node)
        self._visit_sub_scope(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._visit_functiondef(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._visit_function_def(node)

    def visit_Lambda(self, node: ast.Lambda):
        self._visit_sub_scope(node)

    def visit_ListComp(self, node: ast.ListComp):
        self._visit_sub_scope(node)

    def visit_SetComp(self, node: ast.SetComp):
        self._visit_sub_scope(node)

    def visit_DictComp(self, node: ast.DictComp):
        self._visit_sub_scope(node)

    def visit_GeneratorExp(self, node: ast.GeneratorExp):
        self._visit_sub_scope(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        self.scopes.peek().add_defined_variable(node.name, node)
        self._visit_sub_scope(node)

    def _visit_import(self, node: ast.Import | ast.ImportFrom):
        for alias in node.names:
            self.scopes.peek().add_imported_name(alias.name, node)

    def visit_Import(self, node: ast.Import):
        self._visit_import(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        self._visit_import(node)

    def visit_Global(self, node: ast.Global):
        self.scopes.peek().global_names.extend(node.names)

    def visit_Nonlocal(self, node: ast.Nonlocal):
        self.scopes.peek().nonlocal_names.extend(node.names)

    def visit_Call(self, node: ast.Call):
        self._visit_attribute_or_name(node.func)
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name):
        if not self.inside_attribute:
            self.scopes.peek().add_used_reference(node)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        if not self.inside_attribute:
            self.scopes.peek().add_used_reference(node.value)
        self.inside_attribute = True
        self.generic_visit(node)
        self.inside_attribute = False

    def _visit_assign_target(
        self,
        target: ast.Name | ast.Tuple | ast.List
    ):
        if isinstance(target, ast.Name):
            self.scopes.peek().add_possibly_defined_variable(
                target.id, target
            )
        elif isinstance(target, (ast.Tuple, ast.List)):
            for sub_target in target.elts:
                self._visit_assign_target(sub_target)

    def visit_Assign(self, node: ast.Assign):
        for target in node.targets:
            self._visit_assign_target(target)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign):
        self._visit_assign_target(node.target)
        self.generic_visit(node)

    def _visit_for(self, node: ast.For | ast.AsyncFor):
        self._visit_assign_target(node.target)
        self.generic_visit(node)

    def visit_For(self, node: ast.For):
        self._visit_for(node)

    def visit_AsyncFor(self, node: ast.AsyncFor):
        self._visit_for(node)

    def visit_withitem(self, node: ast.withitem):
        self._visit_assign_target(node.optional_vars)
        self.generic_visit(node)

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
        return {
            "imports": self._definition_list_to_json(self.imports),
            "functions": self._definition_list_to_json(
                self.functions
            ),
            "classes": self._definition_list_to_json(self.classes),
            "variables": self._definition_list_to_json(
                self.variables
            ),
            "undefined_references": [
                {
                    "id": reference.id,
                    "line_number": reference.lineno,
                    "column_number": reference.col_offset,
                }
                for reference in self.undefined_references
            ],
        }
