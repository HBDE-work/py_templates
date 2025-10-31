from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


@dataclass
class GlobalArgs:
    verbose: bool = False


ARGS: GlobalArgs = GlobalArgs()
"""Global Parameters"""

# Argparse registration spec
# iterated by register_with_argparse
# Each entry is (flags, kwargs) matching ArgumentParser.add_argument
ARGPARSE_SPEC: List[Tuple[List[str],
                          Dict[str,
                               Any]]] = [
                                   (
                                       ['--verbose',
                                        '-v'],
                                       {
                                           'action': 'store_true',
                                           'default': False,
                                           'help': 'Enable verbose output'
                                       },
                                   ),
                               ]
