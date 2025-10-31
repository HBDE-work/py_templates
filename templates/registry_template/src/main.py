#!/usr/bin/env python3

import dataclasses
import inspect

from . import include as loader_methods
from .global_args import ARGS
from .registry import register_with_argparse


def main() -> None:

    # import configured modules
    for _, attr_value in loader_methods.__dict__.items():
        if inspect.isfunction(attr_value):
            _ = attr_value()

    parser = register_with_argparse()
    args = parser.parse_args()

    # Populate the global ARGS singleton so any command can import and read it
    for f in dataclasses.fields(ARGS):
        if hasattr(args, f.name):
            setattr(ARGS, f.name, getattr(args, f.name))

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
