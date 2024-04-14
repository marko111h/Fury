class Player:
    def __init__(self,player_id, name):
        # Basic player attributes
        self.player_id = player_id
        self.name = name

        # Points for destroying vehicles and capturing bases
        self.destruction_points = 0
        self.base_capture_points = 0

        # Players vehicles
        self.vehicles = []

    def add_vehicle(self,vehicle):
        """Adds a vehicle to the player's ownership."""
        self.vehicles.append(vehicle)

    def remove_vehicle(self,vehicle):
        """Removes the vehicle from player ownership."""
        self.vehicles.remove(vehicle)

    def ern_destruction_points(self, points):
        """Increases destruction points."""
        self.destruction_points += points

    def lose_destruction_points(self, points):
        """Reduces destruction points."""
        self.destruction_points -= points

    def earn_base_capture_points(self,points):
        """Increases points for capturing the base."""
        self.base_capture_points += points

    def lose_base_capture_points(self, points):
        """Reduces points for capturing a base."""
        self.base_capture_points -= points

    def __str__(self):
        """Returns player information as a string."""
        return f"Player: {self.name}, ID: {self.player_id}, Destruction Points: {self.destruction_points}, Base Capture Points: {self.base_capture_points}"