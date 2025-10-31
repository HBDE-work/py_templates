from ..registry import register_command


@register_command(
    name='space',
    group='text',
    help='Space out a String',
    param_help={'text': 'the text to space out'}
)
def space(text: str) -> None:
    elements = [t for t in text]
    spaced = ' '.join(elements)
    print(f"{spaced}!!!")
