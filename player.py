#! /usr/bin/env python
# -*- coding:utf-8 -*-
import time
from time import sleep
import json
import eval7
import itertools
import inspect
from websocket import create_connection
# pip install websocket-client

ws = ""
URL = "ws://jp-ai2018t.jp.trendnet.org:3001"
PLAYER = "19211_user_B"
#URL = "ws://JP-AI2018B.jp.trendnet.org:3001"
#PLAYER = "hgxetayn"

anyone_allin = False

def takeAction(ws, action, data):
    global anyone_allin
    if action == "__action":
        print("\n!!! __action !!!")
        round = data["game"]["roundName"]
        # 誰かがallinした場合は降りる
        if anyone_allin == True:
            sendAction(ws, "fold")
            return
        # Action for round
        if round == "Deal":
            takeActionForDeal(ws, action, data)
        elif round == "Flop":
            takeActionForFlop(ws, action, data)
        elif round == "Turn":
            takeActionForTurn(ws, action, data)
        elif round == "River":
            takeActionForRiver(ws, action, data)
        else:
            sendAction(ws, "call")
    elif action == "__bet":
        print("\n!!! __bet !!!")
        sendAction(ws, "check")
    elif action == "__show_action":
        print(data["action"]["action"])
        if data["action"]["action"] == "allin":
            anyone_allin = True
    elif action == "__new_round":
        print("\nNew round. Reset all global flags...")
        anyone_allin = False

def takeActionForDeal(ws, action, data):
    print("=== Action for Deal ===")
    hand,score,type,suitecount,straight = evaluate(data)
    print(hand,score,type,suitecount,straight)
    sendAction(ws, "call")

def takeActionForFlop(ws, action, data):
    print("=== Action for Flop ===")
    hand,score,type,suitecount,straight = evaluate(data)
    print(hand,score,type,suitecount,straight)
    if type == "High Card":
        # 現在役なし
        # かつ次のroundでストレートにならない
        # かつ最終的にフラッシュになる可能性がない
        # 場合は降りる
        if straight < 1 and suitecount < 3:
            sendAction(ws, "fold")
            return
    sendAction(ws, "call")

def takeActionForTurn(ws, action, data):
    print("=== Action for Turn ===")
    hand,score,type,suitecount,straight = evaluate(data)
    print(hand,score,type,suitecount,straight)
    if type == "High Card" or type == "Pair":
        # 現在の役がPair以下で、かつ次のroundでストレートにもフラッシュにもならない場合は降りる
        if straight < 1 and suitecount < 4:
            sendAction(ws, "fold")
            return
    # フルハウス以上の場合はraise
    if type == "Full House" or type == "Quads" or type == "Straight Flush":
        sendAction(ws, "raise")
        return
    sendAction(ws, "call")

def takeActionForRiver(ws, action, data):
    print("=== Action for River ===")
    hand,score,type,suitecount,straight = evaluate(data)
    print(hand,score,type,suitecount,straight)
    # Pair以下の場合は降りる
    if type == "High Card" or type == "Pair":
        sendAction(ws, "fold")
        return
    # フルハウス以上の場合はraise
    if type == "Full House" or type == "Quads" or type == "Straight Flush":
        sendAction(ws, "raise")
        return
    sendAction(ws, "call")

def sendAction(ws, action):
    print("Send \"{0}\" action".format(action))
    ws.send(json.dumps({
        "eventName": "__action",
        "data": {
            "action": action,
            "playerName": PLAYER
        }
    }))

def doListen():
    try:
        ws = create_connection(URL)
        ws.send(json.dumps({
            "eventName": "__join",
            "data": {
                "playerName": PLAYER
            }
        }))
        while 1:
            result = ws.recv()
            if (result == ""):
                print("ws.recv() failed.")
                break
            msg = json.loads(result)
            event_name = msg["eventName"]
            data = msg["data"]
            print(event_name)
            #print(data)
            takeAction(ws, event_name, data)
            if event_name == "__game_stop":
                print("game stopped.")
                break
        ws.close()
    except Exception as e:
        print(e.args)
        ws.close()


def maxsuitcount(cards):
    suit_counts = [len(list(group)) for key, group in itertools.groupby(sorted([x.suit for x in cards]))]
    return max(suit_counts)

def canbe_straight(cards):
    count = 0
    for c in [eval7.Card(x+"d") for x in eval7.ranks]:
        if not c.rank in [x.rank for x in cards]:
            hand_type = eval7.hand_type(eval7.evaluate(cards + [c]))
            if hand_type in ["Straight", "Straight Flush"]:
                count += 1
    return count


def evaluate(data):
    if data["game"]["board"] is not None:
        cards = data["self"]["cards"] + data["game"]["board"]
    else:
        cards = data["self"]["cards"]
    hand = [eval7.Card(x.capitalize()) for x in cards]
    score = eval7.evaluate(hand)
    type = eval7.hand_type(score)
    suitcount = maxsuitcount(hand)
    straight = canbe_straight(hand)
    return (hand,score,type,suitcount,straight)

if __name__ == '__main__':
    while 1:
        doListen()
        sleep(1)
        print("retry doListen()")