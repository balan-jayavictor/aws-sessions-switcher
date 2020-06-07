import argparse

import argcomplete
from config import __version__, config
import aws_sessions_switcher
from aws_sessions_switcher import AwsAssume, util, config_collector, config_parser_util


def configure_environments_parser(env_parser):
    env_parser.add_argument(config.SHORT_VAR_PROJECT_NAME, config.LONG_VAR_PROJECT_NAME,
                            help="Name of the project", required=False)
    env_operations_sub_parser = env_parser.add_subparsers(title="environment-operations",
                                                          dest=config.SUB_ACTION)
    env_add_operation = env_operations_sub_parser.add_parser(config.sub_commands['ADD'])
    env_add_operation.add_argument(config.SHORT_VAR_PROJECT_NAME,
                                   config.LONG_VAR_PROJECT_NAME,
                                   help="Name of the project in which an environment needs to be added",
                                   required=True)
    env_delete_operation = env_operations_sub_parser.add_parser(config.sub_commands['DEL'])
    env_delete_operation.add_argument(config.SHORT_VAR_PROJECT_NAME,
                                      config.LONG_VAR_PROJECT_NAME,
                                      help="Name of the project in which an enviroment needs to be deleted",
                                      required=True)

    env_delete_operation.add_argument(config.SHORT_VAR_ENV_NAME,
                                      config.LONG_VAR_ENV_NAME,
                                      help="Name of the project in which an enviroment needs to be deleted",
                                      required=True)


class ArgumentParser:
    configured_projects = []
    configured_projects_parsers = {}

    def __init__(self) -> object:
        # MAIN Parser
        self.parent_parser = argparse.ArgumentParser(description=util.green_text("aws-sessions-switcher CLI"),
                                                     add_help=True)
        self.parent_parser.add_argument("-l", "--list",
                                        action='store_true',
                                        dest=config.ACTION_LIST_ASSUMPTIONS,
                                        help="Lists all the role assumptions that you can make"
                                        )

        self.parent_parser.add_argument("-v", "--version",
                                        action='version',
                                        version=util.green_text(f'aws-sessions-switcher {__version__.get_version()}'),
                                        help="Lists all the role assumptions that you can make"
                                        )

        self.sub_parser = self.parent_parser.add_subparsers(title="sub-command",
                                                            description="sub-command",
                                                            dest=config.ACTION,
                                                            required=False)

        # COMMAND => configure
        self.sub_parser.add_parser(config.sub_commands['CFGR'])

        # COMMAND => projects
        self.project_parser = self.sub_parser.add_parser(config.sub_commands['PRJ'])
        project_operations_subparser = self.project_parser.add_subparsers(title="project-operations",
                                                                          dest=config.SUB_ACTION)
        project_operations_subparser.add_parser(config.sub_commands['ADD'])
        delete_operation = project_operations_subparser.add_parser(config.sub_commands['DEL'])
        delete_operation.add_argument(config.SHORT_VAR_PROJECT_NAME,
                                      config.LONG_VAR_PROJECT_NAME,
                                      help="Name of the project to be deleted",
                                      required=True)

        # COMMAND => sessions
        self.sessions_parser = self.sub_parser.add_parser(config.sub_commands['SESSIONS'])
        self.sessions_sub_parser = self.sessions_parser.add_subparsers(title="session-operations",
                                                                       dest=config.SUB_ACTION)
        self.sessions_sub_parser.add_parser(config.sub_commands['SWT'])

        # COMMAND => environments
        self.environments_parser = self.sub_parser.add_parser(config.sub_commands['ENV'])
        configure_environments_parser(self.environments_parser)
        # COMMAND => env (same as the previous one, but short version)
        self.environments_parser_short = self.sub_parser.add_parser(config.sub_commands['SHORT_ENV'])
        configure_environments_parser(self.environments_parser_short)

        # COMMAND => reset (deletes all saved config)
        self.sub_parser.add_parser(config.sub_commands['RST'])

        # ENABLE AUTO COMPLETION OF COMMANDS
        argcomplete.autocomplete(self.parent_parser)

        # Instantiate the `aws-sessions-switcher` tool
        self.aws_assume = AwsAssume()

        # DYNAMIC => Now load already configured projects into the parser
        for project_name in self.aws_assume.list_projects(printable=False, validate_configuration=False):
            self.configured_projects.append(project_name)
            self.configured_projects_parsers[project_name] = self.sub_parser.add_parser(project_name)
            _sub = self.configured_projects_parsers[project_name].add_subparsers(title='project_environment',
                                                                                 dest='project_environment',
                                                                                 required=True)
            _envs = self.aws_assume.list_project_environments(project_name, printable=False)
            for environment in _envs:
                env_parser = _sub.add_parser(environment)
                role_parser = env_parser.add_subparsers(title="iam_role", dest='iam_role', required=True)
                roles = self.aws_assume.list_roles(project_name, environment, printable=False)
                {r: role_parser.add_parser(r) for r in roles}

        self.args = self.parent_parser.parse_args().__dict__

    def handle_projects_sub_operations(self):
        if self.args.get(config.SUB_ACTION) in [config.ACTION_LIST, None]:
            self.aws_assume.list_projects()
        elif self.args.get(config.SUB_ACTION) == config.ACTION_ADD:
            self.aws_assume.add_project()
        elif self.args.get(config.SUB_ACTION) == config.ACTION_DELETE:
            _ans = config_collector.ConfirmationDialog(
                f'Are you sure you want to delete project: [{self.args.get(config.VAR_PROJECT_NAME)}]?').get_answer()
            if _ans:
                self.aws_assume.delete_project(self.args.get(config.VAR_PROJECT_NAME))
        else:
            self.project_parser.error("No action requested, add -process or -upload'")

    def handle_environments_sub_operations(self, sub_action):
        if sub_action:
            if sub_action == config.ACTION_ADD:
                # TODO: ADD A NEW ENVIRONMENT
                print(util.yellow_text('Not supported currently. It will be available in later versions...'))
            elif sub_action == config.ACTION_DELETE:
                # TODO: DELETE AN ENVIRONMENT
                print(util.yellow_text('Not supported currently. It will be available in later versions...'))
        else:
            if self.args.get(config.VAR_PROJECT_NAME):
                self.aws_assume.list_project_environments(self.args.get(config.VAR_PROJECT_NAME))
            else:
                self.aws_assume.list_all_environments()

    def run(self):
        # print(util.yellow_text(self.args))
        action = self.args.get(config.ACTION)
        sub_action = self.args.get(config.SUB_ACTION)

        # Configure for initial run
        if action == config.ACTION_CONFIGURE:
            aws_sessions_switcher.configure()
            return

        # LIST ASSUMPTIONS THAT CAN BE MADE
        if self.args.get(config.ACTION_LIST_ASSUMPTIONS) or action is None:
            aws_sessions_switcher.validate_config_file()
            all_config = self.aws_assume.get_all_projects_config()
            for _cfg, _details in list(all_config.items()):
                _details['command'] = "aws-sessions-switcher {} {} {}".format(
                    _details['project_name'], _details['project_environment'], _details['role_name'])

            headers = ['assumptions', 'command_to_run']
            rows = [util.get_assumption_row(details) for project, details in
                    all_config.items()]
            util.print_table(headers, rows)

        # PROJECTS
        elif action == config.ACTION_PROJECT:
            self.handle_projects_sub_operations()

        # ENVIRONMENTS
        elif action in config.ACTION_ENVIRONMENT:
            self.handle_environments_sub_operations(sub_action)

        # SESSIONS
        elif action == config.ACTION_SESSIONS:
            # TODO: PROJECT NAME is Currently not used
            if sub_action == config.ACTION_SWITCH:
                sessions = self.aws_assume.get_active_sessions(self.args.get(config.VAR_PROJECT_NAME), printable=False)
                selected_session = config_collector.SelectionMenu(choices=sessions).get_answer()
                config_parser_util.switch_to_session(selected_session)
            else:
                self.aws_assume.get_active_sessions(self.args.get(config.VAR_PROJECT_NAME))
        elif action == config.ACTION_RESET:
            aws_sessions_switcher.perform_reset()
        # SESSIONS: Switcher: TODO; Switch between multiple sessions

        # TODO: Bash Autocompletion

        # ASSUME
        elif action in self.configured_projects:
            self.aws_assume.assume_role(project_name=action, environment=self.args['project_environment'],
                                        role=self.args['iam_role'])


def main():
    ArgumentParser().run()
