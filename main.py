from flask import Flask
from flask import render_template
from flask import request
from flask import make_response
from flask import session
from flask import flash
from flask import g
from flask import redirect
from flask import url_for
from flask_mail import Mail
from flask_mail import Message

#from config import DevelopmentConfig

import forms

#from models import db
#from models import User
#from models import Comment
from dbconnect import connection

from passlib.hash import sha256_crypt
import random
from MySQLdb import escape_string as thwart
import datetime
import gc
import os
import sys
import platform
import subprocess
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'files'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
#app.config.from_object(DevelopmentConfig)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'Secreto'
app.DEBUG = True
app.MAIL_SERVER = 'smtp.gmail.com'
app.MAIL_PORT = 587
app.MAIL_USE_SSL = False
app.MAIL_USE_TLS = True
app.MAIL_USERNAME = 'pruebasprogramacion10@gmail.com'
app.MAIL_PASSWORD = 'pruebas123'

mail = Mail()


@app.before_request
def before_request():
    if 'username' not in session and request.endpoint in ['transaction', 'thistory', 'user']:
        return redirect(url_for('index'))
    elif 'username' in session and request.endpoint in ['login', 'register']:
        return redirect(url_for('user'))

@app.after_request
def after_request(response):
    print ('despues')
#    print g.test
    return response


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
#    print g.test
    title = "BankAndes"
    return render_template('index.html', title = title)

@app.route('/user')
def user():
#    print g.test
    username = session['username']
    account_id = session['account_id']

    c, conn = connection()

    accounts = c.execute("SELECT created_date, id, amount, last_use_date, active FROM accounts WHERE id = %s and active = %s LIMIT 1",[account_id, 'True'])
    accounts = c.fetchall()

    c.close()
    conn.close()
    gc.collect()

    title = "Home BankAndes"
    return render_template('user.html', title = title, username = username, accounts = accounts)

@app.route('/transactions', methods = ['GET','POST'])
def transaction():
    transaction_form = forms.TransactionForm(request.form)
    if request.method == 'POST' and 'file' not in request.files:
        if request.method == 'POST' and transaction_form.validate():
            c, conn = connection()
            user_id = session['user_id']
            username = session['username']
            account_id = session['account_id']

            account = c.execute("SELECT id, amount, active FROM accounts WHERE id = %s and active = %s LIMIT 1",[account_id, 'True'])
            account = c.fetchall()

            if len(account) != 0:
                amount = transaction_form.amount.data

                if amount <= 10000000:
                    if amount <= account[0][1]:
                        username_dest = transaction_form.desusername.data
                        account_dest = transaction_form.desaccount.data
                        user_dest = c.execute("SELECT users.id, username, accounts.id, active, amount FROM users JOIN accounts ON users.id = accounts.user_id WHERE accounts.id = %s and username = %s and active = %s LIMIT 1",[account_dest, username_dest, 'True'])
                        user_dest = c.fetchall()

                        if len(user_dest) != 0:
                            otp = transaction_form.otp.data
                            otp_val = c.execute("SELECT * FROM otps WHERE otp = %s and user_id = %s and active = %s LIMIT 1",[otp, user_id, 'True'])
                            otp_val = c.fetchall()

                            if len(otp_val) != 0:
                                type = 'Transferencia'
                                now = datetime.datetime.now()
                                format_now = now.strftime('%Y-%m-%d %H:%M:%S')

                                transaction = c.execute("INSERT INTO transactions (account_id, account_id_dest, username_dest, amount, type, otp, created_date) VALUES (%s, %s, %s, %s, %s, %s, %s)", [account_id, account_dest, username_dest, amount, type, otp, format_now])

                                c.execute("UPDATE otps SET active = %s, used_date = %s where otp = %s and user_id = %s", ['False', format_now, otp, user_id])

                                amount_o = account[0][1] - amount
                                c.execute("UPDATE accounts SET amount = %s, last_use_date = %s WHERE user_id = %s", [amount_o, format_now, user_id])

                                amount_d = user_dest[0][4] + amount
                                c.execute("UPDATE accounts SET amount = %s, last_use_date = %s WHERE user_id = %s", [amount_d, format_now, user_dest[0][0]])

                                conn.commit()
                                print ("Number of rows updated:",  c.rowcount)

                #UPDATE otps SET active = 'False', used_date = '2019-06-17 09:01:21' where otp = 732937357 and user_id = 6;

                                success_message = "Transaccion Realizada"
                                flash(success_message)
                            else:
                                error_message = "OTP no valido!"
                                flash(error_message)
                        else:
                            error_message = "usuario o cuenta destino no valido!"
                            flash(error_message)
                    else:
                        error_message = "monto excede fondos en la cuenta ..."
                        flash(error_message)
                else:
                    error_message = "monto supera maximo permitido (COP $ 10.000.000)!"
                    flash(error_message)
            else:
                error_message = "cuenta origen no existe o inactiva!"
                flash(error_message)

            c.close()
            conn.close()
            gc.collect()
    elif request.method == 'POST':
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            file.filename = "TransactionFile.txt"
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(platform.system())
            if platform.system() == 'Windows':
                if not os.path.exists('parseFiles.exe'):
                    subprocess.call(["gcc", "parseFiles.c", "-oparseFiles", "-std=c99", '-w', '-Ofast'], shell=True)
                # subprocess.call(["parseFiles"], shell=True, stdin=sys.stdin)
                result = os.popen("parseFiles").read()
                # print(result)
                if "StartReadingfile" in result:
                    result = result.replace('\n', '')
                    print(result[result.index("StartReadingfile", 0) + 16:-1])
                    data = result[result.index("StartReadingfile", 0) + 16:-1].split(';')
                    for transact in data:
                        fields = transact.split(',')
                        c, conn = connection()
                        user_id = session['user_id']
                        username = session['username']
                        account_id = session['account_id']

                        account = c.execute(
                            "SELECT id, amount, active FROM accounts WHERE id = %s and active = %s LIMIT 1",
                            [account_id, 'True'])
                        account = c.fetchall()

                        if len(account) != 0:
                            amount = int(fields[2])

                            if amount <= 10000000:
                                if amount <= account[0][1]:
                                    username_dest = fields[0]
                                    account_dest = fields[1]
                                    user_dest = c.execute(
                                        "SELECT users.id, username, accounts.id, active, amount FROM users "
                                        "JOIN accounts ON users.id = accounts.user_id WHERE accounts.id = %s "
                                        "and username = %s and active = %s LIMIT 1",
                                        [account_dest, username_dest, 'True'])
                                    user_dest = c.fetchall()

                                    if len(user_dest) != 0:
                                        otp = fields[3]
                                        otp_val = c.execute(
                                            "SELECT * FROM otps WHERE otp = %s and user_id = %s and active = %s LIMIT 1",
                                            [otp, user_id, 'True'])
                                        otp_val = c.fetchall()

                                        if len(otp_val) != 0:
                                            type = 'Transferencia'
                                            now = datetime.datetime.now()
                                            format_now = now.strftime('%Y-%m-%d %H:%M:%S')

                                            transaction = c.execute(
                                                "INSERT INTO transactions (account_id, account_id_dest, username_dest, amount, type, otp, created_date) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                                                [account_id, account_dest, username_dest, amount, type, otp,
                                                 format_now])

                                            c.execute(
                                                "UPDATE otps SET active = %s, used_date = %s where otp = %s and user_id = %s",
                                                ['False', format_now, otp, user_id])

                                            amount_o = account[0][1] - amount
                                            c.execute(
                                                "UPDATE accounts SET amount = %s, last_use_date = %s WHERE user_id = %s",
                                                [amount_o, format_now, user_id])

                                            amount_d = user_dest[0][4] + amount
                                            c.execute(
                                                "UPDATE accounts SET amount = %s, last_use_date = %s WHERE user_id = %s",
                                                [amount_d, format_now, user_dest[0][0]])

                                            conn.commit()
                                            print ("Number of rows updated:", c.rowcount)

                                            # UPDATE otps SET active = 'False', used_date = '2019-06-17 09:01:21' where otp = 732937357 and user_id = 6;

                                            success_message = "Transaccion Realizada"
                                            flash(success_message)
                                        else:
                                            error_message = "OTP no valido!"
                                            flash(error_message)
                                    else:
                                        error_message = "usuario o cuenta destino no valido!"
                                        flash(error_message)
                                else:
                                    error_message = "monto excede fondos en la cuenta ..."
                                    flash(error_message)
                            else:
                                error_message = "monto supera maximo permitido (COP $ 10.000.000)!"
                                flash(error_message)
                        else:
                            error_message = "cuenta origen no existe o inactiva!"
                            flash(error_message)

                        c.close()
                        conn.close()
                        gc.collect()

            else:
                if not os.path.exists('parseFiles.c'):
                    subprocess.call(["gcc", "parseFiles.c", "-oparseFiles", "-std=c99", '-w', '-Ofast'], shell=True)
                subprocess.call(["./parseFiles"], shell=True, stdin=sys.stdin)
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            title = "Transacciones BankAndes"
            return render_template('transaction.html', title=title, form=transaction_form)
    title = "Transacciones BankAndes"
    username = session['username']
    return render_template('transaction.html', title = title, form = transaction_form, username = username)


@app.route('/thistory', methods = ['GET'])
def thistory():
    c, conn = connection()
    account_id = session['account_id']
    sends = c.execute("SELECT created_date, account_id_dest, username_dest, amount FROM transactions WHERE account_id = %s ORDER BY created_date DESC LIMIT 10",[account_id, ])
    sends = c.fetchall()

    receivers = c.execute("SELECT created_date, account_id_dest, username_dest, amount FROM transactions WHERE account_id_dest = %s ORDER BY created_date DESC LIMIT 10",[account_id, ])
    receivers = c.fetchall()

    c.close()
    conn.close()
    gc.collect()

    title = "Transaction History"
    username = session['username']
    return render_template('thistory.html', sends = sends, receivers = receivers, title = title, username = username)

@app.route('/login', methods = ['GET', 'POST'])
def login():
        c, conn = connection()
#    try:
        login_form = forms.LoginForm(request.form)
        if request.method == 'POST' and login_form.validate():
            username = login_form.username.data
            password = login_form.password.data
            user = c.execute("SELECT users.id, username, password, accounts.id as account FROM users JOIN accounts ON users.id = accounts.user_id  WHERE username = %s LIMIT 1",[username, ])
            user = c.fetchall()
            if len(user) !=0:
                if sha256_crypt.verify(password, user[0][2]):
                    success_message = 'Bienvenido {} a BankAndes'.format(username)
                    flash(success_message)
                    session['username'] = username
                    session['user_id'] = user[0][0]
                    session['account_id'] = user[0][3]
                    c.close()
                    conn.close()
                    return redirect(url_for('transaction'))

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
    return redirect(url_for('index'))


def generar_otp(user_id, created_date):

    c, conn = connection()
    otp_list = []
    for r in range(1, 101):
        otp = random.randint(1000000, 999999999)
        row_o = [otp, user_id, created_date, created_date,'True']
        otp_row = c.execute("INSERT INTO otps (otp, user_id, created_date, used_date, active) VALUES (%s, %s, %s, %s, %s)", row_o)
        conn.commit()
        otp_list.append(otp)

    success_message = "100 Codigos de Validacion Creados"
    flash(success_message)

    c.close()
    conn.close()
    gc.collect()

    return otp_list

@app.route('/register', methods = ['GET', 'POST'])
def register():
    register_form = forms.RegisterForm(request.form)
    if request.method == 'POST' and register_form.validate():
        username = register_form.username.data
        email = register_form.email.data
        password = sha256_crypt.encrypt(str(register_form.password.data))
        c,conn = connection()
        user = c.execute("SELECT * FROM users where username = (%s)", [username, ])
        user = c.fetchall()
        print (len(user))
        if len(user)!=0:
            success_message ="{} ya existe, prueba uno diferente!".format(username)
            flash(success_message)
        else:
            now = datetime.datetime.now()
            format_now = now.strftime('%Y-%m-%d %H:%M:%S')
            c.execute("INSERT into users (username, password, email, created_date) VALUES (%s, %s, %s, %s)"
            ,(username, password, email, format_now))
            conn.commit()

            user = c.execute("SELECT * FROM users WHERE username = %s LIMIT 1",[username, ])
            user = c.fetchall()
            if len(user) !=0:
                user_id = user[0][0]
                otp_val = c.execute("SELECT * FROM otps WHERE user_id = %s and active = %s LIMIT 1",[user_id, 'True'])
                otp_val = c.fetchall()

                if len(otp_val) == 0:
                    otp_list = generar_otp(user_id, format_now)

                print (otp_list)

                in_amount = c.execute("SELECT * FROM accounts WHERE user_id = %s LIMIT 1",[user_id, ])
                in_amount = c.fetchall()

                if len(in_amount) == 0:
                    amount = 50000000
                    c.execute("INSERT into accounts (user_id, amount, created_date, last_use_date, active) VALUES (%s, %s, %s, %s, %s)",[user_id, amount, format_now, format_now, 'True'])
                    conn.commit()

            success_message = 'Felicitaciones. {} ha sido registrado!'.format(username)
            flash(success_message)

            c.close()
            conn.close()
            gc.collect()

            try:

                msg = Message('Gracias por su registro!',
                            sender = app.MAIL_USERNAME,
                            recipients = [user[0][3]])

                msg.html = render_template('email.html', user = user[0][1], otp_list = otp_list)
                mail.send(msg)
            except Exception as e:

                error_message = "El correo de confirmacion NO pudo ser enviado!"
                flash(error_message)
                return redirect(url_for('login'))

            return redirect(url_for('login'))

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
    mail.init_app(app)
    app.run(port=8080)
