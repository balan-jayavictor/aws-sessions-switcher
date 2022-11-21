from __future__ import print_function, unicode_literals

from InquirerPy import prompt
from dataclasses import dataclass

from aws_sessions_switcher import util

default_style = {
    'separator': '#cc5454',
    'questionmark': '#E91E63',
    'selected': '#673AB7',
    'pointer': '#673ab7',
    'instruction': '#2196f3',
    'answer': '#2196f3 ',
    'question': '#9ACD32',
}

selection_style = {
    'separator': '#cc5454',
    'questionmark': '#2196f3',
    'selected': '#FFFF00',
    'pointer': '#673ab7',
    'instruction': '#2196f3',
    'answer': '#2196f3',
    'question': '#9ACD32',
}

class ConfigCollector:
    questions = [
        {
            'type': 'input',
            'name': 'project_name',
            'message': 'What\'s the project name?',
            'validate': util.generic_text_validator
        },
        {
            'type': 'input',
            'name': 'project_environment',
            'message': 'Type the environment identifier?',
            'validate': util.generic_text_validator
        },
        {
            'type': 'input',
            'name': 'role_arn',
            'message': 'Type the ARN of the AWS Role, you want to assume?',
        },
        {
            'type': 'input',
            'name': 'role_name',
            'message': 'Give a name to this role:',
            'validate': util.generic_text_validator
        },
        {
            'type': 'confirm',
            'name': 'mfa_required',
            'message': 'Is MFA Required?',
            'default': False,
        },
        {
            'type': 'input',
            'name': 'mfa_device_arn',
            'message': 'Type the ARN of the MFA device?',
            'when': lambda answers: answers['mfa_required'],
            'validate': util.not_empty
        },
        {
            'type': 'input',
            'name': 'mfa_device_session_duration',
            'message': 'Session duration in seconds? (Default: 3600)',
            'default': '3600',
            'when': lambda answers: answers['mfa_required'],
            'validate': util.numbers_only
        },
    ]

    def collect(self):
        answers = prompt(self.questions, style=default_style)
        # pprint(answers)
        return answers


@dataclass
class ConfirmationDialog:
    question: str = None

    def get_answer(self):
        answers = prompt([{
            'type': 'confirm',
            'name': 'confirmation',
            'message': self.question,
            'default': False,
        }], style=default_style, style_override=False)
        return answers.get('confirmation', 'N')


@dataclass
class InputDialog:
    question: str = None

    def get_answer(self):
        answers = prompt([{
            'type': 'input',
            'name': 'value',
            'message': self.question,
            'default': '',
            'validate': util.numbers_only
        }], style=default_style, style_override=False)
        return answers.get('value', '')


@dataclass
class SelectionMenu:
    choices: list = None

    def prepare_list(self):
        return [dict({'name': x}) for x in self.choices]

    def get_answer(self):
        answers = prompt(questions=[{
            'type': 'list',
            'qmark': '❯',
            'message': 'Select a session to switch to',
            'name': 'switch_to_session',
            'choices': self.prepare_list(),
            'validate': lambda answer: 'You must choose at least one topping.' \
                if len(answer) == 0 else True
        }], style=selection_style, style_override=False)

        return answers.get('switch_to_session', None)
