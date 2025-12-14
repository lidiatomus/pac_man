from pacman_logic.reflex import ReflexAgent
from pacman_logic.minmax import MinmaxAgent
from pacman_logic.alphabeta import AlphaBetaAgent

def get_pacman_action(game_state, agent_type='reflex', depth=2):
    """
    Get the action for Pacman based on the specified agent type and depth.
    """
    agent_type = agent_type.lower()
    if agent_type == 'reflex':
        agent = ReflexAgent()
    elif agent_type == 'minmax':
        agent = MinmaxAgent(depth=depth)
    elif agent_type in ('alphabeta', 'alpha-beta', 'alpha_beta'):
        agent = AlphaBetaAgent(depth=depth)
    else:
        raise ValueError("Unknown agent type: " + str(agent_type))
    return agent.get_action(game_state)
