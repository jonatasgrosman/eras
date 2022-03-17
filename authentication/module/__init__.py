import logging.config
from flask import Flask
from pymongo import MongoClient

from module.util.cryptUtil import AESCipher

# APP INITIALIZATION

SECRET_KEY = 'supersecretkey'

config = {
    'APP_NAME': 'authentication-module',
    'APP_HOST': '0.0.0.0',
    'APP_PORT': 50000,
    'APP_VERSION': '0.19',
    'APP_STAGE': 'PRODUCTION',
    'CIPHER': AESCipher(SECRET_KEY),
    'SECRET_KEY': SECRET_KEY,
    'JWT_ALGORITHM': 'HS256',
    'JWT_SECRET_KEY': SECRET_KEY,
    'JWT_DELTA_EXPIRATION': 60 * 30000000000,  # 30 min (in seconds)
    'JWT_DELTA_LONG_EXPIRATION': 60 * 60 * 24 * 2,  # 2 days (in seconds)
    'MONGO_HOST': '0.0.0.0',
    'MONGO_PORT': 27017,
    'MONGO_DBNAME': 'authentication',
    'MONGO_USERNAME': None,
    'SMTP_HOST': 'smtp.email.com',
    'SMTP_PORT': 587,
    'SMTP_USE_TLS': True,
    'SMTP_SENDER': 'ERAS',
    'SMTP_LOGIN': 'mailer@email.com',
    'SMTP_PASSWORD': 'PASSWORD_HERE',
    'EMAIL_HEADER': '<div style="background:#2A3F54; height:80px; text-align:center; color:#FFFFFF; font-family:Arial;'
                    'line-height:80px;"><h3>ERAS</h3></div>',
    'EMAIL_FOOTER': '<div style="background:#2A3F54; height:150px; text-align:center; color:#FFFFFF; font-family:Arial;'
                    'line-height:150px;"></div>',
    'RECOVERY_PASSWORD_PAGE_URL': 'http://PAGE_URL_OR_IP[:PORT]/#/recovery-password',
    'RECOVERY_PASSWORD_EMAIL_SUBJECT': 'ERAS - password recovery',
    'RECOVERY_PASSWORD_EMAIL_MESSAGE': '<p>To recover your password please access the link below</p>',
    'WELCOME_PAGE_URL': 'http://localhost/#/recovery-password',
    'WELCOME_EMAIL_SUBJECT': 'ERAS - Welcome',
    'WELCOME_EMAIL_MESSAGE': '<p>Congratulations,</p> <p>You were invited to use ERAS platform, '
                                       'access the link below to complete your sign up</p>',
    'LOG_FILE_PATH': 'eras-authentication.log'
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


# import module.routes
import module.route.rootRoutes
import module.route.authRoutes
import module.route.userRoutes

