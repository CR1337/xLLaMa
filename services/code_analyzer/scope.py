from __future__ import annotations
import ast
from typing import Dict, List
import builtins
from definition import Definition


class Scope:

    node: ast.AST

    imported_names: List[Definition]
    defined_functions: List[Definition]
    defined_classes: List[Definition]
    possibly_defined_variables: List[Definition]
    defined_variables: List[Definition]
    assigned_self_members: List[Definition]
    assigned_class_members: List[Definition]

    self_members: Dict[str, List[ast.Attribute]]
    class_members: Dict[str, List[ast.Attribute]]
    self_member_assignments: Dict[str, List[ast.Attribute]]
    class_member_assignments: Dict[str, List[ast.Attribute]]

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
            Definition(name, [None], set(), True)
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
        self.assigned_self_members = []
        self.assigned_class_members = []

        self.self_members = {}
        self.self_member_assignments = {}
        self.class_members = {}
        self.class_member_assignments = {}

        self.used_references = []
        self.defined_references = []
        self.undefined_references = []

        self.global_names = []
        self.nonlocal_names = []

        self.parent = parent
        self.children = []
        self.is_global = False
        self.is_builtin = False

    def add_imported_name(self, id: str, node: ast.AST):
        self.imported_names.append(Definition(id, [node], set(), False))

    def add_defined_function(
        self,
        id: str,
        function_definition: ast.FunctionDef | ast.AsyncFunctionDef
    ):
        self.defined_functions.append(Definition(
            id, [function_definition], set(), False
        ))

    def add_defined_class(self, id: str, class_definition: ast.ClassDef):
        self.defined_classes.append(Definition(
            id, [class_definition], set(), False
        ))

    def add_possibly_defined_variable(self, id: str, node: ast.AST):
        self.possibly_defined_variables.append(Definition(
            id, [node], set(), False
        ))

    def add_defined_variable(self, id: str, node: ast.AST):
        self.defined_variables.append(Definition(
            id, [node], set(), False
        ))

    def add_used_reference(self, reference: ast.Name):
        self.used_references.append(reference)

    def add_self_member(self, node: ast.AST, id: str):
        if id not in self.self_members:
            self.self_members[id] = []
        self.self_members[id].append(node)

    def add_class_member(self, node: ast.AST, id: str):
        if id not in self.class_members:
            self.class_members[id] = []
        self.class_members[id].append(node)

    def add_self_member_assignment(self, node: ast.AST, id: str):
        if id not in self.self_member_assignments:
            self.self_member_assignments[id] = []
        self.self_member_assignments[id].append(node)

    def add_class_member_assignment(self, node: ast.AST, id: str):
        if id not in self.class_member_assignments:
            self.class_member_assignments[id] = []
        self.class_member_assignments[id].append(node)

    def handle_possibly_defined_variables(self):
        for definition in self.possibly_defined_variables:
            if any(
                definition.id in name
                for name in self.global_names + self.nonlocal_names
            ):
                self.add_used_reference(definition.nodes[0])
                continue
            if any(
                definition.id == other_definition.id
                for other_definition in self.defined_variables
            ):
                self.add_used_reference(definition.nodes[0])
                continue
            self.add_defined_variable(definition.id, definition.nodes[0])
        self.possibly_defined_variables = []

    def _find_definition_in_scope(
        self, id: str, scope: Scope
    ) -> Definition | None:
        for definition in scope.definitions:
            if definition.id == id:
                return definition
        return None

    def _find_definition_in_scope_chain(
        self, id: str, scope: Scope
    ) -> Definition | None:
        while scope:
            if definition := self._find_definition_in_scope(id, scope):
                return definition
            scope = scope.parent
        return None

    def _handle_used_reference(self, reference: ast.Name):
        if any(
            reference.id in global_name
            for global_name in self.global_names
        ):
            self.global_scope.add_used_reference(reference)
        elif any(
            reference.id in nonlocal_name
            for nonlocal_name in self.nonlocal_names
        ):
            self.parent.add_used_reference(reference)
        elif definition := self._find_definition_in_scope(reference.id, self):
            if definition.nodes[0] is not reference:
                definition.references.update([reference])
        elif self not in (self.global_scope, self.builtin_scope):
            self.parent.add_used_reference(reference)
        elif definition := self._find_definition_in_scope(
            reference.id, self.builtin_scope
        ):
            definition.references.update([reference])
        else:
            self.undefined_references.append(reference)

    def handle_used_references(self):
        for reference in self.used_references:
            self._handle_used_reference(reference)

    def _handle_members(
        self,
        members: List[Dict[str, List[ast.Attribute]]],
        member_assignments: List[Dict[str, List[ast.Attribute]]],
        assigned_members: List[Definition]
    ):
        remaining_members = {}
        for id, nodes in members.items():
            if definition := self._find_definition_in_scope(id, self):
                definition.references.update(nodes)
            else:
                remaining_members[id] = nodes
        for id, assign_nodes in member_assignments.items():
            definition = Definition(id, assign_nodes, set(), False)
            for nodes in remaining_members[id]:
                definition.references.update(nodes)
                del remaining_members[id]
            assigned_members.append(definition)
        for nodes in remaining_members.values():
            for node in nodes:
                self.undefined_references.append(node)

    def handle_members(self):
        self._handle_members(
            self.class_members,
            self.class_member_assignments,
            self.assigned_class_members
        )
        self._handle_members(
            self.self_members,
            self.self_member_assignments,
            self.assigned_self_members
        )

    def add_child(self, child: Scope):
        if self.is_builtin:
            child.is_global = True
        self.children.append(child)

    def remove_unused_definitions(self):
        to_remove = []
        for definition in self.definitions:
            if len(definition.references) == 0:
                to_remove.append(definition)
        self.imported_names = [
            d for d in self.imported_names if d not in to_remove
        ]
        self.defined_functions = [
            d for d in self.defined_functions if d not in to_remove
        ]
        self.defined_classes = [
            d for d in self.defined_classes if d not in to_remove
        ]
        self.defined_variables = [
            d for d in self.defined_variables if d not in to_remove
        ]
