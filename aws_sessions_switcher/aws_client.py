import sys

import boto3
from botocore.exceptions import ClientError, ParamValidationError

from config import config
from aws_sessions_switcher import util


def get_sts_credentials(project_name, project_config, mfa_token, session_name):
    try:
        base_creds = config.get_base_credentials_for_project(project_name)
        sts_client = boto3.client(
            'sts',
            aws_access_key_id=base_creds['key_id'],
            aws_secret_access_key=base_creds['access_key']
        )

        response = sts_client.assume_role(
            RoleArn=project_config['role_arn'],
            RoleSessionName=session_name,
            DurationSeconds=int(project_config['mfa_device_session_duration']),
            SerialNumber=project_config['mfa_device_arn'],
            TokenCode=mfa_token
        )
        util.debug_log(f"Response from STS service: {response}")
        return response
    except ClientError as e:
        print(util.red_text("An error occured while calling "
                            "assume role: {}".format(e)))
        sys.exit(1)
    except ParamValidationError:
        e = sys.exc_info()[1]
        print(util.red_text("ERROR: " + e.args[0]))
        sys.exit(1)


def get_sts_credentials_without_mfa(project_name, project_config, session_name):
    try:
        base_creds = config.get_base_credentials_for_project(project_name)
        sts_client = boto3.client(
            'sts',
            aws_access_key_id=base_creds['key_id'],
            aws_secret_access_key=base_creds['access_key']
        )

        response = sts_client.assume_role(
            RoleArn=project_config['role_arn'],
            RoleSessionName=session_name,
            DurationSeconds=int(project_config['mfa_device_session_duration']),
        )
        util.debug_log(f"Response from STS service: {response}")
        return response
    except ClientError as e:
        print(util.red_text("An error occured while calling "
                            "assume role: {}".format(e)))
        sys.exit(1)
    except ParamValidationError:
        e = sys.exc_info()[1]
        print(util.red_text("ERROR: " + e.args[0]))
        sys.exit(1)
