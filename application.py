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


@app.route("/store",methods=['POST','GET'])
def store():
    #if request.method=='POST':
        #storevisit+=1
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
            return redirect(url_for("login"))

@app.route("/search",methods=['POST'])
def search():
    if 'username' in session:
        username = session['username']
        user=db.execute("SELECT name,mobile FROM userlogin WHERE userid = :id", {"id": username}).fetchone()

    isbn=request.form.get("isbn")
    title=request.form.get("title")
    author=request.form.get("author")


    '''
    searchstr=""
    if len(isbn)>0:
        searchstr+=" isbn like "+isbn;
    if len(searchstr)>0:
        searchstr+=" or"
    if len(title)>0:
        searchstr+=" title like "+title;
    if len(searchstr)>0:
        searchstr+=" or"
    if len(author)>0:
        searchstr+=" author like "+author;

    #books= db.execute("SELECT * FROM books where author like :author or title like :title or isbn like :isbn",{"author": author,"title": title,"isbn": isbn}).fetchall()
    #books= db.execute("SELECT * FROM books where:searchstr",{"searchstr": searchstr}).fetchall()
    '''

    books1=[]
    books2=[]
    books3=[]
    if len(isbn)>0:
        searchstr="%"+isbn+"%";
        books1=db.execute("SELECT * FROM books where isbn like :searchstr",{"searchstr":searchstr}).fetchall()

    if len(title)>0:
        searchstr="%"+title+"%";
        books2=db.execute("SELECT * FROM books where title like :searchstr",{"searchstr":searchstr}).fetchall()

    if len(author)>0:
        searchstr="%"+author+"%";
        books3=db.execute("SELECT * FROM books where author like :searchstr",{"searchstr":searchstr}).fetchall()

    books=books1+books2+books3

    return render_template("search.html",user=user,books=books)


@app.route("/books/<string:isbn>/<string:message>")
def book(isbn,message):
    if 'username' in session:
        book=db.execute("SELECT * FROM books where isbn=:searchstr",{"searchstr":isbn}).fetchone()
        reviews=db.execute("SELECT name,rating,userreview FROM review JOIN userlogin ON review.userid=userlogin.userid where isbn=:searchstr",{"searchstr":isbn}).fetchall()
        return render_template("book.html",book=book,reviews=reviews,message=message)
    else:
        return redirect(url_for('index'))

@app.route("/postreview/<string:isbn>")
def postreview(isbn):
    if 'username' in session:
        return render_template("postreview.html",isbn=isbn)
    else:
        return redirect(url_for('index'))

@app.route("/reviewadd/<string:isbn>",methods=['POST','GET'])
def reviewadd(isbn):
    if 'username' in session:
        username = session['username']
        rating=request.form['rating']
        userreview=request.form['review']
        if db.execute("SELECT * FROM review WHERE userid = :id and isbn=:isbn", {"id": username,"isbn":isbn}).rowcount == 0:
            db.execute("INSERT INTO review (rating,userreview,isbn,userid) VALUES (:rating,:userreview,:isbn,:userid)",
                    {"rating":rating,"userreview":userreview,"isbn": isbn, "userid": username})
            db.commit()
            return redirect(url_for('book',isbn=isbn,message="Your review added successfully."))
        else:
            db.execute("update review set rating=:rating,userreview=:userreview where userid= :userid and isbn= :isbn ",
                        {"rating":rating, "userreview":userreview,"userid":username,"isbn":isbn})
            db.commit()
            return redirect(url_for('book',isbn=isbn,message="Your review updated successfully."))


    else:
        return redirect(url_for('index'))


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
