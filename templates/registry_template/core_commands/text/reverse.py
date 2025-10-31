from registry import register_command


@register_command(
    "text",
    "reverse",
    help='Reverse a Text',
    param_help={'text': 'text to reverse'}
)
def reverse_text(text: str) -> None:
    reversed_text = text[::-1]
    print(f"{reversed_text}")
