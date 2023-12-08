import json
import random
import time
import sys

from inspect import currentframe
from colorama import Fore, Back, Style

lengths = []
loadedData = {}

debug = False
colorize = True


def getLine():
    cf = currentframe()
    return cf.f_back.f_lineno


def col(code: str) -> str:
    return code if colorize else ""


def loadSet(target: str) -> None:
    global lengths
    global loadedData
    with open(target, encoding='utf8') as f:
        data = json.load(f)
        pools = data["pools"]
        loadedData = pools
        for pool in pools:
            lengths.append(pool["length"])

        debugPrint("Loaded", len(pools), "quiz pools with", sum(lengths), "cards total", getLine())
        debugPrint("Lengths:", lengths, getLine())


def saveSet(target: str) -> None:
    with open(target, "w", encoding='utf8') as opened:
        toSave = {
            "pools": loadedData
        }
        json.dump(toSave, opened, ensure_ascii=False)


def getCard(index: int) -> dict:
    pool_index: int = 0
    all_cards: int = 0
    for set_index, number_of_cards in enumerate(lengths):
        all_cards += number_of_cards
        if index > all_cards:
            pass
        else:
            all_cards -= number_of_cards
            pool_index = set_index
            break
    # debugPrint(pool_index, index, all_cards, getLine())

    card = loadedData[pool_index]["cards"][index - all_cards]
    card["pool_id"] = pool_index
    card["global_index"] = index

    return card


def setCardScore(index: int, score: int) -> None:
    card = getCard(index)
    debugPrint(card, getLine())
    localIndex = card["global_index"] - sum(lengths[:card["pool_id"]])
    debugPrint(localIndex, getLine())
    loadedData[card["pool_id"]]["cards"][localIndex] = {
        "side1": card["side1"],
        "side2": card["side2"],
        "score": score
    }


def getCardsRandom(num: int) -> list:
    # weighed random from card scores
    indices = []
    scores = []
    indexCount = 0
    cards = []
    for pool in loadedData:
        for card in pool["cards"]:
            indices.append(indexCount)
            indexCount += 1
            scores.append(1 + ((10 - (card["score"] + 5)) * 0.9))
    weights = [score / sum(scores) for score in scores]
    debugPrint("Weights:", weights, getLine())
    debugPrint("Indices:", indices, getLine())
    randomIndices = random.choices(indices, weights=weights, k=num)
    debugPrint("Random Indices:", randomIndices, getLine())
    for index in randomIndices:
        cards.append(getCard(index))

    return cards


def getCardsRandomFromPool(pool: int, num: int) -> list:
    return random.choices(loadedData[pool]["cards"], k=num)


def getQusetions(cards: list) -> list:
    questionsToReturn = []
    for card in cards:
        poolId = card["pool_id"]
        randomInPool = getCardsRandomFromPool(poolId, 3)
        answers = [card["side2"]] + [cardRandom["side2"] for cardRandom in randomInPool]
        random.shuffle(answers)
        question = {
            "question": card["side1"],
            "answers": answers,
            "correct": card["side2"],
            "global_index": card["global_index"],
            "score": card["score"]
        }
        questionsToReturn.append(question)

    return questionsToReturn


def mainLoop(questions: list) -> None:
    correctAnswers = 0
    quitEarly = False
    for num, question in enumerate(questions):
        print(col(Fore.CYAN), num + 1, "/", len(questions), ". ", col(Fore.GREEN), col(Back.BLACK),
              question["question"], " (", question["score"], ")", col(Style.RESET_ALL), sep="")
        spaces = " " * (len(str(num + 1)) + 5)
        correctAnswerIndex = -1
        for index, answer in enumerate(question["answers"]):
            print(f"{col(Style.BRIGHT)}{spaces}{index + 1}{col(Style.RESET_ALL)}. {answer}")
            if answer == question["correct"]:
                correctAnswerIndex = index + 1

        userAnswer = ""
        isValid = False

        while not isValid:
            userAnswer = input(col(Fore.CYAN) + "Answer (1-4, n for don't know): " + col(Fore.RESET))
            isValid = userAnswer == "q" or userAnswer == "n" or (userAnswer.isdigit() and 1 <= int(userAnswer) <= 4)
            print(col(Fore.RED) + "Invalid input!" + col(Fore.RESET)) if not isValid else None

        if userAnswer == "q":
            print(col(Fore.RED) + "You quit early!" + col(Fore.RESET))
            print(col(Fore.LIGHTYELLOW_EX) + "You answered", correctAnswers, "questions correctly out of", num,
                  "question(s)." + col(Fore.RESET))
            quitEarly = True
            break

        if userAnswer == "n":
            print(col(Fore.GREEN) + "Correct answer: ", col(Style.BRIGHT), correctAnswerIndex, ". ",
                  question["correct"], col(Fore.RESET),
                  sep="")
            question["score"] -= 1
            setCardScore(question["global_index"], question["score"])
            continue

        if int(userAnswer) == correctAnswerIndex:
            print(col(Fore.LIGHTGREEN_EX) + "Correct!:", question["score"], "->", question["score"] + 1,
                  col(Fore.RESET))
            question["score"] += 1
            setCardScore(question["global_index"], question["score"])
            correctAnswers += 1
        else:
            print(col(Fore.LIGHTRED_EX) + "Incorrect!:", question["score"], "->", question["score"] - 1,
                  col(Fore.RESET))
            print(col(Fore.GREEN) + "Correct answer: ", col(Style.BRIGHT), correctAnswerIndex, ". ",
                  question["correct"], col(Fore.RESET),
                  sep="")
            question["score"] -= 1
            setCardScore(question["global_index"], question["score"])

    print(col(Fore.LIGHTYELLOW_EX) + "You answered", correctAnswers, "questions correctly out of", len(questions),
          "questions." + col(Fore.RESET)) if not quitEarly else None


def parseArgs(args: list) -> list[list[str]]:
    global debug
    debug = "--debug" in args or "-d" in args if len(sys.argv) > 1 else False
    debugPrint("Debug mode enabled!", getLine())
    debugPrint("Raw Arguments:", args, getLine())

    parsedArgs = []
    for arg in args:
        if arg.startswith("-"):
            parsedArgs.append([arg])
        else:
            parsedArgs[-1].append(arg)

    debugPrint("Parsed Arguments:", parsedArgs, getLine())
    return parsedArgs


def interpretArgs(args: list[list[str]]) -> dict[str, str]:
    global colorize
    interpreted = {}
    for argGroup in args:
        if argGroup[0] == "--debug" or argGroup[0] == "-d":
            continue
        elif argGroup[0] == "--clear" or argGroup[0] == "-c":
            interpreted["toClear"] = True
        elif argGroup[0] == "--help" or argGroup[0] == "-h":
            print("Usage: python quiz.py [options]")
            print("Options:")
            print("  --help, -h: Display this help message.")
            print("  --debug, -d: Enable debug mode.")
            print("  --clear, -c: Clear all scores from the file specified in --file. If --file is not specified, "
                  "the program will exit.")
            print("  --file, -f: Load a specific file from a path.")
            print("  --dir, -D: Set a specific root directory to load files from. If --file is also specified, "
                  "this will be ignored.")
            print("  --num-cards, -n: Load a specific number of cards, default is 20.")
            print("  --no-colorize, -N: Disable colorization.")
            quit(0)
        elif argGroup[0] == "--dir" or argGroup[0] == "-D":
            if len(argGroup) < 2:
                print("FATAL: No directory name provided to load!")
                quit(1)

            if not argGroup[1].endswith("/"):
                argGroup[1] += "/"

            dirName = argGroup[1]
            interpreted["dir"] = dirName
        elif argGroup[0] == "--file" or argGroup[0] == "-f":
            if len(argGroup) < 2:
                print("FATAL: No file name provided to load!")
                quit(1)

            if not argGroup[1].endswith(".json"):
                print("FATAL: File name provided is not a .json file!")
                quit(1)

            fileName = argGroup[1]
            interpreted["file"] = fileName

        elif argGroup[0] == "--num-cards" or argGroup[0] == "-n":
            if len(argGroup) < 2:
                print("FATAL: No file name provided to load!")
                quit(1)

            try:
                numCards = int(argGroup[1])
            except ValueError:
                print("FATAL: Number of cards provided is not an integer!")
                quit(1)

            interpreted["numCards"] = numCards

        elif argGroup[0] == "--no-colorize" or argGroup[0] == "-N":
            interpreted["noColorize"] = True
            colorize = False
        else:
            print("WARNING: Unknown argument:", argGroup[0], "Continuing...")
            continue

    return interpreted


def debugPrint(*args) -> None:
    if debug:
        print(f"{col(Fore.RED)}[quiz.py:{args[-1]}]{col(Fore.YELLOW)}", *args[:-1], col(Style.RESET_ALL))


if __name__ == '__main__':
    args = sys.argv[1:]
    parsedArgs = parseArgs(args)
    interpreted = interpretArgs(parsedArgs)

    start = time.time()
    # extra argument handling
    if "file" in interpreted:
        if "toClear" in interpreted:
            print(col(Fore.YELLOW) + "Clearing scores from", interpreted["file"] + col(Fore.RESET))
            loadSet(interpreted["file"])
            for pool in loadedData:
                for card in pool["cards"]:
                    card["score"] = 0
            saveSet(interpreted["file"])
            print(col(Fore.GREEN) + "Done!" + col(Fore.RESET))
            quit(0)
        file = interpreted["file"]
        numRandom = interpreted["numCards"] if "numCards" in interpreted else 20
    elif "dir" in interpreted:
        dirName = interpreted["dir"]
        files = [[dirName + "N5.json", 20], [dirName + "N4.json", 10], [dirName + "N3.json", 5]]
        fileWeights = [0.5, 0.25, 0.125]

        result = random.choices(files, weights=fileWeights, k=1)[0]
        file = result[0]
        numRandom = result[1]
    else:
        files = [["N5.json", 20], ["N4.json", 10], ["N3.json", 5]]
        fileWeights = [0.5, 0.25, 0.125]

        result = random.choices(files, weights=fileWeights, k=1)[0]
        file = result[0]
        numRandom = result[1]

    # load the json file
    debugPrint("Loading", file, "with", numRandom, "random cards", getLine())
    print(col(Fore.CYAN), "=========>", file[:-5], f"({numRandom} questions)", "<=========")
    loadSet(file)

    # pick random cards
    randomCards = getCardsRandom(numRandom)
    questions = getQusetions(randomCards)
    debugPrint(questions, getLine())

    end = time.time()
    debugPrint("Preparation done in", end - start, "ms.", getLine())

    mainLoop(questions)

    saveSet(file)
