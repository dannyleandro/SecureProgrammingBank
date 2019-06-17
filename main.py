from flask import Flask
from flask import render_template
from flask import request
from flask import make_response
from flask import session
from flask import flash
from flask import g
from flask import redirect
from flask import url_for

#from config import DevelopmentConfig

import forms

#from models import db
#from models import User
#from models import Comment
from dbconnect import connection

from passlib.hash import sha256_crypt
from MySQLdb import escape_string as thwart
import datetime
import gc

app = Flask(__name__)
#app.config.from_object(DevelopmentConfig)
app.secret_key = 'Secreto'

@app.before_request
def before_request():
    if 'username' not in session and request.endpoint in ['comment']:
        return redirect(url_for('login'))
    elif 'username' in session and request.endpoint in ['login', 'register']:
        return redirect(url_for('index'))

@app.after_request
def after_request(response):
    print 'despues'
#    print g.test
    return response

@app.route('/')
def index():
#    print g.test
    if 'username' in session:
        username = session['username']
        user_id = session['user_id']
        print username

    title = "BankAndes"
    return render_template('index.html', title = title)

@app.route('/comment', methods = ['GET','POST'])
def comment():
    c, conn = connection()
    comment_form = forms.CommentForm(request.form)
    if request.method == 'POST' and comment_form.validate():
        user_id = session['user_id']
        print user_id
        now = datetime.datetime.now()
        text = comment_form.comment.data
        print text
        format_now = now.strftime('%Y-%m-%d %H:%M:%S')
        print format_now
        comment = c.execute("INSERT into comments (user_id, text, created_date) VALUES (%s, %s, %s)", [user_id, text, format_now])
        conn.commit()

        success_message = 'Nuevo comentario creado!'
        flash(success_message)

    c.close()
    conn.close()
    gc.collect()

    title = "BankAndes"
    return render_template('comment.html', title = title, form = comment_form)
"""
@app.route('/reviews', methods = ['GET'])
def reviews():
    comments = Comment.query.join(User).add_columns(User.username, Comment.text)
    return render_template('reviews.html', comments = comments)
"""
@app.route('/login', methods = ['GET', 'POST'])
def login():
        c, conn = connection()
#    try:
        login_form = forms.LoginForm(request.form)
        if request.method == 'POST' and login_form.validate():
            username = login_form.username.data
            print username
            password = login_form.password.data
            print password
            user = c.execute("SELECT * FROM users WHERE username = %s LIMIT 1",[username, ])
            user = c.fetchall()
            print  len(user)
            if len(user) !=0:
                if sha256_crypt.verify(password, user[0][2]):
                    success_message = 'Bienvenido {} a BankAndes'.format(username)
                    flash(success_message)
                    session['username'] = username
                    session['user_id'] = user[0][0]
                    c.close()
                    conn.close()
                    return redirect(url_for('index'))

            error_message = "usuario o contrasena no validos!"
            flash(error_message)

        c.close()
        conn.close()
        gc.collect()
        title = "Login BankAndes"
        return render_template('login.html', title = title, form = login_form)

#    except Exception as e:
        #flash(e)
#        c.close()
#        conn.close()
#        gc.collect()
#        error = "usuario o contrasena no validos!"
#        return render_template("login.html", error = error, title = title, form = login_form)

@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    if 'username' in session:
        session.clear()
        success_message = "has cerrado sesion correctamente!"
        flash(success_message)
    return redirect(url_for('login'))

@app.route('/register', methods = ['GET', 'POST'])
def register():
    register_form = forms.RegisterForm(request.form)
    if request.method == 'POST' and register_form.validate():
        username = register_form.username.data
        print username
        email = register_form.email.data
        print email
        password = sha256_crypt.encrypt(str(register_form.password.data))
        print password
        c,conn = connection()
        user = c.execute("SELECT * FROM users where username = (%s)", [username, ])
        user = c.fetchall()
        print len(user)
        if len(user) != 0:
            success_message = '{} ya existe, prueba uno diferente!'.format(username)
            flash(success_message)
        else:
            now = datetime.datetime.now()
            format_now = now.strftime('%Y-%m-%d %H:%M:%S')
            c.execute("INSERT into users (username, password, email, created_date) VALUES (%s, %s, %s, %s)"
            ,(username, password, email, format_now))
            conn.commit()

            success_message = 'Felicitaciones. {} ha sido registrado!'.format(username)
            flash(success_message)

            c.close()
            conn.close()
            gc.collect()
            return redirect (url_for('login'))

        c.close()
        conn.close()
        gc.collect()

    title = "Register BankAndes"
    return render_template('register.html', title = title, form = register_form)


#@app.route('/cookie')
#def cookie():
#    response = make_response( render_template('index.html'))
#    response.set_cookie('custome_cookie', 'Token')
#    return response


if __name__ == '__main__':
#    db.init_app(app)
#    with app.app_context():
#        db.create_all()
    app.run(port=8080)
