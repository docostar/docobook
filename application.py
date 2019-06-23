import os

from flask import Flask,redirect,url_for,session,render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)


# Check for environment variable


if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
#homemsg="Userid or Password wrong."
#Session["username"] = "admin"



@app.route("/")
def index():
    if 'username' in session:
        username = session['username']
        user=db.execute("SELECT name,mobile FROM userlogin WHERE userid = :id", {"id": username}).fetchone()
        return render_template("store.html",user=user)
    return render_template("login.html",message="")

@app.route("/login",methods=['GET','POST'])
def login():
    return render_template("login.html",message="Useid or Password wrong")


@app.route("/store",methods=['POST'])
def store():
    user_id = request.form.get("userid")
    password = request.form.get("password")

    if db.execute("SELECT * FROM userlogin WHERE userid = :id", {"id": user_id}).rowcount == 0:
        #homemsg="userid "+ user_id+" doesn't exist."
        return redirect(url_for("login"))
        #return render_template("index.html", message="User doesn't exist.")
    else:
        dbpassword=db.execute("SELECT password FROM userlogin WHERE userid = :id", {"id": user_id}).fetchone()
        dbpassword=dbpassword.password

    if password==dbpassword:
        user=db.execute("SELECT name,mobile FROM userlogin WHERE userid = :id", {"id": user_id}).fetchone()
        session['username'] = user_id
        return render_template("store.html",user=user)
    else:
        #homemsg="Wrong Password"
        return redirect(url_for("login"))
        #return render_template("index.html", message="Wrong Password")

@app.route("/registration",methods=['GET', 'POST'])
def registration():
    return render_template("registration.html",message="")
@app.route("/succsess",methods=['POST'])
def succsess():
        userid=request.form.get("userid")
        if db.execute("SELECT * FROM userlogin WHERE userid = :id", {"id": userid}).rowcount != 0:
            return render_template("registration.html", message="userid "+ userid +" already exist.")

        else:
            password=request.form.get("password")
            name=request.form.get("usename")
            mobile=request.form.get("mobile")
            db.execute("INSERT INTO userlogin (userid,password,name,mobile) VALUES (:userid,:password,:name,:mobile)",
                    {"userid":userid,"password":password,"name": name, "mobile": mobile})
            db.commit()
            return render_template("success.html",userid=userid)

@app.route('/logout',methods=['GET', 'POST'])
def logout():
   # remove the username from the session if it is there
   session.pop('username', None)
   return redirect(url_for('index'))

if __name__ == '__main__':
    app.debug = True
    app.secret_key = "any random string"
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
