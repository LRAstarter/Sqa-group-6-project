"""Represent a user account without reading files or processing transactions."""


class User:
    """Store a username, account type, and available credit in integer cents."""

    VALID_TYPES = {"AA", "FS", "BS", "SS"}

    def __init__(self, username: str, user_type: str, credit_cents: int = 0):
        """Create a user from parsed fields with a valid type and nonnegative credit."""
        if not isinstance(username, str) or not username.strip() or len(username) > 15:
            raise ValueError("Username must contain 1 to 15 characters.")
        if user_type not in self.VALID_TYPES:
            raise ValueError("Account type must be AA, FS, BS, or SS.")
        self._username = username
        self._user_type = user_type
        self.set_credit_cents(credit_cents)

    def get_username(self) -> str:
        """Return the username used to identify this account."""
        return self._username

    def get_type(self) -> str:
        """Return the two letter account type."""
        return self._user_type

    def get_credit_cents(self) -> int:
        """Return available credit in cents rather than floating point dollars."""
        return self._credit_cents

    def set_credit_cents(self, amount_cents: int):
        """Replace credit with a nonnegative integer amount, or raise ValueError."""
        if type(amount_cents) is not int or amount_cents < 0:
            raise ValueError("Credit must be a nonnegative integer number of cents.")
        self._credit_cents = amount_cents

    def is_admin(self) -> bool:
        """Return whether the account has administrator privileges."""
        return self._user_type == "AA"

    def can_buy(self) -> bool:
        """Return whether the account type permits buying games."""
        return self._user_type in {"AA", "FS", "BS"}

    def can_sell(self) -> bool:
        """Return whether the account type permits selling games."""
        return self._user_type in {"AA", "FS", "SS"}
