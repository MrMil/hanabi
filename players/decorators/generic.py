from game import Clue, Play, Discard, ResolvedClue

from game import Card, Tokens, Rules
from typing import NamedTuple, List, Tuple

import inspect

def generic_player_decorator(subdecorator):
    """
    subdecorator(player, player_args, ...) is the parameter's signature
    Allows running smart logic either before or after the player made it's move

    Usage:
    @generic_player_decorator
    def my_decorator(player, player_args, rules):
        print(rules)
        return player(*player_args)
    """
    def generic_decorator_player_wrapper(player):
        """
        This is the actual decorator, it received the original "decorator"
        as a closure parameter and the player it decorates as a parameter
        """
        def generic_decotrator_internal(
            ips, state, log: List[NamedTuple], hands: List[List[Card]],
            rules: Rules, tokens: Tokens, slots: List[int],
            discard_pile: List[List[int]]) -> Tuple[None, NamedTuple]:
            """
            This function replaces the original player function as the API
            for the Hanabi class
            """
            possible_args = {"ips": ips,
                             "state": state,
                             "log": log,
                             "hands": hands,
                             "rules": rules,
                             "tokens": tokens,
                             "slots": slots,
                             "discard_pile": discard_pile,
                             "player": player} # 'player' was not an original player function parameter. 
                                               # Used to pass original player to the subdecorator function

            player_args = inspect.getfullargspec(player).args

            player_args_list = []
            for argname in player_args:
                player_args_list.append(possible_args[argname])

            possible_args["player_args"] = player_args_list # probably the subdecorator function will want this

            subdecorator_args = inspect.getfullargspec(subdecorator).args
            subdecorator_args_list = []
            for argname in subdecorator_args:
                subdecorator_args_list.append(possible_args[argname])

            return subdecorator(*subdecorator_args_list)

        return generic_decotrator_internal

    return generic_decorator_player_wrapper
