import os
class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True


class ProductionConfig(Config):
    DEBUG = False
    JWT_COOKIE_SECURE = True


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    DEVELOPMENT = True
    JWT_COOKIE_SECURE = False
    SSL_CONTEXT = 'adhoc'



class TestingConfig(Config):
    DEBUG = True
    TESTING = True


config = {
   'development': DevelopmentConfig,
   'testing': TestingConfig,

   'default': DevelopmentConfig
}