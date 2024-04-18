# from scripts.game_client import GameClient


class Tank:
    def __init__(self, id, curr_position, spawn_position, capture_points, speed_points, hit_points, fire_power,
                 destruction_points, owner, prev_attacker, order_position):
        self.id = id
        self.curr_position = curr_position
        self.spawn_position = spawn_position
        self.capture_points = capture_points
        self.speed_points = speed_points
        self.starting_hit_points = hit_points  # added this beacuse we will need it in respawning
        self.hit_points = hit_points
        self.fire_power = fire_power
        self.destruction_points = destruction_points
        self.owner = owner
        self.prev_attacker = prev_attacker
        self.order_position = order_position

    def get_id(self):
        return self.id

    def get_curr_position(self):
        return self.curr_position

    def get_spawn_position(self):
        return self.spawn_position

    def get_capture_points(self):
        return self.capture_points

    def get_speed_points(self):
        return self.speed_points

    def get_starting_hit_points(self):
        return self.starting_hit_points

    def get_hit_points(self):
        return self.hit_points

    def get_fire_power(self):
        return self.fire_power

    def get_destruction_points(self):
        return self.destruction_points

    def get_owner(self):
        return self.owner

    def get_prev_attacker(self):
        return self.prev_attacker

    def get_order_position(self):
        return self.order_position

    def add_destruction_points(self, value):
        self.destruction_points += value

    def shoot(self, target):
        target.take_damage(self)

    def move(self, new_position):
        self.curr_position = new_position

        # if new_position not in game_client.get_base():
        #     self.capture_points = 0

    # def earn_capture_point(self, game_client: GameClient):
    #     if self.curr_position in game_client.get_base():
    #         self.capture_points += 1

    def take_damage(self, shooter):
        self.hit_points -= 1
        self.prev_attacker = shooter

        if self.hit_points == 0:
            self.capture_points = 0
            self.curr_position = self.spawn_position
            self.hit_points = self.starting_hit_points
            shooter.add_destruction_points(self.hit_points)
