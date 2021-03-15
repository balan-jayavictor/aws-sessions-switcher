import copy
import os
import sys

import configparser

from config import config
from aws_sessions_switcher import util, config_parser_util, config_collector, aws_client


def validate_config_file():
    if not os.path.isfile(config.AWS_ASSUME_CONFIG_PATH):
        util.error_log(f'Could not locate configuration file at "{config.AWS_ASSUME_CONFIG_PATH}"', _exit=False)
        util.info_log(f"Run `aws-sessions-switcher configure` to create one")
        sys.exit(1)


def configure(write_mode='w', check_file_existence=True):
    if check_file_existence and os.path.isfile(config.AWS_ASSUME_CONFIG_PATH):
        util.error_log(
            'File %s already exists.'
            'Run `aws-sessions-switcher projects add` if you want to add a new project configuration.'
            'Type \'aws-sessions-switcher -h\' to see all the available sub-commands' % (
                config.AWS_ASSUME_CONFIG_PATH,))
    else:
        _collector = config_collector.ConfigCollector()
        answers = _collector.collect()
        if not answers:
            return
        cfg_parser = configparser.ConfigParser()
        cfg_parser[f"{answers['project_name']}-{answers['project_environment']}"] = answers
        with open(config.AWS_ASSUME_CONFIG_PATH, write_mode) as configfile:
            cfg_parser.write(configfile)

        print(util.yellow_text(
            f"Note: Make sure to put your security credentials under "
            f"\"{util.get_base_aws_profile_for_project(answers['project_name'])}\" "
            f"section of your AWS Credentials"))


def perform_reset():
    if os.path.exists(config.AWS_ASSUME_CONFIG_PATH):
        try:
            ans = config_collector.ConfirmationDialog(
                f'This file => "{config.AWS_ASSUME_CONFIG_PATH}" will be deleted. '
                f'Are you sure you want to perform a reset?: ').get_answer()
            if ans:
                os.remove(config.AWS_ASSUME_CONFIG_PATH)
                util.info_log(f'The file "{config.AWS_ASSUME_CONFIG_PATH}" is deleted')
        except Exception:
            util.error_log(f'The file "{config.AWS_ASSUME_CONFIG_PATH}" could not be deleted')
    else:
        util.error_log(f'The file "{config.AWS_ASSUME_CONFIG_PATH}" does not exist')
    pass


class AwsAssume:
    all_projects_config = {}
    all_active_sessions = config_parser_util.get_all_active_sessions()

    def __init__(self, action=None) -> None:
        if os.path.isfile(config.AWS_ASSUME_CONFIG_PATH):
            self.all_projects_config = config_parser_util.get_all_projects()

    def get_all_projects_config(self):
        return self.all_projects_config

    def list_projects(self, printable=True, validate_configuration=True) -> []:
        if validate_configuration:
            validate_config_file()

        _pjts = []
        for env, details in self.all_projects_config.items():
            if details.get('project_name') not in _pjts:
                if printable:
                    print(util.green_text(f"- {details['project_name']}"))
                _pjts.append(details['project_name'])
        return _pjts

    def list_project_environments(self, project_name, printable=True):
        validate_config_file()
        _pjt_envs = []
        for env, details in self.all_projects_config.items():
            if details.get('project_name') and project_name == details['project_name']:
                _pjt_envs.append(details['project_environment'])
                if printable:
                    print(util.green_text(f"- {details['project_environment']}"))
        return _pjt_envs

    def list_all_environments(self, printable=True, with_project_prefix=True):
        validate_config_file()
        for env, details in self.all_projects_config.items():
            prefix = f"{details['project_name']}-" if with_project_prefix else ''
            if printable:
                print(util.green_text(f"- {prefix}{details['project_environment']}"))

    def list_roles(self, project_name, environment, printable=False) -> []:
        validate_config_file()
        roles = []
        for env, details in self.all_projects_config.items():
            if details.get('project_name') and project_name == details['project_name'] and environment == details[
                'project_environment']:
                roles.append(details['role_name'])
                if printable:
                    util.info_log(f"{details['role_name']} => {details['role_arn']}")
        return roles

    def add_project(self):
        validate_config_file()
        configure('a', False)
        # new_project = config_collector.ConfigCollector().collect()
        # self.all_projects_config.update(new_project)
        # cfg_parser = configparser.ConfigParser()
        # cfg_parser[f"{new_project['project_name']}-{new_project['project_environment']}"] = new_project
        # with open(config.AWS_ASSUME_CONFIG_PATH, 'a') as configfile:
        #     cfg_parser.write(configfile)

    def delete_project(self, project_name):
        validate_config_file()
        configs = copy.deepcopy(self.all_projects_config)
        for cfg in configs:
            if project_name in cfg:
                self.all_projects_config.pop(cfg)

        writer = configparser.ConfigParser()
        for name, value in self.all_projects_config.items():
            writer[name] = value
        with open(config.AWS_ASSUME_CONFIG_PATH, 'w') as configfile:
            writer.write(configfile)

    def assume_role(self, project_name, environment, role):
        project_config = self.all_projects_config[f'{project_name}-{environment}']
        util.info_log(f"Attempting to assume role: \"{role}\" using ARN: \"{project_config['role_arn']}\" "
                      f"on project: {project_name}")
        session_name = f"session-{project_name}-{environment}"
        options = [
            ('aws_access_key_id', 'AccessKeyId'),
            ('aws_secret_access_key', 'SecretAccessKey'),
            ('aws_session_token', 'SessionToken'),
            ('aws_security_token', 'SessionToken'),
        ]

        if project_config['mfa_required'] == 'True':
            mfa_token = config_collector.InputDialog(
                f"MFA TOKEN for device {project_config['mfa_device_arn']}").get_answer()
            session_creds = aws_client.get_sts_credentials(project_name, project_config, mfa_token, session_name)
        else:
            session_creds = aws_client.get_sts_credentials_without_mfa(project_name, project_config, session_name)

        new_session = {k: session_creds['Credentials'][v] for k, v in options}
        new_session.update(
            {'expiration': session_creds['Credentials']['Expiration'].strftime(config.EXPIRATION_TIMESTAMP_FORMAT)})
        config_parser_util.replace_config_section(config.AWS_ASSUME_CONFIG_PATH, session_name, new_session)

        # replace the default profile in the AWS_CREDS file
        config_parser_util.replace_config_section(config.AWS_CREDS_PATH, 'default', new_session)
        print(util.green_text('- SUCCESS!'))


    def get_active_sessions(self, project_name, printable=True):
        validate_config_file()
        sessions = self.all_active_sessions
        remaining_times = {session_name: util.get_remaining_time(session_details['expiration']) for
                           session_name, session_details in sessions.items()}
        if not remaining_times:
            print(util.yellow_text(
                f'- No active sessions present. Run `aws-sessions-switcher -l` to see all possible role assumptions you can make'))
            return
        else:
            headers = ['session_name', 'remaining_time', 'configured_to_be_used_with_aws_command']
            rows = [util.get_session_row(session_name, remaining_time, sessions[session_name]) for
                    session_name, remaining_time in remaining_times.items()]
            if printable:
                util.print_table(headers, rows)
                print(
                    f'Note: If {util.yellow_text("`configured_to_be_used_with_aws_command`")}is False,\n'
                    f'run {util.green_text("`aws-sessions-switcher sessions switch`")} and select this session to activate it')
            return [session for session in remaining_times]
