import json
import copy
import itertools


def generate_all_cards():
    allcard = list(itertools.product('AKQJT98765432', 'SHDC'))
    t = ()
    for card in allcard:
        t = t +  (''.join(card),)
    return t

ALL_CARDS = generate_all_cards()


SUIT_TO_KEY = {
    "S": "suit_s",
    "H": "suit_h",
    "D": "suit_d",
    "C": "suit_c"
}

SCORE_CARDS = ["AH", "2H", "3H", "4H", "5H", "6H", "7H", "8H", "9H", "TH", "JH", "QH", "KH", "QS", "TC"]

SCORE_CARDS2 = ["AH", "2H", "3H", "4H", "5H", "6H", "7H", "8H", "9H", "TH", "JH", "QH", "KH", "QS"]

HEART_CARDS = ["2H", "3H", "4H", "5H", "6H", "7H", "8H", "9H", "TH", "JH", "QH", "KH", "AH"]

CARD_ORDER = ["2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K", "A"]

def score_card_filter(table_cards):
    return filter(lambda x: x in SCORE_CARDS2, table_cards)

def suit_card_exclude(cards, suit):
    return filter(lambda x: x[1] != suit , cards)

def suit_card_filter(cards, suit):
    return filter(lambda x: x[1] == suit , cards)

def players_with_score_card(observation):
    players_with_score_card = 0

    #check if multi-player have score card
    for p in observation["players"]:
        score_cards = filter(lambda x: x in SCORE_CARDS2, p["score_cards"])
        if len(score_cards) > 0:
            players_with_score_card += 1
    return players_with_score_card


# next player's name include myself.
def next_players(observation):
    return observation["round"]["round_players"][observation["round"]["turn_number"]:]

# the card suit in this round
def round_suit(observation):
    if observation["round"]["turn_card"] == "":
        return None

    return observation["round"]["turn_card"][1]

def safe_suit(observation):

    s_suit = 0
    h_suit = 0
    d_suit = 0
    c_suit = 0
    result = []

    for p in observation["players"]:
        if p["player_name"] != observation["overview"]["my_name"]:
            if p["no_suit"]["S"] == True:
                s_suit += 1
            elif p["no_suit"]["H"] == True:
                h_suit += 1
            elif p["no_suit"]["D"] == True:
                d_suit += 1
            elif p["no_suit"]["C"] == True:
                c_suit += 1
    if s_suit == 0:
        result.append("S")
    if h_suit == 0:
        result.append("H")
    if d_suit == 0:
        result.append("D")
    if c_suit == 0:
        result.append("C")

    return result

#for first turn use
def pick_a_safe_card(observation, hand_cards):
    safe_suits = safe_suit(observation)
    if "H" in safe_suits:
        safe_suits.remove("H")
    cards_no_show, tmp = cards_in_opponent(observation)
    me = get_self_player_info(observation)
    if len(safe_suits) > 0:
        best_suit = ""
        best_suit_count = 0
        for s in safe_suits:
            suit_card_count = len(suit_card_filter(cards_no_show, s))
            if suit_card_count > best_suit:
                best_suit_count = suit_card_count

        candidates = ordered_suit_card(hand_cards, best_suit)

        if len(candidates) > 0: #magic number here TODO
            if best_suit_count > 6:
                return candidates[0]
            else:
                return candidates[-1]
    else:
        print("fixed me pick_a_safe_card")
        return hand_cards.pop()

    return None
    #two choice take this round or safely pick a small card


def cards_in_opponent(observation):
    opponent_known_cards = {}
    allcards = copy.deepcopy(ALL_CARDS)
    cards_no_show = [x for x in allcards if x not in observation["overview"]["open_cards"]["all"]]
    for p in observation["players"]:
        if p["player_name"] != observation["overview"]["my_name"]:
            opponent_known_cards[p["player_name"]] = p["known_cards"]

    return cards_no_show, opponent_known_cards

def hand_card_with_suit(hand_cards, suit):
    return filter(lambda x: x[1] == suit, hand_cards)

def cards_in_opponent_with_suit(observation, suit):
    cards, opponent = cards_in_opponent(observation)
    candidates = filter(lambda x: x[1] == suit, cards)
    return candidates

def hand_card_suits(hand_cards):
    suits = []
    for c in hand_cards:
        if c[1] not in suits:
            suits.append(c[1])
    return suits

def rest_player_no_round_suit(observation):
    suit = round_suit(observation)
    if suit == None:
        print("should not happend! you are first player. check it first")
        return None

    no_suit_player = []
    players = next_players(observation).pop(1) #remove self
    for p in observation["players"]:
        if p["player_name"] in players:
            if p["no_suit"][suit] == True:
                no_suit_player.append(p["player_name"])
    return no_suit_player

def take_this_round_with_small_card(table_cards, hand_cards):
    suit = table_cards[0][1]
    compares = [x for x in table_cards if x[1] == suit]
    target = 0
    for c in compares:
        if CARD_ORDER.index(c[0]) > target:
            target = CARD_ORDER.index(c[0])

    target_card = CARD_ORDER[target] + suit
    candidates = [x for x in hand_cards if x[1] == suit]
    ordered = sorted (map(lambda x: CARD_ORDER.index(x[0]), candidates))
    candidates = map(lambda x: CARD_ORDER[x] + suit, ordered)

    choosen = None
    for c in candidates:
        if CARD_ORDER.index(c[0]) > target:
            choosen = c
            break

    return choosen

def lost_this_round_with_big_card(table_cards, hand_cards):
    suit = table_cards[0][1]
    compares = [x for x in table_cards if x[1] == suit]
    target = 0
    for c in compares:
        if CARD_ORDER.index(c[0]) > target:
            target = CARD_ORDER.index(c[0])

    target_card = CARD_ORDER[target] + suit
    candidates = [x for x in hand_cards if x[1] == suit]
    ordered = sorted (map(lambda x: CARD_ORDER.index(x[0]), candidates))[::-1]
    candidates = map(lambda x: CARD_ORDER[x] + suit, ordered)

    choosen = None
    for c in candidates:
        if CARD_ORDER.index(c[0]) < target:
            choosen = c
            break

    return choosen

def ordered_suit_card(cards, suit, reverse=False):
    candidates = [x for x in cards if x[1] == suit]
    if reverse:
        ordered = sorted (map(lambda x: CARD_ORDER.index(x[0]), candidates))
    else:
        ordered = sorted (map(lambda x: CARD_ORDER.index(x[0]), candidates))[::-1]

    return map(lambda x: CARD_ORDER[x] + suit, ordered)



def rank_score_cards(cards):
    heart_cards = filter(lambda x: x in HEART_CARDS, cards)
    ordered = sorted (map(lambda x: HEART_CARDS.index(x), heart_cards))[::-1]
    return map(lambda x: HEART_CARDS[x], ordered)

def player_with_heart(data):
    opponent = 0
    me = 0
    for p in data["players"]:
        if data["overview"]["my_name"] != p["score_cards"]:
            for c in p["score_cards"]:
                if c[1] == "H" or c == "QS":
                    opponent += 1
                    break
        else:
            for c in p["score_cards"]:
                if c[1] == "H" or c == "QS":
                    me = 1
                    break

    return me, opponent

def get_self_player_info(observation):
    for p in observation["players"]:
        if observation["overview"]["my_name"] == p["player_name"]:
            return p
    return None


class recorder:
    def __init__(self):
        self.debug = False
        player_info = {
            "deal_score": 0,
            "expose_card": [],
            "game_score": 0,
            "no_suit": {
                "C": False,
                "D": False,
                "H": False,
                "S": False
            },
            "opened_card": [],
            "player_name": "",
            "player_number": "",
            "play_order": {
                "card": [],
                "order": []
            },
            "cards_get": [],
            "score_cards": [],
            "known_cards": [],
            "hand_cards": []
        }
        self._game = {
            "overview": {
                "my_name": "",
                "ah_owner": "",
                "exposed": False,
                "heart_break": False,
                "open_cards": {
                    "all": [
                    ],
                    "suit_c": [],
                    "suit_d": [],
                    "suit_h": [],
                    "suit_s": []
                },
                "tc_owner": ""
            },
            "players": [
            ],
            "round":{
                "round_players": [],
                "turn_number": 1,
                "table_cards": [],
                "turn_card": ""
            }
        }
        self._game["players"].append(copy.deepcopy(player_info))
        self._game["players"].append(copy.deepcopy(player_info))
        self._game["players"].append(copy.deepcopy(player_info))
        self._game["players"].append(copy.deepcopy(player_info))
        #Backup for new deal
        self._reset = copy.deepcopy(self._game)

    def set_player_name(self, myname):
        self._game["overview"]["my_name"] = myname

    def calculate_score(self):
        ah_multi = 1
        tc_multi = 2
        if self._game["overview"]["exposed"]:
            ah_multi = 2

        for p in self._game["players"]:
            hcard = map(lambda x: 1 if x[1] == "H" else 0, p["score_cards"])
            score = sum(hcard)
            if "QS" in p["score_cards"]:
                socre = score + 13
            socre = score * ah_multi
            if "TC" in p["score_cards"]:
                socre = score * tc_multi
            p["deal_score"] = -score

    def get_self_player_info(self):
        for p in self._game["players"]:
            if self._game["overview"]["my_name"] == p["player_name"]:
                return p
        return None

    def get_observation(self):
        return self._game

    def action_hook(self, action, data):
        if action == "turn_end":
            round_player = data["roundPlayers"]
            player = data["turnPlayer"]
            card = data["turnCard"]
            self._game["round"]["table_cards"].append(card)
            card_suit = card[1]
            index = -1
            player_index = round_player.index(player) + 1
            if player_index == 1:
                self._game["round"]["turn_card"] = card
            self._game["round"]["turn_number"] = player_index
            exist = -1
            empty = 0
            self._game["overview"]["open_cards"]["all"].append(card)
            self._game["overview"]["open_cards"][SUIT_TO_KEY[card_suit]].append(card)
            for p in self._game["players"]:
                if p["player_name"] == "":
                    empty = self._game["players"].index(p)
                if p["player_name"] == player:
                    exist = self._game["players"].index(p)
                    break
            if exist != -1:
                index = exist
            else:
                index = empty

            self._game["players"][index]["player_name"]  = player
            self._game["players"][index]["opened_card"].append(card)
            self._game["players"][index]["play_order"]["card"].append(card)
            self._game["players"][index]["play_order"]["order"].append(player_index)
            if card_suit == "H":
                self._game["overview"]["heart_break"] = True

            if self.debug:
                print(json.dumps(self._game, indent=4))

        if action == "round_end":
            player = data["roundPlayer"]
            first_player = data["roundPlayers"][0]
            cards = []
            first_suit = ""
            self._game["round"]["turn_card"] = ""
            # loop table card
            for p in data["players"]:
                card = p["roundCard"]
                cards.append(card)
                if card == "TC":
                    self._game["overview"]["tc_owner"] = player
                if card == "AH":
                    self._game["overview"]["ah_owner"] = player
                if p["playerName"] == first_player:
                    first_suit = card[1]
            # find player no suit
            for p in data["players"]:
                card_suit = p["roundCard"][1]
                cp = p["playerName"]
                if card_suit != first_suit:
                    # missing some suit
                    for pl in self._game["players"]:
                        if pl["player_name"] == cp:
                            pl["no_suit"][card_suit] = True

            for p in self._game["players"]:
                if p["player_name"] == player:
                    p["cards_get"].extend(cards)
                    for c in cards:
                        if c in SCORE_CARDS:
                            p["score_cards"].append(c)
            #calculate score
            self.calculate_score()


        if action == "expose_cards_end":
            for p in data["players"]:
                if len(p["exposedCards"]) and p["exposedCards"][0] == "AH":
                    self._game["overview"]["ah_owner"] = p["playerName"]
                    self._game["exposed"] = True
                    for pl in self._game["players"]:
                        if pl["player_name"] == p["playerName"] and "AH" not in pl["known_cards"]:
                            pl["known_cards"].append("AH")
                            break

        if action == "pass_cards_end":
            for p in data["players"]:
                if "pickedCards" in p and len(p["pickedCards"]) > 0:
                    #exchange card
                    me = p["playerName"]
                    my_card = p["cards"]
                    picked_card = p["pickedCards"]
                    #give card to...
                    for pl in data["players"]:
                        if me == pl["receivedFrom"]:
                            to = pl["playerName"]
                    #now we know card give to...
                    for pl in self._game["players"]:
                        if to == pl["player_name"]:
                            pl["known_cards"].extend(picked_card)
            for p in self._game["players"]:
                if p["player_name"] == me:
                    p["hand_cards"] = my_card

        if action == "new_deal":
            self._game = copy.deepcopy(self._reset)
            #iter all player
            for p in data["players"]:
                index = data["players"].index(p)
                self._game["players"][index]["player_name"] = p["playerName"]
                if "cards" in p:
                    self._game["players"][index]["hand_cards"] = p["cards"]

        if action == "your_turn":
            #update hand cards
            for p in data["players"]:
                if "cards" in p:
                    my_cards = p["cards"]
                    me = p["playerName"]
            for p in self._game["players"]:
                if me == p["player_name"]:
                    p["hand_cards"] = my_cards

        if action == "new_round":
            self._game["round"]["round_players"] = data["roundPlayers"]
            self._game["round"]["turn_number"] = 1
            self._game["round"]["round_card"] = ""
            self._game["round"]["table_cards"] = []
