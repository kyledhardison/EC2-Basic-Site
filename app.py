from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from sqlite3 import IntegrityError
import hashlib
import os

UPLOAD_FOLDER = "./uploads/"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////tmp/test.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), unique=False, nullable=False)
    firstname = db.Column(db.String(100), unique=False, nullable=False)
    lastname = db.Column(db.String(100), unique=False, nullable=False)
    email = db.Column(db.String(100), unique=False, nullable=False)
    file = db.Column(db.String(100), unique=False, nullable=False)
    wordcount = db.Column(db.String(100), unique=False, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login.html", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            data = request.form
            user = data["username"]
            passhash = hashlib.md5(bytes(data["password"], "utf-8")).hexdigest()
            query = User.query.filter_by(username=user).first()
        except:
            return render_template("login.html",
                                    message="Data processing failed")
        if not query:
            return render_template("login.html",
                                    message="Username or password is invalid")
        elif passhash != query.password:
            return render_template("login.html",
                                    message="Username or password is invalid")
        else:
            return render_template("user.html", username=query.username, 
                                   firstname=query.firstname, 
                                   lastname=query.lastname, 
                                   email=query.email, file=query.file,
                                   wordcount=query.wordcount)
    return render_template("login.html")

@app.route("/register.html", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            data = request.form
            username = data["username"]
            passhash = hashlib.md5(bytes(data["password"], "utf-8")).hexdigest()
            first = data["firstname"]
            last = data["lastname"]
            email = data["email"]
        except:
            return render_template("register.html",
                                   message="Data processing failed")
        try:
            # Handle file upload
            file = request.files['file']
            filename = secure_filename(file.filename)
            updir = UPLOAD_FOLDER + username + "/"
            if not os.path.exists(updir):
                os.mkdir(updir)
            filepath = os.path.join(updir, filename)
            file.save(filepath)

            # Process file wordcount
            f = open(filepath, "r")
            wordcount = len(f.read().split())
            f.close()
        except:
            return render_template("register.html",
                                   message="File processing failed. " + 
                                   "Only upload plain text files.")

        try:
           user = User(username=username, password=passhash, firstname=first,
                       lastname=last, email=email, file=filepath, 
                       wordcount=wordcount)
           db.session.add(user)
           db.session.commit()
        except (IntegrityError, exc.IntegrityError) as e:
            return render_template("register.html",
                                   message="Username already exists")
        return render_template("user.html", username=username, firstname=first,
                               lastname=last, email=email, file=filepath,
                               wordcount=wordcount)
    return render_template("register.html")

@app.route("/uploads/<user>/<filename>", methods=["GET"])
def getfile(user, filename):
    try:
        return send_file(os.path.join("./uploads/", user, filename),
                                      as_attachment=True)
    except:
        self.Error(400)
