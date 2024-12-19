from . import customer, customer_user
from app.models import (
    db,
    User,
    Professional,
    Service,
    ServiceRequest,
    Review,
)
from datetime import datetime
from app.forms import ServiceRemarkForm

from flask import jsonify, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user


@customer.route("/user/customer/dashboard", methods=["GET"])
@login_required
@customer_user
def dashboard():
    form = ServiceRemarkForm()

    services = Service.query.all()
    service_history = ServiceRequest.query.filter_by(customer=current_user.id).all()
    # Sort the service history based on status - accepted first, then close, followed by rejected
    service_history = sorted(service_history, key=lambda x: x.status, reverse=False)

    service_history_modified = []
    for service_request in service_history:
        service_request_modified = {
            "id": service_request.id,
            "service": Service.query.get(service_request.service).name,
            "professional": User.query.get(service_request.professional).name,
            "professional_phone": User.query.get(service_request.professional).phone,
            "date_requested": service_request.date_requested,
            "date_accepted": service_request.date_accepted,
            "date_completed": service_request.date_completed,
            "status": service_request.status,
        }
        service_history_modified.append(service_request_modified)

    return render_template(
        "dashboard_customer.html",
        services=services,
        service_history=service_history_modified,
        form=form,
    )


@customer.route("/user/customer/service/book", methods=["GET", "POST"])
@login_required
@customer_user
def book_package():
    if current_user.is_blocked:
        flash(
            "You are blocked due to an anomalous activity in the account. Please contact Admin for further details."
        )
        return redirect(url_for("customer.dashboard"))

    if request.method == "GET":
        service_id = request.args.get("id")
        professionals = Professional.query.filter_by(
            service=service_id, approval="approved"
        ).all()

        professionals = [
            professional
            for professional in professionals
            if User.query.get(professional.id).is_blocked == False
        ]

        packages = []
        for professional in professionals:
            packages.append(
                {
                    "id": professional.id,
                    "name": User.query.get(professional.id).name,
                    "description": professional.description,
                    "experience": professional.experience,
                    "avg_rating": professional.avg_rating,
                    "tot_reviews": professional.tot_reviews,
                }
            )

        response = {"packages": packages}
        return jsonify(response)

    # Package ID denotes the Professional ID
    package_id = request.args.get("id")

    sr_requested = ServiceRequest.query.filter_by(
        customer=current_user.id, status="requested"
    ).all()
    sr_accepted = ServiceRequest.query.filter_by(
        customer=current_user.id, status="accepted"
    ).all()

    if sr_accepted or sr_requested:
        flash(
            "You already have a pending service request. Please wait for the professional to accept it. Only one service request can be made at a time."
        )
        return redirect(url_for("customer.dashboard"))

    if User.query.get(package_id).is_blocked:
        flash(
            "The professional you are trying to book is blocked. Please try booking another professional."
        )
        return redirect(url_for("customer.dashboard"))

    service_id = Professional.query.get(package_id).service

    new_service_request = ServiceRequest(
        service=service_id,
        customer=current_user.id,
        professional=package_id,
        status="requested",
    )
    db.session.add(new_service_request)
    db.session.commit()

    flash("Service booked successfully!")
    return redirect(url_for("customer.dashboard"))


@customer.route("/user/customer/service-request/close", methods=["GET", "POST"])
@login_required
@customer_user
def close_service():
    service_request_id = request.args.get("id")
    form = ServiceRemarkForm()

    if request.method == "GET":
        service_request = ServiceRequest.query.get(service_request_id)

        if service_request.customer != current_user.id:
            flash("You are not authorized to close this service request")
            return redirect(url_for("customer.dashboard"))

        form_data = {
            "id": service_request_id,
            "service": Service.query.get(service_request.service).name,
            "professional": User.query.get(service_request.professional).name,
            "phone": User.query.get(service_request.professional).phone,
            "date_requested": service_request.date_requested,
            "date_accepted": service_request.date_accepted,
        }
        return jsonify(form_data)

    if form.validate_on_submit():
        service_request = ServiceRequest.query.get(service_request_id)

        if service_request.customer != current_user.id:
            flash("You are not authorized to close this service request")
            return redirect(url_for("customer.dashboard"))

        new_review = Review(
            customer=current_user.id,
            professional=service_request.professional,
            service_request=service_request.id,
            comment=form.remarks.data,
            rating=int(form.rating.data),
        )

        db.session.add(new_review)
        db.session.commit()

        service_request.review = new_review.id
        service_request.date_completed = datetime.now()
        service_request.status = "closed"
        db.session.commit()

        professional = Professional.query.get(service_request.professional)
        professional.avg_rating = (
            (professional.avg_rating * float(professional.tot_reviews))
            + float(form.rating.data)
        ) / (float(professional.tot_reviews) + 1.0)
        professional.tot_reviews += 1
        db.session.commit()

        flash("Service closed successfully!")
        return redirect(url_for("customer.dashboard"))

    flash("Form validation failed, please try again later")
    return redirect(url_for("user.dashboard"))


@customer.route("/user/customer/search", methods=["GET", "POST"])
@login_required
@customer_user
def search():
    if request.method == "POST":
        data = request.get_json()
        search_by = data["search_by"]
        search_text = data["search_text"]

        result = {"status": "success", "data": []}

        professionals = []

        if search_by == "Service Name":
            if search_text == "":
                professionals = Professional.query.all()[1:]
            else:
                search_service = Service.query.filter(
                    Service.name.ilike(f"%{search_text}%")
                ).all()
                if search_service:
                    search_service = search_service[0]
                    professionals = Professional.query.filter(
                        Professional.service == search_service.id
                    ).all()
                else:
                    result["status"] = "error"
                    return jsonify(result)

        elif search_by == "Pincode":
            if search_text == "":
                professionals = Professional.query.all()[1:]
            else:
                users = User.query.filter(User.pincode.ilike(f"%{search_text}%")).all()
                users = [user for user in users if user.role == "professional"]
                professionals = Professional.query.filter(
                    Professional.id.in_([user.id for user in users])
                ).all()

        elif search_by == "Location":
            if search_text == "":
                professionals = Professional.query.all()[1:]
            else:
                users = User.query.filter(User.address.ilike(f"%{search_text}%")).all()
                users = [user for user in users if user.role == "professional"]
                professionals = Professional.query.filter(
                    Professional.id.in_([user.id for user in users])
                ).all()

        elif search_by == "Rating":
            try:
                if search_text == "":
                    search_text = 0.0
                search_text = float(search_text)
                professionals = Professional.query.filter(
                    Professional.avg_rating >= search_text
                ).all()
            except:
                result["status"] = "error"

        elif search_by == "Review Count":
            try:
                if search_text == "":
                    search_text = 0
                search_text = int(search_text)
                professionals = Professional.query.filter(
                    Professional.tot_reviews >= search_text
                ).all()
            except:
                result["status"] = "error"

        if professionals:
            for professional in professionals:
                service = Service.query.get(professional.service)
                user = User.query.get(professional.id)
                result["data"].append(
                    {
                        "id": professional.id,
                        "service_name": service.name,
                        "base_price": service.price,
                        "completion_time": str(service.duration)
                        + " "
                        + service.period.capitalize(),
                        "professional_name": user.name,
                        "professional_experience": professional.experience,
                        "professional_location": user.address,
                        "professional_pincode": user.pincode,
                        "professional_average_rating": professional.avg_rating,
                        "professional_tot_reviews": professional.tot_reviews,
                    }
                )

        return jsonify(result)

    options = ["Service Name", "Pincode", "Location", "Rating", "Review Count"]

    return render_template(
        "search.html",
        role="customer",
        options=options,
        fetch_url=url_for("customer.search"),
    )


@customer.route("/user/customer/summary", methods=["GET"])
@login_required
@customer_user
def summary():
    return render_template(
        "summary.html", role="customer", fetch_url=url_for("customer.get_summary")
    )


@customer.route("/user/customer/get-summary", methods=["GET"])
@login_required
@customer_user
def get_summary():
    data = {
        "graph2": {"labels": ["Completed", "Requested", "Accepted"], "data": [0, 0, 0]}
    }

    data["graph2"]["data"][0] = len(
        ServiceRequest.query.filter(
            ServiceRequest.status == "closed",
            ServiceRequest.customer == current_user.id,
        ).all()
    )
    data["graph2"]["data"][1] = len(
        ServiceRequest.query.filter(
            ServiceRequest.status == "requested",
            ServiceRequest.customer == current_user.id,
        ).all()
    )
    data["graph2"]["data"][2] = len(
        ServiceRequest.query.filter(
            ServiceRequest.status == "accepted",
            ServiceRequest.customer == current_user.id,
        ).all()
    )

    return jsonify(data)
