from flask import Flask
from config import config


def create_app(config_name="default"):
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config.from_object(config[config_name])

    from app.routes.main import main_bp
    from app.routes.dashboard import dashboard_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(dashboard_bp)

    return app