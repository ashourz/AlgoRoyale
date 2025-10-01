import re


def is_valid_db_name(db_name):
    # PostgreSQL identifiers: start with letter/underscore, then letters/numbers/underscores, max 63 chars
    return (
        isinstance(db_name, str)
        and 1 <= len(db_name) <= 63
        and re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", db_name)
    )
