import inspect
import warnings
from argparse import ArgumentParser
from dataclasses import fields
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, cast, get_type_hints

from .global_args import ARGPARSE_SPEC, GlobalArgs

CommandMetadata = Dict[str, object]
CommandEntry = Tuple[Optional[str], str, Callable[..., object], CommandMetadata]

_registry: List[CommandEntry] = []


def _global_arg_dests() -> Set[str]:
    dests: Set[str] = set()
    for flags, kwargs in ARGPARSE_SPEC:
        if 'dest' in kwargs:
            dests.add(str(kwargs['dest']))
        else:
            long_flags = [f for f in flags if f.startswith('--')]
            chosen = long_flags[0] if long_flags else flags[0]
            dests.add(chosen.lstrip('-').replace('-', '_'))
    return dests


def register_command(
    name: str,
    group: Optional[str] = None,
    help: Optional[str] = None,
    param_help: Optional[Dict[str,
                              str]] = None,
    arg_options: Optional[Dict[str,
                               Dict[str,
                                    object]]] = None,
    **metadata: object
):
    def decorator(func: Callable[..., object]) -> Callable[..., object]:
        # Automatically extract function signature info
        sig = inspect.signature(func)
        func_metadata: CommandMetadata = {
            'signature': sig,
            'params': {
                param_name: param
                for param_name,
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


def get_registry() -> List[CommandEntry]:
    return _registry.copy()


def find_command(group: Optional[str],
                 name: str) -> Optional[Tuple[Callable[...,
                                                       object],
                                              CommandMetadata]]:
    """Find a command function and its metadata by group and name"""
    for reg_group, reg_name, func, metadata in _registry:
        if reg_group == group and reg_name == name:
            return func, metadata
    return None


def register_with_argparse() -> ArgumentParser:
    """Registry based Parser"""
    parser = ArgumentParser()

    # Register global arguments
    for g_flags, g_kwargs in ARGPARSE_SPEC:
        parser.add_argument(*g_flags, **g_kwargs)

    subparsers = parser.add_subparsers(dest='group', help='Command groups')

    group_parsers: Dict[str,
                        object] = {}

    global_subparsers: object = None

    def _add_cmd(sp: object, cmd_name: str, cmd_help: Optional[str]) -> ArgumentParser:
        return cast(ArgumentParser, getattr(sp, 'add_parser')(cmd_name, help=cmd_help))

    for group, name, func, metadata in get_registry():
        target_subparsers: object
        if group is None:
            if global_subparsers is None:
                global_subparsers = subparsers
            target_subparsers = global_subparsers
        else:
            if group not in group_parsers:
                group_parser = subparsers.add_parser(group, help=f'{group} commands')
                group_subparsers = group_parser.add_subparsers(dest='command')
                group_parsers[group] = group_subparsers
            target_subparsers = group_parsers[group]

        # Create command parser with help from docstring or metadata
        raw_help = metadata.get('help', func.__doc__ or f'{name} command')
        help_text: Optional[str] = raw_help if isinstance(raw_help, str) else None
        cmd_parser = _add_cmd(target_subparsers, name, help_text)

        # Add every global arg to this command's parser
        for g_flags, g_kwargs in ARGPARSE_SPEC:
            cmd_parser.add_argument(*g_flags, **g_kwargs)

        # Use metadata signature if available, otherwise inspect
        raw_sig = metadata.get('signature')
        raw_params = metadata.get('params')
        if isinstance(raw_sig, inspect.Signature) and isinstance(raw_params, dict):
            params: Dict[str, inspect.Parameter] = cast(Dict[str, inspect.Parameter], raw_params)
        else:
            params = dict(inspect.signature(func).parameters)

        type_hints = get_type_hints(func)

        # Dest names already registered on this parser by the global arg block
        global_dests: Set[str] = _global_arg_dests()

        for param_name, param in params.items():
            # Skip params covered by a global arg and warn if mutiple differtent implementation of the same param
            if param_name in global_dests:
                is_required = param.default == inspect.Parameter.empty
                if is_required:
                    warnings.warn(
                        f"[registry] '{func.__name__}': parameter '{param_name}' "
                        f"shadows a global arg but declares no default"
                        f"it will receive the global arg value"
                        'Add a default or rename it!',
                        UserWarning,
                        stacklevel=2,
                    )
                else:
                    cmd_type = type_hints.get(param_name)
                    global_fields = {
                        f.name: f.type
                        for f in fields(GlobalArgs)
                    }
                    global_hint = global_fields.get(param_name)
                    if cmd_type is not None and global_hint is not None and cmd_type != global_hint:
                        warnings.warn(
                            f"[registry] '{func.__name__}': parameter '{param_name}' "
                            f"shadows a global arg with a mismatched type "
                            f"(command expects {cmd_type!r}, global arg is {global_hint!r})",
                            UserWarning,
                            stacklevel=2,
                        )
                continue  # already registered by the global arg block

            param_type = type_hints.get(param_name, str)

            # Get help text for this parameter from metadata
            raw_param_help = metadata.get('param_help',
                                          {})
            param_help_map: Dict[str, str] = cast(Dict[str, str], raw_param_help) \
                if isinstance(raw_param_help, dict) else {}
            param_help: str = param_help_map.get(param_name, f'{param_name} parameter')

            # Get argparse options from metadata
            raw_arg_options = metadata.get('arg_options',
                                           {})
            arg_options_map: Dict[
                str,
                Dict[str,
                     object]] = cast(Dict[str,
                                          Dict[str,
                                               object]],
                                     raw_arg_options) if isinstance(raw_arg_options,
                                                                    dict) else {}
            arg_options: Dict[str,
                              object] = arg_options_map.get(param_name,
                                                            {})

            if param.default == inspect.Parameter.empty:
                # Required argument
                add_args = [param_name]
                add_kwargs: Dict[str,
                                 Any] = {
                                     'help': param_help
                                 }
                # Only add type if no action is specified
                if 'action' not in arg_options:
                    add_kwargs['type'] = param_type
                add_kwargs.update(arg_options)
                cmd_parser.add_argument(*add_args, **add_kwargs)
            else:
                # Optional argument
                add_args = [f'-{param_name[0]}', f'--{param_name}']
                add_kwargs = {
                    'help': f'{param_help} (default: {param.default})'
                }
                # Only add type and default if no action is specified
                if 'action' not in arg_options:
                    add_kwargs['type'] = param_type
                    add_kwargs['default'] = param.default
                add_kwargs.update(arg_options)
                cmd_parser.add_argument(*add_args, **add_kwargs)

        cmd_parser.set_defaults(func=func, metadata=metadata)

    return parser
