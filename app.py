import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt

# init the app, configure secret key
app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"

# init bcrypt to hash and check hashed passwords
bcrypt = Bcrypt(app)

# create instance folder
instance_path = os.path.join(os.path.dirname(__file__), "instance")
if not os.path.exists(instance_path):
    os.mkdir(instance_path)

# set database name, initialize database
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(instance_path, 'database.db')}"
db = SQLAlchemy(app)


# database models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)  # Increase the length for hashed passwords


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


# create the dummy users
with app.app_context():
    db.create_all()
    # add sample passwords
    if not User.query.filter_by(username="admin").first():
        admin_password_hash = bcrypt.generate_password_hash("admin").decode("utf-8")
        admin_user = User(username="admin", password=admin_password_hash)
        db.session.add(admin_user)

    if not User.query.filter_by(username="user1").first():
        user1_password_hash = bcrypt.generate_password_hash("password1").decode("utf-8")
        user1 = User(username="user1", password=user1_password_hash)
        db.session.add(user1)

    if not User.query.filter_by(username="user2").first():
        user2_password_hash = bcrypt.generate_password_hash("password2").decode("utf-8")
        user2 = User(username="user2", password=user2_password_hash)
        db.session.add(user2)
    db.session.commit()


# login manager, user loader and related routes
login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("view_contacts"))
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# app routes
@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("home.html")


@app.route("/add_contact", methods=["GET", "POST"])
@login_required
def add_contact():
    if request.method == "POST":
        name = request.form["name"]
        phone_number = request.form["phone_number"]
        new_contact = Contact(name=name, phone_number=phone_number, user_id=current_user.id)
        db.session.add(new_contact)
        db.session.commit()
    return render_template("add_contact.html")


@app.route("/view_contacts")
@login_required
def view_contacts():
    contacts = Contact.query.filter_by(user_id=current_user.id).all()
    return render_template("view_contacts.html", contacts=contacts)


@app.route("/confirm_delete/<contact_id>")
@login_required
def confirm_delete(contact_id):
    delete_candidate = Contact.query.filter_by(id=contact_id).first()
    return render_template("confirm_delete.html", contact=delete_candidate)


@app.route("/delete/<contact_id>")
@login_required
def delete_contact(contact_id):
    Contact.query.filter_by(id=contact_id).delete()
    db.session.commit()
    return redirect(url_for("view_contacts"))


@app.route("/edit_contact/<contact_id>", methods=["GET", "POST"])
@login_required
def edit_contact(contact_id):
    candidate = Contact.query.filter_by(id=contact_id).first()
    if request.method == "POST":
        candidate.name = request.form["name"]
        candidate.phone_number = request.form["phone_number"]
        db.session.commit()
        return redirect(url_for("view_contacts"))
    return render_template("edit_contact.html", contact=candidate)
    # TODO: finish implementation


if __name__ == "__main__":
    app.run(debug=True)
