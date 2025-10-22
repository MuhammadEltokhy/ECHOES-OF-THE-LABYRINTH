import random
from typing import List, Tuple
from map.room import Room
from entity.enemies import create_enemy

class Dungeon:
    def __init__(self, floor_level, seed=None):
        self.floor_level = floor_level
        self.seed = seed
        if seed:
            random.seed(seed + floor_level)
        self.width = 80
        self.height = 40
        self.rooms: List[Room] = []
        self.corridors: List[Tuple[int, int]] = []
        self.enemies = []
        self.start_pos = None
        self.exit_pos = None
        self.is_final_floor = (floor_level >= 5)
        self.generate()
    def generate(self):
        num_rooms = 6 + self.floor_level
        for i in range(num_rooms):
            width = random.randint(8, 15)
            height = random.randint(6, 12)
            placed = False
            for _ in range(50):
                x = random.randint(1, self.width - width - 2)
                y = random.randint(1, self.height - height - 2)
                new_room = Room(x, y, width, height)
                if not self.room_overlaps(new_room):
                    if i == 0:
                        room_type = "start"
                    elif i == num_rooms - 1:
                        room_type = "exit" if not self.is_final_floor else "boss"
                    else:
                        room_type = random.choice([
                            "normal", "normal", "normal",
                            "treasure", "trap", "echo"
                        ])
                    new_room.room_type = room_type
                    new_room.populate(self.floor_level)
                    self.rooms.append(new_room)
                    placed = True
                    break
            if not placed and len(self.rooms) > 3:
                break
        self.connect_rooms()
        if self.rooms:
            self.start_pos = self.rooms[0].get_random_walkable_position()
            self.exit_pos = self.rooms[-1].get_random_walkable_position()
        self.spawn_enemies()
    def room_overlaps(self, new_room: Room) -> bool:
        for room in self.rooms:
            if (new_room.x < room.x + room.width + 1 and
                new_room.x + new_room.width + 1 > room.x and
                new_room.y < room.y + room.height + 1 and
                new_room.y + new_room.height + 1 > room.y):
                return True
        return False
    def connect_rooms(self):
        for i in range(len(self.rooms) - 1):
            room1 = self.rooms[i]
            room2 = self.rooms[i + 1]
            x1 = room1.x + room1.width // 2
            y1 = room1.y + room1.height // 2
            x2 = room2.x + room2.width // 2
            y2 = room2.y + room2.height // 2
            if random.random() < 0.5:
                self.create_h_corridor(x1, x2, y1)
                self.create_v_corridor(y1, y2, x2)
            else:
                self.create_v_corridor(y1, y2, x1)
                self.create_h_corridor(x1, x2, y2)
    def create_h_corridor(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.corridors.append((x, y))
    def create_v_corridor(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.corridors.append((x, y))
    def spawn_enemies(self):
        enemy_types = ["shade", "warden", "whisper"]
        enemies_per_room = 1 + (self.floor_level // 2)
        for room in self.rooms:
            if room.room_type in ["normal", "trap", "echo"]:
                num_enemies = random.randint(0, enemies_per_room)
                for _ in range(num_enemies):
                    enemy_type = random.choice(enemy_types)
                    pos = room.get_random_walkable_position()
                    enemy = create_enemy(enemy_type, pos[0], pos[1], self.floor_level)
                    self.enemies.append(enemy)
                    room.enemies.append(enemy)
            elif room.room_type == "treasure" and random.random() < 0.5:
                pos = room.get_random_walkable_position()
                mimic = create_enemy("mimic", pos[0], pos[1], self.floor_level)
                self.enemies.append(mimic)
                room.enemies.append(mimic)
    def get_tile(self, x, y):
        for room in self.rooms:
            if (room.x <= x < room.x + room.width and
                room.y <= y < room.y + room.height):
                local_x = x - room.x
                local_y = y - room.y
                return room.get_tile(local_x, local_y)
        if (x, y) in self.corridors:
            return "."
        return "#"
    def is_walkable(self, x, y):
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        for enemy in self.enemies:
            if enemy.alive and enemy.x == x and enemy.y == y:
                return False
        tile = self.get_tile(x, y)
        return tile in [".", "'", " ", ">"]
    def get_room_at(self, x, y):
        for room in self.rooms:
            if (room.x <= x < room.x + room.width and
                room.y <= y < room.y + room.height):
                return room
        return None
    def get_trap_at(self, x, y):
        room = self.get_room_at(x, y)
        if room:
            for trap in room.traps:
                if trap.x == x and trap.y == y:
                    return trap
        return None
    def get_feature_at(self, x, y):
        room = self.get_room_at(x, y)
        if room:
            for feature in room.features:
                if feature.x == x and feature.y == y:
                    return feature
        return None
    def get_enemy_at(self, x, y):
        for enemy in self.enemies:
            if enemy.alive and enemy.x == x and enemy.y == y:
                return enemy
        return None
    def remove_dead_enemies(self):
        self.enemies = [e for e in self.enemies if e.alive]
        for room in self.rooms:
            room.enemies = [e for e in room.enemies if e.alive]
    def __repr__(self):
        return f"Dungeon(Floor:{self.floor_level}, Rooms:{len(self.rooms)}, Enemies:{len(self.enemies)})"