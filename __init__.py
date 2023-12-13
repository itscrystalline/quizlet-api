from playwright.sync_api import sync_playwright, Playwright, BrowserType
import requests, json

print("This module is for get data from quizlet only!")

requests.packages.urllib3.disable_warnings()

__url = "https://quizlet.com/webapi/3.4/studiable-item-documents?filters%5BstudiableContainerId%5D=REPLACEHERE&filters%5BstudiableContainerType%5D=1&perPage=PERPAGEHERE&page=PAGEHERE"

Normal = "Normal"
Slow = "Slow"


def GetDataByID(id: int, engine: BrowserType, page: int = 1, perpage: int = 1, token: str = "") -> dict:
    """
    Get data (id is needed)
    :param id: int:
    :param engine: instance of the playwright engine, use `playwright.chromium`, `playwright.firefox`, `playwright.webkit`:
    :param page: int: page number:
    :param perpage: int: number of cards per page:
    :param token: str: token for next page:
    :return Raw json data in python format:
    """
    browser = engine.launch()
    page = browser.new_page()
    re_url = __url.replace("REPLACEHERE", str(id)).replace("PERPAGEHERE", str(perpage)).replace("PAGEHERE", str(page))

    if type(id) is not int:
        raise TypeError("Quizlet ID should be integer")
    if token != "":
        page.goto(re_url + "&pagingToken=" + token)
    else:
        page.goto(re_url)

    # other actions...
    content = page.inner_html("pre")
    browser.close()
    return json.loads(content)


def GetTokenByID(id: int) -> str:
    if type(id) is not int:
        raise TypeError("Quizlet ID should be integer")
    return json.loads(requests.get(__url.replace(str(id), "REPLACEHERE")).json())["responses"][0]["paging"]["token"]


def GetTokenByData(data: dict) -> str:
    return data["responses"][0]["paging"]["token"]


def GetCardSetByData(data: dict) -> list:
    return data["responses"][0]["models"]["studiableItem"]


def GetCardByData(data: dict, index: int = 0) -> dict:
    return data["responses"][0]["models"]["studiableItem"][index]


def GetIDByCardSet(cardSet: list) -> int:
    return cardSet[0]["studiableContainerId"]


def GetIDByCard(card: dict) -> int:
    return card["studiableContainerId"]


def GetCreatorIDByCardSet(cardSet: dict) -> int:
    return cardSet[0]["creatorId"]


def GetCreatorIDByCard(card: dict) -> int:
    return card["creatorId"]


def GetTotalCardsByData(data: dict) -> int:
    return data["responses"][0]["paging"]["total"]


class Card:
    def __init__(self, rawCardData: dict) -> None:
        self.side1 = rawCardData["cardSides"][0]["media"]
        self.side2 = rawCardData["cardSides"][1]["media"]

    def GetText(self, side: int) -> str:
        match side:
            case 1:
                return self.side1[0]["plainText"]
            case 2:
                return self.side2[0]["plainText"]
            case _:
                raise ValueError("side must be 1 or 2")

    def GetLanguage(self, side: int) -> str:
        match side:
            case 1:
                return self.side1[0]["languageCode"]
            case 2:
                return self.side2[0]["languageCode"]
            case _:
                raise ValueError("side must be 1 or 2")

    def GetUrlTextToSpeech(self, side: int, speed: int | float | str = "Normal") -> str:
        if speed == "Normal":
            match side:
                case 1:
                    try:
                        return "https://quizlet.com" + self.side1[0]["ttsUrl"]
                    except TypeError:
                        return None
                case 2:
                    try:
                        return "https://quizlet.com" + self.side2[0]["ttsUrl"]
                    except TypeError:
                        return None
                case _:
                    raise ValueError("side must be 1 or 2")

        elif speed == "Slow":
            match side:
                case 1:
                    try:
                        return "https://quizlet.com" + self.side1[0]["ttsSlowUrl"]
                    except TypeError:
                        return None
                case 2:
                    try:
                        return "https://quizlet.com" + self.side2[0]["ttsSlowUrl"]
                    except TypeError:
                        return None
                case _:
                    raise ValueError("side must be 1 or 2")

        elif speed < 50:
            raise ValueError(
                "Speed can't be less than 50%\nMust be 50 or more than or be either \"Normal\" or \"Slow\"")
        match side:
            case 1:
                # speedIndex : int = self.side1["ttsurl"].rfind("&speed")
                # tts = self.side1["ttsurl"][:speedIndex]
                # 2nd return
                try:
                    return "https://quizlet.com" + self.side1[0]["ttsurl"][
                                                   :self.side1[0]["ttsurl"].rfind("&speed")] + "&speed=" + str(speed)
                except TypeError:
                    return None
            case 2:
                try:
                    return "https://quizlet.com" + self.side2[0]["ttsurl"][
                                                   :self.side2[0]["ttsurl"].rfind("&speed")] + "&speed=" + str(speed)
                except TypeError:
                    return None
            case _:
                raise ValueError("side must be 1 or 2")


if __name__ == '__main__':
    with sync_playwright() as playwright:
        print(GetDataByID(5920504, playwright.firefox))
