# H.E.R.O. Remake

## Helicopter Emergency Rescue Operation

A remake of the classic Atari 2600 game H.E.R.O., developed in Python with Pygame.

## Description

Control Roderick Hero, equipped with a personal helicopter, as you navigate dangerous underground mines to rescue trapped miners. Face enemies, destroy obstacles, and manage your energy to complete 5 progressively harder levels.

## Features

### Game Systems

- **5 Levels** loaded from an external file (`screens.json`), editable with the included editor
- **Dynamic level sizes** in multiples of the 8x16 tile viewport (e.g.: 16x24, 32x24, 48x32)
- **Two-axis scrolling** with a smooth camera that follows the player
- **Start Screen** with background image, theme music, and top 3 high scores
- **Persistent Scoring System** saved in JSON (top 10)
- **Game Over Screen** with name entry to register your score
- **Realistic Physics** with gravity, helicopter flight, and active descent
- **Energy System** that drains while flying and recovers while on the ground
- **Lives System** with an extra life every 20,000 points
- **Full Sound Effects** (shots, explosions, death, helicopter, footsteps, victory, splatter)
- **ColecoVision-style HUD** with 3D panels, life and bomb icons
- **Fullscreen** by default with aspect-ratio-preserving scaling (Alt+Enter to toggle)
- **Exit Confirmation** with Y/N dialog
- **Procedural Cave Background** with rock texture
- **Floating Scores** that appear when destroying enemies and blocks
- **Level Complete Animation** in 3 ColecoVision-style phases
- **SID Audio Emulation** (Commodore 64) available for sound effects
- **Level Editor** included (`editor.py`)

### Game Mechanics

#### Movement
- **Helicopter Flight**: Press up to fly (consumes energy)
- **Active Descent**: Press down to descend faster (inverted propeller)
- **Animated Walking**: When moving on the ground, with alternating footsteps and sound
- **Gravity**: The player falls when not flying
- **Energy Recovery**: Energy recovers automatically while on the ground

#### Combat
- **Laser Shot**: Destroys enemies and collides with walls/blocks
- **Dynamite**: Area explosions that destroy blocks, walls, and nearby enemies

#### Enemies
- **Bats** (V): Patrol horizontally, bounce off walls. Speed increases per level (+5%)
- **Spiders** (A): Move vertically from the ceiling, hanging from a thread. Descend up to 2 tiles and return

#### Visual Effects
- **Explosion Flash**: The screen flashes white/black during dynamite explosions
- **Explosion Animation**: Animated sprites (bomb1, bomb2, bomb3) for dynamite
- **Player Sprites**: Idle, flying, shooting, and walking (2 frames)
- **Spider Thread**: White line connecting the spider to the ceiling

### Objectives

1. **Find the Miner** (M) in each level
2. **Rescue the Miner** by touching them
3. **Complete all 5 Levels** to win the game

### Scoring System

| Action | Points |
|--------|--------|
| Destroy enemy with laser | 50 |
| Destroy enemy with dynamite | 75 |
| Destroy dirt (#) with dynamite | 20 |
| Destroy rocks (R) with dynamite | 10 |
| Rescue miner | 1,000 |
| Remaining energy bonus | 1:1 (drained in animation) |
| Remaining bombs bonus | 50 per bomb |

**Extra Life**: You get an additional life every 20,000 accumulated points.

## Controls

### Keyboard

| Key | Action |
|-----|--------|
| **Left/Right arrows** | Move left/right |
| **Up arrow** | Fly upward (consumes energy) |
| **Down arrow** | Fast descent (inverted propeller) |
| **SPACE** | Shoot laser |
| **Z** | Place dynamite |
| **ESC** | Return to menu (in game) / Exit (in menu, with confirmation) |
| **ALT+ENTER** | Toggle fullscreen/windowed |
| **ENTER** | Confirm name (on game over) |

### Xbox/Gamepad Controller

| Button/Stick | Action |
|-------------|--------|
| **Left Stick** | Move (gradual, with dead zone) |
| **A Button** | Start game (in menu) |
| **X Button** | Shoot laser |
| **B Button** | Place dynamite |

## Levels

Levels are loaded from `screens.json` and can be edited with `editor.py`.

### Dynamic Size

Levels can be any size in multiples of the **viewport** (8 rows x 16 columns = 256x512 px). The viewport is the visible portion of the level on screen. The camera follows the player with smooth scrolling on both axes.

Examples of valid sizes:
- **16x24** (1x3 viewports) — classic size, vertical scrolling only
- **32x24** (2x3 viewports) — double width, horizontal and vertical scrolling
- **48x32** (3x4 viewports) — large level in both dimensions

Dimensions are automatically inferred from the map in `screens.json` (no explicit width/height properties required).

### Level 1 - Tutorial: Dynamite Rescue
- Introductory level with destructible rocks (16x24)
- 2 bats and 1 spider
- Destructible rocks (R) and dirt (#), indestructible granite (G)
- Miner trapped in a lower section

### Level 2 - Enlarged Copy of Level 1
- Expanded version of level 1 (32x24, horizontal scrolling)
- Demonstrates dynamic-sized levels

### Level 3 - Narrow Maze
- Narrow passages with blocked sections (16x24)
- Complex navigation between sections
- Destructible blocks at key points

### Level 4 - Many Blocks
- Horizontal layers of destructible blocks (16x24)
- Requires intensive use of dynamite
- Spiders and bats between layers

### Level 5 - Wide Cavern
- Wide level with horizontal scrolling (32x24)
- Combination of narrow passages and blocks
- Multiple vertical sections

## Level Complete Animation

Upon rescuing the miner, a 3-phase animation plays:

1. **Energy Drain**: Remaining energy is converted to points 1:1, with ascending beeps
2. **Bomb Explosions**: Remaining bombs explode one by one in the HUD, adding 50 points each
3. **Victory Screen**: Dark overlay with "LEVEL COMPLETE!" and victory sound

## HUD (Heads-Up Display)

ColecoVision TMS9918A-style HUD with 3D gray side panels:

```
+--------+------------------------------------+--------+
| Gray   | POWER [================          ] | Gray   |
| panel  | [life][life][life]    [bomb][bomb]  | panel  |
|        | LEVEL: 1                     12500  |        |
+--------+------------------------------------+--------+
```

- **POWER**: Energy bar (yellow=full, red=empty)
- **Lives**: Miniature player icons
- **Bombs**: Bomb icons aligned to the right
- **LEVEL**: Current level number
- **Score**: Score aligned to the right

## Installation and Running

### Requirements

```
Python 3.8+
pygame 2.0+
numpy (optional, for SID emulation)
```

### Installation

```bash
# Install dependencies
pip install pygame numpy

# Run the game
python hero.py

# Run the level editor
python editor.py
```

### File Structure

```
hero/
├── hero.py                  # Main game (Game class, loop, render)
├── constants.py             # Game constants
├── player.py                # Player class (physics, animation, walking)
├── enemy.py                 # Enemy class (bats and spiders)
├── laser.py                 # Laser class (projectiles)
├── dynamite.py              # Dynamite class (explosives with animated sprites)
├── miner.py                 # Miner class (rescue objective)
├── audio_effects.py         # Commodore 64 SID emulation
├── editor.py                # Visual level editor
├── screens.json             # Level definitions (editable)
├── scores.json              # High scores (auto-generated)
├── CLAUDE.md                # Technical documentation for development
├── README.md                # This file
├── fonts/
│   └── PressStart2P-vaV7.ttf
├── images/
│   └── hero_background.png  # Start screen background
├── sprites/
│   ├── player.png           # Player idle sprite
│   ├── player_fly.png       # Flying sprite
│   ├── player_shooting.png  # Shooting sprite
│   ├── player_walk1.png     # Walk animation frame 1
│   ├── player_walk2.png     # Walk animation frame 2
│   ├── bat1.png             # Bat sprite frame 1
│   ├── bat2.png             # Bat sprite frame 2
│   ├── spider.png           # Spider sprite
│   ├── miner.png            # Miner sprite
│   ├── bomb1.png            # Bomb animation frame 1
│   ├── bomb2.png            # Bomb animation frame 2
│   └── bomb3.png            # Bomb animation frame 3
├── tiles/
│   ├── wall.png             # Dirt (#)
│   ├── floor.png            # Floor/platform (.)
│   ├── granite.png          # Indestructible granite (G)
│   ├── breakable_wall.png   # Destructible rocks (R)
│   ├── lamp.png             # Lamp (L)
│   └── blank.png            # Empty space
└── sounds/
    ├── shoot.wav            # Shooting effect
    ├── explosion.wav        # Explosion effect
    ├── death.wav            # Death effect
    ├── splatter.wav         # Enemy death effect
    ├── helicopter.wav       # Helicopter sound (loop)
    ├── walk1.wav            # Left footstep
    ├── walk2.wav            # Right footstep
    ├── win_screen.wav       # Level complete sound
    └── splash_screen_theme.wav  # Main menu music
```

The game generates procedural graphics as a fallback if images are not found.

## High Score System

### Persistence
- Scores are automatically saved to `scores.json`
- Top 10 scores are kept
- Top 3 are displayed on the start screen

## Map Legend

| Symbol | Meaning |
|--------|---------|
| `S` | Start - Player starting position |
| `#` | Dirt (solid, destructible with dynamite) |
| `.` | Floor/platform (solid, indestructible) |
| `G` | Granite (solid, indestructible) |
| `R` | Rocks (solid, destructible with dynamite) |
| `V` | Enemy - Bat (horizontal patrol) |
| `A` | Enemy - Spider (moves vertically with thread) |
| `L` | Lamp (toggles darkness mode on touch) |
| `M` | Miner to rescue (level objective) |
| ` ` | Empty space (cave background) |

## Tips and Strategies

### Conserving Energy
- Energy is consumed when flying with the propeller
- It recovers automatically while standing on the ground
- Use gravity and active descent (down arrow) to descend quickly without spending energy
- Plan your route before flying

### Using Dynamite
- Dynamite explodes in 1.5 seconds
- Area of effect: 80 pixel radius
- Destroys dirt (#) and rocks (R). Does not destroy granite (G) or floors (.)
- Can eliminate multiple enemies at once
- Warning: the explosion also damages the player

### Combat
- Laser shots have a short cooldown (0.2s)
- The laser collides with walls, floors, and blocks (does not destroy them)
- Shoot from a safe distance
- Spiders move vertically, bats move horizontally

### High Score
- Rescue quickly to conserve energy (it converts to points)
- Save bombs for additional bonus (50 pts each)
- Destroy as many enemies as possible

## Level Editor

Run `python editor.py` to open the visual level editor. It allows you to create and modify levels saved in `screens.json`.

### Editor Controls

| Key | Action |
|-----|--------|
| **Arrows** | Move cursor tile by tile |
| **Shift+Arrows** | Move cursor while painting with selected tile |
| **Q / A** | Jump one viewport up / down |
| **Z / X** | Jump one viewport left / right |
| **Space / Enter** | Place selected tile |
| **1-9, F, G** | Select tile type |
| **Tab / Shift+Tab** | Cycle tile type |
| **Ctrl+Right** | Add viewport to the right (+16 columns) |
| **Ctrl+Left** | Remove right viewport (-16 columns) |
| **Ctrl+Down** | Add viewport below (+8 rows) |
| **Ctrl+Up** | Remove bottom viewport (-8 rows) |
| **Ctrl+S** | Save levels |
| **Ctrl+N** | New level |
| **Ctrl+Delete** | Delete current level |
| **PgUp / PgDn** | Switch levels |
| **ESC** | Exit editor |

### Minimap

The editor HUD shows a minimap with the level's viewport grid, highlighting the current viewport. This helps with orientation in large levels.

## Credits

### Original Game
- **H.E.R.O.** (1984) by Activision
- Designed by John Van Ryzin
- Original platform: Atari 2600

### This Remake
- Developed with Python and Pygame
- Modular architecture with separate classes
- 5 editable levels with included editor
- ColecoVision-style HUD
- SID audio emulation

## Technology

- **Language**: Python 3.13
- **Framework**: Pygame 2.6.1
- **Audio**: Pygame.mixer + SID emulation (Commodore 64)
- **Graphics**: PNG sprites + procedural generation (fallback)
- **Persistence**: JSON (scores and levels)
- **Input**: Keyboard + Xbox Controller (with gradual joystick)

## Possible Future Improvements

- [ ] More levels (6-20 like the original)
- [x] Dynamic-sized levels with 2D scrolling
- [x] Editor with viewport resize support
- [ ] Animate bats (wings)
- [ ] Decorative background tiles
- [x] Lamps that toggle lights off when touched
- [ ] Snakes emerging from caves
- [ ] Enemies that vibrate in place
- [ ] Magma blocks and level

## License

This is an educational and fan remake project. H.E.R.O. is property of Activision.
