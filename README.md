# 🟡 Pac-Man AI Edition

A modern **Pac-Man clone built with Pygame**, featuring multiple **AI-controlled ghosts**, pathfinding algorithms, power-ups, fruits, and smooth movement inspired by the original arcade game.

---

## 🎮 Features

### ✅ Core Gameplay

* Classic Pac-Man maze with pellets and energizers
* Player-controlled or AI-controlled Pac-Man
* Lives, score system, and win/lose conditions
* Tunnel wrap-around for Pac-Man and ghosts

---

## 👻 Ghost AI System

Ghosts **move only on valid paths**, never through walls, and exhibit different behaviors depending on their state.

### 🧠 AI Modes (switchable at runtime)

Press number keys to change ghost pathfinding:

| Key | Algorithm                  |
| --- | -------------------------- |
| `1` | BFS (Breadth-First Search) |
| `2` | DFS (Depth-First Search)   |
| `3` | A* (A-Star Search)         |
| `4` | Random movement            |

Each ghost computes its next tile using the selected algorithm, then **moves smoothly in pixel space** toward it.

---

## 🔄 Ghost States

### 🔴 Normal (Chase / Scatter)

* Ghosts actively target Pac-Man or predefined maze corners
* Smooth floating movement (no teleporting)
* Move at normal speed

### 🔵 Frightened (After Energizer)

* Ghosts turn dark blue
* Movement becomes slower and random
* Pac-Man can eat ghosts for bonus points

### 👀 Dead

* Ghost body disappears, leaving only eyes
* Eyes return quickly to the Ghost House
* Ghost regenerates and re-enters normal state

---

## ⚡ Power Mode (Energizers)

* Triggered when Pac-Man eats a big pellet
* Lasts for a limited time
* All ghosts switch to frightened state
* Visual power timer displayed at bottom of screen

---

## 🍒 Fruit System

* Fruits spawn after a specific number of pellets are eaten
* Fruits spawn **only on walkable tiles**, never inside walls
* Each fruit:

  * Exists for a limited time
  * Grants bonus points when collected
  * Disappears properly after being eaten or on death

---

## 🧩 Movement System

* All entities move in **pixel space**, not tile jumps
* Ghosts smoothly interpolate toward target tiles
* Different speeds based on ghost state:

  * Normal: standard speed
  * Frightened: slower
  * Dead: faster

---

## 🗺 Map & Difficulty

* Supports multiple difficulty levels:

  * EASY
  * MEDIUM
  * HARD
* Optional procedural mutation of predefined maps
* Ghost House gate detection for proper respawn behavior

---

## 🎛 Controls

### Player

| Key        | Action            |
| ---------- | ----------------- |
| Arrow Keys | Move Pac-Man      |
| `A`        | Toggle Pac-Man AI |
| `ESC`      | Quit game         |

### AI & Debug

| Key   | Action                                   |
| ----- | ---------------------------------------- |
| `1–4` | Change ghost AI algorithm                |
| `P`   | Toggle path visualization                |
| `R`   | Toggle map mutation                      |
| `5–7` | Change difficulty (Easy / Medium / Hard) |
| `F`   | Toggle fullscreen                        |



✔ Shorten this for a **course submission**
✔ Make a **professor-friendly version**
✔ Add **screenshots section**
✔ Add **AI theory explanation**

Just tell me 👍
