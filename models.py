from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields
from passlib.apps import custom_app_context as pwd_context

db = SQLAlchemy()

class Base(db.Model):
    __abstract__ = True
    created_on = db.Column(db.DateTime, default=db.func.now())
    updated_on = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

class Puzzle(Base):
    id = db.Column(db.Integer, primary_key = True)
    game_url = db.Column(db.String(200), unique=True, nullable=True)
    fen = db.Column(db.String(100), unique=True, nullable=False)
    solution = db.Column(db.String(100), nullable=True)
    
    def __repr__(self):
        return "<Puzzle {}>".format(self.fen)

class PuzzleSerializer(Schema):
    id = fields.Integer()
    game_url = fields.Str()
    fen = fields.Str()
    solution = fields.Str()

class User(Base):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)
    
    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)