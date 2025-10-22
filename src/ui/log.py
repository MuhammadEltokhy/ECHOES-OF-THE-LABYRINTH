from textual.widget import Widget
from rich.text import Text
from rich.panel import Panel
from collections import deque

class GameLog(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.messages = deque(maxlen=10)
        self.color_map = {
            "info": "cyan",
            "success": "green",
            "warning": "yellow",
            "error": "red",
            "dim": "dim",
        }
    def render(self):
        log_text = Text()
        for msg, msg_type in self.messages:
            color = self.color_map.get(msg_type, "white")
            log_text.append(f"• {msg}\n", style=color)
        if not self.messages:
            log_text.append("...\n", style="dim")
        return Panel(log_text, border_style="yellow", title="Log")
    def add_message(self, message: str, msg_type: str = "info"):
        self.messages.append((message, msg_type))
        self.refresh()
    def clear(self):
        self.messages.clear()
        self.refresh()