import json

from flask import Flask, request
from quizlet_api.QuizletAPI import QuizletAPI

QuizletAPIWebServer = Flask(__name__)
loadedAPIs = {}


@QuizletAPIWebServer.route('/<quizletId>')
def load(quizletId):
    if quizletId in loadedAPIs:
        return json.dumps({"status": f"Already loaded", "id": quizletId}), 409
    try:
        loadedAPIs[quizletId] = QuizletAPI(int(quizletId), QuizletAPI.engine_firefox)
    except ValueError:
        return json.dumps({"status": "Invalid ID", "id": quizletId}), 400
    return json.dumps({"status": "Loaded ID", "id": quizletId}), 200


@QuizletAPIWebServer.route('/<quizletId>/cards')
def getcards(quizletId):
    if quizletId not in loadedAPIs:
        res, code = load(quizletId)
        if code != 200:
            return res
    return json.dumps({"status": "Success", "id": quizletId, "cards": loadedAPIs[quizletId].GetCardSetRaw()}), 200


@QuizletAPIWebServer.route('/<quizletId>/card/<index>')
def getcard(quizletId, index):
    if quizletId not in loadedAPIs:
        res, code = load(quizletId)
        if code != 200:
            return res

    try:
        index = int(index)
    except ValueError:
        return json.dumps({"status": "Invalid index", "id": quizletId}), 400

    return json.dumps({"status": "Success", "id": quizletId, "card": loadedAPIs[quizletId].GetCardRaw(index)}), 200


@QuizletAPIWebServer.route('/<quizletId>/card/<index>/texts')
def getcardtexts(quizletId, index):
    if quizletId not in loadedAPIs:
        res, code = load(quizletId)
        if code != 200:
            return res

    try:
        index = int(index)
    except ValueError:
        return json.dumps({"status": "Invalid index", "id": quizletId}), 400

    return json.dumps(
        {"status": "Success", "id": quizletId, "texts": loadedAPIs[quizletId].GetCard(index).GetTexts()}), 200


@QuizletAPIWebServer.route('/<quizletId>/card/<index>/languages')
def getcardlanguages(quizletId, index):
    if quizletId not in loadedAPIs:
        res, code = load(quizletId)
        if code != 200:
            return res

    try:
        index = int(index)
    except ValueError:
        return json.dumps({"status": "Invalid index", "id": quizletId}), 400

    return json.dumps(
        {"status": "Success", "id": quizletId, "languages": loadedAPIs[quizletId].GetCard(index).GetLanguages()}), 200


@QuizletAPIWebServer.route('/<quizletId>/card/<index>/tts')
def getcardtts(quizletId, index):
    if quizletId not in loadedAPIs:
        res, code = load(quizletId)
        if code != 200:
            return res

    try:
        index = int(index)
    except ValueError:
        return json.dumps({"status": "Invalid index", "id": quizletId}), 400

    speed = request.args.get('speed', default='Normal', type=str)

    # if speed is an int or float in string form, convert it to a int or float
    try:
        speed = int(speed)
    except ValueError:
        try:
            speed = float(speed)
        except ValueError:
            pass

    try:
        tts = loadedAPIs[quizletId].GetCard(index).GetUrlTextToSpeechs(speed=speed)
    except ValueError as e:
        return json.dumps({"status": str(e), "id": quizletId}), 400

    return json.dumps(
        {"status": "Success", "id": quizletId,
         "tts": tts}), 200


@QuizletAPIWebServer.route('/<quizletId>/creatorid')
def getcreatorid(quizletId):
    if quizletId not in loadedAPIs:
        res, code = load(quizletId)
        if code != 200:
            return res
    return json.dumps({"status": "Success", "id": quizletId, "creatorid": loadedAPIs[quizletId].GetCreatorID()}), 200


@QuizletAPIWebServer.route('/<quizletId>/totalcards')
def gettotalcards(quizletId):
    if quizletId not in loadedAPIs:
        res, code = load(quizletId)
        if code != 200:
            return res
    return json.dumps({"status": "Success", "id": quizletId, "totalcards": loadedAPIs[quizletId].GetTotalCards()}), 200


if __name__ == '__main__':
    QuizletAPIWebServer.run(port=1712)
