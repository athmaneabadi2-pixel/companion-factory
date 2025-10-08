\# Tests \& CI (Companion Factory)



\## Tests locaux (smoke)

Prérequis : Python 3.13, `pip install pytest requests python-dotenv`



```cmd

set START\_LOCAL=1

set START\_CMD=.\\scripts\\run\_server.bat  ^  rem ou: python app.py

set BASE\_URL=http://127.0.0.1:5000

set INTERNAL\_TOKEN=dev-123

pytest -q -s



