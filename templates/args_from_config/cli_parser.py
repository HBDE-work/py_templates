#!/usr/bin/env python3

from argparse import ArgumentParser, Namespace
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Argument:
    flags: List[str] = field(default_factory=list)
    kwargs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Arguments:
    command_args: List[Argument] = field(default_factory=list)


@dataclass
class Command:
    name: str
    subcommands: List[Arguments] = field(default_factory=list)
    help: Optional[str] = field(default=None)


@dataclass
class CommandList:
    commands: List[Command] = field(default_factory=list)
    globals: List[Argument] = field(default_factory=list)

    @staticmethod
    def from_dict(command_config: Dict[str, Any]) -> 'CommandList':
        """
        Use this constructor to construct a subcommand argument list from a dictionary:
        ```python
        command_config: dict = {
            'globals': [{
                'flags': ['-u',
                        '--username'],
                'kwargs': {
                    'help': 'username'
                }
            }],
            'commands':
                [
                    {
                        'name': 'first',
                        'help': 'Main Command Helptext',
                        'subcommands': [{
                            'flags': ['-t',
                                    '--test'],
                            'kwargs': {
                                'help': 'A Helptext'
                            }
                        }]
                    },
                    {
                        'name':
                            'second',
                        'help':
                            'Second Command Helptext',
                        'subcommands':
                            [{
                                'flags': ['-f',
                                        '--fail'],
                                'kwargs': {
                                    'help': 'Another Helptext'
                                }
                            }]
                    }
                ]
        }
        command_list = CommandList.new(command_config)
        args: Namespace = compile(command_list)
        ```
        """
        globals_ = [
            Argument(flags=global_arg['flags'],
                     kwargs=global_arg['kwargs'])
            for global_arg in command_config.get('globals',
                                                 [])
        ]

        # Parse commands
        commands = []
        for command in command_config.get('commands', []):
            subcommands = []
            for subcommand in command.get('subcommands', []):
                subcommands.append(
                    Arguments(
                        command_args=[
                            Argument(flags=subcommand['flags'],
                                     kwargs=subcommand['kwargs'])
                        ]
                    )
                )
            command_name = command.get('name')
            commands.append(
                Command(name=command_name,
                        help=command.get('help'),
                        subcommands=subcommands)
            )

        return CommandList(commands=commands, globals=globals_)

    def keys(self) -> List[str]:
        return [k.name for k in self.commands]

    def items(self) -> List[Tuple[str, List[Arguments]]]:
        return [(cmd.name, cmd.subcommands) for cmd in self.commands]

    def compiled(self, global_help: Optional[str] = None) -> Tuple[ArgumentParser, Namespace]:
        """Construct the parser and the args and return them"""
        # TODO: impl regex, sorter, filter
        if global_help is None:
            global_help = f'Choices: {self.keys()}'
        parser = ArgumentParser()
        subparsers = parser.add_subparsers(dest="command", required=True, help=global_help)
        for command in self.commands:
            sub = subparsers.add_parser(
                command.name,
                help=f"{command.name.upper()}: {command.help}"
            )
            for subcommand in command.subcommands:
                for arguments in subcommand.command_args:
                    # subcommand specific argument
                    try:
                        sub.add_argument(*arguments.flags, **arguments.kwargs)
                    except TypeError as t_err:
                        print(f'{t_err}: could not use ({arguments.flags}, {arguments.kwargs})')
            # global
            for argument in self.globals:
                sub.add_argument(*argument.flags, **argument.kwargs)
        return (parser, parser.parse_args())


if __name__ == '__main__':
    print("Test this module!")
    command_config = {
        'globals': [{
            'flags': ['-u',
                      '--username'],
            'kwargs': {
                'help': 'username'
            }
        }],
        'commands':
            [
                {
                    'name': 'first',
                    'help': 'Main Command Helptext',
                    'subcommands': [{
                        'flags': ['-t',
                                  '--test'],
                        'kwargs': {
                            'help': 'A Helptext'
                        }
                    }]
                },
                {
                    'name':
                        'second',
                    'help':
                        'Second Command Helptext',
                    'subcommands':
                        [{
                            'flags': ['-f',
                                      '--fail'],
                            'kwargs': {
                                'help': 'Another Helptext'
                            }
                        }]
                }
            ]
    }
    commands = CommandList.from_dict(command_config)
    parser, args = commands.compiled()
    print(args.test, args.username)
