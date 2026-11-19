import re


def password_validation_errors(password, username):
    """Rules shared conceptually with the create-user form; API remains authoritative."""
    checks = (
        (len(password) >= 8, "at least 8 characters"),
        (bool(re.search(r"[A-Z]", password)), "an uppercase letter"),
        (bool(re.search(r"[a-z]", password)), "a lowercase letter"),
        (bool(re.search(r"[0-9]", password)), "a number"),
        (bool(re.search(r"[^A-Za-z0-9\s]", password)), "a symbol"),
        (username.lower() not in password.lower(), "no username"),
    )
    return [label for passed, label in checks if not passed]
