import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = "dev-secret-key-change-me"
    APP_NAME = "AGROTEK AI"
    APP_SUBTITLE = "Spatial Agriculture Intelligence Platform"
    APP_REGION = "Kabupaten Jember, Jawa Timur"


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
