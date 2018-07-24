#! /usr/bin/env python
# -*- coding:utf-8 -*-
import time
from time import sleep
import json
import eval7
from websocket import create_connection
# pip install websocket-client

ws = ""
URL = "ws://jp-ai2018t.jp.trendnet.org:3001"
PLAYER = "19211_user_A"
#URL = "ws://JP-AI2018B.jp.trendnet.org:3001"
#PLAYER = "hgxetayn"

def takeAction(ws, action, data):
    if action == "__action":
        ws.send(json.dumps({
            "eventName": "__action",
            "data": {
                "action": "call",
                "playerName": PLAYER
            }
        }))
    elif action == "__bet":
        ws.send(json.dumps({
            "eventName": "__action",
            "data": {
                "action": "bet",
                "playerName": PLAYER,
                "amount": 100
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
            print(data)
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


def evaluate(cards):
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