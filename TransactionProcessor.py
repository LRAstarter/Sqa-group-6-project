"""Transaction-file processing for Backend.

Backend inherits from TransactionMixin, so every method here works on the
attributes Backend creates in __init__:

    self.userAccounts   (UserAccounts)
    self.availableGames (AvailableGames)
    self.gamesCollection (GameCollection)

Transaction codes (every line starts with a 2-digit code followed by "_"):
    00  end of file, stop processing
    01  create user        XX_UUUUUUUUUUUUUUU_TT_CCCCCCCCC
    02  delete user        XX_UUUUUUUUUUUUUUU_TT_CCCCCCCCC
    03  list a game        XX_IIIIIIIIIIIIIIIIIII_SSSSSSSSSSSSSSS_PPPPPP
    04  buy a game         XX_IIIIIIIIIIIIIIIIIII_SSSSSSSSSSSSSSS_UUUUUUUUUUUUUUU_PPPPPP
    05  refund             XX_UUUUUUUUUUUUUUU_SSSSSSSSSSSSSSS_CCCCCCCCC
    06  set user credit    XX_UUUUUUUUUUUUUUU_TT_CCCCCCCCC

Every fatal error message starts with "ERROR: ".
"""
from phase4_support import Game, User

# ---- Field widths: change these if your files use different sizes ----------
USER_W = 15     # usernames (buyer / seller / user)
TYPE_W = 2      # account type
CREDIT_W = 9    # credits, last two digits are cents
GAME_W = 19     # game name in transaction lines
PRICE_W = 6     # price, last two digits are cents

# Characters treated as padding around text fields (spaces or underscores).
PAD = " _"


class FatalError(Exception):
    """A transaction broke a rule. The message always starts with 'ERROR: '."""

    def __init__(self, message: str):
        super().__init__(f"ERROR: {message}")


def _text(raw: str) -> str:
    """Strip padding from a text field (works for left or right justified)."""
    return raw.strip(PAD)


def _cents(raw: str, label: str, line_no: int) -> int:
    """Convert a zero-padded digit field to an int number of cents."""
    if not (raw.isascii() and raw.isdigit()):
        raise FatalError(f"Line {line_no}: {label} '{raw}' must be all digits")
    return int(raw)


def _split(line: str, widths: list, line_no: int) -> list:
    """Cut a line into fixed-width fields after the 'XX_' code prefix."""
    expected = 3 + sum(widths) + (len(widths) - 1)
    if len(line) != expected:
        raise FatalError(
            f"Line {line_no}: expected {expected} characters, got {len(line)}"
        )
    if line[2] != "_":
        raise FatalError(f"Line {line_no}: missing '_' after the code")

    fields = []
    pos = 3
    for i, width in enumerate(widths):
        fields.append(line[pos:pos + width])
        pos += width
        if i < len(widths) - 1:
            if line[pos] != "_":
                raise FatalError(f"Line {line_no}: missing '_' at position {pos + 1}")
            pos += 1
    return fields


class TransactionMixin:
    """Adds readMDTF() and its helpers to Backend."""

    # ---- entry points ------------------------------------------------------
    def readMDTF(self, path: str = "transactions.txt") -> bool:
        """Apply a transaction file. Prints the error and returns False on a fatal error."""
        try:
            self.processMDTF(path)
        except FatalError as e:
            print(e)                      # already starts with "ERROR: "
            return False
        return True

    def processMDTF(self, path: str) -> None:
        """Apply a transaction file. Raises FatalError on the first fatal error."""
        handlers = {
            "01": self._tx_create_user,
            "02": self._tx_delete_user,
            "03": self._tx_list_game,
            "04": self._tx_buy_game,
            "05": self._tx_refund,
            "06": self._tx_set_credit,
        }
        with open(path, "r", encoding="utf-8") as f:
            for line_no, raw in enumerate(f, start=1):
                line = raw.rstrip("\r\n")
                if not line.strip():
                    continue

                code = line[:2]
                if code == "00":            # end of transactions
                    return

                handler = handlers.get(code)
                if handler is None:
                    raise FatalError(f"Line {line_no}: unknown transaction code {code!r}")
                handler(line, line_no)

    # ---- helpers -----------------------------------------------------------
    def _tx_require_user(self, username: str, line_no: int):
        user = self.userAccounts.find_user(username)
        if user is None:
            raise FatalError(f"Line {line_no}: user '{username}' does not exist")
        return user

    def _tx_user_fields(self, line: str, line_no: int):
        """Parse the XX_UUU_TT_CCC layout used by codes 01, 02 and 06."""
        name, acct_type, credit = _split(line, [USER_W, TYPE_W, CREDIT_W], line_no)
        return _text(name), acct_type.strip(), _cents(credit, "credit", line_no)

    # ---- 01: create user ---------------------------------------------------
    def _tx_create_user(self, line: str, line_no: int) -> None:
        name, acct_type, credit = self._tx_user_fields(line, line_no)
        try:
            user = User(name, acct_type, credit)
        except ValueError as e:
            raise FatalError(f"Line {line_no}: {e}")
        if not self.userAccounts.add_user(user):
            raise FatalError(f"Line {line_no}: user '{name}' already exists")

    # ---- 02: delete user ---------------------------------------------------
    def _tx_delete_user(self, line: str, line_no: int) -> None:
        name, _, _ = self._tx_user_fields(line, line_no)
        if not self.userAccounts.remove_user(name):
            raise FatalError(f"Line {line_no}: cannot delete, user '{name}' does not exist")
        # Clean up the deleted user's listings and owned games too.
        self.availableGames.remove_seller(name)
        self.gamesCollection.remove_owner(name)

    # ---- 06: set credit ----------------------------------------------------
    def _tx_set_credit(self, line: str, line_no: int) -> None:
        name, _, credit = self._tx_user_fields(line, line_no)
        if not self.userAccounts.update_credit(name, credit):
            raise FatalError(f"Line {line_no}: cannot set credit, user '{name}' does not exist")

    # ---- 03: list a game for sale -----------------------------------------
    def _tx_list_game(self, line: str, line_no: int) -> None:
        game, seller, price = _split(line, [GAME_W, USER_W, PRICE_W], line_no)
        game, seller = _text(game), _text(seller)
        price = _cents(price, "price", line_no)

        if not self.availableGames.add_game(Game(game, seller, price)):
            raise FatalError(f"Line {line_no}: game '{game}' is already listed")

    # ---- 04: buy a game ----------------------------------------------------
    def _tx_buy_game(self, line: str, line_no: int) -> None:
        game, seller, buyer, price = _split(line, [GAME_W, USER_W, USER_W, PRICE_W], line_no)
        game, seller, buyer = _text(game), _text(seller), _text(buyer)
        price = _cents(price, "price", line_no)

        buyer_user = self._tx_require_user(buyer, line_no)
        seller_user = self._tx_require_user(seller, line_no)

        # Validate everything first so a fatal error leaves the data untouched.
        if buyer_user.get_credit_cents() - price < 0:
            raise FatalError(f"Line {line_no}: '{buyer}' has insufficient credit")
        if self.gamesCollection.owns_game(buyer, game):
            raise FatalError(f"Line {line_no}: '{buyer}' already owns '{game}'")

        buyer_user.set_credit_cents(buyer_user.get_credit_cents() - price)
        seller_user.set_credit_cents(seller_user.get_credit_cents() + price)
        self.gamesCollection.add_game(buyer, game)

    # ---- 05: refund --------------------------------------------------------
    def _tx_refund(self, line: str, line_no: int) -> None:
        buyer, seller, amount = _split(line, [USER_W, USER_W, CREDIT_W], line_no)
        buyer, seller = _text(buyer), _text(seller)
        amount = _cents(amount, "refund", line_no)

        buyer_user = self._tx_require_user(buyer, line_no)
        seller_user = self._tx_require_user(seller, line_no)

        if seller_user.get_credit_cents() - amount < 0:
            raise FatalError(f"Line {line_no}: '{seller}' cannot cover the refund")

        seller_user.set_credit_cents(seller_user.get_credit_cents() - amount)
        buyer_user.set_credit_cents(buyer_user.get_credit_cents() + amount)

        self._tx_remove_refunded_game(buyer, seller, line_no)

    def _tx_remove_refunded_game(self, buyer: str, seller: str, line_no: int) -> None:
        """Remove the refunded game from the buyer's collection.

        The 05 line has no game name, so the game is inferred: it must be a
        game the buyer owns that this seller currently lists. If that is not
        exactly one game, nothing is removed and a warning is printed.
        """
        candidates = [
            game for game in self.gamesCollection.get_games(buyer)
            if self.availableGames.find_game(game, seller) is not None
        ]
        if len(candidates) == 1:
            self.gamesCollection.remove_game(buyer, candidates[0])
        else:
            print(f"WARNING: Line {line_no}: could not tell which game '{buyer}' "
                  f"bought from '{seller}' ({len(candidates)} candidates); "
                  f"no game removed")