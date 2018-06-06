#!/usr/bin/env python3.6
import argparse
from game import Hanabi, EndMode, DEFAULT_RULES
import players


def run_game_n_times(players_list, t, end_mode=EndMode.official, suits=5, allow_cheats=False):
    score = []
    
    ips = [None] * len(players_list) # intergame player state

    for i in range(t):
        h = Hanabi(players_list, rules=DEFAULT_RULES._replace(suits=suits), allow_cheats=allow_cheats, end_mode=end_mode, ips=ips)
        match_result, ips = h.run_and_return_ips()
        score.append(match_result)

    import pandas as pd
    d = pd.Series(score)
    print(d.describe())
    print(d.value_counts().sort_index())
    return d


def run_game_once(players_list, end_mode=EndMode.official, suits=5, 
                  allow_cheats=False, thin_log=False, target_score=None):
    score_in_range = False
    while not score_in_range:
        h = Hanabi(players_list, rules=DEFAULT_RULES._replace(suits=suits), allow_cheats=allow_cheats, end_mode=end_mode)
        h.run()
        score_in_range = (target_score is None 
                          or target_score[0] <= h.score <= target_score[1])
    h.print_history(thin=thin_log)
    return h


def create_player_by_name(player_name):
    name_segments = player_name.split('@')[::-1] # deco1@deco2@player -> [player, deco2, deco1]
    if len(name_segments) < 1:
        raise RuntimeError("Bad player name")
    player = getattr(players, name_segments[0]) # player
    
    for decorator_name in name_segments[1:]:
        decorator = getattr(players.decorators, decorator_name)
        player = decorator(player) # player -> deco2(player) -> deco1(deco2(player))

    return player


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('player_name', help='<player_name> or <player1_name>,<decorator_name>@<player2_name>')
    parser.add_argument('-t', '--times', default=1, type=int)
    parser.add_argument('-n', '--players', default=3, type=int)
    parser.add_argument('-c', '--allow-cheats', default=False, action='store_true')
    parser.add_argument('-e', '--end-mode', default='official', choices=[e.name for e in EndMode])
    parser.add_argument('-s', '--suits', default=5, type=int)
    parser.add_argument('-i', '--one-io-player', default=False, action='store_true')
    parser.add_argument('-g', '--target-score', default=None, type=int, nargs=2)

    args = parser.parse_args()
    
    player_names = args.player_name.split(',')
    players_list = ([create_player_by_name(pn) for pn in player_names] * args.players)
    players_list = players_list[:args.players]

    if args.one_io_player:
        players_list.pop()
        players_list.append(players.make_io_player('Human Player'))

    h_args = dict(end_mode = EndMode[args.end_mode], 
                  suits = args.suits, 
                  allow_cheats = args.allow_cheats)
    if args.times > 1:
        return run_game_n_times(players_list, t=args.times, **h_args)
    else:
        return run_game_once(players_list, target_score=args.target_score, **h_args)

if __name__ == '__main__':
    ret = main()
