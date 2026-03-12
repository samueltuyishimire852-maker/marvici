from flask import Flask,render_template,request,redirect,session,send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail,Message
from werkzeug.security import generate_password_hash,check_password_hash
import datetime
import os

app = Flask(__name__)

app.secret_key="marvici_secure"

app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///database.db"
app.config["UPLOAD_FOLDER"]="uploads"

# Email configuration
app.config["MAIL_SERVER"]="smtp.gmail.com"
app.config["MAIL_PORT"]=587
app.config["MAIL_USE_TLS"]=True
app.config["MAIL_USERNAME"]="your_email@gmail.com"
app.config["MAIL_PASSWORD"]="your_password"

db=SQLAlchemy(app)
mail=Mail(app)

OPEN_TIME=datetime.time(8,0)
CLOSE_TIME=datetime.time(18,0)

# ---------------------
# DATABASE MODELS
# ---------------------

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(100),unique=True)
    password=db.Column(db.String(200))
    role=db.Column(db.String(20))
    email=db.Column(db.String(200))

class Document(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    filename=db.Column(db.String(200))
    user=db.Column(db.String(100))

class Group(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))

class Task(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(200))
    description=db.Column(db.String(500))
    assigned_to=db.Column(db.String(100))

class Activity(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user=db.Column(db.String(100))
    action=db.Column(db.String(200))
    time=db.Column(db.DateTime,default=datetime.datetime.utcnow)

# ---------------------
# LOGIN
# ---------------------

@app.route("/",methods=["GET","POST"])
def login():

    if request.method=="POST":

        username=request.form["username"]
        password=request.form["password"]

        user=User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password,password):

            session["user"]=username
            session["role"]=user.role

            activity=Activity(user=username,action="Logged in")
            db.session.add(activity)
            db.session.commit()

            return redirect("/dashboard")

    return render_template("login.html")

# ---------------------
# REGISTER
# ---------------------

@app.route("/register",methods=["GET","POST"])
def register():

    if request.method=="POST":

        username=request.form["username"]
        email=request.form["email"]

        password=generate_password_hash(request.form["password"])

        user=User(username=username,password=password,email=email,role="member")

        db.session.add(user)
        db.session.commit()

        return redirect("/")

    return render_template("register.html")

# ---------------------
# DASHBOARD
# ---------------------

@app.route("/dashboard",methods=["GET","POST"])
def dashboard():

    if "user" not in session:
        return redirect("/")

    message=""

    now=datetime.datetime.now().time()

    if request.method=="POST":

        if OPEN_TIME<=now<=CLOSE_TIME:

            file=request.files["file"]

            path=os.path.join(app.config["UPLOAD_FOLDER"],file.filename)

            file.save(path)

            doc=Document(filename=file.filename,user=session["user"])

            db.session.add(doc)

            activity=Activity(user=session["user"],action="Uploaded "+file.filename)

            db.session.add(activity)
            db.session.commit()

            message="File uploaded successfully"

        else:
            message="Submission closed"

    return render_template("dashboard.html",message=message,close_time=CLOSE_TIME)

# ---------------------
# FILE PREVIEW
# ---------------------

@app.route("/preview/<filename>")
def preview(filename):

    return render_template("preview.html",file=filename)

# ---------------------
# DOWNLOAD
# ---------------------

@app.route("/download/<filename>")
def download(filename):

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename,
        as_attachment=True
    )

# ---------------------
# GROUPS
# ---------------------

@app.route("/groups")
def groups():

    groups=Group.query.all()

    return render_template("groups.html",groups=groups)

# ---------------------
# ADMIN PANEL
# ---------------------

@app.route("/admin")
def admin():

    if session.get("role")!="admin":
        return redirect("/")

    users=User.query.count()
    files=Document.query.count()

    docs=Document.query.all()

    activities=Activity.query.order_by(Activity.time.desc()).limit(20).all()

    tasks=Task.query.all()

    return render_template(
        "admin_dashboard.html",
        users=users,
        files=files,
        docs=docs,
        activities=activities,
        tasks=tasks
    )

# ---------------------
# ASSIGN TASK
# ---------------------

@app.route("/assign_task",methods=["POST"])
def assign_task():

    title=request.form["title"]
    desc=request.form["description"]
    user=request.form["user"]
    email=request.form["email"]

    task=Task(title=title,description=desc,assigned_to=user)

    db.session.add(task)
    db.session.commit()

    msg=Message(
        "New Task Assigned",
        sender=app.config["MAIL_USERNAME"],
        recipients=[email]
    )

    msg.body=f"You have been assigned a task: {title}"

    mail.send(msg)

    return redirect("/admin")

# ---------------------
# LOGOUT
# ---------------------

@app.route("/logout")
def logout():

    session.clear()
    return redirect("/")

# ---------------------

if __name__ == "__main__":
    
    import os

    if not os.path.exists("uploads"):
        os.mkdir("uploads")

    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=5000, debug=True)


