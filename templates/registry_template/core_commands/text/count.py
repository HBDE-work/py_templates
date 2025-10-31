from registry import register_command


@register_command(
    "text",
    "count",
    help='Count Words',
    param_help={'text': 'text to count words of'}
)
def count_words(text: str) -> None:
    word_count = len(text.split())
    print(f"Word count:{word_count}")
