import runpy
from pathlib import Path
from unittest.mock import Mock, patch

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / ".github/scripts/modify_alb_listener.py"
ALB_ARN = "arn:aws:elasticloadbalancing:eu-west-2:123456789012:loadbalancer/app/tdr-frontend-intg/123"
LISTENER_ARN = "arn:aws:elasticloadbalancing:eu-west-2:123456789012:listener/app/tdr-frontend-intg/123/456"


@pytest.fixture
def client():
    client = Mock()
    client.describe_load_balancers.return_value = {
        "LoadBalancers": [
            {"LoadBalancerName": "tdr-frontend-intg", "LoadBalancerArn": ALB_ARN}
        ]
    }
    client.describe_listeners.return_value = {
        "Listeners": [{"ListenerArn": LISTENER_ARN}]
    }
    client.describe_rules.return_value = {
        "Rules": [
            {"IsDefault": True, "RuleArn": "default-rule"},
            {"IsDefault": False, "RuleArn": "frontend-rule"},
        ]
    }
    return client


def run_script(client, service="TDRApp"):
    with patch("boto3.client", return_value=client), patch(
        "sys.argv", [str(SCRIPT), "123456789012", "intg", service]
    ):
        runpy.run_path(str(SCRIPT), run_name="__main__")


def set_target_groups(client, *names):
    groups = [
        {"TargetGroupName": name, "TargetGroupArn": f"target-group-{index}"}
        for index, name in enumerate(names)
    ]
    client.get_paginator.return_value.paginate.return_value = [
        {"TargetGroups": [group]} for group in groups
    ]
    return groups


def tag_response(name):
    return {"TagDescriptions": [{"Tags": [{"Key": "Name", "Value": name}]}]}


def test_restores_frontend_by_environment_tag_on_later_page(client):
    groups = set_target_groups(client, "tdr-generated-staging", "tdr-generated-intg")
    client.describe_tags.side_effect = [
        tag_response("tdr-frontend-staging"),
        tag_response("tdr-frontend-intg"),
    ]

    run_script(client)

    client.get_paginator.assert_called_once_with("describe_target_groups")
    assert client.describe_tags.call_args_list[1].kwargs == {
        "ResourceArns": [groups[1]["TargetGroupArn"]]
    }
    client.modify_rule.assert_called_once_with(
        RuleArn="frontend-rule",
        Actions=[{"Type": "forward", "TargetGroupArn": groups[1]["TargetGroupArn"]}],
    )


@pytest.mark.parametrize("match_count", [0, 2])
def test_rejects_missing_or_ambiguous_frontend_before_changing_rules(client, match_count):
    set_target_groups(client, "tdr-generated-one", "tdr-generated-two")
    client.describe_tags.side_effect = [
        tag_response("tdr-frontend-intg") if index < match_count
        else {"TagDescriptions": [{"Tags": []}]}
        for index in range(2)
    ]

    with pytest.raises(ValueError, match=f"'tdr-frontend-intg', found {match_count}"):
        run_script(client)

    client.modify_rule.assert_not_called()


def test_service_unavailable_still_uses_name_prefix(client):
    groups = set_target_groups(client, "tdr-generated-intg", "tdr-su-example-intg")

    run_script(client, "ServiceUnavailable")

    client.describe_tags.assert_not_called()
    client.modify_rule.assert_called_once_with(
        RuleArn="frontend-rule",
        Actions=[{"Type": "forward", "TargetGroupArn": groups[1]["TargetGroupArn"]}],
    )
