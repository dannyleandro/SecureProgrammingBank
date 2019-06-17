# coding=utf-8
from flask import Flask,render_template,request,session,logging,url_for,redirect
from flaskext.mysql import MySQL
from passlib.hash import sha256_crypt

mysql = MySQL()
app = Flask(__name__)

#Configuracion de base de datos
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_PORT']= 3306
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']='admin'
app.config['MYSQL_DATABASE_DB']='Registro'

mysql.init_app(app)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/Home")
def home2():
    return render_template("home.html")

@app.route("/Registro", methods=["GET","POST"])
def Registro():
    
    if request.method == "POST":
        
        name = request.form.get("Nombre")
        username = request.form.get("Usuario")
        password = request.form.get("Contraseña")
        confirm = request.form.get("Confirmar Contraseña")
        secure_password = sha256_crypt.hash(str(password))
           
        if password == confirm:
            conn = mysql.connect()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users(name, username, password) VALUES(%s, %s, %s)", (name, username, secure_password))
            conn.commit()
            cursor.close()
            return redirect(url_for('ingresar'))
        else:
            return render_template("registro.html")
    
    else:
        return render_template("registro.html")


@app.route("/Ingresar",methods=["GET","POST"])
def ingresar():
    
    if request.method == "POST":
        
        username = request.form.get("Usuario")
        password = request.form.get("Contraseña") 
        secure_password = sha256_crypt.hash(str(password))


        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE username=%(username)s",{"username":username})
        userdb = cursor.fetchone()
        conn.commit()
        cursor.execute("SELECT password FROM users WHERE username=%(username)s",{"username":username})
        passdb = cursor.fetchone()
        conn.commit()
        cursor.close()
        
        if userdb[0] == username:
            if sha256_crypt.verify(password,passdb[0]):
                #passdb[0] == secure_password:
                return render_template("transacciones.html")  
            else: 
                return render_template("ingresar.html")
        else:
            return render_template("ingresar.html") 

    return render_template("ingresar.html")

@app.route("/Transacciones",methods=["GET","POST"])
def transacciones():
    
    if request.method == "POST":
        
        origen = request.form.get("origen")
        destino = request.form.get("destino") 
        otp = request.form.get("clave de autorización") 

        #Rutina para validar la OTP del cliente

        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT otp FROM otp WHERE username=%(username)s AND otp=%(otp)s",{"username":username,"otp":otp})
        otpdb = cursor.fetchone()
        conn.commit()
        cursor.close()
        
        if otpdb[0] == otp:
            if sha256_crypt.verify(password,passdb[0]):
                #passdb[0] == secure_password:
                return render_template("transacciones.html")  
            else: 
                return render_template("ingresar.html")
        else:
            return render_template("ingresar.html") 

    return render_template("ingresar.html")


app.run(debug=True)