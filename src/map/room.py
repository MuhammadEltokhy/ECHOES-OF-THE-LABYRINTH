import random
from typing import List, Tuple, Optional
from entity.player import Item

class Trap:
    def __init__(self, x, y, trap_type):
        self.x = x
        self.y = y
        self.trap_type = trap_type  
        self.triggered = False
        self.visible = False
        self.symbol = "."
    def trigger(self, player, log):
        if self.triggered:
            return
        self.triggered = True
        self.visible = True
        if self.trap_type == "spike":
            damage = random.randint(15, 25)
            player.take_damage(damage)
            log.add_message(f"Spikes shoot from the floor! -{damage} HP", "error")
            self.symbol = "^"
        elif self.trap_type == "poison":
            damage = random.randint(5, 10)
            player.take_damage(damage)
            player.lose_sanity(5)
            log.add_message(f"Poison gas fills the air! -{damage} HP", "error")
            self.symbol = "~"
        elif self.trap_type == "collapse":
            damage = random.randint(20, 30)
            player.take_damage(damage)
            player.lose_sanity(10)
            log.add_message(f"The floor collapses beneath you! -{damage} HP", "error")
            self.symbol = "X"
        elif self.trap_type == "echo":
            player.lose_sanity(20)
            log.add_message("You see yourself standing there... watching you.", "error")
            self.symbol = "*"
class Door:
    def __init__(self, x, y, key_required=None):
        self.x = x
        self.y = y
        self.key_required = key_required
        self.locked = key_required is not None
        self.symbol = "+" if self.locked else "'"
    def unlock(self, player, log):
        if not self.locked:
            return True
        if player.inventory.has_key(self.key_required):
            self.locked = False
            self.symbol = "'"
            log.add_message(f"You unlock the door with the {self.key_required}.", "success")
            return True
        else:
            log.add_message(f"This door requires a {self.key_required}.", "warning")
            return False
class RoomFeature:
    def __init__(self, x, y, feature_type, data=None):
        self.x = x
        self.y = y
        self.feature_type = feature_type  
        self.data = data or {}
        self.used = False
    def interact(self, player, log):
        if self.used:
            return
        if self.feature_type == "chest":
            self.used = True
            loot_type = random.choice(["weapon", "armor", "potion", "key"])
            if loot_type == "weapon":
                weapon = Item(f"Blade +{random.randint(5, 15)}", "weapon", random.randint(5, 15))
                player.inventory.add_item(weapon)
                log.add_message(f"Found {weapon.name}!", "success")
            elif loot_type == "armor":
                armor = Item(f"Armor +{random.randint(3, 10)}", "armor", random.randint(3, 10))
                player.inventory.add_item(armor)
                log.add_message(f"Found {armor.name}!", "success")
            elif loot_type == "potion":
                potion = Item(f"Health Potion", "potion", random.randint(20, 40))
                player.inventory.add_item(potion)
                log.add_message(f"Found a Health Potion!", "success")
            elif loot_type == "key":
                key_name = random.choice(["Iron Key", "Silver Key", "Gold Key"])
                key = Item(key_name, "key", 0)
                player.inventory.add_item(key)
                log.add_message(f"Found a {key_name}!", "success")
        elif self.feature_type == "altar":
            self.used = True
            choice = random.choice(["heal", "sanity", "curse"])
            if choice == "heal":
                player.heal(30)
                log.add_message("The altar glows warmly. You feel restored.", "success")
            elif choice == "sanity":
                player.restore_sanity(20)
                log.add_message("Your mind clears at the altar.", "success")
            else:
                player.lose_sanity(15)
                log.add_message("The altar whispers dark secrets...", "error")
        elif self.feature_type == "fountain":
            self.used = True
            if random.random() < 0.5:
                player.heal(20)
                log.add_message("The water is refreshing.", "success")
            else:
                player.take_damage(10)
                log.add_message("The water burns like acid!", "error")
class Room:
    def __init__(self, x, y, width, height, room_type="normal"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.room_type = room_type 
        self.tiles = []
        self.traps: List[Trap] = []
        self.doors: List[Door] = []
        self.features: List[RoomFeature] = []
        self.enemies: List = []
        self.visited = False
        self.fully_explored = False
        self.is_echo_zone = False
        self.generate_tiles()
    def generate_tiles(self):
        self.tiles = []
        for dy in range(self.height):
            row = []
            for dx in range(self.width):
                if dx == 0 or dx == self.width - 1 or dy == 0 or dy == self.height - 1:
                    row.append("#")
                else:
                    row.append(".")
            self.tiles.append(row)
    def add_trap(self, local_x, local_y, trap_type):
        world_x = self.x + local_x
        world_y = self.y + local_y
        trap = Trap(world_x, world_y, trap_type)
        self.traps.append(trap)
    def add_door(self, local_x, local_y, key_required=None):
        world_x = self.x + local_x
        world_y = self.y + local_y
        door = Door(world_x, world_y, key_required)
        self.doors.append(door)
        if 0 <= local_y < len(self.tiles) and 0 <= local_x < len(self.tiles[0]):
            self.tiles[local_y][local_x] = door.symbol
    def add_feature(self, local_x, local_y, feature_type):
        world_x = self.x + local_x
        world_y = self.y + local_y
        feature = RoomFeature(world_x, world_y, feature_type)
        self.features.append(feature)
    def get_tile(self, local_x, local_y):
        if 0 <= local_y < len(self.tiles) and 0 <= local_x < len(self.tiles[0]):
            return self.tiles[local_y][local_x]
        return "#"
    def is_walkable(self, local_x, local_y):
        tile = self.get_tile(local_x, local_y)
        return tile in [".", "'", " "]
    def get_random_walkable_position(self):
        walkable = []
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.is_walkable(x, y):
                    walkable.append((self.x + x, self.y + y))
        if walkable:
            return random.choice(walkable)
        return (self.x + self.width // 2, self.y + self.height // 2)
    def populate(self, floor_level):
        if self.room_type == "trap":
            num_traps = random.randint(2, 5)
            trap_types = ["spike", "poison", "collapse"]
            for _ in range(num_traps):
                x = random.randint(2, self.width - 3)
                y = random.randint(2, self.height - 3)
                trap_type = random.choice(trap_types)
                self.add_trap(x, y, trap_type)
        elif self.room_type == "treasure":
            x = self.width // 2
            y = self.height // 2
            self.add_feature(x, y, "chest")
        elif self.room_type == "echo":
            self.is_echo_zone = True
            num_traps = random.randint(1, 3)
            for _ in range(num_traps):
                x = random.randint(2, self.width - 3)
                y = random.randint(2, self.height - 3)
                self.add_trap(x, y, "echo")
        elif self.room_type == "normal":
            if random.random() < 0.3:
                feature_type = random.choice(["altar", "fountain"])
                x = random.randint(2, self.width - 3)
                y = random.randint(2, self.height - 3)
                self.add_feature(x, y, feature_type)
            if random.random() < 0.4:
                x = random.randint(2, self.width - 3)
                y = random.randint(2, self.height - 3)
                trap_type = random.choice(["spike", "poison"])
                self.add_trap(x, y, trap_type)
    def __repr__(self):
        return f"Room({self.room_type}, {self.width}x{self.height})"