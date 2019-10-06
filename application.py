import os

from flask import Flask, session, render_template, redirect, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_paginate import Pagination, get_page_args


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
    if 'username' in session:
        return render_template("index.html", username=session["username"])
    else:
        return redirect("/login")

@app.route("/login", methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect("/")
    else:
        print(request.method)
        if "log-in" in request.form:
            username = request.form['username']
            password = request.form['password']
            login = 'Username or Password is incorrect'
            if db.execute("SELECT * FROM users WHERE username= :username AND password= :password", {"username": username, "password": password}).rowcount == 0:
                return render_template("login.html", login=login, error=True)
            else:
                session['username'] = username
                return redirect("/")
        elif "sign-up" in request.form:
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            if len(password) == 0 or len(username) == 0 or len(email) == 0:
                signup = 'any of the field can\'t be blank'
                return render_template("login.html", signup=signup, error1=True)
            try:
                db.execute("INSERT INTO users (email, username, password) VALUES (:email, :username, :password)", {"email":email, "username":username, "password":password})
                db.commit() 
                session['username'] = username
                return redirect("/")
            except:
                signup = 'username or email exists, please try different username and/or email'
                return render_template("login.html", signup=signup, error1=True)
        else:
            return render_template("login.html")


@app.route("/signout")
def signout():
    session.clear()
    return redirect("/")

books = db.execute("SELECT * FROM books").fetchall()
def get_books(offset=0, per_page=10):
    return books[offset: offset + per_page]

@app.route('/books/')
def show_books():
    username = ""
    if 'username' in session:
        username = session['username']
    else:
        return redirect("/login")
    books = db.execute("SELECT * FROM books").fetchall()
    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    total = len(books)
    pagination_books = get_books(offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    return render_template('books.html',
                           books=pagination_books,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           username=username
                           )
discussions = db.execute("SELECT * FROM discussions").fetchall()

def get_discussions(offset=0, per_page = 10):
    return discussions[offset: offset + per_page]

@app.route('/discussions')
def show_discussions():
    #discussions = db.execute("SELECT * FROM discussions").fetchall()
    username = ""
    if 'username' in session:
        username = session['username']
    else:
        return redirect("/login")
    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    total = len(discussions)
    print(total)
    pagination_discussions = get_discussions(offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')
    return render_template('discussions.html',
                           discussions=pagination_discussions,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           username=username
                           )

@app.route('/discussions/<int:discussion_id>', methods=['GET', 'POST'])
def discussion(discussion_id):
    username = ""
    if 'username' in session:
        username = session['username']
    else:
        return redirect("/login")
    if 'comment' in request.form:
        temp_url = f'/discussions/{discussion_id}'
        comment = request.form['comment']
        if len(comment) < 1:
            return redirect(temp_url)
        username = session['username']
        user = db.execute("SELECT user_id FROM users WHERE username=:username",{"username" : username}).fetchone()
        user_id = user['user_id']
        db.execute("INSERT INTO comments (discussion_id,comment, user_id) VALUES (:discussion_id, :comment, :user_id)",
                    {"discussion_id": discussion_id, "comment" : comment, "user_id" : user_id})
        db.commit()
        return redirect(temp_url)
    discussion = db.execute("SELECT * FROM discussions WHERE discussion_id = :discussion_id", {"discussion_id" : discussion_id}).fetchone()
    if discussion is None:
        return render_template("error.html", message="No such discussion post.")
    user = db.execute("SELECT * FROM users WHERE user_id = :user_id", {"user_id" : discussion['user_id']}).fetchone()
    comments = db.execute("SELECT comments.comment, comments.comment_date, comments.user_id, users.username FROM comments INNER JOIN users ON comments.user_id = users.user_id")
    return render_template("discussion.html", discussion=discussion, user=user, comments=comments, username=username)

@app.route("/books/<int:book_id>", methods=["GET", "POST"])
def book(book_id):
    username = ""
    if 'username' in session:
        username = session['username']
    else:
        return redirect("/login")
    if 'comment' in request.form:
        temp_url = f'/books/{book_id}'
        comment = request.form['comment']
        if len(comment) < 1:
            return redirect(temp_url)
        username = session['username']
        user = db.execute("SELECT user_id FROM users WHERE username=:username",{"username" : username}).fetchone()
        user_id = user['user_id']
        db.execute("INSERT INTO comments (discussion_id,comment, user_id) VALUES (:discussion_id, :comment, :user_id)",
                    {"discussion_id": discussion_id, "comment" : comment, "user_id" : user_id})
        db.commit()
        return redirect(temp_url)
    discussion = db.execute("SELECT * FROM discussions WHERE discussion_id = :discussion_id", {"discussion_id" : discussion_id}).fetchone()
    if discussion is None:
        return render_template("error.html", message="No such discussion post.")
    user = db.execute("SELECT * FROM users WHERE user_id = :user_id", {"user_id" : discussion['user_id']}).fetchone()
    comments = db.execute("SELECT comments.comment, comments.comment_date, comments.user_id, users.username FROM comments INNER JOIN users ON comments.user_id = users.user_id")
    return render_template("discussion.html", discussion=discussion, user=user, comments=comments, username=username)