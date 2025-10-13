import re


def is_valid_identifier(value: str) -> bool:
    # PostgreSQL identifiers: start with letter/underscore, then letters/numbers/underscores, max 63 chars
    return (
        isinstance(value, str)
        and 1 <= len(value) <= 63
        and re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", value)
    )
