# Wumpus World — Tactical Field Edition

A Python/Pygame implementation of the classic AI **Wumpus World** problem, featuring a 4x4 grid environment, procedural hazard generation, a knowledge-based autonomous agent, and a tactical military-themed UI.

![Status](https://img.shields.io/badge/status-active-brightgreen) ![Python](https://img.shields.io/badge/python-3.x-blue) ![Pygame](https://img.shields.io/badge/pygame-2.6.1-orange)

---

## 📖 Overview

This project simulates the classic **Wumpus World** — an AI environment used to teach propositional logic and knowledge-based agents. The player (or an autonomous agent) explores a hidden 4x4 grid, avoiding pits and the deadly Wumpus, while trying to locate and grab the gold and return safely.

The game includes both a **manual play mode** and an **auto-pilot mode**, where the agent uses logical deduction to navigate the grid based on sensed percepts (breeze, stench, glitter).

---

## 🎮 Features

- **4x4 Grid World** with procedurally generated pits, a Wumpus, and gold
- **Safe Spawn Guarantee** — the starting cell `(0,0)` is always hazard-free
- **Sensory Percepts** — breeze (nearby pit), stench (nearby Wumpus), glitter (gold in cell)
- **Manual Mode** — control the agent using arrow keys
- **Auto-Pilot Mode** — a knowledge-based AI agent that deduces safe cells and explores autonomously
- **Tactical Military UI** — custom color palette, HUD with score/position/mode display
- **Procedurally Synthesized Audio** — sound effects generated in real time via sine/square waveforms (no external audio files)
- **State Machine** — clean separation between `MENU`, `PLAYING`, and `GAME_OVER` states
- **Optional Web Server Mode** — serves a companion HTML/CSS UI via a background HTTP server

---

## 🕹️ Controls

| Key | Action |
|---|---|
| `Enter` | Deploy agent (start game from menu) |
| `Arrow Keys` | Move agent (Up / Down / Left / Right) |
| `A` | Toggle Auto-Pilot mode |
| `R` | Reset / redeploy |

---

## 🏗️ Class Architecture

The codebase follows a clean separation of concerns across four core classes:

| Class | Responsibility |
|---|---|
| **`Cell`** | Represents a single grid coordinate. Holds boolean flags for hidden entities (Wumpus, pit, gold), sensory cues (stench, breeze, glitter), and reveal status. |
| **`World`** | Manages the 4x4 matrix, procedural hazard/item generation (ensuring the spawn point is safe), and broadcasts sensory percepts to orthogonal neighbors. |
| **`Agent`** | Tracks player/AI state — grid coordinates, running score, survival/victory status, and memory of visited/safe tiles. |
| **`Game`** | The Pygame-based core engine — handles window setup, input, state machine transitions, framerate capping, and UI rendering. |

---

## 🧠 AI Logic & Decision-Making

When auto-pilot is active, the agent navigates using **localized propositional deduction** and a **prioritized action heuristic**.

### Deductive Reasoning
At each turn, the agent analyzes its current cell. If no sensory inputs are present (no breeze, no stench), it deduces that all adjacent cells are 100% safe and updates its internal knowledge base accordingly.

### Decision Hierarchy
To select its next move, the agent evaluates adjacent cells using a strict checklist:

1. **Grab Gold** — move immediately to an adjacent cell if gold is detected there.
2. **Safe Exploration** — move to an unvisited, verified-safe neighboring cell.
3. **Safe Backtracking** — retrace steps through previously explored safe cells if forward progress is blocked.
4. **Blind Guesswork** — take a calculated risk on an unverified adjacent cell when no safe options remain.

---

## ⚠️ Core Challenges

| Challenge | Impact & Context |
|---|---|
| **Limited Deductive Horizon** | The AI's logic is local and reactive — it only marks cells safe if the current room is entirely clear. It lacks advanced cross-cell intersection logic, leading to occasional premature blind guesses. |
| **Dynamic Audio Buffering** | Audio is synthesized via real-time math calculations (sine/square waves converted to byte arrays) instead of static files. While memory-efficient, this can cause OS-dependent audio driver lag and frame drops. |
| **Asynchronous Interface Dualism** | Running a background HTTP web server alongside the main Pygame rendering loop requires strict thread-safe isolation to prevent blocking locks and keep the UI fluid. |

---

## 🎓 Key Learning Outcomes

- **Practical Knowledge Representation** — mapping raw sensory percepts (breeze, stench) into an active AI knowledge matrix to drive real-time agent behavior.
- **Finite State Machine (FSM) Mastery** — implementing a clean state architecture (`MENU`, `PLAYING`, `GAME_OVER`) that isolates input logic from visual rendering layers.
- **Constrained Procedural Generation** — designing map-generation algorithms that balance randomness with fairness, ensuring the player's starting zone is always safe and the level remains solvable.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.x
- Pygame (`pip install pygame`)

### Run the Game
```bash
python Wampusgame.py
```

### Run with Web UI (optional)
```bash
python Wampusgame.py --web --port 8000
```
This launches a background HTTP server and opens a companion browser-based UI at `http://localhost:8000/`.

---

## 📸 Screenshots

The game features a tactical field UI showing:
! [Main menu with deployment prompt](https://github.com/kashifkhan117401-bit/Wampus-Game/blob/main/Documentation/1.png?raw=true)
- [Live HUD (score, position, mode)](https://github.com/kashifkhan117401-bit/Wampus-Game/blob/main/Documentation/2.png?raw=true)
- [Revealed hazard tiles (failure) with tactical iconography](https://github.com/kashifkhan117401-bit/Wampus-Game/blob/main/Documentation/Failed.png?raw=true)
- [Mission outcome screens (success)](https://github.com/kashifkhan117401-bit/Wampus-Game/blob/main/Documentation/Successfull.png?raw=true)

---

## 📄 Project Report

This project was submitted as part of an academic assignment:

- **Project:** Wumpus World
- **Institution:** University of Management and Technology (UMT)
- **Instructor:** Mam Zeenat Tanveer
- **Section:** A7

---

## ✍️ Author

**Kashif Hafeez**

- 📧 Email: [kashifkhan117401@gmail.com](mailto:kashifkhan117401@gmail.com)
- 🌐 Portfolio: [kashifhafeez-portfolio1.vercel.app](https://kashifhafeez-portfolio1.vercel.app/)
- 💼 LinkedIn: [in/kashif-hafeez-545794330](https://linkedin.com/in/kashif-hafeez-545794330)
- 📷 Instagram: [@i_kashiif](https://www.instagram.com/i_kashiif?igsh=MTUwaTEzNTFocWs2eQ==)
- 📘 Facebook: [Kashif Hafeez](https://www.facebook.com/share/1AZ6rpfhxb/)

---

## 📜 License

This project was created for educational purposes as part of a university coursework submission.

