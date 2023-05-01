import websocket
import _thread
import time
import rel
import json
import requests

wsAPIBaseURL = "wss://api.graspity.com:8001"
restAPIBaseURL = "https://api.graspity.com:8000"

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXUyJ9.eyJpc3MiOiJncmFzcGl0eS5zdmMuYXV0aCIsInN1YiI6IlNvTzFoZ0FGLnBjZWc5T29fWnRDZ3cifQ.Gg2CBWm8Xkuh_csTygpr_dni_4SuYS_O-1tWhJ2CS2o"
userId = "SoO1hgAF.pceg9Oo_ZtCgw" # MY userId
communityId = "S9qGDgAF.oCXxEAKWPh1Ug"

def authAndSubscribe():
    auth = {"t": 3, "p": token, "ocid": "auth"}
    ws.send(json.dumps(auth))

    subs = {"t": 200, "p": {"communityId": communityId}, "ocid": "subscribe"}
    ws.send(json.dumps(subs))


def getLastMessages(channelId, offset, limit, filter):
    page = requests.get(
        restAPIBaseURL +
        "/communities/" + communityId +
        "/channels/" + channelId +
        "/messages/offset/" + str(offset) +
        "/limit/" + str(limit) +
        "/direction/1/?" + filter,
        headers = {"Authorization":"Bearer " + token}).json()
    return page

def sendReply(ws, channelId, originalMessage, replyText):

    msg = {
        "type": "TEXT",
        "authorDisplayName": "Hello Bot",
        "data": replyText,
        "tags": [],
        "mentions": [originalMessage["author"]]
    }

    requests.post(
        restAPIBaseURL +
        "/communities/" + communityId +
        "/channels/" + channelId +
        "/messages/" + str(originalMessage["index"]) +
        "/replies",
        data=json.dumps(msg),
        headers = {"Authorization":"Bearer " + token}
    )


def processPageAndReply(ws, channelId, originalMessage, page):

    if page["type"] != "CHANNEL_MESSAGE_PAGE":
        print("Error - can't obtain messages page")
        return

    messages = page["payload"]["items"]
    print("items-count=" + str(len(messages)))

    plainText = "";

    for item in messages:
        msg = item["object"]

        # Exclude bot's messages
        if msg["author"] != userId:
            plainText = msg["authorDisplayName"] + ": " + msg["data"] + "\n\n" + plainText

    replyText = "Hello [@" + originalMessage["authorDisplayName"] + "](mn:" + originalMessage["author"] + ")" + "\n\n"
    replyText += "Here the text I've processed: \n\n" \
                 "```\n" + \
                 plainText + \
                 "```\n\n" + \
                 "Regards,\nHello Bot"

    sendReply(ws, channelId, originalMessage, replyText)


def onBotMentioned(ws, channelId, message):

    # do not process own messages
    if message["author"] == userId:
        print("Oh it was me...")
        return

    print("BOT WAS MENTIONED IN CHANNEL " + channelId)

    if message["threadIndex"] is None:
        print("in public")
        page = getLastMessages(channelId, message["index"], 10, "")
        processPageAndReply(ws, channelId, message, page)
    else:
        print("in thread " + str(message["threadIndex"]))
        page = getLastMessages(channelId, message["index"], 10, "td=" + str(message["threadIndex"]))
        processPageAndReply(ws, channelId, message, page)



def on_message(ws, message):

    print(message)

    msg = json.loads(message)
    if msg["t"] == 1:
        pong = {"t": 2, "p": msg["p"]}
        ws.send(json.dumps(pong))

    elif msg["t"] == 100:

        channelId = msg["p"]["channelId"]

        # 0 - new message
        if msg["p"]["payload"]["type"] == 0:

            mentions = msg["p"]["payload"]["payload"]["mentions"]
            print("mentions=" + json.dumps(mentions));

            if userId in mentions:
                onBotMentioned(ws, channelId, msg["p"]["payload"]["payload"])


def on_error(ws, error):
    print(error)

def on_close(ws, close_status_code, close_msg):
    print("### closed ###")

def on_open(ws):
    print("Opened connection")
    print("Auth and subscribe...")
    authAndSubscribe()

if __name__ == "__main__":

    #websocket.enableTrace(True)
    ws = websocket.WebSocketApp(wsAPIBaseURL + "/ws",
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)

    ws.run_forever(dispatcher=rel, reconnect=5)  # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
    rel.signal(2, rel.abort)  # Keyboard Interrupt
    rel.dispatch()
