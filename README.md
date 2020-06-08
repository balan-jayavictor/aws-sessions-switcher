aws-sessions-switcher: Manage multiple aws sessions and switch between them seamlessly
======================================================================================

Working with multiple AWS Accounts from the command like can sometimes be difficult if you have to switch between
multiple projects or between environments of the same project.

`aws-sessions-switcher` is a tool I developed to help myself to make switching between accounts / roles across projects easier.
I don't see why such a tool cannot be of help to someone like me and hence decided to make it available to everyone who
might be interested.

I hope it helps someone someday!

If you have any suggestions or want to contribute to this tool, you are very welcome ! 

PS: This is a work in progress, and there is definitely a LOT to improve / optimize.

Installation:
-------------
```shell script
pip install aws-sessions-switcher
```

Basic setup
===========

Setup 1: Configure a project 
-----------------------------
```shell script
aws-sessions-switcher configure
```
Type the details about your AWS Environment, the role you would like to assume, project name etc...
You can configure additional projects by executing `aws-sessions-switcher projects add` command

![configure](https://github.com/balan-jayavictor/aws-sessions-switcher/blob/master/info/configure.png?raw=true "Configuring your first project")


Setup 2: Update your AWS Credentials file 
------------------------------------------
The previous command will tell you under what profile name your AWS credentials must be placed, in the default `~/.aws/credentials` file 


Setup 3: Now see all the assumptions you can make
-------------------------------------------------
Running `aws-sessions-switcher` or `aws-sessions-switcher -l` will tell you how to assume the different roles that you have configured using this tool!

![assumptions](https://github.com/balan-jayavictor/aws-sessions-switcher/blob/master/info/assumptions.png?raw=true "All the assumptions you can make")

Some Example commands
=====================

| command                             | description                                                                                 |
|-------------------------------------|---------------------------------------------------------------------------------------------|
| `aws-sessions-switcher configure`                           | Sets up the tool                                                                            |
| `aws-sessions-switcher reset`                               | Deletes the configuration file created by this tool                                          |
| `aws-sessions-switcher -l`                                  | List all the assumptions that can be made                                                   |
| `aws-sessions-switcher projects`                            | Lists all the configured projects                                                           |
| `aws-sessions-switcher environments`                        | Lists all environments for all projects                                                     |
| `aws-sessions-switcher environments -n ABCD`                | Lists only the environments configured for the project named ABCD                           |
| `aws-sessions-switcher sessions`                            | Lists all the sessions you have created using this tool                                     |
| `aws-sessions-switcher sessions switch`                     | Gives the ability to switch between multiple sessions                                       |
| `aws-sessions-switcher projects add`                        | Add an additional project                                                                   |
| `aws-sessions-switcher projects delete -n ABCD`             | Deletes the configuration of the project named ABCD                                         |
| `aws-sessions-switcher environments add -n ABCD`            | TODO:                                                                                       |
| `aws-sessions-switcher environment delete -n ABCD -e dev`   | TODO:                                                                                       |
| `aws-sessions-switcher my\_project dev admin`               | Attempts to assume 'admin' role on the 'dev' environment of the project named 'my\_project' |


Sample Outputs
==============
#### Configuring your first project
![configure](https://github.com/balan-jayavictor/aws-sessions-switcher/blob/master/info/configure.png?raw=true "Configuring your first project")

#### All the assumptions you can make
![assumptions](https://github.com/balan-jayavictor/aws-sessions-switcher/blob/master/info/assumptions.png?raw=true "All the assumptions you can make")

#### Assuming a role from one of the configured projects
![role_assumption](https://github.com/balan-jayavictor/aws-sessions-switcher/blob/master/info/role_assumption.png?raw=true "")

#### All the active sessions
![sessions.png](https://github.com/balan-jayavictor/aws-sessions-switcher/blob/master/info/sessions.png?raw=true "All the active sessions")

#### Switching between active sessions
![switching_sessions.png](https://github.com/balan-jayavictor/aws-sessions-switcher/blob/master/info/sessions_switch.png?raw=true "Switching between active sessions")
