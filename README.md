# ECHOES-OF-THE-LABYRINTH
**A psychological horror roguelike where your past haunts you.**

---

## 📖 Story

You awaken in darkness. The walls breathe. The floor shifts beneath your feet. Your shadow moves on its own.

The **Labyrinth** is alive—a shifting dungeon that feeds on fear and memory. Shadow copies of yourself, **Echoes**, hunt you through the corridors, mimicking your every move from moments ago. The deeper you venture, the more your sanity fractures.

Can you reach the **Chamber of Mirrors** and escape... or will you become another Echo, trapped forever?

---

## 🎮 How to Play

### Installation
## Clone The Repo

```bash
# Install required dependencies
pip install textual rich

# Run the game
python main.py
```
## Download The Last Release

### Controls

| Key | Action |
|-----|--------|
| `W` / `↑` | Move Up |
| `S` / `↓` | Move Down |
| `A` / `←` | Move Left |
| `D` / `→` | Move Right |
| `SPACE` | Wait (skip turn) |
| `I` | Inventory *(planned)* |
| `M` | Full Map *(planned)* |
| `N` | New Game |
| `L` | Load Game |
| `Q` | Quit |

---

## ⚔️ Game Mechanics

### Player Stats

- **HP (Health Points)**: Your life force. Reaches 0 = death.
- **Stamina**: Used for special actions and combat. Regenerates slowly.
- **Sanity**: Your mental stability. Drains constantly. At 0, the Labyrinth consumes your mind.
- **Attack/Defense**: Combat effectiveness. Improved by equipment.

### Sanity System 🧠

Sanity is your most critical resource:

- Drains every turn (faster on deeper floors)
- Drops faster when you:
  - Encounter enemies
  - Trigger traps
  - Enter Echo Zones
  - Witness hallucinations

**Low Sanity Effects (<30):**
- Hallucinations (fake walls, false exits)
- Vision distortion
- In the final chamber: you see a false ending

---

## 👻 Enemies

### Shade (S)
*"Your own shadow, hunting you"*

- Follows your movement from 5 turns ago
- Low HP but high attack
- Killing one damages your sanity

### Warden (W)
*"A guardian that never sleeps"*

- Patrols fixed routes
- High defense, medium attack
- Alerts when player is adjacent

### Whisper (?)
*"A presence you cannot see"*

- Invisible until you get close
- Materializes suddenly, causing sanity loss
- Fast and deadly

### Mimic ($ → M)
*"Not what it seems"*

- Disguised as treasure
- Reveals itself when approached
- Ambush attack

---

## 🗺️ Room Types

| Type | Description |
|------|-------------|
| **Normal** | Standard rooms, may have minor traps/loot |
| **Treasure** | Contains chests (watch for Mimics!) |
| **Trap** | Filled with deadly traps |
| **Echo Zone** | Mirrors your movements—step wrong, you're trapped by your shadow |
| **Boss** | Final floor challenge |

### Traps

- **Spike Pits (^)**: High physical damage
- **Poison Gas (~)**: Damage + sanity loss
- **Collapse (X)**: Massive damage
- **Echo Traps (*)**: Pure sanity damage + confusion

---

## 📦 Items & Loot

### Weapons
- Increase Attack stat
- Found in chests or dropped by enemies
- Equip the best you find

### Armor
- Increases Defense stat
- Reduces incoming damage

### Potions
- **Health Potions**: Restore HP instantly
- Consume on use

### Keys
- Required to unlock special doors
- Come in different types (Iron, Silver, Gold)

### Special Features
- **Altars (†)**: May heal, restore sanity, or curse you
- **Fountains (∩)**: Risky—may heal or harm

---

## 🏆 Victory Conditions

You must reach **Floor 5: The Chamber of Mirrors**.

### The Final Puzzle

The Chamber shows multiple reflections of you. Only one is real.

A voice riddles:

> *"The first shadow was your own,*  
> *The second was fear,*  
> *The third remains unseen."*

### Endings

**🌫️ False Ending (Sanity < 30)**
- You see a fake exit
- Step through → trapped forever as an Echo

**🚪 Normal Ending (Sanity ≥ 30, not enough clues)**
- You escape, but something feels... wrong
- Did you really leave?

**✨ True Ending (Sanity ≥ 30 + found Echo Zone clues)**
- You realize the exit is a trap
- Turn back instead
- True freedom

---

## 💀 Death Causes

- Killed by enemies
- Trap damage
- Sanity reaches 0 → *"The Labyrinth absorbed your mind"*
- Caught by your own Shade

---

## 🎯 Strategy Tips

1. **Manage Sanity**: Your #1 priority. Avoid unnecessary combat.
2. **Watch Your Echo**: Shades follow your path. Don't corner yourself.
3. **Explore Carefully**: Traps are hidden until triggered.
4. **Combat is Risky**: Every fight costs time (and sanity drain continues).
5. **Equip Smart**: Better gear = easier fights = less time = more sanity.
6. **Pay Attention**: The narrative clues matter for the true ending.

---

## 🧩 Procedural Generation

Each playthrough is unique:

- **Seed-based generation**: Rooms, corridors, and enemy placement
- Floor layouts change between sessions
- Enemy difficulty scales with floor depth
- Save system preserves your seed

---

## 💾 Save System

- **Auto-save**: After completing each floor
- **Manual save**: Quit anytime (`Q` key)
- **Load**: Resume from the main menu (`L` key)

Save includes:
- Player stats, inventory, and position
- Current floor and turn count
- Narrative clues collected
- World seed (for consistent dungeon layout)

---

## 🎨 Legend

```
@   = You (the player)
█   = Wall
·   = Floor
S   = Shade (echo enemy)
W   = Warden (patrol enemy)
?   = Whisper (invisible enemy)
M   = Mimic (ambush enemy)
□   = Chest
†   = Altar
∩   = Fountain
>   = Exit (stairs down)
^   = Spike trap (visible)
~   = Poison trap (visible)
+   = Locked door
'   = Open door
```

---

## 🛠️ Technical Details

### Architecture

```
echoes-of-the-labyrinth/
├── main.py                 # Entry point, Textual app
├── entities/
│   ├── player.py          # Player class, inventory, stats
│   └── enemies.py         # Enemy AI (Shade, Warden, Whisper, Mimic)
├── map/
│   ├── dungeon.py         # Procedural generation, floor management
│   └── room.py            # Room types, traps, features
├── ui/
│   ├── game_display.py    # Main game rendering
│   └── log.py             # Message log system
├── data/
│   └── game_state.py      # Save/load, turn processing
└── README.md
```

### Dependencies

- **textual**: Modern TUI framework (better than curses)
- **rich**: Beautiful terminal rendering

---

## 🔮 Future Enhancements (Optional)

- [ ] Full inventory management UI
- [ ] Mini-map overlay
- [ ] More enemy types
- [ ] Boss fights with unique mechanics
- [ ] Achievement system
- [ ] Seed-based replay mode
- [ ] ASCII animations (flickering torches, breathing walls)
- [ ] Sound effects via terminal beeps

---

## 🎭 Atmosphere & Design

The game emphasizes **psychological horror**:

- Minimal UI clutter (fog of war)
- Constant dread (sanity drain)
- Environmental storytelling (room descriptions, log messages)
- Uncertainty (invisible enemies, hidden traps)
- Meta-horror (fighting your own echoes)

**This is not just a combat game—it's a mind game.**

---

## 🐛 Known Issues

- Inventory UI not fully interactive yet *(planned)*
- Full map overlay not implemented *(planned)*
- Final puzzle currently auto-resolves *(needs input system enhancement)*

---

## 📜 License

Created for educational and entertainment purposes.

---

## 👤 Credits

**Developed by**: Tokhy (Nice to meat u man)
**Framework**: [Textual](https://github.com/Textualize/textual) by Textualize  
**Inspired by**: My own mid-night imagines!

---

> *"In the Labyrinth, your greatest enemy is yourself."*

🌑 **Good luck, wanderer. You'll need it.**
