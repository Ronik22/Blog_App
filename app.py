from flask import Flask, redirect, url_for, render_template, request
from flask import session, flash
from datetime import timedelta, datetime
from flask_sqlalchemy import SQLAlchemy
import os
import bcrypt

from werkzeug.utils import redirect

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=30)

db = SQLAlchemy(app)

class users(db.Model):
    _id = db.Column("id",db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    pwd = db.Column(db.String(100))
    email = db.Column(db.String(100), default='N/A')
    datetime = db.Column(db.String(100), default='N/A')

    def __init__(self, name, email, datetime, pwd):
        self.name = name
        self.email = email
        self.pwd = pwd
        self.datetime = datetime

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(30), nullable=False, default='N/A')
    content = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return 'Blog post ' + str(self.id)


@app.route('/posts', methods=['GET','POST'])
def posts():
    if "user" in session:
        if request.method == 'POST':
            post_title = request.form['title']
            post_content = request.form['content']
            post_author = session["user"]
            new_post = BlogPost(title=post_title,content=post_content,author=post_author)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/posts')
        else:
            all_posts = BlogPost.query.order_by(BlogPost.date_posted).all()
            return render_template('posts.html', posts=all_posts)
    else:
        flash("You are not logged in!",category='danger')
        return redirect(url_for("login"))


@app.route('/posts/delete/<int:id>')
def delete(id):
    if "user" in session:
        post = BlogPost.query.get_or_404(id)
        if post.author == session["user"] or session["user"] == "admin":
            db.session.delete(post)
            db.session.commit()
            return redirect('/posts')
        else:
            flash("Only the author can delete the post",category='danger')
            return redirect('/posts')
    else:
        flash("You are not logged in!",category='danger')
        return redirect(url_for("login"))


@app.route('/posts/edit/<int:id>', methods=['GET','POST'])
def edit(id):
    if "user" in session:
        post = BlogPost.query.get_or_404(id)
        if post.author == session["user"] or session["user"] == "admin":
            if request.method == 'POST':
                post.title = request.form['title']
                post.author = session["user"]
                post.content = request.form['content']
                db.session.commit()     
                return redirect('/posts')
            else:
                return render_template('edit.html',post=post)
        else:
            flash("Only the author can edit the post",category='danger')
            return redirect('/posts')
    else:
        flash("You are not logged in!",category='danger')
        return redirect(url_for("login"))

@app.route('/posts/new', methods=['GET', 'POST'])
def new_post():
    if "user" in session:
        if request.method == 'POST':
            post_title = request.form['title']
            post_author = session["user"]
            post_content = request.form['content']
            new_post = BlogPost(title=post_title, content=post_content, author=post_author)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/posts')
        else:
            return render_template('new_post.html')
    else:
        flash("You are not logged in!",category='danger')
        return redirect(url_for("login"))

@app.route("/")
def home():
    return render_template("intro.html")

@app.route("/view")     # username: admin, password: admin
def view():
    if  "user" in session and session["user"] == "admin":
        return render_template("view.html", values = users.query.all())
    else:
        flash("You need administrator privileges to view this page",category='danger')
        return redirect(url_for("user"))


@app.route('/view/delete/<int:id>')
def deleteusers(id):
    if "user" in session and session["user"] == "admin":
        currentuser = users.query.get_or_404(id)
        if currentuser.name == "admin":
            flash("Admin can't be deleted",'danger')
        else:
            db.session.execute(f"UPDATE blog_post SET author='Unknown' WHERE author='{currentuser.name}';")
            db.session.delete(currentuser)
            db.session.commit()
            flash(f"User deleted from the database and posts (if any) are assigned to 'unknown' author",category='success')
        return redirect(url_for("view"))
    else:
        flash("You need administrator privileges to view this page",category='danger')
        return redirect(url_for("login"))


@app.route("/login", methods=["POST","GET"])
def login():
    if request.method == "POST":
        user = request.form["nm"]
        pwd = request.form["pwd"]

        found_user = users.query.filter_by(name=user).first()
        if found_user:
            if bcrypt.checkpw(pwd.encode('utf-8'),found_user.pwd) == True:
                session.permanent = True
                session["user"] = user
                session["pwd"] = found_user.pwd
                session["email"] = found_user.email
                session["datetime"] = found_user.datetime
                flash("Login Successful!",category='success')
                return redirect(url_for("user"))
            else:
                flash("Password is wrong!",category='danger')
                return redirect(url_for("login"))
        else:
            flash("User Not Found!",category='danger')
            return redirect(url_for("login"))
    else:
        if "user" in session:
            flash("Already Logged in!",category='info')
            return redirect(url_for("user"))
        return render_template("login.html") 

@app.route("/register", methods=["POST","GET"])
def register():
    if request.method == "POST":
        user = request.form["nm"]
        pwd = request.form["pwd"]
        pwd = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())

        found_user = users.query.filter_by(name=user).first()
        if found_user:
            flash("User already exists",category='info')
            return redirect(url_for("register"))
        else:
            session.permanent = True
            session["user"] = user
            usr = users(user, "", "", pwd)
            db.session.add(usr)
            db.session.commit()

            flash("User Registered Successfully!",category='success')
            return redirect(url_for("user"))
    else:
        if "user" in session:
            flash("Already Logged in!",category='info')
            return redirect(url_for("user"))
        return render_template("register.html") 

@app.route("/user", methods=["POST","GET"])
def user():
    email = None
    datetime = None
    if "user" in session:
        user = session["user"]

        if request.method == "POST":
            email = request.form["email"]
            datetime = request.form["datetime"]

            session["email"] = email
            session["datetime"] = datetime
            found_user = users.query.filter_by(name=user).first()
            found_user.email = email
            found_user.datetime = datetime
            db.session.commit()
            flash("Email and datetime were saved!",category='success')
        else:
            if "email" in session and "datetime" in session:
                email = session["email"]
                datetime = session["datetime"]
        return render_template("user.html", email=email, name=user, datetime=datetime)
    else:
        flash("You are not logged in!",category='danger')
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("email", None)
    session.pop("datetime", None)

    flash("You have been logged out!",category="info")
    return redirect(url_for("login"))

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)