import os
from routes.files import files
from routes.auth import auth
from flask import Flask
from models import db, User, SharedFile
from flask_login import LoginManager
from flask_mail import Mail, Message
from extensions import mail

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024 * 1024
app.config["SECRET_KEY"] = "fhdjugirjghi76786598645uyh8itrjbut9t8r7y8jsduhriutyghue"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cloud.db"
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "akt.cloud.storage@gmail.com"
app.config["MAIL_PASSWORD"] = "gqpjwynliqclekhg"


mail.init_app(app)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


app.register_blueprint(auth)
app.register_blueprint(files)


@app.route('/favicon.ico')
def favicon():
    return '', 204

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=5000, debug=True)
