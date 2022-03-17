import logging.config
from flask import Flask
from pymongo import MongoClient

# APP INITIALIZATION

config = {
    'APP_NAME': 'data-module',
    'APP_HOST': '0.0.0.0',
    'APP_PORT': 50001,
    'APP_VERSION': '0.19',
    'APP_STAGE': 'PRODUCTION',
    'AUTHENTICATION_HOST': 'http://0.0.0.0:50000',
    'AUTHENTICATION_LOGIN': 'data@eras',
    'AUTHENTICATION_PASSWORD': 'pass',
    'NLP_HOST': 'http://0.0.0.0:50002',
    'MONGO_HOST': '0.0.0.0',
    'MONGO_PORT': 27017,
    'MONGO_DBNAME': 'data',
    'MONGO_USERNAME': None,
    'MONGO_PASSWORD': None,
    'LOG_FILE_PATH': 'eras-data.log'
}

db = MongoClient(config['MONGO_HOST'], config['MONGO_PORT'])[config['MONGO_DBNAME']]

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
import module.route.rootRoutes
import module.route.projectRoutes
import module.route.ontologySummaryRoutes
import module.route.documentPackageRoutes
import module.route.documentRoutes
