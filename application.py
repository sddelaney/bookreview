import os

from flask import Flask, session, render_template, request, redirect, jsonify
from flask_session import Session
from sqlalchemy import create_engine, func
from sqlalchemy.orm import scoped_session, sessionmaker
import requests
from helpers import login_required, apology
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
import json
from models import *

app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "POST":

        isbn, title, author =request.form.get("isbn"), request.form.get("title"), request.form.get("author") 
        if isbn:
            rows = Books.query.filter(Books.isbn.like(f'%{isbn}%'))
            # rows = db.execute('SELECT * FROM books WHERE isbn LIKE :isbn',
            #               {"isbn":f"%{isbn}%"})
        elif title:
            rows = Books.query.filter(Books.title.like(f'%{title}%'))
            # rows = db.execute('SELECT * FROM books WHERE title LIKE :title',
            #               {"title":f"%{title}%"})
        elif author:
            rows = Books.query.filter(Books.author.like(f'%{author}%'))
            # rows = db.execute('SELECT * FROM books WHERE author LIKE :author',
            #               {"author":f"%{author}%"})
        else:
            return apology("must provide query of one element", 400) 

        if rows.first() != None:
            return render_template("results.html", rows=rows)
        else:
            return apology("nothing found", 400) 
    else:
        return render_template('index.html')

@app.route("/logout")
def logout():
    session.clear()
    return render_template('login.html')


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        
        if not request.form.get("username"):
            return apology("must provide username", 400)
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        elif not request.form.get("confirmation"):
            return apology("must provide confirmation password", 400) 
        elif not request.form.get("confirmation") == request.form.get("password"):
            return apology("passwords don't match", 400) 

        rows = Users.query.filter_by(name=request.form.get("username")).all()
        # rows = db.execute('SELECT * FROM users WHERE name = :username',
        #                   {"username":request.form.get("username")})

        if len(rows)>0:
            return apology("username taken", 400)
        else:
            user = Users(name=request.form.get("username"), password=generate_password_hash(request.form.get("password")))
            db.session.add(user)
            # db.execute("INSERT INTO users (name,password) VALUES (:username, :hashed)",
            #               {"username":request.form.get("username"), "hashed":generate_password_hash(request.form.get("password"))})
        
        db.session.commit()
        checkid = Users.query.filter_by(name=request.form.get("username")).first()
        # checkid = db.execute("SELECT * FROM users WHERE name = :username",
        #                   {"username":request.form.get("username")})
        
        # Remember which user has logged in
        session["user_id"] = checkid.id

        # Redirect user to log in
        return redirect("/")     

    else:
        return render_template('register.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        
        if not request.form.get("username"):
            return apology("must provide username", 400)
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        rows = Users.query.filter_by(name=request.form.get("username")).all()
        # rows = db.execute('SELECT * FROM users WHERE name = :username',
        #                   {"username":request.form.get("username")})
        
        if len(rows)>0:
            row = rows[0]
            if (row.name==request.form.get("username") 
                and check_password_hash(row.password, request.form.get("password"))):
                session["user_id"] = row.id 
                # Redirect user to log in
                return redirect("/")  
            else:
                return apology("incorrect password", 400) 
        else:
            return apology("no user found", 400)
    else:
        return render_template('login.html')        




@app.route("/review/<string:isbn>", methods=["POST"])
@login_required
def review(isbn):

    if not request.form.get("review"):
        return apology("must provide review", 400)
    elif not request.form.get("rating"):
        return apology("must provide rating", 400)

    rows = Reviews.query.filter_by(userid=session["user_id"]).all()
    # rows = db.execute('SELECT * FROM reviews WHERE userid = :userid',
    #                       {"userid":session["user_id"]})

    if len(rows)>0:
        for row in rows:
            if row.isbn == isbn:
                return apology("you have already reviewed this", 400)
    
    review = Reviews(isbn=isbn, 
                    userid=session["user_id"], 
                    score=request.form.get("rating"), 
                    review=request.form.get("review"), 
                    date=datetime.datetime.now())
    db.session.add(review)
    # db.execute("INSERT INTO reviews (isbn,userid, score, review, date) VALUES (:isbn, :userid, :score, :review, now())",
    #                 {
    #                     "isbn":isbn, 
    #                     "userid":session["user_id"],
    #                     "score":request.form.get("rating"),
    #                     "review":request.form.get("review")
    #                 })
    db.session.commit()
    return redirect(f'/book/{isbn}')




@app.route("/book/<string:isbn>", methods=["GET"])
@login_required
def book(isbn):

    row = Books.query.filter_by(isbn=isbn).first()
    # rows = db.execute('SELECT * FROM books WHERE isbn = :isbn LIMIT 1',
    #                       {"isbn":isbn})    

    reviews = db.session.query(Reviews, Users).filter(Reviews.userid == Users.id).filter_by(isbn=isbn).all()
    # reviews = db.execute('SELECT * FROM reviews JOIN users ON userid = id WHERE isbn = :isbn',
    #                       {"isbn":isbn})
    
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "QkaOQgj4Zg31pO9WeqWUtA", "isbns": f"{isbn}"})

    return render_template('book.html', row=row, isbn=isbn, reviews=reviews, res=res.json()["books"][0])


@app.route("/books", methods=["GET"])
@login_required
def books():
    rows = Books.query.all()
    # rows = db.execute('SELECT * FROM books')
    
    if len(rows)>0:
        return render_template("results.html", rows=rows)
    else:
        return apology("must provide query of one element", 400) 



@app.route("/api/<string:isbn>", methods=["GET"])
@login_required
def api(isbn):

    row = Books.query.filter_by(isbn=isbn).first()
    rating = db.session.query(func.count('*'), func.avg(Reviews.score)).first()
    # rows = db.execute('SELECT * FROM books WHERE isbn = :isbn LIMIT 1',
    #                       {"isbn":isbn})
    # ratings = db.execute('SELECT count(*), avg(score) FROM reviews WHERE isbn = :isbn',
    #                       {"isbn":isbn}) 

    obj = {}
    obj["isbn"] = row.isbn
    obj["title"] = row.title
    obj["author"] = row.author
    obj["year"] = row.year
    obj["review_count"] = rating[0]
    obj["average_score"] = float(rating[1])
    return jsonify(obj)