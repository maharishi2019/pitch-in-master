from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "c2cf45d51cf3e8615ff0d24e6bd51fc3"

db = SQLAlchemy(app)

class User(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    email = db.Column(db.String(255))
    password = db.Column(db.String(255))
    location = db.Column(db.String(255))

    def __init__(self, username, password, email, location):
        self.username = username
        self.email = email
        self.password = password
        self.location = location
        
@app.route("/")
def index():
    if "user" in session:
        x = User.query.filter_by(username=session["user"]).first()
        same_location = User.query.filter_by(location=x.location).all()
        return render_template("index.html", same_location=same_location)
    else:
        return render_template("index.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if(request.method == "POST"):
        username = request.form["username"]
        password = request.form["password"]
        #validation for if user exists and if the password matches or not 
        if(len(User.query.filter_by(username=username).all()) > 0):
            if(User.query.filter_by(username=username).first().password == password):
                session.permenant = True
                session["user"] = username
                session["logged_in"] = True
                return redirect(url_for("index"))
            else:
                flash("Credentials Invalid")
                return redirect(url_for("login"))
        else:
            flash("User doesn't exist")
            return redirect(url_for("login"))
    else:
        return render_template("login.html")

@app.route("/registration", methods=["POST", "GET"])
def registration():
    if(request.method == "POST"):
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        location = "%s;%s;%s" % (request.form["city"], request.form["state"], request.form["country"])
        #validation for both email and username
        if(len(User.query.filter_by(username=username).all()) > 0 or len(User.query.filter_by(email=email).all()) > 0):
            flash("Username or email already exists")
            return redirect(url_for("registration"))
        else:
            new_user = User(username, password, email, location)
            print(location)
            db.session.add(new_user)
            db.session.commit()
            session.permenant = True
            session["user"] = username
            session["logged_in"] = True
            a_file = open("entries.json", "r+")
            json_object = json.load(a_file)
            a_file.close()
            y = {
                "name": username, 
                "checklist":[],
                "committed":[]
            }
            json_object["entries"].append(y)
            a_file = open("entries.json", "w")
            json.dump(json_object, a_file)
            a_file.close()
            return redirect(url_for("index"))
    else:
        return render_template("registration.html")
  
@app.route("/new_post", methods=["POST", "GET"])
def new_post():
    if(request.method == "POST"):
        new_checklist = request.form["checklist"].split("\r\n")
        with open("entries.json", "r") as a_file:
            json_object = json.load(a_file)
        a_file.close()
        for i in json_object["entries"]:
            if i["name"] == session["user"]:
                i["checklist"] = new_checklist
        a_file = open("entries.json", "w")
        json.dump(json_object, a_file)
        a_file.close()
        flash("Successfully published!")
        return redirect(url_for("new_post"))
    else:
        checklist = []
        with open('entries.json') as json_file: 
            data = json.load(json_file) 
            for i in data['entries']:
                if(i["name"] == session["user"]):
                    checklist = i["checklist"]
        return render_template("new_post.html", checklist=checklist)

@app.route("/feed", methods=["GET", "POST"])
def feed():
    if request.method == "GET":
        with open("entries.json") as file:
            entries = json.load(file)['entries']
            usernames, checklist, commits = [[],[],[]]
            for entry in entries:
                usernames.append(entry["name"])
                checklist.append(entry["checklist"])
                commits.append(entry["committed"])

    return render_template("feed.html", usernames=usernames, checklist=checklist, commits=commits, leng=len(usernames))
    
@app.route("/<usr>")
def visit(usr):
    user = usr
    items = []
    with open('entries.json') as data:
        entry = json.load(data)
        for i in entry['entries']:
            names = i["name"]
            if names == usr:
                items = i["checklist"]

    return render_template("explore.html", user=user, items=items)

@app.route("/<item>")
def commit(item):
    a_file = open("entries.json", "r+")
    json_object = json.load(a_file)
    a_file.close()
    for i in json_object["entries"]:
        if i["name"] == session["user"]:
            i["commit"].append(item)
    a_file = open("entries.json", "w")
    json.dump(json_object, a_file)
    return redirect(url_for("index"))
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route("/profile_page")
def profile_page():
    return render_template("profile_page.html")

@app.route("/change_password", methods=["POST", "GET"])
def change_password():
    if(request.method == "POST"):
        current_password = request.form["current-password"]
        new_password = request.form["new-password"]

        if(User.query.filter_by(username=session["user"]).first().password == current_password):
            User.query.filter_by(username=session["user"]).first().password = new_password
            flash("Password change successful!")
            return redirect(url_for("index"))
        else:
            flash("Password change unsuccessful!")
            return redirect(url_for("index"))
    else:
        return redirect(url_for("profile_page"))
if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
