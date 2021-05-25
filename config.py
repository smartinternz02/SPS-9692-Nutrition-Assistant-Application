from decouple import config


class Config(object):
    # Set up the App SECRET_KEY
    SECRET_KEY = config('SECRET_KEY', default='S#perS3crEt_007')

    # This will create a file in <app> FOLDER
    username = 'uGTTV26l2O'
    password = '0mU7gEQYJc'
    server = 'remotemysql.com'
    database = 'uGTTV26l2O'
    SQLALCHEMY_DATABASE_URI = 'mysql://'+ username + ':' + password + '@' + server + '/' + database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True


