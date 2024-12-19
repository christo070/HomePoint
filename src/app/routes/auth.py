from . import auth, bcrypt
from app.models import db, User, Customer, Professional, Admin
from app.forms import (
    LoginForm,
    ProfessionalRegistrationForm,
    CustomerRegistrationForm
)
from flask import render_template, redirect, url_for, flash, session
from flask_login import login_required, login_user, logout_user, current_user


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("user.dashboard"))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for("user.dashboard"))
        else:
            flash("Login Unsuccessful. Please check credentials")

    return render_template("login.html", form=form)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out, redirecting to login")
    return redirect(url_for("auth.login"))


@auth.route("/signup/customer", methods=["GET", "POST"])
def signup_customer():
    if current_user.is_authenticated:
        return redirect(url_for("user.dashboard"))

    form = CustomerRegistrationForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        new_user = User(
            email=form.email.data,
            password=hashed_password,
            name=form.name.data,
            phone=form.phone.data,
            address=form.address.data,
            pincode=form.pincode.data,
            date_created=None,
            role="customer",
        )
        db.session.add(new_user)
        db.session.commit()
        new_customer = Customer(id=new_user.id)
        db.session.add(new_customer)
        db.session.commit()
        flash("Customer Registration Successful, Redirecting to Login")
        return redirect(url_for("auth.login"))

    return render_template("signup.html", form=form, user="customer")


@auth.route("/signup/professional", methods=["GET", "POST"])
def signup_professional():
    if current_user.is_authenticated:
        return redirect(url_for("user.dashboard"))

    form = ProfessionalRegistrationForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )
        new_user = User(
            email=form.email.data,
            password=hashed_password,
            name=form.name.data,
            phone=form.phone.data,
            address=form.address.data,
            pincode=form.pincode.data,
            date_created=None,
            role="professional",
        )
        db.session.add(new_user)
        db.session.commit()
        new_professional = Professional(
            id=new_user.id,
            experience=form.experience.data,
            service=form.service.data,
            description=form.description.data,
            approval="pending",
        )
        db.session.add(new_professional)
        db.session.commit()
        flash("Service Professional Registration Successful, Redirecting to Login")
        return redirect(url_for("auth.login"))

    return render_template("signup.html", form=form, user="professional")

