from __future__ import annotations
import ast
from stack import Stack
from definition import Definition
from scope import Scope
from typing import Any, Callable, Dict, List, Tuple
from functools import wraps


def visit_sub_scope(func: Callable[[CodeVisitor, ast.AST], None]):
    @wraps(func)
    def wrapper(self, node: ast.AST):
        is_classdef = isinstance(node, ast.ClassDef)
        is_functiondef = isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef)
        )
        scope = Scope(node, self.scopes.peek())

        self.scopes.peek().add_child(scope)
        self.scopes.push(scope)
        if is_classdef:
            self.class_scopes.push(scope)
        elif is_functiondef:
            self.function_scopes.push(scope)

        func(self, node)
        self.generic_visit(node)

        scope.handle_possibly_defined_variables()
        scope.handle_used_references()
        self.scopes.pop()
        if is_classdef:
            scope.handle_members()
            self.class_scopes.pop()
        elif is_functiondef:
            self.function_scopes.pop()

        self.read_out_scope(scope)
        if scope.parent.is_builtin:
            scope.builtin_scope.remove_unused_definitions()
            self.read_out_scope(scope.builtin_scope)

    return wrapper


class CodeVisitor(ast.NodeVisitor):

    scopes: Stack
    class_scopes: Stack
    function_scopes: Stack

    nested_assignments: Stack
    nested_assignment_targets: Stack
    nested_attributes: Stack

    imports: List[Definition]
    functions: List[Definition]
    classes: List[Definition]
    variables: List[Definition]
    assigned_self_members: List[Definition]
    assigned_class_members: List[Definition]

    undefined_references: List[ast.Name]

    def __init__(self):
        self.scopes = Stack()
        self.scopes.push(Scope.create_builtin_scope())
        self.class_scopes = Stack()
        self.function_scopes = Stack()

        self.nested_assignments = Stack()
        self.nested_assignment_targets = Stack()
        self.nested_attributes = Stack()

        self.imports = []
        self.functions = []
        self.classes = []
        self.variables = []
        self.assigned_self_members = []
        self.assigned_class_members = []

        self.undefined_references = []

    @visit_sub_scope
    def visit_Module(self, node: ast.Module):
        pass

    def _handle_member(
        self,
        node: ast.Attribute,
        name: str,
        class_reference_name: str,
        add_member_func: Callable[
            [Scope, Tuple[ast.Name, str]], None
        ],
        add_member_assignment_func: Callable[
            [Scope, Tuple[ast.Name, str]], None
        ]
    ):
        if self.class_scopes.is_empty() or self.function_scopes.is_empty():
            return
        if not any(
            definition.id == class_reference_name
            for definition in self.function_scopes.peek().defined_variables
        ):
            return

        if not self.nested_assignments.is_empty():
            if node == self.nested_assignment_targets.peek():
                add_member_assignment_func(node, name)
                return

        add_member_func(node, name)

    def _handle_self_member(self, node: ast.Attribute, name: str):
        self._handle_member(
            node,
            name,
            "self",
            self.class_scopes.peek().add_self_member,
            self.class_scopes.peek().add_self_member_assignment
        )

    def _handle_class_member(self, node: ast.Attribute, name: str):
        self._handle_member(
            node,
            name,
            "cls",
            self.class_scopes.peek().add_class_member,
            self.class_scopes.peek().add_class_member_assignment
        )

    def _visit_attribute_or_name(self, node: ast.Attribute | ast.Name):
        if isinstance(node, ast.Attribute):
            node_copy = node
            while isinstance(node_copy.value, ast.Attribute):
                node_copy = node_copy.value
            if node_copy.value.id == "self":
                self._handle_self_member(node, node_copy.attr)
            elif node_copy.value.id == "cls":
                self._handle_class_member(node, node_copy.attr)
            self.scopes.peek().add_used_reference(node.value)
        elif isinstance(node, ast.Name):
            self.scopes.peek().add_used_reference(node)
        self.generic_visit(node)

    @visit_sub_scope
    def visit_ClassDef(self, node: ast.ClassDef):
        self.scopes.peek().parent.add_defined_class(node.name, node)
        for base in node.bases:
            self._visit_attribute_or_name(base)
        for decorator in node.decorator_list:
            self._visit_attribute_or_name(decorator)

    @visit_sub_scope
    def _visit_functiondef(self, node: ast.FunctionDef | ast.AsyncFunctionDef):
        self.scopes.peek().parent.add_defined_function(node.name, node)
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

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._visit_functiondef(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._visit_function_def(node)

    @visit_sub_scope
    def visit_Lambda(self, node: ast.Lambda):
        pass

    @visit_sub_scope
    def visit_ListComp(self, node: ast.ListComp):
        pass

    @visit_sub_scope
    def visit_SetComp(self, node: ast.SetComp):
        pass

    @visit_sub_scope
    def visit_DictComp(self, node: ast.DictComp):
        pass

    @visit_sub_scope
    def visit_GeneratorExp(self, node: ast.GeneratorExp):
        pass

    @visit_sub_scope
    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        self.scopes.peek().add_defined_variable(node.name, node)

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
        if self.nested_attributes.is_empty():
            self.scopes.peek().add_used_reference(node)
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        self._visit_attribute_or_name(node)
        self.nested_attributes.push(node)
        self.generic_visit(node)
        self.nested_attributes.pop()

    def _handle_assign_target(
        self,
        target: ast.AST
    ):
        if isinstance(target, ast.Name):
            self.scopes.peek().add_possibly_defined_variable(
                target.id, target
            )
        elif isinstance(target, (ast.Tuple, ast.List)):
            for sub_target in target.elts:
                self._handle_assign_target(sub_target)

    def _visit_assign(
        self,
        node: ast.Assign | ast.AnnAssign | ast.NamedExpr,
        targets: List[ast.AST]
    ):
        self.nested_assignments.push(node)
        for target in targets:
            self._handle_assign_target(target)
            self.nested_assignment_targets.push(target)
            self.visit(target)
            self.nested_assignment_targets.pop()
        if node.value:
            self.visit(node.value)
        # self.generic_visit(node)
        self.nested_assignments.pop()

    def visit_Assign(self, node: ast.Assign):
        self._visit_assign(node, node.targets)

    def visit_AnnAssign(self, node: ast.AnnAssign):
        self._visit_assign(node, [node.target])

    def visit_NamedExpr(self, node: ast.NamedExpr):
        self._visit_assign(node, [node.target])

    def _visit_for(self, node: ast.For | ast.AsyncFor):
        self._handle_assign_target(node.target)
        self.generic_visit(node)

    def visit_For(self, node: ast.For):
        self._visit_for(node)

    def visit_AsyncFor(self, node: ast.AsyncFor):
        self._visit_for(node)

    def visit_withitem(self, node: ast.withitem):
        self._handle_assign_target(node.optional_vars)
        self.generic_visit(node)

    def _definition_list_to_json(
        self, definitions: list[Definition]
    ) -> List[Dict[str, Any]]:
        return [
            definition.to_json()
            for definition in definitions
        ]

    def read_out_scope(self, scope: Scope):
        self.imports.extend(scope.imported_names)
        self.functions.extend(scope.defined_functions)
        self.classes.extend(scope.defined_classes)
        self.variables.extend(scope.defined_variables)
        self.undefined_references.extend(
            scope.undefined_references
        )
        self.assigned_self_members.extend(
            scope.assigned_self_members
        )
        self.assigned_class_members.extend(
            scope.assigned_class_members
        )

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
            "assigned_self_members": self._definition_list_to_json(
                self.assigned_self_members
            ),
            "assigned_class_members": self._definition_list_to_json(
                self.assigned_class_members
            ),
            "undefined_references": [
                {
                    "id": reference.id,
                    "line_number": reference.lineno,
                    "column_number": reference.col_offset,
                }
                for reference in self.undefined_references
            ]
        }
