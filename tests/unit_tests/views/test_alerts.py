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
"""Tests for superset.views.alerts access control configuration."""

from superset.constants import MODEL_VIEW_RW_METHOD_PERMISSION_MAP
from superset.views.alerts import AlertView, BaseAlertReportView, ReportView


def test_base_alert_report_view_has_class_permission_name() -> None:
    assert BaseAlertReportView.class_permission_name == "ReportSchedule"


def test_alert_view_has_class_permission_name() -> None:
    assert AlertView.class_permission_name == "ReportSchedule"


def test_report_view_has_class_permission_name() -> None:
    assert ReportView.class_permission_name == "ReportSchedule"


def test_base_alert_report_view_has_method_permission_name() -> None:
    assert (
        BaseAlertReportView.method_permission_name
        == MODEL_VIEW_RW_METHOD_PERMISSION_MAP
    )


def test_alert_view_inherits_method_permission_name() -> None:
    assert AlertView.method_permission_name == MODEL_VIEW_RW_METHOD_PERMISSION_MAP


def test_report_view_inherits_method_permission_name() -> None:
    assert ReportView.method_permission_name == MODEL_VIEW_RW_METHOD_PERMISSION_MAP


def test_method_permission_map_covers_list() -> None:
    assert MODEL_VIEW_RW_METHOD_PERMISSION_MAP.get("list") == "read"


def test_log_method_has_read_permission() -> None:
    """The 'log' method is not in the standard permission map,
    so it relies on @permission_name('read') decorator."""
    method = BaseAlertReportView.log
    assert hasattr(method, "_permission_name")
    assert method._permission_name == "read"


def test_list_method_has_read_permission() -> None:
    method = BaseAlertReportView.list
    assert hasattr(method, "_permission_name")
    assert method._permission_name == "read"
