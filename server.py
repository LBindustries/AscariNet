from flask import Flask, session, url_for, redirect, request, render_template, abort
from flask_sqlalchemy import SQLAlchemy
import sys
app = Flask(__name__)
app.secret_key = "fantabosco" #chiave dell'app

# SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db' #indirizzo del db
db = SQLAlchemy(app)

class User(db.Model): #classi del db
    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    passwd = db.Column(db.String(80))
    mac = db.Column(db.String(16))
    nome = db.Column(db.String(80))
    cognome = db.Column(db.String(80))
    classe = db.Column(db.String(2))
    email = db.Column(db.String(80))
    tipo = db.Column(db.Integer())

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


# Funzioni del sito
def login(username, password): #funzione di login
    user = User.query.filter_by(username=username).first()
    try:
        return password == user.passwd
    except AttributeError:
        # Se non esiste l'Utente
        return False
def establishAuth(username): #funzione per permessi amministrativi
    print(username)
    user = User.query.all()
    for utenze in user:
        if username == utenze.username:
            return utenze.tipo
# Sito
@app.route('/') #radice del sito, viene anche utilizzato per il logoff
def page_home():
    if 'username' not in session:
        return redirect(url_for('page_login'))
    else: #logoff, metti il codice per il cambio delle password prima del session.pop()
        session.pop('username')
        return redirect(url_for('page_login'))

@app.route('/login', methods=['GET', 'POST']) #pagina di login
def page_login():
    if request.method == 'GET': #se viene visualizzata
        css = url_for("static", filename="style.css")
        return render_template("login.html.j2", css=css)
    else: #se viene inviato un POST
        if login(request.form['username'], request.form['password']):
            session['username'] = request.form['username']
            return redirect(url_for('page_dashboard', user=session['username']))
        else: #se la password immessa dall'utente è inesatta
            abort(403)

@app.route('/dashboard') #dashboard
def page_dashboard():
    banner = url_for("static", filename="banner.png") #risorse
    banner2 = url_for("static", filename="banner2.png")
    css = url_for("static", filename="style.css")
    if 'username' not in session: #se l'utente non è autenticato
        abort(403)
    else: #se l'utente è autenticato
        return render_template("dashboard.html.j2", css=css, user=session['username'], banner=banner, banner2=banner2)

@app.route('/user_add', methods=['GET', 'POST']) #pagina di aggiunta
def page_user_add():
    banner = url_for("static", filename="banner.png") #risorse
    banner2 = url_for("static", filename="banner2.png")
    css = url_for("static", filename="style.css")
    if 'username' not in session: #se l'utente non è autenticato
        return render_template("dashboard.html.j2", css=css, user=session['username'], banner=banner, banner2=banner2)
    if request.method == 'GET': #se viene visualizzata la pagina
        if establishAuth(session['username']) == 1:  #se l'utente è amministratore
            css = url_for("static", filename="style.css")
            return render_template("User/add.html.j2", css=css, type="utenti", user=session["username"], banner2=banner2)
        else: #se l'utente non è amministratore
            abort(403)
    else:
        nuovouser = User(request.form['username'], request.form['passwd'], request.form['mac'], request.form['nome'], request.form['cognome'], request.form['classe'], request.form['email'], 2) #crea un nuovo utente
        db.session.add(nuovouser) #aggiunge l'utente al db
        db.session.commit() #commit del db
        return redirect(url_for('page_user_list'))

@app.route('/user_del/<int:uid>') #pagina di rimozione, riceve come parametro un intero dalla pagina web
def page_user_del(uid):
    banner = url_for("static", filename="banner.png") #risorse
    banner2 = url_for("static", filename="banner2.png")
    css = url_for("static", filename="style.css")
    if 'username' not in session and establishAuth(session['username']) != 1: #se l'utente non è amministratore o non è autenticato
        return render_template("dashboard.html.j2", css=css, user=session['username'], banner=banner, banner2=banner2)
    user = User.query.get(uid) #ricerca dell'utente per primary-key
    db.session.delete(user) #rimozione utente
    db.session.commit() #commit del db
    return redirect(url_for('page_user_list'))

@app.route('/user_list') #lista utente
def page_user_list():
    banner = url_for("static", filename="banner.png") #risorse
    banner2 = url_for("static", filename="banner2.png")
    css = url_for("static", filename="style.css")
    if 'username' not in session: #se l'utente non è autenticato
        return render_template("dashboard.html.j2", css=css, user=session['username'], banner=banner, banner2=banner2)
    if  establishAuth(session['username']) != 1: #se l'utente non è amministratore
        return render_template("dashboard.html.j2", css=css, user=session['username'], banner=banner, banner2=banner2)
    users = User.query.all() #query di tutti gli utenti
    css = url_for("static", filename="style.css")
    return render_template("User/list.html.j2", css=css, users=users, type="utenti", user=session["username"])

@app.route('/user_show/<int:uid>', methods=['GET', 'POST']) #funzione di modifica, riceve come parametro un intero dalla pagina web
def page_user_show(uid):
    banner = url_for("static", filename="banner.png") #risorse
    banner2 = url_for("static", filename="banner2.png")
    css = url_for("static", filename="style.css")
    if 'username' not in session and establishAuth(session['username']) != 1: #se l'utente non è amministratore o non è autenticato
        return redirect(url_for('page_dashboard'))
    if request.method == "GET": #se la pagina viene visualizzata
        if establishAuth(session['username']) == 1: #una precauzione se per qualche motivo non va il controllo sopra
            users = User.query.get(uid)
            css = url_for("static", filename="style.css")
            return render_template("User/show.html.j2", css=css, users=users, user=session["username"])
        else:
            return render_template("dashboard.html.j2", css=css, user=session['username'], banner=banner, banner2=banner2)
    else:
        users = User.query.get(uid) #ricerca dell'utente
        users.username = request.form["username"] #sovrascrittura parametri
        users.passwd = request.form["passwd"]
        users.mac = request.form["mac"]
        users.nome = request.form["nome"]
        users.cognome = request.form["cognome"]
        users.classe = request.form["classe"]
        users.email = request.form["email"]
        db.session.commit() #commit del db
        return redirect(url_for('page_user_list'))

@app.route('/user_blacklist/<int:uid>', methods=['GET', 'POST']) #funzione per la blacklist, riceve come parametro un intero dalla pagina
def page_user_blacklist(uid):
    banner = url_for("static", filename="banner.png") #risorse
    banner2 = url_for("static", filename="banner2.png")
    css = url_for("static", filename="style.css")
    if 'username' not in session and establishAuth(session['username']) != 1: #se l'utente non è amministratore o non è autenticato.
        return render_template("dashboard.html.j2", css=css, user=session['username'], banner=banner, banner2=banner2)
    user = User.query.get(uid) #query per uid
    if user.tipo == 2:
        user.tipo = 3
    elif user.tipo == 3:
        user.tipo = 2
    db.session.commit() #commit
    return redirect(url_for('page_user_list'))
