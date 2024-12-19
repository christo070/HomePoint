"""
The configuration file will be used only if `run.py` is executed by
    $ python3 run.py
not by
    $ flask run
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run()