import json
import random
from rich.text import Text
from entity.player import Player, Item
from map.dungeon import Dungeon

class GameState:
    def __init__(self, seed=None):
        if seed is None:
            seed = random.randint(0, 999999)
        self.seed = seed
        self.current_floor = 1
        self.turn_count = 0
        self.enemies_killed = 0
        self.player = Player()
        self.dungeon = Dungeon(self.current_floor, self.seed)
        if self.dungeon.start_pos:
            self.player.x, self.player.y = self.dungeon.start_pos
        self.in_combat = False
        self.combat_enemy = None
        self.death_cause = ""
        self.true_ending = False
        self.final_puzzle_active = False
        self.puzzle_attempts = 0
        self.narrative_clues = []
    def process_action(self, action: str, log):
        if not self.player.alive:
            return "game_over"
        if self.in_combat and self.combat_enemy:
            return self.process_combat(action, log)
        if self.final_puzzle_active:
            return self.process_final_puzzle(action, log)
        if action in ["up", "down", "left", "right"]:
            result = self.process_movement(action, log)
            if result:
                return result
        elif action == "wait":
            log.add_message("You wait and listen...", "dim")
        self.process_turn(log)
        if (self.player.x, self.player.y) == self.dungeon.exit_pos:
            if self.dungeon.is_final_floor:
                return self.trigger_final_puzzle(log)
            else:
                return "floor_complete"
        return "continue"
    def process_movement(self, direction: str, log):
        new_x, new_y = self.player.move(direction)
        if not self.dungeon.is_walkable(new_x, new_y):
            enemy = self.dungeon.get_enemy_at(new_x, new_y)
            if enemy:
                log.add_message(f"You attack the {enemy.name}!", "warning")
                self.initiate_combat(enemy, log)
                return None
            log.add_message("You can't move there.", "warning")
            return None
        self.player.update_position(new_x, new_y, direction)
        trap = self.dungeon.get_trap_at(new_x, new_y)
        if trap and not trap.triggered:
            trap.trigger(self.player, log)
            if not self.player.alive:
                self.death_cause = "You were killed by a trap."
                return "game_over"
        feature = self.dungeon.get_feature_at(new_x, new_y)
        if feature and not feature.used:
            feature.interact(self.player, log)
        room = self.dungeon.get_room_at(new_x, new_y)
        if room:
            if not room.visited:
                room.visited = True
                if room.is_echo_zone:
                    log.add_message("This room feels... familiar. Wrong.", "error")
                    self.player.lose_sanity(5)
                    self.narrative_clues.append("echo_zone")
        return None
    def process_turn(self, log):
        self.turn_count += 1
        sanity_loss = 1 + (self.current_floor // 2)
        self.player.lose_sanity(sanity_loss)
        self.player.restore_stamina(5)
        for enemy in self.dungeon.enemies:
            if enemy.alive:
                result = enemy.act(self.player, self.dungeon, log)
                if result == "combat":
                    self.initiate_combat(enemy, log)
        if self.player.sanity <= 0:
            self.death_cause = "The Labyrinth absorbed your mind."
            self.player.alive = False
            return "game_over"
        if self.player.sanity < 20:
            if random.random() < 0.3:
                hallucinations = [
                    "The walls breathe in and out.",
                    "You see yourself in the corner, watching.",
                    "Whispers echo: 'Turn back... turn back...'",
                    "The floor ripples like water.",
                    "Your shadow moves independently.",
                ]
                log.add_message(random.choice(hallucinations), "error")
    def initiate_combat(self, enemy, log):
        self.in_combat = True
        self.combat_enemy = enemy
        log.add_message(f"Combat begins with {enemy.name}!", "warning")
        self.narrative_clues.append(f"fought_{enemy.name.lower()}")
    def process_combat(self, action: str, log):
        if not self.combat_enemy or not self.combat_enemy.alive:
            self.in_combat = False
            self.combat_enemy = None
            return "continue"
        enemy = self.combat_enemy
        if action in ["up", "down", "left", "right", "wait"]:
            player_damage = self.player.attack + random.randint(-2, 3)
            actual_damage = enemy.take_damage(player_damage)
            log.add_message(f"You hit {enemy.name} for {actual_damage} damage!", "success")
            if not enemy.alive:
                log.add_message(f"{enemy.name} defeated!", "success")
                self.enemies_killed += 1
                self.in_combat = False
                self.combat_enemy = None
                self.dungeon.remove_dead_enemies()
                if enemy.name == "Shade":
                    log.add_message("You feel a part of yourself fade...", "error")
                    self.player.lose_sanity(10)
                return "continue"
        enemy_damage = enemy.calculate_damage()
        actual_damage = self.player.take_damage(enemy_damage)
        log.add_message(f"{enemy.name} hits you for {actual_damage} damage!", "error")
        if not self.player.alive:
            self.death_cause = f"You were slain by a {enemy.name}."
            return "game_over"
        return "continue"
    def trigger_final_puzzle(self, log):
        self.final_puzzle_active = True
        log.add_message("You enter the Chamber of Mirrors.", "warning")
        log.add_message("Multiple reflections surround you.", "warning")
        log.add_message("Which one is real?", "error")
        if self.player.sanity < 30:
            log.add_message("Your mind is too fractured to see clearly...", "error")
            return self.show_fake_ending(log)
        return self.show_riddle(log)
    def show_riddle(self, log):
        log.add_message("", "info")
        log.add_message("A voice echoes:", "warning")
        log.add_message("'The first shadow was your own,", "dim")
        log.add_message("The second was fear,", "dim")
        log.add_message("The third remains unseen.'", "dim")
        log.add_message("", "info")
        log.add_message("Do you step through the exit? [Y/N]", "warning")
        if "echo_zone" in self.narrative_clues and len(self.narrative_clues) >= 3:
            log.add_message("Something tells you this isn't right...", "warning")
            log.add_message("The real exit is behind you.", "success")
            self.true_ending = True
            return "victory"
        else:
            log.add_message("You step through...", "dim")
            return "victory"
    def show_fake_ending(self, log):
        log.add_message("The exit shimmers before you.", "warning")
        log.add_message("Freedom... finally...", "dim")
        log.add_message("You step through...", "dim")
        log.add_message("", "info")
        log.add_message("But you're still here.", "error")
        log.add_message("You've always been here.", "error")
        log.add_message("You always will be.", "error")
        self.death_cause = "You became an Echo, forever trapped."
        self.player.alive = False
        return "game_over"
    def process_final_puzzle(self, action: str, log):
        return "victory"
    def next_floor(self):
        self.current_floor += 1
        self.dungeon = Dungeon(self.current_floor, self.seed)
        if self.dungeon.start_pos:
            self.player.x, self.player.y = self.dungeon.start_pos
        self.player.heal(20)
        self.player.restore_stamina(50)
    def get_stats_text(self):
        text = Text()
        text.append("═══ STATS ═══\n\n", style="bold cyan")
        hp_percent = self.player.hp / self.player.max_hp
        hp_color = "green" if hp_percent > 0.5 else "yellow" if hp_percent > 0.25 else "red"
        hp_bar = "█" * int(hp_percent * 20)
        hp_empty = "░" * (20 - len(hp_bar))
        text.append(f"HP:  ", style="bold")
        text.append(f"{hp_bar}", style=hp_color)
        text.append(f"{hp_empty}", style="dim")
        text.append(f" {self.player.hp}/{self.player.max_hp}\n", style="dim")
        sanity_percent = self.player.sanity / self.player.max_sanity
        sanity_color = "cyan" if sanity_percent > 0.5 else "yellow" if sanity_percent > 0.25 else "red"
        sanity_bar = "█" * int(sanity_percent * 20)
        sanity_empty = "░" * (20 - len(sanity_bar))
        text.append(f"SAN: ", style="bold")
        text.append(f"{sanity_bar}", style=sanity_color)
        text.append(f"{sanity_empty}", style="dim")
        text.append(f" {self.player.sanity}/{self.player.max_sanity}\n\n", style="dim")
        text.append(f"Attack:  {self.player.attack}\n", style="dim")
        text.append(f"Defense: {self.player.defense}\n", style="dim")
        text.append(f"Stamina: {self.player.stamina}/{self.player.max_stamina}\n\n", style="dim")
        text.append(f"Floor:   {self.current_floor}/5\n", style="yellow")
        text.append(f"Turns:   {self.turn_count}\n", style="dim")
        text.append(f"Kills:   {self.enemies_killed}\n", style="dim")
        return text
    def get_inventory_text(self):
        text = Text()
        text.append("═══ INVENTORY ═══\n\n", style="bold green")
        if not self.player.inventory.items:
            text.append("Empty\n", style="dim")
        else:
            for item in self.player.inventory.items:
                eq = " [E]" if item.equipped else ""
                if item.item_type == "weapon":
                    text.append(f"⚔ {item.name}{eq}\n", style="red")
                elif item.item_type == "armor":
                    text.append(f"🛡 {item.name}{eq}\n", style="blue")
                elif item.item_type == "potion":
                    text.append(f"⚗ {item.name}\n", style="green")
                elif item.item_type == "key":
                    text.append(f"🔑 {item.name}\n", style="yellow")
        text.append(f"\n({len(self.player.inventory.items)}/{self.player.inventory.max_size})\n", 
                   style="dim")
        return text
    def save_to_file(self, filename: str):
        save_data = {
            "seed": self.seed,
            "current_floor": self.current_floor,
            "turn_count": self.turn_count,
            "enemies_killed": self.enemies_killed,
            "player": {
                "x": self.player.x,
                "y": self.player.y,
                "hp": self.player.hp,
                "stamina": self.player.stamina,
                "sanity": self.player.sanity,
                "base_attack": self.player.base_attack,
                "base_defense": self.player.base_defense,
            },
            "narrative_clues": self.narrative_clues,
        }
        try:
            with open(filename, 'w') as f:
                json.dump(save_data, f, indent=2)
        except Exception as e:
            print(f"Save failed: {e}")
    @classmethod
    def load_from_file(cls, filename: str):
        """Load game state from JSON file."""
        with open(filename, 'r') as f:
            save_data = json.load(f)
        game_state = cls(seed=save_data["seed"])
        game_state.current_floor = save_data["current_floor"]
        game_state.turn_count = save_data["turn_count"]
        game_state.enemies_killed = save_data["enemies_killed"]
        game_state.narrative_clues = save_data.get("narrative_clues", [])
        player_data = save_data["player"]
        game_state.player.x = player_data["x"]
        game_state.player.y = player_data["y"]
        game_state.player.hp = player_data["hp"]
        game_state.player.stamina = player_data["stamina"]
        game_state.player.sanity = player_data["sanity"]
        game_state.player.base_attack = player_data["base_attack"]
        game_state.player.base_defense = player_data["base_defense"]
        game_state.dungeon = Dungeon(game_state.current_floor, game_state.seed)
        return game_state