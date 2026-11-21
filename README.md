# Phase 4 supporting classes

```python
from phase4_support import Game, AvailableGames, GameCollection

available = AvailableGames()
available.add_game(Game("Example Game", "Seller1", 1500))
collection = GameCollection()
collection.add_game("Buyer1", "Example Game")
print(available.find_game("Example Game", "Seller1").get_price_cents())
print(collection.get_games("Buyer1"))
```

The example prints 1500 and ['Example Game']. These calls only change in-memory data. They do not charge a buyer, pay a seller, validate an account, or write files.

## To test program Open Backend and click run

## Integration agreement

Money is stored as integer cents, following the supplied C++ Game class. Names are passed without file padding and compared exactly. The file reader should remove padding and END sentinel records before constructing these objects. The file writer handles field widths, numeric formatting, and END records.

GameCollection stores game names and owner usernames, not sale prices or seller objects. Its input and output record order is (game_name, owner_username), matching the collection file layout. The add_game method takes owner_username first; parameter names document this distinction.

AvailableGames rejects duplicate game names when add_game is used, following the supplied frontend's containsName rule. set_games accepts already parsed starting listings. The backend is responsible for account validation and transaction ordering. A purchase records ownership without removing the sale listing. Account deletion can call both remove_seller and remove_owner. Refund handling and decisions about ownership removal belong to the transaction processor and have not been invented here.

The frontend's pending name reservation and session clear methods were not copied into these backend storage classes because they manage interactive session state. The teammate writing the backend must decide when transaction changes are applied. No compatibility with an unseen Python implementation or revised UML is claimed; agree these signatures with the team before merging.

## User integration

User is one account. UserAccounts is the collection of accounts, corresponding to the Current User Accounts File. User replaces the role of the C++ Account class; a separate duplicate Account class is not required.

```python
from phase4_support import User, UserAccounts

accounts = UserAccounts()
accounts.add_user(User("Buyer1", "BS", 15000))
accounts.update_credit("Buyer1", 17500)
print(accounts.find_user("Buyer1").get_credit_cents())
```

This prints 17500. update_credit sets the new total, not an amount to add. The transaction processor computes totals and enforces transaction limits, account credit ceilings, permissions, and sufficient funds before changing accounts. Invalid negative or noninteger credit raises ValueError. Removing an account here does not remove game listings or ownership records; the transaction processor coordinates those calls. No files are read or written by these classes. File readers must skip END records.

Use these classes instead of a teammate's overlapping user implementation, or agree the interfaces before merging; do not keep conflicting account models.

## Class and method descriptions

| Method                                                                                   | Description                                                                            |
| ---------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `Game`                                                                                   | Store a game name, seller username, and price in integer cents.                        |
| `Game.__init__(self, name: str, seller_username: str, price_cents: int)`                 | Create a listing from parsed values; reject a negative or noninteger price.            |
| `Game.get_name(self)`                                                                    | Return the game name without adding file padding.                                      |
| `Game.get_seller_username(self)`                                                         | Return the username of the seller offering the game.                                   |
| `Game.get_price_cents(self)`                                                             | Return the price in cents, so 1500 represents 15 dollars.                              |
| `AvailableGames`                                                                         | Store listings and provide lookups, additions, and seller removal.                     |
| `AvailableGames.__init__(self)`                                                          | Create an empty list of available games.                                               |
| `AvailableGames.set_games(self, games)`                                                  | Replace listings with a copy of an iterable of parsed Game objects.                    |
| `AvailableGames.get_games(self)`                                                         | Return a shallow list copy for iteration or file output.                               |
| `AvailableGames.find_game(self, name: str, seller_username: str)`                        | Return the matching Game, or None when no name and seller match exists.                |
| `AvailableGames.contains_name(self, name: str)`                                          | Return whether any listing already uses this exact game name.                          |
| `AvailableGames.add_game(self, game: Game)`                                              | Add a listing and return True, or return False for a duplicate name.                   |
| `AvailableGames.remove_seller(self, seller_username: str)`                               | Remove all listings for a deleted seller and return the number removed.                |
| `AvailableGames.remove_game(self, game: Game)`                                           | Remove one listing and return True, or return False if its name is not listed.         |
| `GameCollection`                                                                         | Map owner usernames to sets of owned game names.                                       |
| `GameCollection.__init__(self)`                                                          | Create an empty collection of ownership records.                                       |
| `GameCollection.set_collection(self, records)`                                           | Replace ownership using an iterable of (game_name, owner_username) pairs.              |
| `GameCollection.owns_game(self, owner_username: str, game_name: str)`                    | Return whether this owner already owns the named game.                                 |
| `GameCollection.add_game(self, owner_username: str, game_name: str)`                     | Record ownership and return True, or return False if already owned.                    |
| `GameCollection.get_games(self, owner_username: str)`                                    | Return this owner's game names in sorted order, or an empty list.                      |
| `GameCollection.remove_game(self, owner_username: str, game_name: str)`                  | Remove one owned game and return True, or return False if not owned.                   |
| `GameCollection.remove_owner(self, owner_username: str)`                                 | Delete an owner's records and return the number of ownerships removed.                 |
| `GameCollection.get_records(self)`                                                       | Return sorted (game_name, owner_username) pairs for the file writer.                   |
| `GameCollection.__repr__(self)`                                                          | Return a readable string of each owner and their sorted games.                         |
| `User`                                                                                   | Store a username, account type, and available credit in integer cents.                 |
| `User.__init__(self, username: str, user_type: str, credit_cents: int=0)`                | Create a user from parsed fields with a valid type and nonnegative credit.             |
| `User.__repr__(self)`                                                                    | Return a readable string of the username, account type, and credit.                    |
| `User.get_username(self)`                                                                | Return the username used to identify this account.                                     |
| `User.get_type(self)`                                                                    | Return the two letter account type.                                                    |
| `User.get_account_type(self)`                                                            | Return the two letter account type (same value as get_type).                           |
| `User.get_credit_cents(self)`                                                            | Return available credit in cents rather than floating point dollars.                   |
| `User.set_credit_cents(self, amount_cents: int)`                                         | Replace credit with a nonnegative integer amount, or raise ValueError.                 |
| `User.is_admin(self)`                                                                    | Return whether the account has administrator privileges.                               |
| `User.can_buy(self)`                                                                     | Return whether the account type permits buying games.                                  |
| `User.can_sell(self)`                                                                    | Return whether the account type permits selling games.                                 |
| `UserAccounts`                                                                           | Store User objects indexed by their unique usernames.                                  |
| `UserAccounts.__init__(self)`                                                            | Create an empty account collection.                                                    |
| `UserAccounts.set_users(self, users)`                                                    | Replace accounts from parsed User objects, rejecting duplicate usernames.              |
| `UserAccounts.get_users(self)`                                                           | Return User objects sorted by username for iteration or file output.                   |
| `UserAccounts.find_user(self, username: str)`                                            | Return the matching User, or None if the username is absent.                           |
| `UserAccounts.contains_username(self, username: str)`                                    | Return whether an account already uses this exact username.                            |
| `UserAccounts.add_user(self, user: User)`                                                | Add an account and return True, or return False for a duplicate username.              |
| `UserAccounts.remove_user(self, username: str)`                                          | Remove an existing account and return True, or return False if absent.                 |
| `UserAccounts.update_credit(self, username: str, amount_cents: int)`                     | Set absolute credit, returning False if absent and rejecting invalid amounts.          |
| `Backend`                                                                                | Load the data files into the game, user, and ownership objects and apply transactions. |
| `Backend.__init__(self)`                                                                 | Create empty availableGames, userAccounts, and gamesCollection objects.                |
| `Backend.applyMDTF(self)`                                                                | Read the games, users, and ownership files, then apply the transaction file.           |
| `Backend.parse_lineAG(self, line)`                                                       | Parse one fixed-width games.txt line into a Game, with the price in cents.             |
| `Backend.readAG(self, filename)`                                                         | Read games.txt up to END and store the listings in availableGames.                     |
| `Backend.parse_lineUA(self, line: str, line_no: int)`                                    | Parse one 28-character users.txt line into a User, or raise ValueError.                |
| `Backend.readUA(self, path: str)`                                                        | Read users.txt up to END and store the accounts in userAccounts.                       |
| `Backend.parse_line_gc(self, line: str, line_no: int)`                                   | Parse one 42-character ownership line into a (game_name, owner) pair.                  |
| `Backend.readGC(self, path: str)`                                                        | Read the ownership file, require the END record, and store it in gamesCollection.      |
| `FatalError`                                                                             | Exception for a transaction that breaks a rule; its message starts with "ERROR: ".     |
| `TransactionMixin`                                                                       | Add transaction-file processing to Backend using its three data objects.               |
| `TransactionMixin.readMDTF(self, path: str="transactions.txt")`                          | Apply a transaction file; print the error and return False on a fatal error.           |
| `TransactionMixin.processMDTF(self, path: str)`                                          | Apply a transaction file line by line, stopping at 00 or raising FatalError.           |
| `TransactionMixin._tx_require_user(self, username: str, line_no: int)`                   | Return the named User, or raise FatalError if the user does not exist.                 |
| `TransactionMixin._tx_user_fields(self, line: str, line_no: int)`                        | Parse the name, type, and credit fields used by codes 01, 02, and 06.                  |
| `TransactionMixin._tx_create_user(self, line: str, line_no: int)`                        | Code 01: add a new user, with a fatal error if the name already exists.                |
| `TransactionMixin._tx_delete_user(self, line: str, line_no: int)`                        | Code 02: delete a user and their listings and games, fatal if missing.                 |
| `TransactionMixin._tx_set_credit(self, line: str, line_no: int)`                         | Code 06: set a user's credit, with a fatal error if the user is missing.               |
| `TransactionMixin._tx_list_game(self, line: str, line_no: int)`                          | Code 03: add a game to availableGames, fatal if the name is already listed.            |
| `TransactionMixin._tx_buy_game(self, line: str, line_no: int)`                           | Code 04: move credit from buyer to seller and give the buyer the game.                 |
| `TransactionMixin._tx_refund(self, line: str, line_no: int)`                             | Code 05: move credit from seller to buyer, fatal if the seller goes negative.          |
| `TransactionMixin._tx_remove_refunded_game(self, buyer: str, seller: str, line_no: int)` | Remove the refunded game from the buyer when exactly one game matches.                 |
| `_text(raw: str)`                                                                        | Strip padding characters from a text field.                                            |
| `_cents(raw: str, label: str, line_no: int)`                                             | Convert a zero-padded digit field to an integer number of cents.                       |
| `_split(line: str, widths: list, line_no: int)`                                          | Cut a line into fixed-width fields, checking its length and separators.                |
