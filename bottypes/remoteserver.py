class RemoteServer:

    def __init__(self, name):
        self.name = name
        self.occupied = False
        self.occupiedBy = ""

    def request(self, user):
        if not self.occupied:
            self.occupied = True
            self.occupiedBy = user

    def release(self):
        self.occupied = False
        self.occupiedBy = ""

    def add_challenge(self, challenge):
        """
        Add a challenge object to the list of challenges belonging
        to this CTF.
        challenge : A challenge object
        """
        self.challenges.append(challenge)
