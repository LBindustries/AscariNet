from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

class User(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    passwd = db.Column(db.String(80))
    mac = db.Column(db.String(16))
    nome = db.Column(db.String(80))
    cognome = db.Column(db.String(80))
    classe = db.Column(db.String(2))
    email = db.Column(db.String(80))
    tipo = db.Column(db.Integer)

    def __init__(self, username, passwd, mac, nome, cognome, classe, email, tipo):
        self.username = username
        self.passwd = passwd
        self.mac = mac
        self.nome = nome
        self.cognome = cognome
        self.classe = classe
        self.email = email
        self.tipo = tipo

    def __repr__(self):
        return "<User {}>".format(self.username, self.passwd)

db.create_all()

nuovouser = User('admin', 'admin','undefined','undefined','undefined','undefined','undefined',1)
db.session.add(nuovouser)
db.session.commit()
