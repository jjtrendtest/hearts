import recorder

def watch(player_name, mode, observation):
    if recorder.players_with_score_card(observation) > 1:
        return "conservative"

    return "conservative"

