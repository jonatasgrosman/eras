import logging.config
from flask import Flask

# APP INITIALIZATION

config = {
    'APP_NAME': 'nlp-module',
    'APP_HOST': '0.0.0.0',
    'APP_PORT': 50002,
    'APP_VERSION': '0.19',
    'APP_STAGE': 'PRODUCTION',
    'AUTHENTICATION_HOST': 'http://0.0.0.0:50000',
    'AUTHENTICATION_LOGIN': 'nlp@eras',
    'AUTHENTICATION_PASSWORD': 'pass',
    'FREELING_HOST': {'pt-br': '0.0.0.0','en-us': '0.0.0.0'},
    'FREELING_PORT': {
        'pt-br': {'default': 50040, 'with-smart-word-segmentation': 50041},
        'en-us': {'default': 50050, 'with-smart-word-segmentation': 50051}
    },
    'DATA_HOST': 'http://0.0.0.0:50001',
    'LOG_FILE_PATH': 'eras-nlp.log'
}

# FLASK INITIALIZATION

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,email,token')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

# LOGGING INITIALIZATION

# load config from file
# logging.config.fileConfig('logging.ini', disable_existing_loggers=False)

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'root': {
        'level': 'NOTSET',
        'handlers': ['console', 'file'],
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'detailed',
            'stream': 'ext://sys.stdout',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': config['LOG_FILE_PATH'],
            'mode': 'a',
            'maxBytes': 10485760, # 10MB
            'backupCount': 5,
        }
    },
    'formatters': {
        'detailed': {
            'format': '%(asctime)s %(module)-17s line:%(lineno)-4d %(levelname)-8s %(message)s',
        }
    }
})


# import module.old_routes
import module.route.tokenizerPostaggerRoutes
