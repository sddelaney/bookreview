from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Books(db.Model):
    __tablename__  "books"
    isbn = db.Column(db.Integer, primary_key=True)
    title = db.Column()



class Users(db.Model):
    __tablename__  "users"
    id = db.Column(db.Integer, primary_key=True)




class Reviews(db.Model):
    __tablename__  "reviews"
    id = db.Column(db.Integer, primary_key=True)