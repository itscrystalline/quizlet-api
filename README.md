# QuizletAPI
---
A python package attempting to make Quizlet study sets easier to access and use programmatically.

## Usage
`cd` into the directory where you want to install the package and run `git clone https://github.com/MyNameTsThad/quizlet-api.git`.

Then, `cd` into the `quizlet-api` directory and run `pip install -r requirements.txt` to install the required packages.

Now run `playwright install <browser>` to install the required playwright browsers. The available browsers are `chromium`, `firefox`, and `webkit`.

Then, in your python file, import the package with `import quizlet_api`.

Inside the package, there are three classes: `QuizletAPI`, `Card` and `WebServer`. `QuizletAPI` is the main class that you will use to access Quizlet study sets. `Card` represents each card in the study set. `WebServer` is a class that uses `QuizletAPI` to create a web server that allows you to access cards through HTTP requests.

### `QuizletAPI`
`QuizletAPI` is the main class that you will use to access Quizlet study sets. 

Create a `QuizletAPI` object with `QuizletAPI(id, engine)` where `id` is your Quizlet client ID and `engine` is the browser engine that you want to use. The available engines are `QuizletAPI.engine_chromium`, `QuizletAPI.engine_firefox`, and `QuizletAPI.engine_webkit`. These should correspond to the browsers that you installed with `playwright install <browser>`.

It has the following static functions:
- `QuizletAPI.GetDataByID(id, engine)` - Returns a python dictionary containing the raw data from Quizlet for the study set `id`.
- `QuizletAPI.GetDataOnPageByID(id, engine, page = 1, perpage = 500, token = "")` - Returns a python list containing the cards from Quizlet for the study set `id`, at page `page`, with `perpage` cards per page. `token` is the pagination token that you get from `QuizletAPI.GetPagingTokenByID(id)`. If `token` is not provided and `page` is not 1, it will throw an error.
- `QuizletAPI.GetPagingTokenByID(id, engine)` - Returns the pagination token for the study set `id`.

It has the following methods:
- `QuizletAPI.GetToken()` - Returns the pagination token for the study set.
- `QuizletAPI.GetCardSetRaw()` - Returns a python dictionary containing the raw data from Quizlet for the study set.
- `QuizletAPI.GetCardSet()` - Returns a list of `Card` objects for the study set.
- `QuizletAPI.GetCard(index)` - Returns a `Card` object for the card at index `index` in the study set.
- `QuizletAPI.GetCardRaw(index)` - Returns a python dictionary containing the raw data from Quizlet for the card at index `index` in the study set.
- `QuizletAPI.GetCreatorID()` - Returns the creator ID for the study set.
- `QuizletAPI.GetTotalCards()` - Returns the total number of cards in the study set.

It has the following static variables:
- `QuizletAPI.engine_chromium` - Chromium browser engine.
- `QuizletAPI.engine_firefox` - Firefox browser engine.
- `QuizletAPI.engine_webkit` - Webkit browser engine.
- `QuizletAPI.tts_slow` - Slow text-to-speech speed.
- `QuizletAPI.tts_normal` - Normal text-to-speech speed.

### `Card`
`Card` represents each card in the study set. 

It has the static function:
- `Card.fromSet()` - This is a utility function that returns a list of `Card` objects from a python dictionary containing the raw data from Quizlet for the study set.

It has the following methods:
- `Card.GetText(side)` - Returns the text on side `side` of the card.
- `Card.GetTexts()` - Returns a list of the text on both sides of the card.
- `Card.GetLanguage(side)` - Returns the language of side `side` of the card.
- `Card.GetLanguages()` - Returns a list of the languages of both sides of the card.
- `Card.GetUrlTextToSpeech(side, speed = QuizletAPI.tts_normal)` - Returns the URL for the text-to-speech audio of side `side` of the card. `speed` is the speed of the audio. The available preset speeds are `QuizletAPI.tts_slow`and `QuizletAPI.tts_normal`. You can also use a number more than 50 to set the speed.
- `Card.GetUrlTextToSpeechs(speed = QuizletAPI.tts_normal)` - Returns a list of the URLs for the text-to-speech audio of both sides of the card. `speed` is the speed of the audio. The available preset speeds are `QuizletAPI.tts_slow`and `QuizletAPI.tts_normal`. You can also use a number more than 50 to set the speed.

### `WebServer`
`WebServer` is a class that uses `QuizletAPI` to create a `flask` web server that allows you to access cards through HTTP requests.

Run the server using `WebServer.QuizletAPIWebServer.run(port = 8080)`. `port` is the port that the server will run on.

The server has the following endpoints:
- `/<ID>` - Loads the study set with ID `<ID>`.
- `/<ID>/cards/ - Returns a JSON list of the cards in the study set with ID `<ID>`.
- `/<ID>/card/<index>` - Returns a JSON object of the card at index `<index>` in the study set with ID `<ID>`.
- `/<ID>/card/<index>/texts` - Returns a JSON list of the text on both sides of the card at index `<index>` in the study set with ID `<ID>`.
- `/<ID>/card/<index>/languages` - Returns a JSON list of the languages of both sides of the card at index `<index>` in the study set with ID `<ID>`.
- `/<ID>/card/<index>/tts?speed=<speed | Normal>` - Returns a JSON list of the URLs for the text-to-speech audio of both sides of the card at index `<index>` in the study set with ID `<ID>`. `speed` is the speed of the audio. The available preset speeds are `Slow`and `Normal`. You can also use a number more than 50 to set the speed.
- `/<ID>/creatorid` - Returns the creator ID for the study set with ID `<ID>`.
- `/<ID>/totalcards` - Returns the total number of cards in the study set with ID `<ID>`.

