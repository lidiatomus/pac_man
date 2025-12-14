from pacman_logic.util import legal_actions_from, generate_successor, evaluation_function

class ReflexAgent:
    def __init__(self):
        pass

    def get_action(self, state):
        """
        Choose an action based on the evaluation function.
        """
        pacman = state['pacman_pos']
        grid = state['grid']

        # get legal actions, if none then game stops
        legal = legal_actions_from(pacman, grid)
        if not legal:
            return 'STOP'

        # choose best action
        best = None
        best_score = -float('inf')
        for a in legal:
            succ = generate_successor(state, 0, a)
            val = evaluation_function(succ)
            if val > best_score:
                best_score = val
                best = a
        return best
