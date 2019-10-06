import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    next(reader, None)
    for isbn, title, author, year in reader:
        print(f"isbn {isbn} {title}")
        pages = 0
        ratings = 0
        db.execute("INSERT INTO books (isbn, title, author, year, pages, ratings) VALUES (:isbn, :title, :author, :year, :pages, :ratings)",
                    {"isbn": isbn, "title": title, "author": author, "year": year, "pages": pages, "ratings": ratings})
        #print(f"Added {books}")
    db.commit()

if __name__ == "__main__":
    main()