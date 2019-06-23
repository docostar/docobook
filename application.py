import os

from flask import Flask, session,render_template, request
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


@app.route("/")
def index():
    return render_template("index.html")
'''
@app.route("/home")
index()
'''
@app.route("/store",methods=['POST'])
def store():
    try:
        user_id = request.form.get("userid")
    except ValueError:
        return render_template("error.html", message="Invalid Userid.")

    try:
        password = request.form.get("password")
    except ValueError:
        return render_template("error.html", message="Invalid Password.")

    if db.execute("SELECT * FROM userlogin WHERE userid = :id", {"id": user_id}).rowcount == 0:
        return render_template("error.html", message="User doesn't exist.")
    else:
        dbpassword=db.execute("SELECT password FROM userlogin WHERE userid = :id", {"id": user_id}).fetchone()
        #dbpassword=dbpassword[2:-3]
        dbpassword=dbpassword.password
    #return render_template("store.html",username=dbpassword,mobile=password)

    if password==dbpassword:
        user=db.execute("SELECT name,mobile FROM userlogin WHERE userid = :id", {"id": user_id}).fetchone()
        #mobile=db.execute("SELECT mobile FROM userlogin WHERE userid = :id", {"id": user_id}).fetchone()
        return render_template("store.html",user=user)
    else:
        return render_template("error.html", message="Wrong Password")

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

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
