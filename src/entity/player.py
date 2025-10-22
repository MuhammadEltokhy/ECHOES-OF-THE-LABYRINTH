import random
from typing import List, Tuple

class Item:
    def __init__(self, name, item_type, modifier=0):
        self.name = name
        self.item_type = item_type  
        self.modifier = modifier
        self.equipped = False
    def __repr__(self):
        eq = " [E]" if self.equipped else ""
        return f"{self.name}{eq}"
class Inventory:
    def __init__(self):
        self.items: List[Item] = []
        self.max_size = 10
        self.weapon = None
        self.armor = None
    def add_item(self, item: Item) -> bool:
        if len(self.items) < self.max_size:
            self.items.append(item)
            return True
        return False
    def remove_item(self, item: Item):
        if item in self.items:
            self.items.remove(item)
    def equip_weapon(self, weapon: Item):
        if weapon.item_type == "weapon":
            if self.weapon:
                self.weapon.equipped = False
            self.weapon = weapon
            weapon.equipped = True
    def equip_armor(self, armor: Item):
        if armor.item_type == "armor":
            if self.armor:
                self.armor.equipped = False
            self.armor = armor
            armor.equipped = True
    def use_potion(self, potion: Item, player):
        if potion.item_type == "potion":
            player.hp = min(player.max_hp, player.hp + potion.modifier)
            self.remove_item(potion)
            return True
        return False
    def has_key(self, key_name: str) -> bool:
        return any(item.item_type == "key" and item.name == key_name 
                  for item in self.items)
class Player:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.max_hp = 100
        self.hp = 100
        self.max_stamina = 100
        self.stamina = 100
        self.base_attack = 10
        self.base_defense = 5
        self.max_sanity = 100
        self.sanity = 100
        self.inventory = Inventory()
        self.move_history: List[Tuple[int, int, str]] = []
        self.max_history = 20
        self.alive = True
        self.vision_range = 5
    @property
    def attack(self):
        base = self.base_attack
        if self.inventory.weapon:
            base += self.inventory.weapon.modifier
        return base
    @property
    def defense(self):
        base = self.base_defense
        if self.inventory.armor:
            base += self.inventory.armor.modifier
        return base
    def move(self, direction: str) -> Tuple[int, int]:
        new_x, new_y = self.x, self.y
        if direction == "up":
            new_y -= 1
        elif direction == "down":
            new_y += 1
        elif direction == "left":
            new_x -= 1
        elif direction == "right":
            new_x += 1
        return new_x, new_y
    def update_position(self, new_x: int, new_y: int, action: str):
        self.move_history.append((self.x, self.y, action))
        if len(self.move_history) > self.max_history:
            self.move_history.pop(0)
        self.x = new_x
        self.y = new_y
    def take_damage(self, damage: int) -> int:
        actual_damage = max(1, damage - self.defense)
        self.hp -= actual_damage
        if self.hp <= 0:
            self.hp = 0
            self.alive = False
        return actual_damage
    def heal(self, amount: int):
        self.hp = min(self.max_hp, self.hp + amount)
    def lose_sanity(self, amount: int):
        self.sanity = max(0, self.sanity - amount)
    def restore_sanity(self, amount: int):
        self.sanity = min(self.max_sanity, self.sanity + amount)
    def use_stamina(self, amount: int) -> bool:
        if self.stamina >= amount:
            self.stamina -= amount
            return True
        return False
    def restore_stamina(self, amount: int):
        self.stamina = min(self.max_stamina, self.stamina + amount)
    def can_see(self, x: int, y: int) -> bool:
        distance = abs(self.x - x) + abs(self.y - y)
        return distance <= self.vision_range
    def get_echo_position(self, turns_behind: int) -> Tuple[int, int]:
        if turns_behind >= len(self.move_history):
            return None
        idx = -(turns_behind + 1)
        return self.move_history[idx][0], self.move_history[idx][1]
    def __repr__(self):
        return f"Player(HP:{self.hp}/{self.max_hp}, Sanity:{self.sanity}, Pos:{self.x},{self.y})"