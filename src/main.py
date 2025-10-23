# main.py
import sys
from entity.player import Player
from entity.enemies import Shade, Warden, Whisper
from map.dungeon import Dungeon
from map.room import Room
from ui.display import GameDisplay
from ui.log import GameLog
from data.gameplay import GameState
from data.mode import choose_game_mode
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Header, Footer
from textual.binding import Binding
from textual import events
from rich.text import Text
from rich.panel import Panel
import random
import json
import os
from datetime import datetime

class EchoesGame(App):
    CSS = """
    Screen{
        background: $surface;
    }
    #game_container{
        height: 100%;
        width: 100%;
    }
    #main_view{
        width: 3fr;
        height: 100%;
        border: solid $primary;
    }
    #sidebar{
        width: 1fr;
        height: 100%;
        border: solid $accent;
    }
    #stats_panel{
        height: 40%;
        border: solid $secondary;
        padding: 1;
    }
    #log_panel{
        height: 30%;
        border: solid $warning;
        padding: 1;
    }
    #inventory_panel{
        height: 30%;
        border: solid $success;
        padding: 1;
    }
    .game_display{
        width: 100%;
        height: 100%;
        padding: 1;
    }
    """
    BINDINGS = [
        Binding("w,up", "move_up", "Move Up", show=False),
        Binding("s,down", "move_down", "Move Down", show=False),
        Binding("a,left", "move_left", "Move Left", show=False),
        Binding("d,right", "move_right", "Move Right", show=False),
        Binding("space", "wait", "Wait", show=False),
        Binding("i", "inventory", "Inventory", show=True),
        Binding("m", "map", "Map", show=True),
        Binding("q", "quit_game", "Quit", show=True),
        Binding("n", "new_game", "New Game", show=True),
        Binding("l", "load_game", "Load", show=True),
    ]
    def __init__(self):
        super().__init__()
        self.game_state = None
        self.in_menu = True
        self.game_over = False
        self.victory = False
    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="game_container"):
            with Horizontal():
                with Vertical(id="main_view"):
                    yield GameDisplay(id="game_display")
                with Vertical(id="sidebar"):
                    yield Static("", id="stats_panel")
                    yield GameLog(id="log_panel")
                    yield Static("", id="inventory_panel")
        yield Footer()
    def on_mount(self) -> None:
        self.title = "Echoes of the Labyrinth"
        self.show_menu()
    def show_menu(self):
        self.in_menu = True
        menu_text = Text()
        menu_text.append("╔══════════════════════════════════════╗\n", style="bold red")
        menu_text.append("║   ECHOES OF THE LABYRINTH           ║\n", style="bold red")
        menu_text.append("╚══════════════════════════════════════╝\n", style="bold red")
        menu_text.append("\n")
        menu_text.append("You awaken in darkness...\n", style="italic dim")
        menu_text.append("The walls breathe. The floor shifts.\n", style="italic dim")
        menu_text.append("Your shadow moves on its own.\n\n", style="italic dim red")
        menu_text.append("[N] New Game\n", style="bold green")
        menu_text.append("[L] Load Game\n", style="bold cyan")
        menu_text.append("[Q] Quit\n\n", style="bold yellow")
        menu_text.append("Controls: WASD/Arrows=Move | Space=Wait\n", style="dim")
        menu_text.append("          I=Inventory | M=Map | Q=Quit\n", style="dim")
        display = self.query_one("#game_display", GameDisplay)
        display.update_display(menu_text)
        log = self.query_one("#log_panel", GameLog)
        log.clear()
        log.add_message("Welcome to the Labyrinth...", "warning")
    def action_new_game(self):
        if self.in_menu or self.game_over:
            self.start_new_game()
    def action_load_game(self):
        if self.in_menu or self.game_over:
            if self.load_game():
                log = self.query_one("#log_panel", GameLog)
                log.add_message("Game loaded successfully.", "success")
            else:
                log = self.query_one("#log_panel", GameLog)
                log.add_message("No save file found.", "error")
    def start_new_game(self):
        self.in_menu = False
        self.game_over = False
        self.victory = False
        # Choose game mode before creating the game state
        game_mode = choose_game_mode()
        start_floor = game_mode.get_start_floor()
        seed = random.randint(0, 999999) 
        self.game_state = GameState(seed, start_floor=start_floor, mode=game_mode)
        log = self.query_one("#log_panel", GameLog)
        log.clear()
        log.add_message("You awaken in the depths...", "warning")
        log.add_message(f"Seed: {seed}", "dim")
        log.add_message(f"Start: {self.game_state.dungeon.start_pos} Exit: {self.game_state.dungeon.exit_pos}  Enemies: {len(self.game_state.dungeon.enemies)}", "dim")
        self.update_display()
        

    def update_display(self):
        if not self.game_state or self.in_menu:
            return
        display = self.query_one("#game_display", GameDisplay)
        display.render_game(self.game_state)
        stats_panel = self.query_one("#stats_panel", Static)
        stats_text = self.game_state.get_stats_text()
        stats_panel.update(stats_text)
        inv_panel = self.query_one("#inventory_panel", Static)
        inv_text = self.game_state.get_inventory_text()
        inv_panel.update(inv_text)
    def action_move_up(self):
        if not self.in_menu and not self.game_over:
            self.process_turn("up")
    def action_move_down(self):
        if not self.in_menu and not self.game_over:
            self.process_turn("down")
    def action_move_left(self):
        if not self.in_menu and not self.game_over:
            self.process_turn("left")
    def action_move_right(self):
        if not self.in_menu and not self.game_over:
            self.process_turn("right")
    def action_wait(self):
        if not self.in_menu and not self.game_over:
            self.process_turn("wait")
    def process_turn(self, action):
        log = self.query_one("#log_panel", GameLog)
        result = self.game_state.process_action(action, log)
        if result == "game_over":
            self.game_over = True
            self.show_game_over()
        elif result == "victory":
            self.victory = True
            self.show_victory()
        elif result == "floor_complete":
            log.add_message("You descend deeper into the labyrinth...", "warning")
            self.game_state.next_floor()
            self.save_game()
        self.update_display()
    def show_game_over(self):
        display = self.query_one("#game_display", GameDisplay)
        death_text = Text()
        death_text.append("\n\n", style="bold red")
        death_text.append("═" * 40 + "\n", style="bold red")
        death_text.append("   THE LABYRINTH CLAIMS ANOTHER SOUL\n", style="bold red blink")
        death_text.append("═" * 40 + "\n", style="bold red")
        death_text.append("\n")
        cause = self.game_state.death_cause
        death_text.append(f"{cause}\n\n", style="italic red")
        death_text.append(f"Floor Reached: {self.game_state.current_floor}\n", style="dim")
        death_text.append(f"Turns Survived: {self.game_state.turn_count}\n", style="dim")
        death_text.append(f"Enemies Defeated: {self.game_state.enemies_killed}\n\n", style="dim")
        death_text.append("[N] Try Again\n", style="bold green")
        death_text.append("[Q] Quit\n", style="bold yellow")
        display.update_display(death_text)
    def show_victory(self):
        """Display victory screen."""
        display = self.query_one("#game_display", GameDisplay)
        victory_text = Text()
        victory_text.append("\n\n", style="bold green")
        victory_text.append("╔══════════════════════════════════════╗\n", style="bold green")
        victory_text.append("║         YOU HAVE ESCAPED!           ║\n", style="bold green blink")
        victory_text.append("╚══════════════════════════════════════╝\n", style="bold green")
        victory_text.append("\n")
        if self.game_state.true_ending:
            victory_text.append("You saw through the illusion.\n", style="italic cyan")
            victory_text.append("The real exit was behind you all along.\n", style="italic cyan")
            victory_text.append("Freedom... or is this another echo?\n\n", style="italic dim")
        else:
            victory_text.append("You step through the exit...\n", style="italic yellow")
            victory_text.append("But something feels wrong.\n", style="italic yellow")
            victory_text.append("Are you truly free?\n\n", style="italic red dim")
        victory_text.append(f"Floors Conquered: {self.game_state.current_floor}\n", style="dim")
        victory_text.append(f"Turns Taken: {self.game_state.turn_count}\n", style="dim")
        victory_text.append(f"Final Sanity: {self.game_state.player.sanity}\n\n", style="dim")
        victory_text.append("[N] New Game\n", style="bold green")
        victory_text.append("[Q] Quit\n", style="bold yellow")
        display.update_display(victory_text)
    def action_inventory(self):
        if not self.in_menu and not self.game_over:
            log = self.query_one("#log_panel", GameLog)
            log.add_message("Inventory management coming soon!", "info")
    def action_map(self):
        if not self.in_menu and not self.game_over:
            log = self.query_one("#log_panel", GameLog)
            log.add_message("Full map view coming soon!", "info")
    def action_quit_game(self):
        if not self.in_menu and not self.game_over:
            self.save_game()
        self.exit()
    def save_game(self):
        if self.game_state:
            self.game_state.save_to_file("save.json")
    def load_game(self):
        try:
            self.game_state = GameState.load_from_file("save.json")
            self.in_menu = False
            self.game_over = False
            self.update_display()
            return True
        except:
            return False
def main():
    app = EchoesGame()
    app.run()


if __name__ == "__main__":
    main()