import os

from flask import Flask, session,render_template, request
#from flask_session import Session
#from sqlalchemy import create_engine
#from sqlalchemy.orm import scoped_session, sessionmaker

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
    return "<h1>Hello, Doco Book</h1>"
    #return render_template("index.html")

@app.route("/store",methods=['POST'])
def store():
    return render_template("store.html")

@app.route("/registration",methods=['GET', 'POST'])
def registration():
    return render_template("registration.html")

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
