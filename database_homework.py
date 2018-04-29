from flask import Flask
from apps.cms import bp as cms_bp
import config


def create_app():
    app = Flask(__name__)
    app.register_blueprint(cms_bp)
    app.config.from_object(config)
    return app

app = create_app()


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
