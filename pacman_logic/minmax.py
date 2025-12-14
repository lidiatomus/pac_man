from pacman_logic.util import terminal_test, legal_actions_from, generate_successor, evaluation_function

class MinmaxAgent:
    def __init__(self, depth=2):
        self.depth = max(1, depth)

    def get_action(self, state):
        num_ghosts = len(state.get('ghosts', []))
        num_agents = 1 + num_ghosts

        def max_value(s, depth):
            if depth == 0 or terminal_test(s):
                return evaluation_function(s)
            v = -float('inf')
            acts = legal_actions_from(s['pacman_pos'], s['grid'])
            if not acts:
                return evaluation_function(s)
            for a in acts:
                v = max(v, min_value(generate_successor(s, 0, a), depth, 1))
            return v

        def min_value(s, depth, agent_idx):
            if depth == 0 or terminal_test(s):
                return evaluation_function(s)
            v = float('inf')
            gi = agent_idx - 1
            ghost_pos = s['ghosts'][gi] if gi < len(s['ghosts']) else None
            acts = legal_actions_from(ghost_pos, s['grid']) if ghost_pos else ['STOP']
            if not acts:
                acts = ['STOP']
            next_agent = agent_idx + 1
            for a in acts:
                succ = generate_successor(s, agent_idx, a)
                if next_agent == num_agents:
                    v = min(v, max_value(succ, depth - 1))
                else:
                    v = min(v, min_value(succ, depth, next_agent))
            return v

        # choose action with highest minmax value
        best_score = -float('inf')
        best_action = 'STOP'
        for a in legal_actions_from(state['pacman_pos'], state['grid']):
            succ = generate_successor(state, 0, a)
            val = min_value(succ, self.depth, 1) if num_agents > 1 else max_value(succ, self.depth)
            if val > best_score:
                best_score = val
                best_action = a
        return best_action