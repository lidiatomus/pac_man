from ghost_ai import GhostAI

game_state = {
    "ghost_pos": (0, 0),
    "player_pos": (2, 3),
    "map": [
        [0, 0, 0, 1],
        [1, 0, 0, 0],
        [0, 0, 1, 0],
    ],
}

ghost = GhostAI(mode="random")

for step in range(10):
    move = ghost.get_next_move(game_state)
    print(f"Move {step + 1}: {move}")
    game_state["ghost_pos"] = move
