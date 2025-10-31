"""shows how a command uses a global arg"""

from ..global_args import ARGS
from ..registry import register_command


@register_command(
    name='upper',
    group='text',
    help='Convert text to uppercase',
    param_help={
        'text': 'text to convert'
    },
)
def upper(text: str) -> None:
    result: str = text.upper()
    if ARGS.verbose:
        print(f"[verbose] input : {text!r}")
        print(f"[verbose] output: {result!r}")
    print(result)
