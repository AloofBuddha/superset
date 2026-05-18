# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""Tests for RBAC access control on alert/report views."""

import ast
from pathlib import Path


def _parse_alerts_module() -> ast.Module:
    alerts_path = (
        Path(__file__).resolve().parents[3] / "superset" / "views" / "alerts.py"
    )
    return ast.parse(alerts_path.read_text())


def _get_class_node(tree: ast.Module, name: str) -> ast.ClassDef:
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == name:
            return node
    raise AssertionError(f"Class {name} not found")


def _get_class_attr(cls: ast.ClassDef, attr: str) -> ast.Assign | None:
    for node in cls.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == attr:
                    return node
    return None


def test_todo_comment_removed() -> None:
    alerts_source = (
        Path(__file__).resolve().parents[3] / "superset" / "views" / "alerts.py"
    ).read_text()
    assert "TODO: access control rules" not in alerts_source


def test_base_view_has_class_permission_name() -> None:
    tree = _parse_alerts_module()
    cls = _get_class_node(tree, "BaseAlertReportView")
    attr = _get_class_attr(cls, "class_permission_name")
    assert attr is not None
    assert isinstance(attr.value, ast.Constant)
    assert attr.value.value == "ReportSchedule"


def test_base_view_has_method_permission_name() -> None:
    tree = _parse_alerts_module()
    cls = _get_class_node(tree, "BaseAlertReportView")
    attr = _get_class_attr(cls, "method_permission_name")
    assert attr is not None, "method_permission_name must be set on BaseAlertReportView"
    assert isinstance(attr.value, ast.Name)
    assert attr.value.id == "MODEL_VIEW_RW_METHOD_PERMISSION_MAP"


def test_alert_view_has_class_permission_name() -> None:
    tree = _parse_alerts_module()
    cls = _get_class_node(tree, "AlertView")
    attr = _get_class_attr(cls, "class_permission_name")
    assert attr is not None
    assert isinstance(attr.value, ast.Constant)
    assert attr.value.value == "ReportSchedule"


def test_report_view_has_class_permission_name() -> None:
    tree = _parse_alerts_module()
    cls = _get_class_node(tree, "ReportView")
    attr = _get_class_attr(cls, "class_permission_name")
    assert attr is not None
    assert isinstance(attr.value, ast.Constant)
    assert attr.value.value == "ReportSchedule"


def _get_method_decorators(cls: ast.ClassDef, method: str) -> list[str]:
    for node in cls.body:
        if isinstance(node, ast.FunctionDef) and node.name == method:
            names = []
            for dec in node.decorator_list:
                if isinstance(dec, ast.Name):
                    names.append(dec.id)
                elif isinstance(dec, ast.Attribute):
                    names.append(dec.attr)
                elif isinstance(dec, ast.Call):
                    if isinstance(dec.func, ast.Name):
                        names.append(dec.func.id)
                    elif isinstance(dec.func, ast.Attribute):
                        names.append(dec.func.attr)
            return names
    raise AssertionError(f"Method {method} not found in {cls.name}")


def _get_permission_name_arg(cls: ast.ClassDef, method: str) -> str | None:
    for node in cls.body:
        if isinstance(node, ast.FunctionDef) and node.name == method:
            for dec in node.decorator_list:
                if isinstance(dec, ast.Call):
                    func = dec.func
                    name = ""
                    if isinstance(func, ast.Name):
                        name = func.id
                    elif isinstance(func, ast.Attribute):
                        name = func.attr
                    if name == "permission_name" and dec.args:
                        arg = dec.args[0]
                        if isinstance(arg, ast.Constant):
                            return arg.value
    return None


def test_list_method_has_access_and_permission_decorators() -> None:
    tree = _parse_alerts_module()
    cls = _get_class_node(tree, "BaseAlertReportView")
    decorators = _get_method_decorators(cls, "list")
    assert "has_access" in decorators
    assert "permission_name" in decorators
    assert _get_permission_name_arg(cls, "list") == "read"


def test_log_method_has_access_and_permission_decorators() -> None:
    tree = _parse_alerts_module()
    cls = _get_class_node(tree, "BaseAlertReportView")
    decorators = _get_method_decorators(cls, "log")
    assert "has_access" in decorators
    assert "permission_name" in decorators
    assert _get_permission_name_arg(cls, "log") == "read"


def test_model_view_rw_permission_map_imported() -> None:
    tree = _parse_alerts_module()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == "superset.constants":
                names = [alias.name for alias in node.names]
                if "MODEL_VIEW_RW_METHOD_PERMISSION_MAP" in names:
                    return
    raise AssertionError("MODEL_VIEW_RW_METHOD_PERMISSION_MAP not imported")
