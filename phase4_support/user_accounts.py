"""Manage the in-memory collection of current user accounts."""

from .user import User


class UserAccounts:
    """Store User objects indexed by their unique usernames."""

    def __init__(self):
        """Create an empty account collection."""
        self._users = {}

    def set_users(self, users):
        """Replace accounts from parsed User objects, rejecting duplicate usernames."""
        new_users = {}
        for user in users:
            username = user.get_username()
            if username in new_users:
                raise ValueError("Duplicate username: " + username)
            new_users[username] = user
        self._users = new_users

    def get_users(self):
        """Return User objects sorted by username for iteration or file output."""
        return [self._users[name] for name in sorted(self._users)]

    def find_user(self, username: str):
        """Return the matching User, or None if the username is absent."""
        return self._users.get(username)

    def contains_username(self, username: str) -> bool:
        """Return whether an account already uses this exact username."""
        return username in self._users

    def add_user(self, user: User) -> bool:
        """Add an account and return True, or return False for a duplicate username."""
        username = user.get_username()
        if self.contains_username(username):
            return False
        self._users[username] = user
        return True

    def remove_user(self, username: str) -> bool:
        """Remove an existing account and return True, or return False if absent."""
        if not self.contains_username(username):
            return False
        del self._users[username]
        return True

    def update_credit(self, username: str, amount_cents: int) -> bool:
        """Set absolute credit, returning False if absent and rejecting invalid amounts."""
        user = self.find_user(username)
        if user is None:
            return False
        user.set_credit_cents(amount_cents)
        return True
