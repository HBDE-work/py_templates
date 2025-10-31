import argparse
import inspect
from typing import get_type_hints

from registry import get_registry
from include import Directories


def register_with_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
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

            if param.default == inspect.Parameter.empty:
                # Required argument
                cmd_parser.add_argument(param_name, type=param_type, help=param_help)
            else:
                # Optional argument
                cmd_parser.add_argument(
                    f'--{param_name}',
                    type=param_type,
                    default=param.default,
                    help=f'{param_help} (default: {param.default})'
                )

        cmd_parser.set_defaults(func=func)

    return parser


def main() -> None:

    # import configured Directories
    for _, attr_value in Directories.__dict__.items():
        if isinstance(attr_value, staticmethod):
            _ = attr_value()

    parser = register_with_argparse()
    args = parser.parse_args()

    if hasattr(args, 'func'):
        # Extract function arguments from parsed args
        sig = inspect.signature(args.func)
        func_args = {}

        for param_name in sig.parameters.keys():
            if hasattr(args, param_name):
                func_args[param_name] = getattr(args, param_name)

        args.func(**func_args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
