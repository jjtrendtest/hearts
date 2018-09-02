import json
import copy
from functools import reduce

SUIT_TO_KEY = {
    "S": "suit_s",
    "H": "suit_h",
    "D": "suit_d",
    "C": "suit_c"
}

SCORE_CARDS = ["AH", "2H", "3H", "4H", "5H", "6H", "7H", "8H", "9H", "TH", "JH", "QH", "KH", "QS", "TC"]

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
            ]
        }
        self._game["players"].append(copy.deepcopy(player_info))
        self._game["players"].append(copy.deepcopy(player_info))
        self._game["players"].append(copy.deepcopy(player_info))
        self._game["players"].append(copy.deepcopy(player_info))
        #Backup for new deal
        self._reset = copy.deepcopy(self._game)

    def set_player_name(self, myname):
        self._game["my_name"] = myname

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


    def get_observation(self):
        return self._game

    def action_hook(self, action, data):
        if action == "turn_end":
            round_player = data["roundPlayers"]
            player = data["turnPlayer"]
            card = data["turnCard"]
            card_suit = card[1]
            index = -1
            player_index = round_player.index(player) + 1
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
