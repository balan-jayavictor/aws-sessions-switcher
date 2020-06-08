import logging
import re
import sys

import configparser
import datetime
import time
from prettytable import PrettyTable

from config import config


def setup_logger(logger, level=logging.DEBUG):
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    stdout_handler.setFormatter(
        logging.Formatter('%(levelname)s - %(message)s'))
    stdout_handler.setLevel(level)
    logger.addHandler(stdout_handler)
    logger.setLevel(level)


default_logger = logging.getLogger('aws_sessions_switcher')
setup_logger(default_logger, logging.INFO)


def debug_log(message, logger=default_logger, _nocolor=False):
    if _nocolor:
        logger.debug(message)
    else:
        logger.debug(yellow_text(message))


def info_log(message, logger=default_logger, _nocolor=False):
    if _nocolor:
        logger.info(message)
    else:
        logger.info(yellow_text(message))


def error_log(message, logger=default_logger, _exit=True, _nocolor=False):
    if _nocolor:
        logger.error(message)
    else:
        logger.error(red_text(message))
    if _exit:
        sys.exit(1)


#
# def prompter():
#     try:
#         console_input = raw_input
#     except NameError:
#         console_input = input
#
#     return console_input


def colored(r, g, b, text):
    return "\033[38;2;{};{};{}m{} \033[38;2;255;255;255m".format(r, g, b, text)


def blue_text(text):
    return colored(0, 0, 255, text)


def yellow_text(text):
    return colored(255, 255, 0, text)


def green_text(text):
    # return colored(0, 255, 0, text)
    return colored(154, 205, 50, text)


def red_text(text):
    return colored(255, 0, 0, text)


def generic_text_validator(project_name):
    err_msg = 'Only letters, numbers & underscores are allowed'
    return bool(re.match('^[a-zA-Z0-9_]+$', project_name)) or err_msg


def not_empty(val):
    err_msg = 'Cannot be empty'
    return val != "" or err_msg


def numbers_only(val):
    err_msg = 'Only numbers are allowed'
    return bool(re.match('^[0-9]+$', val)) or err_msg


def is_aws_session_active(session_name, session_details):
    try:
        cfg_parser_aws_creds_file = configparser.ConfigParser()
        cfg_parser_aws_creds_file.read(config.AWS_CREDS_PATH)
        if cfg_parser_aws_creds_file['default'] == session_details:
            return True
        return False
    except Exception:
        e = sys.exc_info()[1]
        print(red_text("Unable to check if session %s is active => %s" % (session_name, e.args[0])))


def get_session_time_difference_in_secs(expiration_time):
    exp_ts = time.mktime(datetime.datetime.strptime(expiration_time, config.EXPIRATION_TIMESTAMP_FORMAT).timetuple())
    cur_ts = time.mktime(datetime.datetime.now(datetime.timezone.utc).timetuple())
    return exp_ts - cur_ts


def get_remaining_time(expiration_time):
    _hrs, _min, _sec = str(datetime.timedelta(seconds=get_session_time_difference_in_secs(expiration_time))).split(":")
    return f'{_hrs}h : {_min}m : {_sec}s'


def is_session_expired(session_details):
    if get_session_time_difference_in_secs(session_details['expiration']) <= 0:
        return True
    return False


def get_assumption_row(project_details):
    return [
        f'{project_details["project_name"]}-{project_details["project_environment"]}-{project_details["role_name"]}',
        project_details['command']]


def print_table(headers, rows):
    t = PrettyTable([green_text(h) for h in headers])
    for row in rows:
        t.add_row([yellow_text(item) for item in row])
    print(t)


def get_base_aws_profile_for_project(project_name):
    return f'{config.AWS_ASSUME_BASE_CREDENTIALS_IDENTIFIER_PREFIX}{project_name}'


def get_session_row(session_name, remaining_time, session_details):
    return [session_name, remaining_time, is_aws_session_active(session_name, session_details)]
