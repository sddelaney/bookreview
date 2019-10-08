import os
import csv
from flask import Flask, render_template, request
from models import *
from sqlalchemy import func

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

def main():
    isbn = 'fdsa'
    #rows = db.session.query(func.count('*'), func.avg(Reviews.score)).first()#Reviews.query.filter_by(isbn=isbn).all().avg('score')
    #for row in rows:
    #print(rows[0])
    db.create_all()

    # with open('books.csv', 'r') as f:
    #     reader = csv.DictReader(f)
    #     for row in reader:
    #         book = Books(isbn=row["isbn"], title=row["title"], author=row["author"], year=row["year"])
    #         db.session.add(book)
    # db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        main()