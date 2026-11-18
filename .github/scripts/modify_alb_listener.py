import sys
import boto3

account_number = sys.argv[1]
stage = sys.argv[2]
service_to_deploy = sys.argv[3]

client = boto3.client("elbv2")

alb_name = f"tdr-frontend-{stage}"

load_balancers = client.describe_load_balancers()["LoadBalancers"]
frontend_load_balancer_arn = [lb for lb in load_balancers if lb["LoadBalancerName"] == alb_name][0]["LoadBalancerArn"]
listeners = client.describe_listeners(LoadBalancerArn=frontend_load_balancer_arn)["Listeners"]
frontend_https_listener_arn = [li for li in listeners if alb_name in li["ListenerArn"]][0]["ListenerArn"]

listener_rules = client.describe_rules(ListenerArn=frontend_https_listener_arn)["Rules"]

# Retrieve all listener rules for ALB that are not default
listener_rule_arns = []
for lr in listener_rules:
    if not lr["IsDefault"]:
        arn = lr.get("RuleArn")
        listener_rule_arns.append(arn)

target_groups = [
    target_group
    for page in client.get_paginator("describe_target_groups").paginate()
    for target_group in page["TargetGroups"]
]

if service_to_deploy == "ServiceUnavailable":
    target_group = [tg for tg in target_groups if tg["TargetGroupName"].startswith("tdr-su-")][0]
else:
    matching_target_groups = []
    for candidate in target_groups:
        tag_descriptions = client.describe_tags(
            ResourceArns=[candidate["TargetGroupArn"]]
        )["TagDescriptions"]
        if any(
            tag["Key"] == "Name" and tag["Value"] == alb_name
            for description in tag_descriptions
            for tag in description["Tags"]
        ):
            matching_target_groups.append(candidate)

    if len(matching_target_groups) != 1:
        raise ValueError(
            f"Expected exactly one frontend target group with Name tag "
            f"'{alb_name}', found {len(matching_target_groups)}"
        )
    target_group = matching_target_groups[0]

change_target_group_action = {
    "Type": "forward",
    "TargetGroupArn": target_group["TargetGroupArn"]
}

#Update non-default listener rules with the new target group
for lra in listener_rule_arns:
    response = client.modify_rule(
        RuleArn=lra,
        Actions=[change_target_group_action]
    )
