from game import Clue, Play, Discard, ResolvedClue

from game import Card, Tokens, Rules
from typing import NamedTuple, List, Tuple


def naive2_with_2nd_degree_player(log: List[NamedTuple], hands: List[List[Card]],
                                  rules: Rules, tokens: Tokens, slots: List[int],
                                  discard_pile: List[List[int]]) -> Tuple:
    """
    Zvika and Ofer's naive player
    Improved with 2nd degree clues by Ofer
    This player only gives 2nd degree clues to the next player
    """

    def relative_position(player_id):
        return (player_id - my_id) % len(hands)

    def is_playable(card):
        return slots[card.data.suit] == card.data.rank

    my_id = len(log) % len(hands)
    my_card_ids = [card.id for card in hands[my_id]]

    hinted_cards = set()
    for move in log[-len(hands):]:
        if isinstance(move, ResolvedClue):
            if move.player == my_id:
                hinted_cards = hinted_cards.union(card.id for card in move.cards)

    # Its better to play than hint
    if hinted_cards:
        play_card = max(hinted_cards)
        return Play.create(play_card), 'Play hinted card'

    # Play 2nd degree clues
    for move in log[-len(hands)+1:]:
        if isinstance(move, ResolvedClue):
            if relative_position(move.cur_player) > relative_position(move.player):
                hinted_card = max([card.id for card in move.cards])
                known_card = [card for card in hands[move.player] if card.id == hinted_card][0]
                if slots[known_card.data.suit] == known_card.data.rank - 1:
                    return Play.create(max(my_card_ids)), 'play 2nd degree clue'

    # Its better to hint than discard
    if tokens.clues > 0:
        # If possible give 2nd degree clue
        hintable_card = hands[(my_id+1) % len(hands)][-1]
        if is_playable(hintable_card):
            player_id = (my_id+2) % len(hands)
            for card in hands[player_id]:
                if card.data.suit == hintable_card.data.suit and card.data.rank == hintable_card.data.rank+1:
                    # suit clue
                    if max([card.id for card in hands[player_id] if card.data.suit == hintable_card.data.suit])\
                            == card.id:
                        return Clue.create(player_id, 'suit', card.data.suit), 'give 2nd degree suit clue'
                    # rank clue
                    if max([card.id for card in hands[player_id] if card.data.rank == hintable_card.data.rank+1])\
                            == card.id:
                        return Clue.create(player_id, 'rank', card.data.rank), 'give 2nd degree rank clue'

        # Give regular clue
        for i in range(len(hands) - 1):
            player = (my_id + i + 1) % len(hands)
            player_suits = set([card.data.suit for card in hands[player]])
            player_ranks = set([card.data.rank for card in hands[player]])
            playable_suits = set()
            playable_ranks = set()
            for suit in player_suits:
                card = max([card for card in hands[player] if card.data.suit == suit])
                if slots[card.data.suit] == card.data.rank:
                    playable_suits.add(card.data.suit)
            for rank in player_ranks:
                card = max([card for card in hands[player] if card.data.rank == rank])
                if slots[card.data.suit] == card.data.rank:
                    playable_ranks.add(card.data.rank)

            # its better to go up then sideways
            clue = None
            clue_rank = 0
            if playable_ranks:
                clue = Clue.create(player, 'rank', max(playable_ranks))
                clue_rank = max(player_ranks)
            for suit in playable_suits:
                if slots[suit] > clue_rank:
                    clue = Clue.create(player, 'suit', suit)
                    clue_rank = slots[suit] + 1
            if clue:
                return clue, 'Given actionable clue'

    # Its better to discard then playing like an idiot
    if tokens.clues < rules.max_tokens.clues:
        return Discard.create(min(my_card_ids)), 'Discard oldest card'

    # If all else fails, play like an idiot
    return Play.create(max(my_card_ids)), 'Play like an idiot'
