class Tank:
    def __init__(self,player_id, tank_id, health, sp, spawn_position ):
        # Basic vehicle attributes
        self.tank_id = tank_id
        self.player_id = player_id
        self.vehicle_type = vehicle_type
        self.health = health
        self.spawn_position = spawn_position
        self.position = spawn_position  # Trenutna pozicija se inicijalizuje na početnu
        self.capture_points = 0
        self.shoot_range_bonus = 0
        self.destruction_points = 0  # Poeni za destrukciju
        self.sp = sp


    @staticmethod
    def add_tanks_to_player(current_player, tank_state):
        if not current_player.tanks:
            current_player.add_tanks(tank_state)

    def move(self,new_position):
        """Move the vehicle to the target location."""

        self.position = new_position
        print(f"Vehicle {self.vehicle_id} moving to target: {self.position}")

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

    def destroy(self):
        pass

    def __str__(self):
        """Returns the vehicle information as a string."""
        return f"Vehicle ID: {self.vehicle_id}, HP: {self.hp}, SP: {self.sp}, Destruction Points: {self.destruction_points}"