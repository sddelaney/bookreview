from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import os
import csv

if __name__ == "__main__":
    engine = create_engine(os.getenv("DATABASE_URL"))
    db = scoped_session(sessionmaker(bind=engine))

    with open('books.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows = db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                               {"isbn":     row["isbn"],
                                "title":    row["title"], 
                                "author":   row["author"], 
                                "year":     row["year"]})
    db.commit()