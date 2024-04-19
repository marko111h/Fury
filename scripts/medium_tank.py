from scripts.tank import Tank

class MediumTank(Tank):
    def __init__(self, id, curr_position, spawn_position, capture_points, owner, prev_attacker, order_position):
        super().__init__(id, curr_position, spawn_position, capture_points, 2, 2, 1, 2, owner, prev_attacker, order_position)
