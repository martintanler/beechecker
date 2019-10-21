class BeeKeeper:

    _token = None
    _email = None

    def __init__(self, email: str, token: str):
        self._email = email
        self._token = token

    def get_email(self):
        return self._email

    def get_token(self):
        return self._token
