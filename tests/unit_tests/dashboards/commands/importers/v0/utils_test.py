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
# pylint: disable=import-outside-toplevel, unused-argument

from typing import Any


def test_update_filter_scoping_cross_filter_chart_configuration(
    app_context: None,
) -> None:
    """chart_configuration keys, internal IDs, and excluded lists are remapped."""
    from superset.commands.dashboard.importers.v0 import update_filter_scoping
    from superset.models.dashboard import Dashboard
    from superset.utils import json

    metadata: dict[str, Any] = {
        "chart_configuration": {
            "101": {
                "id": 101,
                "crossFilters": {"scope": {"excluded": [102, 999]}},
            },
            "102": {
                "id": 102,
                "crossFilters": {"scope": {"excluded": [101]}},
            },
            "999": {
                "id": 999,
                "crossFilters": {"scope": {"excluded": [101]}},
            },
        },
    }
    dashboard = Dashboard()
    dashboard.json_metadata = json.dumps(metadata)
    old_to_new = {101: 1, 102: 2}

    update_filter_scoping(dashboard, old_to_new)

    result = json.loads(dashboard.json_metadata)
    chart_cfg = result["chart_configuration"]

    assert "1" in chart_cfg
    assert "2" in chart_cfg
    assert "101" not in chart_cfg
    assert "102" not in chart_cfg
    assert "999" not in chart_cfg

    assert chart_cfg["1"]["id"] == 1
    assert chart_cfg["2"]["id"] == 2

    assert chart_cfg["1"]["crossFilters"]["scope"]["excluded"] == [2]
    assert chart_cfg["2"]["crossFilters"]["scope"]["excluded"] == [1]


def test_update_filter_scoping_global_chart_configuration(
    app_context: None,
) -> None:
    """global_chart_configuration.scope.excluded is remapped."""
    from superset.commands.dashboard.importers.v0 import update_filter_scoping
    from superset.models.dashboard import Dashboard
    from superset.utils import json

    metadata: dict[str, Any] = {
        "global_chart_configuration": {"scope": {"excluded": [101, 102, 999]}},
    }
    dashboard = Dashboard()
    dashboard.json_metadata = json.dumps(metadata)

    update_filter_scoping(dashboard, {101: 1, 102: 2})

    result = json.loads(dashboard.json_metadata)
    assert result["global_chart_configuration"]["scope"]["excluded"] == [1, 2]


def test_update_filter_scoping_default_filters(
    app_context: None,
) -> None:
    """default_filters keys (chart IDs) are remapped."""
    from superset.commands.dashboard.importers.v0 import update_filter_scoping
    from superset.models.dashboard import Dashboard
    from superset.utils import json

    metadata: dict[str, Any] = {
        "default_filters": json.dumps(
            {"101": {"col": "val"}, "102": {"col2": "val2"}, "999": {"x": "y"}}
        ),
    }
    dashboard = Dashboard()
    dashboard.json_metadata = json.dumps(metadata)

    update_filter_scoping(dashboard, {101: 1, 102: 2})

    result = json.loads(dashboard.json_metadata)
    default_filters = json.loads(result["default_filters"])
    assert default_filters == {"1": {"col": "val"}, "2": {"col2": "val2"}}


def test_update_filter_scoping_no_cross_filter_keys(
    app_context: None,
) -> None:
    """No error when cross-filter keys are absent."""
    from superset.commands.dashboard.importers.v0 import update_filter_scoping
    from superset.models.dashboard import Dashboard
    from superset.utils import json

    metadata: dict[str, Any] = {"some_other_key": "value"}
    dashboard = Dashboard()
    dashboard.json_metadata = json.dumps(metadata)

    update_filter_scoping(dashboard, {101: 1})

    result = json.loads(dashboard.json_metadata)
    assert result == {"some_other_key": "value"}


def test_update_filter_scoping_string_excluded_not_list(
    app_context: None,
) -> None:
    """Non-list excluded values (e.g. 'all') are left untouched."""
    from superset.commands.dashboard.importers.v0 import update_filter_scoping
    from superset.models.dashboard import Dashboard
    from superset.utils import json

    metadata: dict[str, Any] = {
        "chart_configuration": {
            "101": {"crossFilters": {"scope": {"excluded": "all"}}},
        },
    }
    dashboard = Dashboard()
    dashboard.json_metadata = json.dumps(metadata)

    update_filter_scoping(dashboard, {101: 1})

    result = json.loads(dashboard.json_metadata)
    assert "1" in result["chart_configuration"]
    assert (
        result["chart_configuration"]["1"]["crossFilters"]["scope"]["excluded"] == "all"
    )
