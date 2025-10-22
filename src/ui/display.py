from textual.widget import Widget
from rich.text import Text
from rich.panel import Panel

class GameDisplay(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game_text = Text("Loading...")
    def render(self):
        return Panel(self.game_text, border_style="cyan", title="The Labyrinth")
    def update_display(self, text: Text):
        self.game_text = text
        self.refresh()
    def render_game(self, game_state):
        player = game_state.player
        dungeon = game_state.dungeon
        view_width = 60
        view_height = 20
        start_x = max(0, player.x - view_width // 2)
        end_x = min(dungeon.width, start_x + view_width)
        start_y = max(0, player.y - view_height // 2)
        end_y = min(dungeon.height, start_y + view_height)
        game_text = Text()
        game_text.append(f"═══ Floor {game_state.current_floor} ", style="bold cyan")
        if dungeon.is_final_floor:
            game_text.append("THE CHAMBER OF MIRRORS ", style="bold red blink")
        game_text.append("═══\n\n", style="bold cyan")
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if not player.can_see(x, y):
                    game_text.append(" ", style="dim")
                    continue
                if x == player.x and y == player.y:
                    game_text.append("@", style="bold yellow")
                    continue
                enemy = dungeon.get_enemy_at(x, y)
                if enemy and enemy.alive:
                    if hasattr(enemy, 'visible') and not enemy.visible:
                        game_text.append(dungeon.get_tile(x, y), style="dim")
                    else:
                        style = f"bold {enemy.color}"
                        game_text.append(enemy.symbol, style=style)
                    continue
                feature = dungeon.get_feature_at(x, y)
                if feature and not feature.used:
                    if feature.feature_type == "chest":
                        game_text.append("□", style="bold yellow")
                    elif feature.feature_type == "altar":
                        game_text.append("†", style="bold cyan")
                    elif feature.feature_type == "fountain":
                        game_text.append("∩", style="bold blue")
                    continue
                if (x, y) == dungeon.exit_pos:
                    game_text.append(">", style="bold green blink")
                    continue
                trap = dungeon.get_trap_at(x, y)
                if trap and trap.visible:
                    game_text.append(trap.symbol, style="bold red")
                    continue
                tile = dungeon.get_tile(x, y)
                if tile == "#":
                    game_text.append("█", style="dim white")
                elif tile == ".":
                    room = dungeon.get_room_at(x, y)
                    if room and room.is_echo_zone:
                        game_text.append("·", style="magenta")
                    else:
                        game_text.append("·", style="dim")
                elif tile == "+":
                    game_text.append("+", style="bold yellow")
                elif tile == "'":
                    game_text.append("'", style="dim cyan")
                else:
                    game_text.append(tile, style="dim")
            game_text.append("\n")
        if player.sanity < 30:
            game_text.append("\n", style="")
            game_text.append("Your vision blurs... reality shifts...\n", 
                           style="italic red blink")
        game_text.append("\n")
        game_text.append("Legend: ", style="bold")
        game_text.append("@ ", style="bold yellow")
        game_text.append("You  ")
        game_text.append("S ", style="bold magenta")
        game_text.append("Shade  ")
        game_text.append("W ", style="bold yellow")
        game_text.append("Warden  ")
        game_text.append("? ", style="bold cyan")
        game_text.append("Whisper\n")
        self.update_display(game_text)