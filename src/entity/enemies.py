import random
from typing import Tuple, List

class Enemy:
    def __init__(self, x, y, name, hp, attack, defense, symbol):
        self.x = x
        self.y = y
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.symbol = symbol
        self.alive = True
        self.color = "red"
    def take_damage(self, damage: int) -> int:
        actual_damage = max(1, damage - self.defense)
        self.hp -= actual_damage
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
        return actual_damage
    def calculate_damage(self) -> int:
        variance = random.randint(-2, 2)
        return max(1, self.attack + variance)
    def move_towards(self, target_x, target_y, dungeon):
        dx = target_x - self.x
        dy = target_y - self.y
        if abs(dx) > abs(dy):
            new_x = self.x + (1 if dx > 0 else -1)
            new_y = self.y
        else:
            new_x = self.x
            new_y = self.y + (1 if dy > 0 else -1)
        if dungeon.is_walkable(new_x, new_y):
            self.x = new_x
            self.y = new_y
            return True
        return False
    def act(self, player, dungeon, log):
        pass
    def __repr__(self):
        return f"{self.name}(HP:{self.hp}/{self.max_hp}, Pos:{self.x},{self.y})"
class Shade(Enemy):
    def __init__(self, x, y, floor_level=1):
        hp = 30 + (floor_level * 10)
        attack = 15 + (floor_level * 3)
        super().__init__(x, y, "Shade", hp, attack, 3, "S")
        self.color = "magenta"
        self.turns_behind = 5 
        self.description = "Your own shadow, hunting you"
    def act(self, player, dungeon, log):
        echo_pos = player.get_echo_position(self.turns_behind)
        if echo_pos:
            target_x, target_y = echo_pos
            if dungeon.is_walkable(target_x, target_y):
                self.x = target_x
                self.y = target_y
                if self.x == player.x and self.y == player.y:
                    log.add_message(f"The {self.name} catches you!", "error")
                    return "combat"
        else:
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            random.shuffle(directions)
            for dx, dy in directions:
                new_x, new_y = self.x + dx, self.y + dy
                if dungeon.is_walkable(new_x, new_y):
                    self.x = new_x
                    self.y = new_y
                    break
class Warden(Enemy):
    def __init__(self, x, y, floor_level=1):
        hp = 50 + (floor_level * 15)
        attack = 12 + (floor_level * 2)
        super().__init__(x, y, "Warden", hp, attack, 8, "W")
        self.color = "yellow"
        self.patrol_route = []
        self.patrol_index = 0
        self.description = "A guardian that never sleeps"
    def set_patrol_route(self, route: List[Tuple[int, int]]):
        self.patrol_route = route
        self.patrol_index = 0
    def act(self, player, dungeon, log):
        if not self.patrol_route:
            self.patrol_route = [
                (self.x, self.y),
                (self.x + 3, self.y),
                (self.x + 3, self.y + 3),
                (self.x, self.y + 3),
            ]
        if self.patrol_route:
            target_x, target_y = self.patrol_route[self.patrol_index]
            if self.x == target_x and self.y == target_y:
                self.patrol_index = (self.patrol_index + 1) % len(self.patrol_route)
            else:
                self.move_towards(target_x, target_y, dungeon)
        distance = abs(self.x - player.x) + abs(self.y - player.y)
        if distance == 1:
            log.add_message(f"The {self.name} spots you!", "warning")
            return "combat"
class Whisper(Enemy):
    def __init__(self, x, y, floor_level=1):
        hp = 25 + (floor_level * 8)
        attack = 20 + (floor_level * 4)
        super().__init__(x, y, "Whisper", hp, attack, 2, "?")
        self.color = "cyan"
        self.visible = False
        self.reveal_distance = 3
        self.description = "A presence you cannot see"
    
    def act(self, player, dungeon, log):
        distance = abs(self.x - player.x) + abs(self.y - player.y)
        if distance <= self.reveal_distance and not self.visible:
            self.visible = True
            self.symbol = "w"
            log.add_message("Something materializes from the shadows!", "error")
            player.lose_sanity(10)
        if self.visible and distance > 1:
            self.move_towards(player.x, player.y, dungeon)
        if self.x == player.x and self.y == player.y:
            return "combat"
class Mimic(Enemy):
    def __init__(self, x, y, floor_level=1):
        hp = 40 + (floor_level * 12)
        attack = 18 + (floor_level * 3)
        super().__init__(x, y, "Mimic", hp, attack, 5, "$")
        self.color = "yellow"
        self.revealed = False
        self.description = "Not what it seems"
    def act(self, player, dungeon, log):
        distance = abs(self.x - player.x) + abs(self.y - player.y)
        if distance <= 1 and not self.revealed:
            self.revealed = True
            self.symbol = "M"
            self.color = "red"
            log.add_message("The treasure chest snaps open with teeth!", "error")
            player.lose_sanity(15)
            return "combat"
        if self.revealed and distance == 1:
            return "combat"
def create_enemy(enemy_type: str, x: int, y: int, floor_level: int) -> Enemy:
    enemy_types = {
        "shade": Shade,
        "warden": Warden,
        "whisper": Whisper,
        "mimic": Mimic,
    }
    enemy_class = enemy_types.get(enemy_type, Shade)
    return enemy_class(x, y, floor_level)