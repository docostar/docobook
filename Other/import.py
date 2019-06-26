import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

startline=3000
endline=5000
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    #f = open("flights.csv")
    f = open("books.csv")
    reader = csv.reader(f)
    temp=0
    for isbn, title, author,year in reader:
        if temp<=startline:
            temp=temp+1
            continue
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                    {"isbn": isbn, "title": title, "author": author, "year": year})
        print(f"isbn:{isbn},title:{title}, author:{author},year:{year} added")

        '''
        temp=temp+1
        if temp>endline:
            break;
        '''
        
    db.commit()

if __name__ == "__main__":
    main()
