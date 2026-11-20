"""Game listing data used by the Phase 4 backend support classes."""


class Game:
    """Store a game name, seller username, and price in integer cents."""

    def __init__(self, name: str, seller_username: str, price_cents: int):
        """Create a listing from parsed values; reject a negative or noninteger price."""
        if type(price_cents) is not int or price_cents < 0:
            raise ValueError("Price must be a nonnegative integer number of cents.")
        self._name = name
        self._seller_username = seller_username
        self._price_cents = price_cents

    def get_name(self) -> str:
        """Return the game name without adding file padding."""
        return self._name

    def get_seller_username(self) -> str:
        """Return the username of the seller offering the game."""
        return self._seller_username

    def get_price_cents(self) -> int:
        """Return the price in cents, so 1500 represents 15 dollars."""
        return self._price_cents
