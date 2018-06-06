
from .generic import generic_player_decorator

@generic_player_decorator
def estimator(player, player_args):
    """
    KanHar's player estimator decorator.
    Estimates final game score in each step.
    """
    ips, state, move, note = ([None]*2 + list(player(*player_args)))[-4:]
    if note != '':
        note += '; '
    note += "estimator: Sorry, unimplemented"

    return ips, state, move, note

