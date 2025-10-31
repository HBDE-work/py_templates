from registry import register_command


@register_command(
    "text",
    "shout",
    help='Shout a String',
    param_help={'text': 'the text to SHOUT'}
)
def shout(text: str) -> None:
    print(f"{text.upper()}!!!")
