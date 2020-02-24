import requests
from flask import Flask, session, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask import render_template, request

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgres://vzkgrsaablwnqh:20dde412d8545e1d9e01151ce2dcab86b0f62780c83841aa8365d2f62792e8af@ec2-50-17-178-87.compute-1.amazonaws.com:5432/ddvng5cd6e6fh5")
db = scoped_session(sessionmaker(bind=engine))
app.secret_key = "any random string"

@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    if request.method == "POST":
        user_name = request.form.get("user_name")
        password = request.form.get("password")
        user = None
        user = db.execute("SELECT * FROM users WHERE user_name = :user_name AND password = :password", {"user_name": user_name, "password": password}).fetchone()
        if user is not None:
            session["username"] = user.user_name
        #    print("session created for the user.")
            return redirect(url_for('home', user=user_name))
        else:
            return render_template("error.html", message="Invalid user name or password was given for login.")

@app.route("/logout")
def logout():
    if session.get("username") is None:
    #    print("Session is already empty")
        return redirect(url_for("index"))
    else:
        session.pop("username", None)
    #    print("session is empty now.")
        return redirect(url_for('index'))

@app.route("/signnup", methods=["GET","POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    if request.method == "POST":
        user_name = request.form.get("user_name")
        password_one = request.form.get("password")
        password_two = request.form.get("confirm_password")
        if password_one == password_two:
            check_name = None
            check_name = db.execute("SELECT * FROM users WHERE user_name = :user_name",{"user_name": user_name}).fetchone()
            if ((check_name != None) and (check_name.user_name == user_name)):
                return render_template("error.html",message="user name is already taken by other user. Choose another user name.")
            else:
                if user_name == password_one:
                    return render_template("error.html",message="User name and password should not be same.")
                db.execute("INSERT INTO users (user_name,password) VALUES (:user_name, :password)", {"user_name": user_name, "password": password_one})
                db.commit()
                new_user = db.execute("SELECT * FROM users WHERE user_name = :user_name",{"user_name": user_name}).fetchone()
                session["username"] = new_user.user_name
    #            print("the new user is in session now.")
                return redirect(url_for('home', user=user_name))
        else:
            return render_template("error.html",message="Password does not match.")

@app.route("/<string:user>", methods=["POST","GET"])
def home(user):
    if session.get("username") is None:
    #    print("No username found in session")
        return redirect(url_for('index'))
    else:
        if request.method == "GET":
            return render_template("home.html", books=None, user=user)
        if request.method == "POST":
            bita = request.form.get("bita")
            isbn_one = "%{}".format(bita)
            isbn_two = "{}%".format(bita)
            isbn_three = "%{}%".format(bita)
            title_one = "%{}".format(bita)
            title_two = "{}%".format(bita)
            title_three = "%{}%".format(bita)
            author_one = "%{}".format(bita)
            author_two = "{}%".format(bita)
            author_three = "%{}%".format(bita)
            books = db.execute("SELECT * FROM books where isbn = :isbn OR isbn LIKE :isbn_one OR isbn LIKE :isbn_two OR isbn LIKE :isbn_three Or author = :author OR author LIKE :author_one Or author LIKE :author_two OR author LIKE :author_three OR title = :title OR title LIKE :title_one OR title LIKE :title_two OR title LIKE :title_three",
                                {"isbn": bita, "isbn_one": isbn_one, "isbn_two": isbn_two, "isbn_three": isbn_three, "author": bita, "author_one": author_one, "author_two": author_two, "author_three": author_three, "title": bita, "title_one": title_one, "title_two": title_two, "title_three": title_three }).fetchall()
            return render_template("home.html", books=books, user=user)

@app.route("/<string:user>/<string:book_isbn>", methods=["POST","GET"])
def bookdetails(user,book_isbn):
    if session.get("username") is None:
    #    print("No username found in session")
        return redirect(url_for('index'))
    else:
        if request.method == "GET":
            book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": book_isbn}).fetchone()
            book_reviews = db.execute("SELECT * FROM review WHERE book_id = :book_id",{"book_id": book.id}).fetchall()
            res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "6CHjiL3JrS9xg7xOFQizQ", "isbns": book_isbn })
            response = res.json()
            rating = response["books"][0]["work_ratings_count"]
            average = response["books"][0]["average_rating"]
            return render_template("bookdetails.html", user=user, book=book, rating=rating,average=average, book_reviews=book_reviews)
        if request.method == "POST":
            book = db.execute("SELECT * FROM books where isbn = :isbn",{"isbn": book_isbn}).fetchone()
            book_rating = request.form.get("rating_integer")
            book_comment = request.form.get("review_comment")
            user_details = db.execute("SELECT * FROM users WHERE user_name = :user_name",{"user_name": user}).fetchone()
            comment = None
            comment = db.execute("SELECT * FROM review WHERE user_id = :user_id AND book_id = :book_id",{"user_id": user_details.id, "book_id": book.id}).fetchone()
            if comment is None:
                db.execute("INSERT INTO review (user_id, book_id,rating_number,rating_comment, user_name) VALUES (:user_id, :book_id, :rating_number, :rating_comment, :user_name)", {"user_id": user_details.id, "book_id": book.id, "rating_number": book_rating, "rating_comment": book_comment, "user_name": user_details.user_name})
                db.commit()
                book_reviews = db.execute("SELECT * FROM review WHERE book_id = :book_id",{"book_id": book.id}).fetchall()
                res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "6CHjiL3JrS9xg7xOFQizQ", "isbns": book_isbn })
                response = res.json()
                rating = response["books"][0]["work_ratings_count"]
                average = response["books"][0]["average_rating"]
                return render_template("bookdetails.html", user=user, book=book, rating=rating,average=average, book_reviews=book_reviews)
            else:
                return render_template("error.html", message="One user can not add multiple comment for the same book.")

@app.route("/api/<string:isbn>")
def api(isbn):
    book_info = None
    book_info = db.execute("SELECT * FROM books WHERE isbn = :isbn",{"isbn": isbn}).fetchone()
    if book_info is None:
        return jsonify({"Error" : "Invalid ISBN number."}), 404

    count = db.execute("SELECT SUM(rating_number) FROM review where book_id = :book_id",{"book_id": book_info.id}).fetchone()
    if count[0] is None:
        count = 0
    else:
        count = int(count[0])
    average = db.execute("SELECT AVG(rating_number) FROM review where book_id = :book_id",{"book_id": book_info.id}).fetchone()
    if average[0] is None:
        average = 0
    else:
        average = int(average[0])
    #return render_template("error.html", message=count)
    return jsonify({
             "title": book_info.title,
             "author": book_info.author,
             "year": book_info.year,
             "isbn": book_info.isbn,
             "review_count": count,
             "average_score": average
    })
