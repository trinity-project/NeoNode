import os
from app import app

ENVIRON=os.environ


if ENVIRON.get("CURRENT_ENVIRON") == "mainnet":
    host = "0.0.0.0"
    debug = False
else:

    host = "0.0.0.0"
    debug = True

if __name__ == '__main__':
    app.run(host=host, port=21332, debug=debug)
