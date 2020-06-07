import os
import sys

import configparser
from configparser import NoOptionError, NoSectionError

from aws_sessions_switcher import util

AWS_CREDS_PATH = '%s/.aws/credentials' % (os.path.expanduser('~'),)
AWS_ASSUME_CONFIG_PATH = f'%s/.aws/{os.getenv("AWS_SESSIONS_SWITCHER_CONFIG_FILENAME", "sessions_switcher")}' % (
    os.path.expanduser('~'),)
AWS_ASSUME_BASE_CREDENTIALS_IDENTIFIER_PREFIX = 'aws-sessions-switcher-'
EXPIRATION_TIMESTAMP_FORMAT = '%Y-%m-%d %H:%M:%S'

# ACTIONS
ACTION = 'action'
SUB_ACTION = 'sub_action'
ACTION_LIST_ASSUMPTIONS = 'list_assumptions'
ACTION_ENVIRONMENT = ['env', 'environments']
ACTION_LIST = 'ls'
ACTION_ADD = 'add'
ACTION_DELETE = 'delete'
ACTION_CONFIGURE = 'configure'
ACTION_PROJECT = 'projects'
ACTION_RESET = 'reset'
ACTION_SESSIONS = 'sessions'
ACTION_SWITCH = 'switch'

# VARIABLES
VAR_PROJECT_NAME = 'project_name'
LONG_VAR_PROJECT_NAME = '--project-name'
SHORT_VAR_PROJECT_NAME = '-n'
SHORT_VAR_ENV_NAME = '-e'
LONG_VAR_ENV_NAME = '--env-name'

sub_commands = {
    'CFGR': ACTION_CONFIGURE,
    'PRJ': ACTION_PROJECT,
    'SESSIONS': ACTION_SESSIONS,
    'ENV': ACTION_ENVIRONMENT[0],
    'SHORT_ENV': ACTION_ENVIRONMENT[1],
    'LIST': ACTION_LIST,
    'ADD': ACTION_ADD,
    'DEL': ACTION_DELETE,
    'RST': ACTION_RESET,
    'SWT': ACTION_SWITCH,
}

project_sub_commands = {
    'LIST': ACTION_LIST,
    'ADD': ACTION_ADD,
    'DELETE': ACTION_DELETE,
}


def get_base_aws_config():
    config = configparser.RawConfigParser()
    try:
        config.read(AWS_CREDS_PATH)
    except configparser.ParsingError:
        e = sys.exc_info()[1]
        print(util.red_text("There was a problem reading or parsing "
                            "your credentials file: %s" % (e.args[0],)))
    return config


def get_base_credentials_for_project(project_name):
    base_config = get_base_aws_config()
    base_profile_name = util.get_base_aws_profile_for_project(project_name)
    try:
        base_credentials_section = base_config[base_profile_name]
        key_id = base_credentials_section['aws_access_key_id']
        access_key = base_credentials_section['aws_secret_access_key']
    except NoSectionError and KeyError:
        util.error_log(
            "Credentials for profile '[%s]' is missing. "
            "You must add this section to your AWS credentials file." % (base_profile_name,))
    except NoOptionError as e:
        util.error_log(e)

    return {
        'key_id': key_id,
        'access_key': access_key
    }
