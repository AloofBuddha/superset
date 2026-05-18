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

import uuid
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from superset.reports.notifications.slackv2 import SlackV2Notification
from superset.utils.core import HeaderDataType


@pytest.fixture
def mock_header_data() -> HeaderDataType:
    return {
        "notification_format": "PNG",
        "notification_type": "Alert",
        "owners": [1],
        "notification_source": None,
        "chart_id": None,
        "dashboard_id": None,
        "slack_channels": ["some_channel"],
        "execution_id": "test-execution-id",
    }


@patch("superset.reports.notifications.slackv2.g")
@patch("superset.reports.notifications.slackv2.logger")
@patch("superset.reports.notifications.slackv2.get_slack_client")
def test_send_slackv2(
    slack_client_mock: MagicMock,
    logger_mock: MagicMock,
    flask_global_mock: MagicMock,
    mock_header_data,
) -> None:
    # `superset.models.helpers`, a dependency of following imports,
    # requires app context
    from superset.reports.models import ReportRecipients, ReportRecipientType
    from superset.reports.notifications.base import NotificationContent

    execution_id = uuid.uuid4()
    flask_global_mock.logs_context = {"execution_id": execution_id}
    slack_client_mock.return_value.chat_postMessage.return_value = {"ok": True}
    content = NotificationContent(
        name="test alert",
        header_data=mock_header_data,
        embedded_data=pd.DataFrame(
            {
                "A": [1, 2, 3],
                "B": [4, 5, 6],
                "C": ["111", "222", '<a href="http://www.example.com">333</a>'],
            }
        ),
        description='<p>This is <a href="#">a test</a> alert</p><br />',
    )

    notification = SlackV2Notification(
        recipient=ReportRecipients(
            type=ReportRecipientType.SLACKV2,
            recipient_config_json='{"target": "some_channel"}',
        ),
        content=content,
    )
    notification.send()
    logger_mock.info.assert_called_with(
        "Report sent to slack", extra={"execution_id": execution_id}
    )
    slack_client_mock.return_value.chat_postMessage.assert_called_with(
        channel="some_channel",
        text="""*test alert*

<p>This is <a href="#">a test</a> alert</p><br />

<None|Explore in Superset>

```
|    |   A |   B | C                                        |
|---:|----:|----:|:-----------------------------------------|
|  0 |   1 |   4 | 111                                      |
|  1 |   2 |   5 | 222                                      |
|  2 |   3 |   6 | <a href="http://www.example.com">333</a> |
```
""",
    )


@patch("superset.reports.notifications.slackv2.g")
@patch("superset.reports.notifications.slackv2.get_slack_client")
def test_slackv2_send_without_channels_raises(
    slack_client_mock: MagicMock,
    flask_global_mock: MagicMock,
    mock_header_data,
) -> None:
    from superset.reports.models import ReportRecipients, ReportRecipientType
    from superset.reports.notifications.base import NotificationContent
    from superset.reports.notifications.exceptions import NotificationParamException

    flask_global_mock.logs_context = {}
    content = NotificationContent(name="test", header_data=mock_header_data)
    notification = SlackV2Notification(
        recipient=ReportRecipients(
            type=ReportRecipientType.SLACKV2,
            recipient_config_json='{"target": ""}',
        ),
        content=content,
    )
    with pytest.raises(NotificationParamException, match="No recipients"):
        notification.send()


@patch("superset.reports.notifications.slackv2.g")
@patch("superset.reports.notifications.slackv2.get_slack_client")
def test_slack_mixin_get_body_truncates_large_table(
    slack_client_mock: MagicMock,
    flask_global_mock: MagicMock,
    mock_header_data,
) -> None:
    from superset.reports.models import ReportRecipients, ReportRecipientType
    from superset.reports.notifications.base import NotificationContent

    flask_global_mock.logs_context = {}
    # Create a large DataFrame that exceeds the 4000-char message limit
    large_df = pd.DataFrame({"col_" + str(i): range(100) for i in range(10)})
    content = NotificationContent(
        name="test",
        header_data=mock_header_data,
        embedded_data=large_df,
        description="desc",
    )
    notification = SlackV2Notification(
        recipient=ReportRecipients(
            type=ReportRecipientType.SLACKV2,
            recipient_config_json='{"target": "some_channel"}',
        ),
        content=content,
    )
    body = notification._get_body(content=content)
    assert "(table was truncated)" in body
