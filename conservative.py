import json
import recorder
import copy


def take_action(action, data, observation, ws):
    print ('-------------------' + action + '-------------------')
    #print (observation)

    if action == "pass_cards":
        pass_cards = data["self"]["cards"].pop(3)
        ws.send(json.dumps(
            {
                "eventName": "pass_my_cards",
                "data": {
                    "dealNumber": data['dealNumber'],
                    "cards": pass_cards
                }
            })
        )
    elif action == "expose_cards":
        if "AH" in data["self"]["cards"]:
            export_cards = ["AH"]
        else:
            export_cards = []
        print export_cards
        ws.send(json.dumps(
           {
               "eventName": "expose_my_cards",
               "data": {
                   "dealNumber": data['dealNumber'],
                   "cards": export_cards
               }
           })
        )
    elif action == "your_turn":
        print recorder.next_players(observation)
        me = recorder.get_self_player_info(observation)
        print (json.dumps(me))
        print (data["self"]["candidateCards"])
        print "------------------------"
        #my_heart, op_heart = recorder.player_with_heart(observation)
        #recorder.count_suit_card_available(observation, data["self"]["cards"], "")
        #if my_heart == 0 and op_heart == 1:
            #possible shoot moon? careful
        #else:
            #conservative safe
            
        #me first
        suit = recorder.round_suit(observation)

        pick_card = None
        if len(observation["round"]["table_cards"]) == 0:
            # I am first TODO select a safe card to throw
            # someone have this suit and ensure higher than me
            # 1. don't start from heart
            # 2. ensure other people have same suit and higher than me, maybe start from higher card if many people own it

            if len(data["self"]["candidateCards"]) == 1:
                pick_card = data["self"]["candidateCards"].pop()
            else:
                print("case 1 TBD")
                candidates = recorder.suit_card_exclude(data["self"]["candidateCards"], "H")
                if len(candidates) > 0:
                    pick_card = candidates.pop()
                else:
                    pick_card = data["self"]["candidateCards"].pop()

        else:
            table_score_cards = recorder.score_card_filter(observation["round"]["table_cards"])
            suit_cards = recorder.hand_card_with_suit(data["self"]["candidateCards"], suit)
            hand_score_cards = recorder.score_card_filter(data["self"]["candidateCards"])
            
            if len(suit_cards) == 0 and len(hand_score_cards) > 0:
                # chance to throw score card
                if "QS" in hand_score_cards:
                    print("case 2-1")
                    pick_card = "QS"
                else:
                    print("case 2-2")
                    print observation["round"]["table_cards"]
                    print data["self"]["candidateCards"]
                    candidates = recorder.ordered_suit_card(hand_score_cards, "H")
                    print candidates
                    print type(candidates)
                    pick_card = candidates[0]
                    print pick_card
                    if pick_card == None:
                        print("case 2-2-1")
                        
            else:
                if len(table_score_cards) > 0:
                    print("case 2-3")
                    print observation["round"]["table_cards"]
                    print data["self"]["candidateCards"]
                    
                    pick_card = recorder.lost_this_round_with_big_card(observation["round"]["table_cards"], data["self"]["candidateCards"])
                    if pick_card == None:
                        print("case 2-3-1")
                        #You will take this round which card. Higher card
                        candidates = recorder.ordered_suit_card(data["self"]["candidateCards"], suit)
                        if len(candidates) == 0:
                            print("case 2-3-1-1 TBD consider which suit")
                            pick_card = data["self"]["candidateCards"][0]
                        else:
                            print("case 2-3-1-2")
                            if len(observation["round"]["table_cards"]) == 3:
                                pick_card = candidates[0]
                            else:
                                pick_card = candidates[-1]
                    print pick_card
                else:
                    if suit == "H" or "QS" in observation["round"]["table_cards"]:
                        print("case 3-1")
                        #TODO check if we can give high card and ensure someone have higher card
                        pick_card = recorder.lost_this_round_with_big_card(observation["round"]["table_cards"], data["self"]["candidateCards"])
                        print pick_card
                    else:
                        if len(observation["round"]["table_cards"]) == 3:
                            #use high card win this round
                            print("case 4-1")
                            print observation["round"]["table_cards"]
                            print data["self"]["candidateCards"]
                            candidates = recorder.ordered_suit_card(data["self"]["candidateCards"], suit)
                            if len(candidates) == 0:
                                #TODO
                                print("case 4-1-1 TBD consider which suit")
                                pick_card = data["self"]["candidateCards"][0]
                            else:
                                if len(candidates) > 1 and "QS" in candidates:
                                    candidates.remove("QS")
                                pick_card = candidates[0]
                            print pick_card
                        else:
                            #TODO calculate a safe card, someone must have this suit
                            print("case 4-2  TBD")
                            pick_card = data["self"]["candidateCards"].pop()

        print pick_card
        if pick_card == None:
            print ("WHY SHOULD NOT HAPPEND FIXED ME")
            pick_card = data["self"]["candidateCards"].pop()

        ws.send(json.dumps(
           {
               "eventName": "pick_card",
               "data": {
                   "dealNumber": data['dealNumber'],
                   "roundNumber": data['roundNumber'],
                   "turnCard": pick_card
               }
           })
        )
