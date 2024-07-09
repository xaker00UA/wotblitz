class Not_Found_Player(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __repr__(self):
        if self.message:
            return f"Not_Found_Player, {self.message}"
        else:
            return "Not_Found_Player has been raised"

    def __str__(self):
        if self.message:
            return f"{self.message}"
        else:
            return "Player not found"


class ConnectionError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
            self.code = args[1]
        else:
            self.message = None

    def __str__(self):
        if self.code:
            return f"ConnectionError, {self.message}, result: {self.code}"
        if self.message:
            return f"ConnectionError, {self.message}"
        else:
            return "ConnectionError has been raised"
