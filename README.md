# python_cowbull_server

## Version: 20.04
Python cowbull server is a Python 3.x Flask based http server, that serves the
cowbull game using python_cowbull_game objects. It serves up the game
by responding to http requests to ``http(s)://server:port/version/game`` and
decides the action based on the method used for the request: ``GET`` starts
a new game and ``POST`` makes a guess against the game.

The app can be launched on a number of platforms: laptop, Docker, Google App Engine, GKE, Docker, etc. In all platforms, there are dependencies (see below) which need to be included in the Python environment.

### Running Locally
To run the game server locally, the following (modified) commands need to be performed (validated on MacOS and assuming pip and virtualenv installed):

```
python3 -m virtualenv -p python3 ~/virtuals/cowbull_server
source ~/virtuals/cowbull_server/bin/activate
pip install -r image-requirements
deactivate
```

To test the program, run the following commands:

```
source ~/virtuals/cowbull_server/bin/activate
PERSISTER='{"engine_name": "file", "parameters": {}}' python main.py
```

> When run as above, the game will start a Flask non-production server offering the game on the localhost on port 5000. To validate the program is running, execute curl commands:

```
curl http://localhost:5000/v1/modes ; echo
curl http://localhost:5000/v1/game ; echo
```

Both curls should return results and a file should have been created in the /tmp directory with a .cow extension; for example: `/tmp/6970299e-2117-4787-beff-3d8c36612379.cow`

> Without specifying the persister, e.g. running `python main.py`, the game engine will expect a Redis instance available on localhost on port 6379. Use Docker to provide Redis as the default persistence engine; for example: `docker run --detach --name redis -p 6379:6370 redis:alpine3.11`


## Related Projects

* [python_digits](https://github.com/dsandersAzure/python_digits) : The python_digits object
used as the base of this game.
* [python_cowbull_game](https://github.com/dsandersAzure/python_cowbull_game) : A Flask
based server which serves up a web server offering the game to callers (human or machine)
* [python_cowbull_console](https://github.com/dsandersAzure/python_cowbull_console) : A
console based game which interacts with the server
* [python_cowbull_webapp](https://github.com/dsandersAzure/python_cowbull_webapp) : A single
page webapp which interacts with the web server using XHR (XMLHttpRequest).

## Depdendencies
All dependecies are included in the image-requirements file. **Note**, requirements.txt is used for specific scenarios (see below.)

## Requests
Make a request by issuing GET or POST methods to:
* `curl http://FLASK_HOST:FLASK_PORT/v0_1/game`

For added benefit, install [jq](https://stedolan.github.io/jq/) to be able 
to parse the JSON returned by the request:
* `curl -s <-X {method}> http://FLASK_HOST:FLASK_PORT/v0_1/game | jq`

### GET
> Remember to export FLASK_HOST (e.g. localhost) and FLASK_PORT (e.g. 5000)

Request (or get) a new game. An optional parameter mode
can be provided and state one of the game modes (easy, normal,
or hard).

* curl -s http://$FLASK_HOST:$FLASK_PORT/v1/game | jq

```
{
  "key": "d04c7555-465c-4f57-b749-4539a14e482b",
  "mode": "Normal",
  "digits": 4,
  "digit-type": 0,
  "guesses": 10,
  "served-by": "(machine-name)",
  "help-text": "This is the normal (default) game. You need to guess 4 digits in the right place and each digit must be a whole number between 0 and 9. There are 10 tries to guess the correct answer.",
  "instruction-text": "Enter 4 digits, each digit between 0 and 9 (0, 1, 2, 3, 4, 5, 6, 7, 8, and 9)."
}
```

* curl -s http://$FLASK_HOST:$FLASK_PORT/v1/game?mode=Easy | jq

```
{
  "key": "d01496ef-1339-40fe-8455-5c7f07f622c1",
  "mode": "Easy",
  "digits": 3,
  "digit-type": 0,
  "guesses": 6,
  "served-by": "(machine name)",
  "help-text": "Easy. You need to guess 3 digits in the right place and each digit must be a whole number between 0 and 9. There are 6 tries to guess the correct answer.",
  "instruction-text": "Enter 3 digits, each digit between 0 and 9 (0, 1, 2, 3, 4, 5, 6, 7, 8, and 9)."
}
```

* curl -s http://$FLASK_HOST:$FLASK_PORT/v1/game?mode=Hex | jq
```
{
  "key": "be8f461a-31de-4134-8edd-11dc99a49368",
  "mode": "Hex",
  "digits": 4,
  "digit-type": 1,
  "guesses": 10,
  "served-by": "(machine name)",
  "help-text": "Hex. You need to guess 4 digits in the right place and each digit must be a hexidecimal number between 0 and F. There are 10 tries to guess the correct answer.",
  "instruction-text": "Enter 4 digits, each digit between 0 and F (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, A, B, C, D, E, and F)."
}
```

### POST
Make a guess against an existing game, passing the key and
an array of Digits (integers between 0 and 9) as raw JSON data.

* curl -s -X POST -H "Content-type: application/json" -d '{"key":"0afbe262-c324-4bd4-bb87-a7c72739b852", "digits":[0, 1, 2, 3, 4, 5]}' http://$FLASK_HOST:$FLASK_PORT/v1/game | jq

```
{
  "game": {
    "key": "0afbe262-c324-4bd4-bb87-a7c72739b852",
    "status": "playing",
    "ttl": 3600,
    "mode": {
      "mode": "Hard",
      "priority": 30,
      "digits": 6,
      "digit_type": 0,
      "guesses_allowed": 6,
      "instruction_text": "Enter 6 digits, each digit between 0 and 9 (0, 1, 2, 3, 4, 5, 6, 7, 8, and 9).",
      "help_text": "Hard. You need to guess 6 digits in the right place and each digit must be a whole number between 0 and 9. There are only 6 tries to guess the correct answer."
    },
    "guesses_made": 1
  },
  "outcome": {
    "bulls": 0,
    "cows": 3,
    "analysis": [
      {
        "index": 0,
        "digit": 0,
        "match": false,
        "multiple": false,
        "in_word": false
      },
      {
        "index": 1,
        "digit": 1,
        "match": false,
        "multiple": false,
        "in_word": true
      },
      {
        "index": 2,
        "digit": 2,
        "match": false,
        "multiple": false,
        "in_word": true
      },
      {
        "index": 3,
        "digit": 3,
        "match": false,
        "multiple": false,
        "in_word": true
      },
      {
        "index": 4,
        "digit": 4,
        "match": false,
        "multiple": false,
        "in_word": false
      },
      {
        "index": 5,
        "digit": 5,
        "match": false,
        "multiple": false,
        "in_word": false
      }
    ],
    "status": "You have 0 bulls and 3 cows"
  },
  "served-by": "(machine name)"
}
```

Errors will be reported back to the caller via JSON; For example:

  * Incorrect number of digits:
 ```
curl -s -X POST -H "Content-type: application/json" -d '{"key":"0afbe262-c324-4bd4-bb87-a7c72739b852", "digits":[0, 1, 2, 3, 5]}' http://$FLASK_HOST:$FLASK_PORT/v1/game | jq

{
  "status": 400,
  "module": "GameMode",
  "method": "guess",
  "exception": "The DigitWord objects are of different lengths and so comparison fails.",
  "message": "There is a problem with the digits provided!"
}
 ```
  * Bad key:
```
curl -s -X POST -H "Content-type: application/json" -d '{"key":"0afbe262-c324-4bd4-bb87-a7c72739b8521", "digits":[0, 1, 2, 3, 4, 5]}' http://$FLASK_HOST:$FLASK_PORT/v1/game | jq

{
  "status": 400,
  "module": "GameServerController",
  "method": "post",
  "exception": "'Unable to open the key file: /tmp/0afbe262-c324-4bd4-bb87-a7c72739b8521.cow'",
  "message": "The request must contain a valid game key."
}
```
  * Bad JSON data:
```
curl -s -X POST -H "Content-type: application/json" -d '{"key":"0afbe262-c324-4bd4-bb87-a7c72739b852", "digit":[0, 1, 2, 3, 4, 5]}' http://$FLASK_HOST:$FLASK_PORT/v1/game | jq

{
  "status": 400,
  "module": "GameMode",
  "method": "__init__",
  "exception": "'digits'",
  "message": "The request must contain an array of digits called 'digits'"
}
```
