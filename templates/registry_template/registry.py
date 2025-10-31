import inspect
from argparse import ArgumentParser
from typing import Callable, Dict, Optional, Tuple, get_type_hints

_registry: list[tuple[str, str, Callable[..., None], Dict]] = []


def register_command(
    group: str,
    name: str,
    help: Optional[str] = None,
    param_help: Optional[Dict[str,
                              str]] = None,
    arg_options: Optional[Dict[str,
                               Dict]] = None,
    **metadata
):
    """Register a command with optional metadata for argument parsing"""
    def decorator(func: Callable[..., None]):
        # Automatically extract function signature info
        sig = inspect.signature(func)
        func_metadata = {
            'signature': sig,
            'params': {
                name: param
                for name,
                param in sig.parameters.items()
            },
            'help': help or func.__doc__,
            'param_help': param_help or {},
            'arg_options': arg_options or {},
            **metadata
        }

        _registry.append((group, name, func, func_metadata))
        return func

    return decorator


def get_registry() -> list[tuple[str, str, Callable[..., None], Dict]]:
    return _registry.copy()


def find_command(group: str, name: str) -> Optional[Tuple[Callable[..., None], Dict]]:
    """Find a command function and its metadata by group and name"""
    for reg_group, reg_name, func, metadata in _registry:
        if reg_group == group and reg_name == name:
            return func, metadata
    return None


def register_with_argparse() -> ArgumentParser:
    """Registry based Parser"""
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest='group', help='Command groups')

    group_parsers = {}

    for group, name, func, metadata in get_registry():
        if group not in group_parsers:
            group_parser = subparsers.add_parser(group, help=f'{group} commands')
            group_subparsers = group_parser.add_subparsers(dest='command')
            group_parsers[group] = group_subparsers

        # Create command parser with help from docstring or metadata
        help_text = metadata.get('help', func.__doc__ or f'{name} command')
        cmd_parser = group_parsers[group].add_parser(name, help=help_text)

        # Use metadata signature if available, otherwise inspect
        if 'signature' in metadata:
            sig = metadata['signature']
            params = metadata['params']
        else:
            sig = inspect.signature(func)
            params = {
                name: param
                for name,
                param in sig.parameters.items()
            }

        type_hints = get_type_hints(func)

        for param_name, param in params.items():
            param_type = type_hints.get(param_name, str)

            # Get help text for this parameter from metadata
            param_help = metadata.get('param_help',
                                      {}).get(param_name,
                                              f'{param_name} parameter')

            # Get argparse options from metadata
            arg_options = metadata.get('arg_options',
                                       {}).get(param_name,
                                               {})

            if param.default == inspect.Parameter.empty:
                # Required argument
                add_args = [param_name]
                add_kwargs = {
                    'type': param_type,
                    'help': param_help
                }
                add_kwargs.update(arg_options)
                cmd_parser.add_argument(*add_args, **add_kwargs)
            else:
                # Optional argument
                add_args = [f'-{param_name[0]}', f'--{param_name}']
                add_kwargs = {
                    'type': param_type,
                    'default': param.default,
                    'help': f'{param_help} (default: {param.default})'
                }
                add_kwargs.update(arg_options)
                cmd_parser.add_argument(*add_args, **add_kwargs)

        cmd_parser.set_defaults(func=func, metadata=metadata)

    return parser
