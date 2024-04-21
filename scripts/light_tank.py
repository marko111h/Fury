from scripts.tank import Tank

class LightTank(Tank):
    def __init__(self, id, curr_position, spawn_position, capture_points, owner, prev_attacker, order_position):
        hp = 1
        sp = 3
        damage_p = 1
        destruction_p = 1

        super().__init__(id, curr_position, spawn_position, capture_points, sp, hp, damage_p, destruction_p, owner, prev_attacker, order_position)
