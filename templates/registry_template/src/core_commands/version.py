"""Global command example — no group, runs directly as `python -m registry_template version`."""

from ..registry import register_command

VERSION = "0.1.0"


@register_command(
    name='version',
    # group is omitted → this is a global command available directly on the
    # root parser: `python -m registry_template version`
    help='Print the tool version',
)
def print_version() -> None:
    """Print the current tool version."""
    print(f"registry_template v{VERSION}")
