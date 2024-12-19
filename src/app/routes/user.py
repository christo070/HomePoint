from . import user
from app.models import db, User, Professional, Service, Customer, ServiceRequest, Review
from app.forms import CustomerProfileForm, ProfessionalProfileForm, AdminProfileForm
from flask import jsonify, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user, logout_user


@user.route("/user/dashboard", methods=["GET"])
@login_required
def dashboard():
    if current_user.role == "customer":
        return redirect(url_for("customer.dashboard"))
    elif current_user.role == "professional":
        return redirect(url_for("professional.dashboard"))
    elif current_user.role == "admin":
        return redirect(url_for("admin.dashboard"))
    flash("Please login to continue")
    return redirect(url_for("auth.login"))


@user.route("/user/search", methods=["GET"])
@login_required
def search():
    if current_user.role == "customer":
        return redirect(url_for("customer.search"))
    elif current_user.role == "professional":
        return redirect(url_for("professional.search"))
    elif current_user.role == "admin":
        return redirect(url_for("admin.search"))
    flash("Please login to continue")
    return redirect(url_for("auth.login"))


@user.route("/user/summary", methods=["GET"])
@login_required
def summary():
    if current_user.role == "customer":
        return redirect(url_for("customer.summary"))
    elif current_user.role == "professional":
        return redirect(url_for("professional.summary"))
    elif current_user.role == "admin":
        return redirect(url_for("admin.summary"))
    flash("Please login to continue")
    return redirect(url_for("auth.login"))


# User Profile Routes - View, Edit, Delete
@user.route("/user/profile/view", methods=["GET", "POST"])
@login_required
def profile():
    user = User.query.get(current_user.id)

    if request.method == "GET":
        user_data = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "address": user.address,
            "pincode": user.pincode,
            "role": user.role,
        }

        if current_user.role == "professional":
            professional = Professional.query.get(user.id)
            user_data["experience"] = professional.experience
            user_data["service"] = Service.query.get(professional.service).name
            user_data["description"] = professional.description
            user_data["rating"] = professional.avg_rating
            user_data["tot_reviews"] = professional.tot_reviews

            form = ProfessionalProfileForm(obj=user)
            form.experience.data = user_data["experience"]
            form.service.data = user_data["service"]
            form.description.data = user_data["description"]

        elif current_user.role == "customer":
            form = CustomerProfileForm(obj=user)
        elif current_user.role == "admin":
            form = AdminProfileForm(obj=user)

        return render_template("profile.html", user=user_data, form=form)


    if current_user.role == "professional":
        form = ProfessionalProfileForm()
    elif current_user.role == "customer":
        form = CustomerProfileForm()
    elif current_user.role == "admin":
        form = AdminProfileForm()

    if form.validate_on_submit():
        existing_email = User.query.filter_by(email = form.email.data).all()
        if existing_email == []:
            current_user.email = form.email.data
        elif current_user.email != form.email.data:
            flash("Email already exists")
            return redirect(url_for("user.profile"))

        current_user.name = form.name.data
        current_user.phone = form.phone.data
        current_user.address = form.address.data
        current_user.pincode = form.pincode.data

        if current_user.role == "professional":
            professional = Professional.query.get(current_user.id)
            professional.experience = form.experience.data
            professional.description = form.description.data

        db.session.commit()
        flash("Profile updated successfully")

    return redirect(url_for("user.profile"))


@user.route("/user/profile/delete", methods=["POST"])
@login_required
def delete_profile():

    if current_user.role not in ("admin", "deleted"):
        if current_user.role == "professional":
            Reviews = Review.query.filter_by(professional = current_user.id).all()
            for review in Reviews:
                review.professional = 0
            db.session.commit()

            ServiceRequests = ServiceRequest.query.filter_by(professional = current_user.id).all()
            for request in ServiceRequests:
                request.professional = 0
                if request.status in ("requested", "accepted"):
                    request.status = "cancelled"
            db.session.commit()

            professional = Professional.query.get(current_user.id)
            db.session.delete(professional)
            db.session.commit()

        elif current_user.role == "customer":
            ServiceRequests = ServiceRequest.query.filter_by(customer = current_user.id).all()
            for request in ServiceRequests:
                request.customer = 0
                if request.status in ("requested", "accepted"):
                    request.status = "cancelled"
            db.session.commit()

            Reviews = Review.query.filter_by(customer = current_user.id).all()
            for review in Reviews:
                review.customer = 0
            db.session.commit()

            customer = Customer.query.get(current_user.id)
            db.session.delete(customer)
            db.session.commit()

        db.session.delete(current_user)
        db.session.commit()

        logout_user()
        flash("Profile deleted successfully")
        return redirect(url_for("auth.login"))

    flash("User profile cannot be deleted")
    return redirect(url_for("user.profile"))


@user.route("/user/messages", methods=["GET"])
@login_required
def messages():
    data = {}

    flash("Feature under development")
    return redirect(url_for("user.dashboard"))

    # return jsonify(data)
