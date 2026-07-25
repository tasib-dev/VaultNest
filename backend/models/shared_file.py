from models.database import db


class SharedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(64), unique=True, nullable=False)

    username = db.Column(db.String(50), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
