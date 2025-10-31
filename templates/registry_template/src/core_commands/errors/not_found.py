from ...registry import register_command


@register_command(
    name='notfound',
    group='error',
    help='Raise FileNotFound Error',
    param_help={'text': 'Error Text'}
)
def raise_notfound(text: str) -> None:
    raise FileNotFoundError(text)
