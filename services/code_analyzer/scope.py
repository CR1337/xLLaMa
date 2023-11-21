from __future__ import annotations
import ast
from typing import List
from dataclasses import dataclass
import builtins


@dataclass
class Definition:

    id_: str
    node: ast.AST
    references: List[ast.AST]


class Scope:

    node: ast.AST

    imported_names: List[Definition]
    defined_functions: List[Definition]
    defined_classes: List[Definition]
    possibly_defined_variables: List[Definition]
    defined_variables: List[Definition]

    used_references: List[ast.Name]
    defined_references: List[ast.Name]
    undefined_references: List[ast.Name]

    global_names: List[str]
    nonlocal_names: List[str]

    parent: Scope
    children: List[Scope]
    is_global: bool
    is_builtin: bool

    @classmethod
    def create_builtin_scope(cls) -> Scope:
        scope = Scope(None, None)
        scope.imported_names = [
            Definition(name, None, [])
            for name in builtins.__dict__.keys()
        ]
        scope.is_builtin = True
        return scope

    @property
    def definitions(self) -> List[Definition]:
        return (
            self.imported_names
            + self.defined_functions
            + self.defined_classes
            + self.defined_variables
        )

    @property
    def global_scope(self) -> Scope:
        scope = self
        while not scope.is_global:
            scope = scope.parent
        return scope

    @property
    def builtin_scope(self) -> Scope:
        return self.global_scope.parent

    def __init__(self, node: ast.AST, parent: Scope):
        self.node = node

        self.imported_names = []
        self.defined_functions = []
        self.defined_classes = []
        self.possibly_defined_variables = []
        self.defined_variables = []

        self.used_references = []
        self.defined_references = []
        self.undefined_references = []

        self.global_names = []
        self.nonlocal_names = []

        self.parent = parent
        self.children = []
        self.is_global = False
        self.is_builtin = False

    def add_imported_name(self, id_: str, node: ast.AST):
        self.imported_names.append(Definition(id_, node, []))

    def add_defined_function(
        self,
        id_: str,
        function_definition: ast.FunctionDef | ast.AsyncFunctionDef
    ):
        self.defined_functions.append(Definition(
            id_, function_definition, []
        ))

    def add_defined_class(self, id_: str, class_definition: ast.ClassDef):
        self.defined_classes.append(Definition(id_, class_definition, []))

    def add_possibly_defined_variable(self, id_: str, node: ast.AST):
        self.possibly_defined_variables.append(Definition(
            id_, node, []
        ))

    def add_defined_variable(self, id_: str, node: ast.AST):
        self.defined_variables.append(Definition(
            id_, node, []
        ))

    def add_used_reference(self, reference: ast.Name):
        self.used_references.append(reference)

    def handle_possibly_defined_variables(self):
        for definition in self.possibly_defined_variables:
            if any(
                definition.id_ in name
                for name in self.global_names + self.nonlocal_names
            ):
                self.add_used_reference(definition.node)
                continue
            if any(
                definition.id_ == other_definition.id_
                for other_definition in self.defined_variables
            ):
                self.add_used_reference(definition.node)
                continue
            self.add_defined_variable(definition.id_, definition.node)
        self.possibly_defined_variables = []

    def _find_definition_in_scope(
        self, id_: str, scope: Scope
    ) -> Definition | None:
        for definition in scope.definitions:
            if definition.id_ == id_:
                return definition
        return None

    def _find_definition_in_scope_chain(
        self, id_: str, scope: Scope
    ) -> Definition | None:
        while scope:
            if definition := self._find_definition_in_scope(id_, scope):
                return definition
            scope = scope.parent
        return None

    def _handle_used_reference(self, reference: ast.Name):
        if any(
            reference.id in global_name
            for global_name in self.global_names
        ):
            if definition := self._find_definition_in_scope(
                reference.id, self.global_scope
            ):
                definition.references.append(reference)
            else:
                self.undefined_references.append(reference)
        elif any(
            reference.id in nonlocal_name
            for nonlocal_name in self.nonlocal_names
        ):
            if definition := self._find_definition_in_scope_chain(
                reference.id, self.parent
            ):
                definition.references.append(reference)
            else:
                self.undefined_references.append(reference)
        elif definition := self._find_definition_in_scope(reference.id, self):
            definition.references.append(reference)
        elif definition := self._find_definition_in_scope_chain(
            reference.id, self.parent
        ):
            definition.references.append(reference)
        elif definition := self._find_definition_in_scope(
            reference.id, self.global_scope
        ):
            definition.references.append(reference)
        elif definition := self._find_definition_in_scope(
            reference.id, self.builtin_scope
        ):
            definition.references.append(reference)
        else:
            self.undefined_references.append(reference)

    def handle_used_references(self):
        for reference in self.used_references:
            self._handle_used_reference(reference)

    def add_child(self, child: Scope):
        if self.is_builtin:
            child.is_global = True
        self.children.append(child)
