import asyncio
import json
import requests
from playwright.async_api import async_playwright, BrowserType

requests.packages.urllib3.disable_warnings()


class QuizletAPI:
    __urlTemplate = "https://quizlet.com/webapi/3.4/studiable-item-documents?filters%5BstudiableContainerId%5D=REPLACEHERE&filters%5BstudiableContainerType%5D=1&perPage=PERPAGEHERE&page=PAGEHERE"
    tts_normal = "Normal"
    tts_slow = "Slow"
    engine_chromium = 0
    engine_firefox = 1
    engine_webkit = 2

    @staticmethod
    def GetPagingTokenByID(id: int) -> str:
        if type(id) is not int:
            raise TypeError("Quizlet ID should be integer")
        return \
            json.loads(requests.get(QuizletAPI.__urlTemplate.replace(str(id), "REPLACEHERE")).json())["responses"][0][
                "paging"][
                "token"]

    @staticmethod
    async def GetDataByID(id: int, engine: engine_chromium | engine_firefox | engine_webkit) -> dict:
        """
        Get data on a page (id is needed)
        :param id: int:
        :param engine: instance of the playwright engine, use `playwright.chromium`, `playwright.firefox`, `playwright.webkit`:
        :return Raw json data in python format:
        """
        data = await QuizletAPI.GetDataOnPageByID(id, engine)
        token = data["responses"][0]["paging"]["token"]
        fullResponse = data
        returnedLength = len(data["responses"][0]["models"]["studiableItem"])
        page = 2
        while returnedLength >= 500:
            data = await QuizletAPI.GetDataOnPageByID(id, engine, token=token, page=page)
            token = data["responses"][0]["paging"]["token"]
            fullResponse["responses"][0]["models"]["studiableItem"] += data["responses"][0]["models"]["studiableItem"]
            returnedLength = len(data["responses"][0]["models"]["studiableItem"])
            page += 1
        return fullResponse

    @staticmethod
    async def GetDataOnPageByID(id: int, engine: engine_chromium | engine_firefox | engine_webkit, page: int = 1,
                                perpage: int = 500, token: str = "", keepSession: bool = False, ) -> dict:
        """
        Get data on a page (id is needed)
        :param id: int:
        :param engine: instance of the playwright engine, use `playwright.chromium`, `playwright.firefox`, `playwright.webkit`:
        :param page: int: page number:
        :param perpage: int: number of cards per page:
        :param token: str: token for next page:
        :return Raw json data in python format:
        """
        async with async_playwright() as playwright:
            match engine:
                case QuizletAPI.engine_chromium:
                    engine = playwright.chromium
                case QuizletAPI.engine_firefox:
                    engine = playwright.firefox
                case QuizletAPI.engine_webkit:
                    engine = playwright.webkit

            browser = await engine.launch()
            webpage = await browser.new_page()
            re_url = QuizletAPI.__urlTemplate.replace("REPLACEHERE", str(id)).replace("PERPAGEHERE",
                                                                                      str(perpage)).replace("PAGEHERE",
                                                                                                            str(page))

            if type(id) is not int:
                raise TypeError("Quizlet ID should be integer")
            if token != "":
                await webpage.goto(re_url + "&pagingToken=" + token)
            else:
                await webpage.goto(re_url)

            # other actions...
            content = await webpage.inner_html("pre")
            await browser.close()
            return json.loads(content)
        raise ValueError("playwright errored or something")

    def __init__(self, id: int, engine: engine_webkit | engine_chromium | engine_firefox):
        self.id = id
        self.data = asyncio.run(QuizletAPI.GetDataByID(id, engine))

    def GetToken(self) -> str:
        return self.data["responses"][0]["paging"]["token"]

    def GetCardSetRaw(self) -> list:
        return self.data["responses"][0]["models"]["studiableItem"]

    def GetCardSet(self) -> list:
        return Card.fromSet(self.GetCardSetRaw())

    def GetCardRaw(self, index: int = 0) -> dict:
        return self.data["responses"][0]["models"]["studiableItem"][index]

    def GetCard(self, index: int = 0):
        return Card(self.GetCardRaw(index))

    def GetQuizletID(self) -> int:
        return self.data["responses"][0]["models"]["studiableItem"][0]["studiableContainerId"]

    def GetCreatorID(self) -> int:
        return self.data["responses"][0]["models"]["studiableItem"][0]["creatorId"]

    def GetTotalCards(self) -> int:
        return self.data["responses"][0]["paging"]["total"]


class Card:
    @staticmethod
    def fromSet(set: list[dict]) -> list:
        cards = []
        for card in set:
            cards.append(Card(card))
        return cards

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
