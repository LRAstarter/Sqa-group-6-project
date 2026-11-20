"""Manage in-memory game listings without reading files or applying transactions."""

from .game import Game


class AvailableGames:
    """Store listings and provide lookups, additions, and seller removal."""

    def __init__(self):
        """Create an empty list of available games."""
        self._games = []

    def set_games(self, games):
        """Replace listings with a copy of an iterable of parsed Game objects."""
        self._games = list(games)

    def get_games(self):
        """Return a shallow list copy for iteration or file output."""
        return list(self._games)

    def find_game(self, name: str, seller_username: str):
        """Return the matching Game, or None when no name and seller match exists."""
        for game in self._games:
            if (game.get_name() == name
                    and game.get_seller_username() == seller_username):
                return game
        return None

    def contains_name(self, name: str) -> bool:
        """Return whether any listing already uses this exact game name."""
        return any(game.get_name() == name for game in self._games)

    def add_game(self, game: Game) -> bool:
        """Add a listing and return True, or return False for a duplicate name."""
        if self.contains_name(game.get_name()):
            return False
        self._games.append(game)
        return True

    def remove_seller(self, seller_username: str) -> int:
        """Remove all listings for a deleted seller and return the number removed."""
        old_count = len(self._games)
        self._games = [game for game in self._games
                       if game.get_seller_username() != seller_username]
        return old_count - len(self._games)
