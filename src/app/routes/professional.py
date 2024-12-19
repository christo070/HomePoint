from . import professional, professional_user
from app.models import (
    db,
    User,
    ServiceRequest,
    Review,
    Service
)
from datetime import datetime
from flask import jsonify, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user


@professional.route("/user/professional/dashboard", methods=["GET"])
@login_required
@professional_user
def dashboard():
    if current_user.is_blocked:
        flash("Your account is blocked due to an anomalous activity. Please contact Admin for further details.")

    # Accepted service requests => Professional accepted service request initiated by customer
    accepted_service_requests = ServiceRequest.query.filter_by(
        professional=current_user.id, status="accepted"
    ).all()
    accepted_service_requests_modified = []
    rating = -1
    for service_request in accepted_service_requests:
        customer = User.query.get(service_request.customer)
        service_request_modified = {
            "id": service_request.id,
            "customer": customer.name,
            "phone": customer.phone,
            "address": customer.address,
            "pincode": customer.pincode,
            "rating": rating,
        }
        accepted_service_requests_modified.append(service_request_modified)

    # Open service requests => Professional took no action on the service request initiated by customer
    open_service_request = ServiceRequest.query.filter_by(
        status="requested", professional=current_user.id
    ).all()
    open_service_request_modified = []
    rating = -1
    for service_request in open_service_request:
        customer = User.query.get(service_request.customer)
        service_request_modified = {
            "id": service_request.id,
            "customer": customer.name,
            "phone": customer.phone,
            "address": customer.address,
            "pincode": customer.pincode,
            "rating": rating,
        }
        open_service_request_modified.append(service_request_modified)


    # Closed service requests => Professional completed the service request initiated by customer
    closed_service_requests = ServiceRequest.query.filter_by(
        professional=current_user.id, status="closed"
    ).all()
    closed_service_requests_modified = []
    for service_request in closed_service_requests:
        customer = User.query.get(service_request.customer)
        service_request_modified = {
            "id": service_request.id,
            "customer": customer.name,
            "phone": customer.phone,
            "address": customer.address,
            "pincode": customer.pincode,
            "rating": Review.query.get(service_request.review).rating,
        }
        closed_service_requests_modified.append(service_request_modified)

    return render_template(
        "dashboard_professional.html",
        accepted_service_requests=accepted_service_requests_modified,
        closed_service_requests=closed_service_requests_modified,
        open_service_requests=open_service_request_modified,
    )


@professional.route("/user/professional/service-request/accept", methods=["POST"])
@login_required
@professional_user
def accept_service_request():
    service_request_id = request.args.get("service_request_id")
    if current_user.is_blocked:
        flash("Your account is blocked due to an anomalous activity. Please contact Admin for further details.")
        return redirect(url_for("professional.dashboard"))

    service_request = ServiceRequest.query.get(service_request_id)
    if current_user.id == service_request.professional:
        service_request.status = "accepted"
        service_request.date_accepted = datetime.now()
        db.session.commit()
        flash("Service request accepted")
    else:
        flash("You are not authorized to accept this service request")
    return redirect(url_for("professional.dashboard"))


@professional.route("/user/professional/service-request/reject", methods=["POST"])
@login_required
@professional_user
def reject_service_request():
    service_request_id = request.args.get("service_request_id")

    if current_user.is_blocked:
        flash("Your account is blocked due to an anomalous activity. Please contact Admin for further details.")
        return redirect(url_for("professional.dashboard"))

    service_request = ServiceRequest.query.get(service_request_id)
    if current_user.id == service_request.professional:
        service_request.status = "rejected"
        db.session.commit()
        flash("Service request rejected")
    else:
        flash("You are not authorized to reject this service request")
    return redirect(url_for("professional.dashboard"))


# get customer reviews of the professional (frontend not implemented yet)
@professional.route("/user/professional/reviews", methods=["GET"])
@login_required
@professional_user
def my_reviews():
    reviews = Review.query.filter_by(professional=current_user.id).all()
    reviews_modified = []

    for review in reviews:
        review_modified = {
            "id": review.id,
            "date": review.date,
            "service_request": review.service_request,
            "comment": review.comment,
            "rating": review.rating,
            "customer": User.query.get(review.customer).name,
        }
        reviews_modified.append(review_modified)

    return render_template("reviews.html", reviews=reviews_modified)


@professional.route('/user/professional/search', methods=['GET', 'POST'])
@login_required
@professional_user
def search():
    if request.method == "POST":
        data = request.get_json()
        search_by = data["search_by"]
        search_text = data["search_text"]

        result = {
            "status": "success",
            "data": []
        }
        date_format = "%Y-%m-%d"
        if search_by == "Date":
            service_requests = ServiceRequest.query.filter_by(professional=current_user.id).all()

            if search_text != "":
                search_text = datetime.strptime(search_text, date_format)
                service_requests_modified = []

                for service_request in service_requests:
                    date_requested = datetime.strftime(service_request.date_requested, date_format)
                    date_requested = datetime.strptime(date_requested, date_format)

                    if search_text == date_requested:
                        service_requests_modified.append(service_request)

                service_requests = service_requests_modified

        elif search_by == "Location":
            service_requests = ServiceRequest.query.filter_by(professional=current_user.id).all()
            service_requests = [service_request for service_request in service_requests if search_text.lower() in User.query.get(service_request.customer).address.lower()]

        elif search_by == "Pincode":
            service_requests = ServiceRequest.query.filter_by(professional=current_user.id).all()
            service_requests = [service_request for service_request in service_requests if search_text in User.query.get(service_request.customer).pincode]

        for service_request in service_requests:
            customer = User.query.get(service_request.customer)
            service_request_modified = {
                "id": service_request.id,
                "customer": customer.name,
                "phone": customer.phone,
                "email": customer.email,
                "address": customer.address,
                "pincode": customer.pincode,
                "status": service_request.status,
                "date_requested": service_request.date_requested,
                "date_accepted": service_request.date_accepted,
                "date_completed": service_request.date_completed,
            }
            result["data"].append(service_request_modified)

        return jsonify(result)

    options = ["Location", "Pincode", "Date"]

    return render_template(
        "search.html", role="professional", options = options, fetch_url = url_for("professional.search")
    )


@professional.route('/user/professional/service-request-details', methods=['GET'])
@login_required
@professional_user
def get_service_request_details():
    id = request.args.get("id")
    service_request = ServiceRequest.query.get(id)

    if service_request.professional != current_user.id:
        flash("You are not authorized to view this service request")
        return redirect(url_for("professional.dashboard"))

    review = Review.query.get(service_request.review)
    service_request_data = {
        "id": id,
        "customer": User.query.get(service_request.customer).name,
        "professional": User.query.get(service_request.professional).name,
        "service": Service.query.get(service_request.service).name,
        "date_requested": service_request.date_requested,
        "date_accepted": service_request.date_accepted,
        "date_completed": service_request.date_completed,
        "status": service_request.status,
        "rating": review.rating,
        "review_comment": review.comment
    }
    return render_template("service_request_details.html", service_request = service_request_data)


# Summary showing graphs of the professional's performance
@professional.route('/user/professional/summary', methods=['GET'])
@login_required
@professional_user
def summary():
    return render_template(
        "summary.html",
        role = 'professional',
        fetch_url = url_for("professional.get_summary")
    )


@professional.route('/user/professional/get-summary', methods=['GET'])
@login_required
@professional_user
def get_summary():
    data = {
        "graph1": {
            'labels': ['Poor', 'Fair', 'Good', 'Great', 'Excellent'],
            'data': [0, 0, 0, 0, 0],
            'total': 0
        },
        "graph2": {
            'labels': ['Completed', 'Requested', 'Accepted'],
            'data': [0, 0, 0]
        }
    }

    reviews = Review.query.filter_by(professional=current_user.id).all()

    for review in reviews:
        if review.rating <= 1:
            data["graph1"]["data"][4] += 1
        elif review.rating <= 2:
            data["graph1"]["data"][3] += 1
        elif review.rating <= 3:
            data["graph1"]["data"][2] += 1
        elif review.rating <= 4:
            data["graph1"]["data"][1] += 1
        elif review.rating <= 5:
            data["graph1"]["data"][0] += 1
        data["graph1"]['total'] += 1

    data["graph2"]["data"][0] = len(ServiceRequest.query.filter(ServiceRequest.status == 'closed', ServiceRequest.professional == current_user.id).all())
    data["graph2"]["data"][1] = len(ServiceRequest.query.filter(ServiceRequest.status == 'requested', ServiceRequest.professional == current_user.id).all())
    data["graph2"]["data"][2] = len(ServiceRequest.query.filter(ServiceRequest.status == 'accepted', ServiceRequest.professional == current_user.id).all())

    return jsonify(data)

