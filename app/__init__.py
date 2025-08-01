
from flask import Flask
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'
    csrf.init_app(app)

    from app.routes.auth import auth
    app.register_blueprint(auth)

    from app.routes.main import main
    app.register_blueprint(main)

    from app.routes.teacher import teacher
    app.register_blueprint(teacher)

    return app
