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
- **Game Over Screen** with name entry, death song music, and score registration
- **Victory Screen** with rainbow-cycling "VICTORY!" text when all levels are completed
- **Realistic Physics** with gravity, helicopter flight, and active descent
- **Pixel-perfect collision** using pygame masks for precise player-tile interaction
- **Energy System** that drains while flying and recovers while on the ground
- **Lives System** with an extra life every 20,000 points
- **Death Animation** with white flash and skeleton sprite (procedurally generated)
- **Full Sound Effects** (shots, explosions, death, death song, helicopter, footsteps, victory, splatter, rock break/crack)
- **Animated Propeller** that spins slowly on ground and fast while flying (4 rotation frames)
- **ColecoVision-style HUD** with 3D panels, life and bomb icons
- **Fullscreen** by default with aspect-ratio-preserving scaling (Alt+Enter to toggle)
- **Exit Confirmation** with Y/N dialog
- **Procedural Cave Background** with configurable dot density and brightness
- **C64-style Floor Textures** with chevrons, clusters, holes, and edge teeth
- **Moss/Root Overlays** on exposed floor edges (4 directions: up, down, left, right)
- **Floating Scores** that appear when destroying enemies and blocks
- **Level Complete Animation** in 3 ColecoVision-style phases
- **SID Audio Emulation** (Commodore 64) available for sound effects
- **Level Editor** included (`editor.py`) with integrated texture editor (F3)

### Game Mechanics

#### Movement
- **Helicopter Flight**: Press up to fly (consumes energy)
- **Active Descent**: Press down to descend faster (inverted propeller)
- **Animated Walking**: When moving on the ground, with alternating footsteps and sound
- **Gravity**: The player falls when not flying
- **Energy Recovery**: Energy recovers automatically while on the ground
- **Animated Propeller**: Rotates slowly when idle, fast when flying

#### Combat
- **Laser Shot**: Destroys enemies and collides with walls/blocks. Destroys rocks (R) and lava rocks (W) with multiple hits.
- **Dynamite**: Area explosions that destroy blocks, walls, lava rocks, and nearby enemies

#### Enemies
- **Bats** (V): Patrol horizontally, bounce off walls. Speed increases per level (+5%)
- **Spiders** (A): Move vertically from the ceiling, hanging from a thread. Descend up to 2 tiles and return
- **Bugs** (B): Flying enemies with 4-frame animation, patrol horizontally
- **Snakes** (<, >): Emerge from caves in the specified direction

#### Hazards
- **Toxic Water** (~): Kills the player on contact. Animated with scrolling effect.
- **Lava** (X): Indestructible, kills the player on contact.
- **Lava Rocks** (W): Destructible with dynamite/laser, kills the player on contact.

#### Visual Effects
- **Death Animation**: White flash followed by a skeleton sprite, then respawn or game over
- **Explosion Flash**: The screen flashes white/black during dynamite explosions
- **Explosion Animation**: Animated sprites (bomb1, bomb2, bomb3) for dynamite
- **Player Sprites**: Idle, flying, shooting, and walking (2 frames) with animated propeller
- **Spider Thread**: White line connecting the spider to the ceiling
- **Cave Textures**: Procedural floor textures (C64 style) and moss overlays on edges

### Objectives

1. **Find the Miner** (M) in each level
2. **Rescue the Miner** by touching them
3. **Complete all 5 Levels** to win the game

### Scoring System

| Action | Points |
|--------|--------|
| Destroy enemy with laser | 50 |
| Destroy enemy with dynamite | 75 |
| Kill snake | 60 |
| Destroy dirt (#) with dynamite | 20 |
| Destroy rocks (R) with dynamite | 10 |
| Destroy lava rocks (W) | 30 |
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

## Death Animation

When the player dies (enemy contact, explosion, or lava):

1. **White Flash** (0.35s): The player sprite turns white and a screen flash fades out
2. **Skeleton** (1.0s): A bone-colored skeleton sprite appears at the death position
3. **Respawn** or **Game Over**: If lives remain, the level restarts. Otherwise, the game over screen with death song plays.

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
├── hero.py                      # Main game (Game class, loop, render) (~2156 lines)
├── constants.py                 # Game constants + texture params (~271 lines)
├── player.py                    # Player class (physics, animation, pixel-perfect collision) (~346 lines)
├── enemy.py                     # Enemy class (bats, spiders, bugs, snakes) (~384 lines)
├── laser.py                     # Laser class (projectiles, rock destruction)
├── dynamite.py                  # Dynamite class (explosives with animated sprites)
├── miner.py                     # Miner class (rescue objective)
├── palette.py                   # Procedural textures: floor/lava overlay + moss/roots (~570 lines)
├── audio_effects.py             # Commodore 64 SID emulation
├── editor.py                    # Visual level editor + texture editor (F3) (~1661 lines)
├── screens.json                 # Level definitions (editable)
├── scores.json                  # High scores (auto-generated)
├── texture_params.json          # Texture parameters (editable from editor)
├── CLAUDE.md                    # Technical documentation for development
├── README.md                    # This file
├── fonts/
│   └── PressStart2P-vaV7.ttf
├── images/
│   └── hero_background.png      # Start screen background
├── sprites/
│   ├── player.png               # Player idle sprite
│   ├── player_fly.png           # Flying sprite
│   ├── player_shooting.png      # Shooting sprite
│   ├── player_walk1.png         # Walk animation frame 1
│   ├── player_walk2.png         # Walk animation frame 2
│   ├── bat1.png                 # Bat sprite frame 1
│   ├── bat2.png                 # Bat sprite frame 2
│   ├── spider.png               # Spider sprite
│   ├── bug1.png - bug4.png      # Bug animation (4 frames)
│   ├── snake_head.png           # Snake head sprite
│   ├── snake_neck.png           # Snake neck sprite
│   ├── miner.png                # Miner sprite
│   ├── bomb1.png                # Bomb animation frame 1
│   ├── bomb2.png                # Bomb animation frame 2
│   └── bomb3.png                # Bomb animation frame 3
├── tiles/
│   ├── wall.png                 # Dirt (#)
│   ├── floor.png                # Floor/platform (.)
│   ├── granite.png              # Indestructible granite (G)
│   ├── breakable_wall.png       # Destructible rocks (R)
│   ├── broken_wall.png          # Damaged rocks (R after hits)
│   ├── lava.png                 # Lava (X) - indestructible, kills on contact
│   ├── lava_breakable_wall.png  # Lava rocks (W) - destructible
│   ├── lava_broken_wall.png     # Damaged lava rocks (W after hits)
│   ├── lamp.png                 # Lamp (L)
│   ├── toxic_water.png          # Toxic water (~)
│   ├── toxic_water_strip.png    # Toxic water animation strip
│   └── blank.png                # Empty space
└── sounds/
    ├── shoot.wav                # Shooting effect
    ├── explosion.wav            # Explosion effect
    ├── death.wav                # Death effect
    ├── death_song.wav           # Game over music
    ├── splatter.wav             # Enemy death effect
    ├── helicopter.wav           # Helicopter sound (loop)
    ├── walk1.wav                # Left footstep
    ├── walk2.wav                # Right footstep
    ├── rock_break.wav           # Rock destroyed
    ├── rock_crack.wav           # Rock cracked
    ├── win_screen.wav           # Level complete sound
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
| `R` | Rocks (solid, destructible with dynamite/laser) |
| `X` | Lava (solid, indestructible, kills on contact) |
| `W` | Lava rocks (solid, destructible, kills on contact) |
| `V` | Enemy - Bat (horizontal patrol) |
| `A` | Enemy - Spider (moves vertically with thread) |
| `B` | Enemy - Bug (flying, 4-frame animation) |
| `<` | Enemy - Snake (emerges left) |
| `>` | Enemy - Snake (emerges right) |
| `L` | Lamp (toggles darkness mode on touch) |
| `~` | Toxic water (kills on contact, animated) |
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
- Destroys dirt (#), rocks (R), and lava rocks (W). Does not destroy granite (G), floors (.), or lava (X)
- Can eliminate multiple enemies at once
- Warning: the explosion also damages the player

### Combat
- Laser shots have a short cooldown (0.2s)
- The laser destroys rocks (R) and lava rocks (W) after multiple hits
- Shoot from a safe distance
- Spiders move vertically, bats move horizontally, bugs fly with 4-frame animation
- Avoid lava (X) and lava rocks (W) - they kill on contact even during collision

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
| **1-9, F, G, H, J, K, L, Z** | Select tile type |
| **Tab / Shift+Tab** | Cycle tile type |
| **Ctrl+Right** | Add viewport to the right (+16 columns) |
| **Ctrl+Left** | Remove right viewport (-16 columns) |
| **Ctrl+Down** | Add viewport below (+8 rows) |
| **Ctrl+Up** | Remove bottom viewport (-8 rows) |
| **Ctrl+S** | Save levels |
| **Ctrl+N** | New level |
| **Ctrl+Delete** | Delete current level |
| **PgUp / PgDn** | Switch levels |
| **P** | Open palette editor |
| **F3** | Open texture editor |
| **ESC** | Exit editor |

### Texture Editor (F3)

The editor includes a real-time texture parameter editor accessible with F3. It allows you to adjust all floor/moss texture parameters with live preview and save to `texture_params.json`.

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
- **Graphics**: PNG sprites + procedural generation (textures, cave backgrounds, skeleton)
- **Collision**: Pixel-perfect using pygame masks
- **Persistence**: JSON (scores, levels, texture parameters)
- **Input**: Keyboard + Xbox Controller (with gradual joystick)

## Possible Future Improvements

- [ ] More levels (6-20 like the original)
- [x] Dynamic-sized levels with 2D scrolling
- [x] Editor with viewport resize support
- [x] Animate bats (wings)
- [x] Decorative background tiles (cave textures, moss)
- [x] Lamps that toggle lights off when touched
- [x] Snakes emerging from caves
- [x] Bug enemies (flying, 4-frame animation)
- [x] Lava blocks and level
- [x] Death animation with skeleton
- [x] Victory screen
- [x] Animated propeller on helicopter
- [x] Pixel-perfect collision
- [x] Texture editor in level editor
- [ ] More enemy types
- [ ] Boss battles

## License

This is an educational and fan remake project. H.E.R.O. is property of Activision.
