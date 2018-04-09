import requests
import chess
import time
import re
import sys

def fetch_user_games(username, page=1):
    options = {
        'rated': 1,
        'playing': 0,
        'with_analysis': 1,
        'with_moves': 1,
        'with_opening': 1,
        'with_movetimes': 0,
        'nb': 100,
        'page': page
    }
    url = 'https://lichess.org/api/user/{username}/games'.format(username=username)
    resp = requests.get(url, params = options)
    if int(resp.status_code) == 429:
        time.sleep(70)
        return fetch_user_games(username, page)
    time.sleep(1.3)
    gamesList = list(filter(is_preferred_game, resp.json()['currentPageResults']))
    if (resp.json()['nbPages'] > resp.json()['currentPage']) and (page < 5):
        return gamesList + fetch_user_games(username, page + 1)
    return gamesList

def is_preferred_game(game_json):
    try:
        return (game_json['variant'] == 'standard') &\
                (game_json['rated'] == True) &\
                (game_json['clock']['totalTime'] >= 420) &\
                (game_json['turns'] >= 10) &\
                (game_json['players']['white']['rating'] > 1550) &\
                (game_json['players']['black']['rating'] > 1550)
    except:
        return False

def eval_is_inaccuracy(eval_dict):
    try:
        return (eval_dict['judgment']['name'] == 'Inaccuracy')
    except:
        return False

def separate_uci_move(uci_str):
    return "{}-{}".format(uci_str[0:2], uci_str[2:])

def parse_analyzed_game_json(game):
    try:
        if game['turns'] < 20:
            return []
        turns = game['turns']-3 # trying to get a somewhat non-ending position
        moves = game['moves'].split()
        analysis = game['analysis']
        inaccuracies = []

        for ply in range(6, turns):

            if 'mate' in analysis[ply]:
                continue

            if eval_is_inaccuracy(analysis[ply]):
                try:
                    board = setup_board(moves[0:ply])
                except: # in case python-chess spots something weird, skip it no problem
                    continue
                move_played = str(moves[ply])
                best_move_san = str(analysis[ply]['variation'].split()[0])
                engine_eval = analysis[ply]['eval']
                url = str(game['url'])

                if (not (-160 < engine_eval < 160)): # avoiding super imbalanced positions
                    continue

                if re.search('=[NBR]', (move_played + best_move_san), re.IGNORECASE): # avoids front-end difficulties
                    continue

                best_move_uci = separate_uci_move(analysis[ply]['best'])
                inaccuracies.append({
                    'init_fen': board.fen(),
                    'move_played': move_played,
                    'best_move_san': best_move_san,
                    'best_move_uci': best_move_uci,
                    'game_url': url
                })
        return inaccuracies
    except:
        return []

def setup_board(moves):
    board = chess.Board()
    for m in moves:
        board.push_san(m)
    return board

def flatten(l):
    return [item for sublist in l for item in sublist]

def fetch_player_inaccuracies(username):
    games = fetch_user_games(username)
    analyzed_games = filter(lambda x: 'analysis' in x, games)
    parsed_games = map(parse_analyzed_game_json, analyzed_games)
    return flatten(parsed_games)

def is_preferred_tournament(tourney_dict):
    return (tourney_dict['rated'] == True) &\
            (tourney_dict['nbPlayers'] > 20) &\
            (tourney_dict['clock']['limit'] >= 300) &\
            (tourney_dict['variant']['key'] == 'standard')

def fetch_current_finished_tournaments():
    resp = requests.get("https://lichess.org/api/tournament")
    time.sleep(1.3)
    if resp.status_code == 200:
        resp = resp.json()
    else:
        raise Exception("Something went wrong with Lichess /api/tournament endpoint")
    tournaments = resp['finished']
    preferred_tournaments = filter(is_preferred_tournament, tournaments)
    tournament_ids = map(lambda t: t['id'], preferred_tournaments)
    return list(tournament_ids)

def fetch_random_usernames(numPlayers=10):
    players = []
    finished_tournaments = fetch_current_finished_tournaments()
    for t_id in finished_tournaments:
        resp = requests.get("https://lichess.org/api/tournament/{}?page=1".format(t_id))
        time.sleep(1.3)
        if resp.status_code == 200:
            resp = resp.json()
        else:
            raise Exception("Something went wrong with Lichess api/tournament/<id> endpoint")
        standings = [p['name'] for p in resp['standing']['players']]
        players = players + standings
    return list(set(players))[:numPlayers]

def fetch_random_players_inaccuracies(num=10):
    players = fetch_random_usernames(num)
    player_games = fetch_player_list_inaccuracies(players)
    return player_games

def fetch_player_list_inaccuracies(players_list):
    return flatten(map(fetch_player_inaccuracies, players_list))

def store_inaccuracy(inacc_dict, dbconn):
    
    return

def store_inaccuracies(inacc_dicts):
    for d in inacc_dicts:
        store_inaccuracy(d)