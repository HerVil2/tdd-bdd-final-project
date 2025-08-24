from flask import Flask
from service.models import Product, db
from service.routes import bp as api


def create_app(testing: bool = False) -> Flask:
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI=(
            "sqlite:///:memory:" if testing else "sqlite:///products.db"
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        TESTING=testing,
    )

    Product.init_db(app)
    app.register_blueprint(api) 
    return app


app = create_app()
