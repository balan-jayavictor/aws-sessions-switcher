import configparser
import sys

from config import config
from aws_sessions_switcher import util


def replace_config_section(file_name, section_name, section_value):
    cfg_parser = configparser.ConfigParser()
    try:
        cfg_parser.read(file_name)
        cfg_parser[section_name] = section_value
        with open(file_name, 'w') as configfile:
            cfg_parser.write(configfile)
    except configparser.ParsingError:
        e = sys.exc_info()[1]
        print(util.red_text("There was a problem reading or parsing "
                            "file: %s" % (e.args[0],)))
        sys.exit(1)


def get_aws_creds_parser():
    cfg_parser = configparser.ConfigParser()
    cfg_parser.read(config.AWS_CREDS_PATH)
    return cfg_parser


def get_aws_assume_config_parser():
    cfg_parser = configparser.ConfigParser()
    cfg_parser.read(config.AWS_ASSUME_CONFIG_PATH)
    return cfg_parser


def replace_aws_assume_config(cfg_parser_with_new_config):
    with open(config.AWS_ASSUME_CONFIG_PATH, 'w') as configfile:
        cfg_parser_with_new_config.write(configfile)


def get_all_projects():
    cfg_parser = get_aws_assume_config_parser()
    # Read only the project configuration, excluding the sessions
    return {s: dict(cfg_parser.items(s)) for s in cfg_parser.sections() if
            not s.startswith('session-')}


def get_all_active_sessions():
    cfg_parser = get_aws_assume_config_parser()
    all_sessions = {s: dict(cfg_parser.items(s)) for s in cfg_parser.sections() if s.startswith('session-')}
    for session, session_details in list(all_sessions.items()):
        if util.is_session_expired(session_details):
            del all_sessions[session]
            cfg_parser.remove_section(session)
            replace_aws_assume_config(cfg_parser)
    return all_sessions


def switch_to_session(session_name):
    if session_name:
        all_sessions = get_all_active_sessions()
        if session_name not in all_sessions:
            util.error_log(f'Session {session_name} unavailable')

        # replace the default profile in the AWS_CREDS file
        replace_config_section(config.AWS_CREDS_PATH, 'default', all_sessions[session_name])
        print('INFO: Switched to => ' + util.green_text('{}'.format(session_name)))


def is_session_usable_in_aws_creds(session_details):
    aws_creds_config = get_aws_creds_parser()
    aws_creds_sections = aws_creds_config.sections()
    if 'default' in aws_creds_sections:
        print('EQUALITY: %s' % (aws_creds_sections['default'] == session_details))
        return aws_creds_sections['default'] == session_details
    return False
