from phase4_support import GameCollection, UserAccounts, AvailableGames, User, Game
from TransactionProcessor import TransactionMixin, FatalError

class Backend(TransactionMixin):


    def __init__(self):
        self.availableGames = AvailableGames()
        self.userAccounts = UserAccounts()
        self.gamesCollection = GameCollection()

    def applyMDTF(self):
        self.readAG("games.txt")
        self.readUA("users.txt")
        self.readAG("accounts.txt")
        self.readMDTF("transactions.txt")
        



    def parse_lineAG(self,line):
        """Parse one fixed-width record: 26-char game, 15-char seller, 6-digit price."""
        line = line.rstrip("\r\n")
        if len(line) != 49 or line[26] != " " or line[42] != " ":
            raise ValueError(f"ERROR: Bad format: {line!r}")

        game = line[0:26].rstrip("_")       # strip the right-padding zeros
        seller = line[27:42].rstrip("_")
        price = int(line[43:49])/100       # last 2 digits are cents

        return Game(game, seller, price)


    def readAG(self,filename):
        records = []
        with open(filename, "r") as f:
            for line_num, line in enumerate(f, start=1):
                if not line.strip():        # skip blank lines
                    continue
                if line.strip() == "END":
                    break
                try:
                    records.append(self.parse_lineAG(line))
                except ValueError as e:
                    print(f"ERROR: Line {line_num}: {e}")
        self.availableGames.set_games(records)

    # Layout: UUUUUUUUUUUUUUU_TT_CCCCCCCCC
    #         0-14 name | 15 "_" | 16-17 type | 18 "_" | 19-27 credit


    def parse_lineUA(self,line: str, line_no: int) -> dict:
        line = line.rstrip("\r\n")

        if len(line) != 28:
            raise ValueError(
                f"Line {line_no}: expected {28} characters, got {len(line)}"
            )
        if line[15] != "_" or line[18] != "_":
            raise ValueError(f"ERROR: Line {line_no}: missing '_' separators at positions 16 and 19")

        name = line[0:15].rstrip()          # removes space padding (left or right)
        account_type = line[16:18]
        credit_raw = line[19:28].rstrip()

        if not account_type.rstrip():
            raise ValueError(f"ERROR: Line {line_no}: account type is empty")
        if not credit_raw.isdigit():
            raise ValueError(f"ERROR: Line {line_no}: credit '{credit_raw}' is not numeric")

        # Last two digits are the cents
        credit = int(credit_raw)
        user = User(name,account_type,credit)

        return user


    def readUA(self,path: str):
        accounts = []
        with open(path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                if not line.strip():       # skip blank lines
                    continue
                if line.strip() == "END":
                    break
                accounts.append(self.parse_lineUA(line, line_no))
        self.userAccounts.set_users(accounts)

    def parse_line_gc(self,line: str, line_no: int) -> tuple[str, str]:
        line = line.rstrip("\r\n")


        if len(line) != 42:
            raise ValueError(
                f"ERROR: Line {line_no}: expected {42} characters, got {len(line)}"
            )
        if line[26] != "_":
            raise ValueError(f"ERROR: Line {line_no}: missing '_' separator at position {26 + 1}")

        game_name = line[:26].rstrip()       # left justified, so padding is on the right
        owner = line[27:].rstrip()


        if not game_name:
            raise ValueError(f"ERROR: Line {line_no}: game name is empty")

        return game_name, owner


    def readGC(self,path: str):
        records = []
        found_end = False

        with open(path, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, start=1):
                if found_end:
                    raise ValueError(f"ERROR: Line {line_no}: data found after the END record")

                game_name, owner = self.parse_line_gc(line, line_no)

                if game_name == "END":
                    if owner:
                        raise ValueError(f"ERROR: Line {line_no}: END record must have an empty owner")
                    found_end = True
                    continue

                if not owner:
                    raise ValueError(f"ERROR: Line {line_no}: owner is empty")

                records.append((owner,game_name))

        if not found_end:
            raise ValueError("ERROR: File is missing the END record")

        self.gamesCollection.set_collection(records)
    


if __name__ == "__main__":
    dataD = Backend()
    dataD.readAG("games.txt")
    dataD.readUA("users.txt")
    dataD.readGC("accounts.txt")

    #ok = dataD.readMDTF("transactions.txt")   # prints "ERROR: ..." and returns False on a fatal error

    print(dataD.availableGames.get_games())
    print(dataD.userAccounts.get_users())
    print(dataD.gamesCollection.get_records())
