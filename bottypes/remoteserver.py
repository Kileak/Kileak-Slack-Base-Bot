class RemoteServer:

    def __init__(self, name, alias):
        self.name = name
        self.occupied = False
        self.occupiedBy = ""
        self.alias = alias

    def request(self, user):
        if not self.occupied:
            self.occupied = True
            self.occupiedBy = user

    def release(self):
        self.occupied = False
        self.occupiedBy = ""


    def setalias(self, alias):
        self.alias = alias

    def add_challenge(self, challenge):
        """
        Add a challenge object to the list of challenges belonging
        to this CTF.
        challenge : A challenge object
        """
        self.challenges.append(challenge)
