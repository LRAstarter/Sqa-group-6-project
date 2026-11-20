"""Maintain ownership records separately from games offered for sale."""


class GameCollection:
    """Map owner usernames to sets of owned game names."""

    def __init__(self):
        """Create an empty collection of ownership records."""
        self._owned_games = {}

    def set_collection(self, records):
        """Replace ownership using an iterable of (game_name, owner_username) pairs."""
        self._owned_games = {}
        for game_name, owner_username in records:
            self.add_game(owner_username, game_name)

    def owns_game(self, owner_username: str, game_name: str) -> bool:
        """Return whether this owner already owns the named game."""
        return game_name in self._owned_games.get(owner_username, set())

    def add_game(self, owner_username: str, game_name: str) -> bool:
        """Record ownership and return True, or return False if already owned."""
        if self.owns_game(owner_username, game_name):
            return False
        self._owned_games.setdefault(owner_username, set()).add(game_name)
        return True

    def get_games(self, owner_username: str):
        """Return this owner's game names in sorted order, or an empty list."""
        return sorted(self._owned_games.get(owner_username, set()))

    def remove_owner(self, owner_username: str) -> int:
        """Delete an owner's records and return the number of ownerships removed."""
        return len(self._owned_games.pop(owner_username, set()))

    def get_records(self):
        """Return sorted (game_name, owner_username) pairs for the file writer."""
        return sorted((game_name, owner_username)
                      for owner_username, games in self._owned_games.items()
                      for game_name in games)
