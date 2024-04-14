class Vehicle:
    def __init__(self, vehicle_id, hp, sp, destruction_points):
        # Basic vehicle attributes
        self.vehicle_id = vehicle_id
        self.hp = hp # hit points
        self.sp = sp # speed points
        self.destruction_points = destruction_points # points for destory

    def move(self,target):
        """Move the vehicle to the target location."""
        pass
        print(f"Vehicle {self.vehicle_id} moving to target: {target}")

    def shoot(self, target):
        """Shooting on target."""
        pass
        print(f"Vehicle {self.vehicle_id} shooting at target: {target}")

    def take_damage (self, damage):
        """Reducing HP when the vehicle takes damage."""
        self.hp -= damage
        print(f"Vehicle {self.vehicle_id} took {damage} damage. Remaining HP: {self.hp}")

        if self.hp <= 0:
            print(f"Vehicle {self.vehicle_id} is destoryed")

    def __str__(self):
        """Returns the vehicle information as a string."""
        return f"Vehicle ID: {self.vehicle_id}, HP: {self.hp}, SP: {self.sp}, Destruction Points: {self.destruction_points}"