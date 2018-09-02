import json

def take_action(action, data, observation, ws):
    #print ('-------------------' + action + '-------------------')
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
        pick_card = data["self"]["candidateCards"].pop()
        print pick_card
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
