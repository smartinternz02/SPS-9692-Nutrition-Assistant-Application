from decouple import config

from app import create_app, db
from config import Config

DEBUG = config('DEBUG', default=True, cast=bool)

# The configuration
get_config_mode = 'Debug'

app = create_app(Config)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=9000)

