import argparse
import os
from pathlib import Path
import subprocess
import sys

import boto3


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--account", required=True)
    parser.add_argument("--environment", required=True)
    parser.add_argument("--service_action", required=True)
    args = parser.parse_args()

    region = "eu-west-2"
    session = boto3.Session(region_name=region)

    account = session.client("sts").get_caller_identity()["Account"]
    if account != args.account:
        raise RuntimeError(f"Expected account {args.account}, got {account}")

    env = os.environ.copy()
    env["AWS_DEFAULT_REGION"] = region
    env["AWS_REGION"] = region

    service_unavailable_action = "TDRApp" if args.service_action == "Restart" else "ServiceUnavailable"
    desired_service_count = 1 if args.service_action == "Restart" else 0

    listener_script = Path(__file__).with_name("modify_alb_listener.py")
    subprocess.run(
        [
            sys.executable,
            str(listener_script),
            args.account,
            args.environment,
            service_unavailable_action,
        ],
        env=env,
        check=True,
    )

    ecs = session.client("ecs")
    for cluster_page in ecs.get_paginator("list_clusters").paginate():
        for cluster in cluster_page["clusterArns"]:
            print(f"Cluster: {cluster}", flush=True)

            for service_page in ecs.get_paginator("list_services").paginate(
                    cluster=cluster
            ):
                for service in service_page["serviceArns"]:
                    print(f"Scaling to {desired_service_count}: {service}", flush=True)
                    ecs.update_service(
                        cluster=cluster,
                        service=service,
                        desiredCount=desired_service_count,
                        forceNewDeployment=True
                    )


if __name__ == "__main__":
    main()
