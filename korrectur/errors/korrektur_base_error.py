class KorrekturBaseException(Exception):

    def __init__(self, msg: str, *args: object) -> None:
        super().__init__(*args)
        self.message = msg

