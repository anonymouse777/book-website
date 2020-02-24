import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://vzkgrsaablwnqh:20dde412d8545e1d9e01151ce2dcab86b0f62780c83841aa8365d2f62792e8af@ec2-50-17-178-87.compute-1.amazonaws.com:5432/ddvng5cd6e6fh5")
db = scoped_session(sessionmaker(bind=engine))

def main():
    file = open("books.csv")
    reader = csv.reader(file)
    for isbn,title,author,year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)", {"isbn": isbn, "title": title, "author": author, "year": year})
    db.commit()

if __name__ == "__main__":
    main()
