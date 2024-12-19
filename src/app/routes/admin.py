from . import admin, admin_user
from app.models import (
    db,
    User,
    Professional,
    Service,
    ServiceRequest,
    Review,
)
from app.forms import ServiceForm
from flask import jsonify, render_template, request, redirect, url_for, flash
from flask_login import login_required


@admin.route("/user/admin/dashboard", methods=["GET"])
@login_required
@admin_user
def dashboard():
    services = Service.query.all()
    services_modified = []
    for service in services:
        if service.is_available == True:
            service_modified = {
                "id": service.id,
                "name": service.name,
                "base_price": service.price,
                "completion_time": str(service.duration)
                + " "
                + service.period.capitalize(),
                "description": service.description,
            }
            services_modified.append(service_modified)

    service_requests = ServiceRequest.query.all()
    service_requests_modified = []
    for service_request in service_requests:
        service_request_modified = {
            "id": service_request.id,
            "customer": User.query.get(service_request.customer).name,
            "professional": User.query.get(service_request.professional).name,
            "service": Service.query.get(service_request.service).name,
            "date_requested": service_request.date_requested,
            "status": service_request.status,
        }
        service_requests_modified.append(service_request_modified)

    # get professionals whose approval is pending
    professionals = Professional.query.filter_by(approval="pending").all()
    professionals.extend(Professional.query.filter_by(approval="rejected").all())
    professionals.extend(Professional.query.filter_by(approval="approved").all())

    professionals_modified = []
    for professional in professionals:
        user = User.query.get(professional.id)
        professional_modified = {
            "id": professional.id,
            "name": user.name,
            "phone": user.phone,
            "email": user.email,
            "address": user.address,
            "pincode": user.pincode,
            "experience": professional.experience,
            "service": Service.query.get(professional.service).name,
            "description": professional.description,
            "status": professional.approval.capitalize(),
            "approval": professional.approval,
        }
        professionals_modified.append(professional_modified)

    form = ServiceForm()

    return render_template(
        "dashboard_admin.html",
        services=services_modified,
        service_requests=service_requests_modified,
        professionals=professionals_modified,
        form=form,
    )


@admin.route("/user/admin/service/create", methods=["POST"])
@login_required
@admin_user
def create_service():
    form = ServiceForm()

    if form.validate_on_submit():

        new_service = Service(
            name=form.name.data,
            price=form.price.data,
            duration=form.duration.data,
            period=form.period.data,
            date_created=None,
            description=form.description.data,
        )

        db.session.add(new_service)
        db.session.commit()

        flash("Service created successfully")
        return redirect(url_for("user.dashboard"))

    return redirect(url_for("user.dashboard"))


# Get details of all service requests for the service
@admin.route("/user/admin/service/view", methods=["GET"])
@login_required
@admin_user
def view_service():
    service_id = request.args.get("service_id")
    service = Service.query.get(service_id).name

    service_requests = ServiceRequest.query.filter_by(service=service_id).all()
    service_requests_modified = []
    for service_request in service_requests:
        service_request_modified = {
            "id": service_request.id,
            "customer": User.query.get(service_request.customer).name,
            "professional": User.query.get(service_request.professional).name,
            "service": Service.query.get(service_request.service).name,
            "date_requested": service_request.date_requested,
            "date_accepted": service_request.date_accepted,
            "date_completed": service_request.date_completed,
            "status": service_request.status,
            "rating": Review.query.get(service_request.review).rating,
        }
        service_requests_modified.append(service_request_modified)

    return render_template(
        "service_view.html", service_requests=service_requests_modified, service=service
    )


@admin.route("/user/admin/service/edit", methods=["GET", "POST"])
@login_required
@admin_user
def edit_service():
    service_id = request.args.get("id")

    if request.method == "GET":
        data = {}
        try:
            service = Service.query.get(service_id)
            if service:
                data["status"] = "success"
                data["id"] = service.id
                data["name"] = service.name
                data["price"] = service.price
                data["duration"] = service.duration
                data["period"] = service.period
                data["description"] = service.description
            else:
                data["status"] = "error"
                data["message"] = "Service not found"
        except:
            data["status"] = "error"
            data["message"] = "Error when fetching service details"

        return jsonify(data)

    form = ServiceForm()

    if form.validate_on_submit():
        service = Service.query.get(service_id)
        service.name = form.name.data
        service.price = float(form.price.data)
        service.duration = form.duration.data
        service.period = form.period.data
        service.description = form.description.data

        db.session.commit()
        flash("Service updated successfully")
        return redirect(url_for("user.dashboard"))

    flash("Service update failed")
    return redirect(url_for("user.dashboard"))


@admin.route("/user/admin/service/delete", methods=["POST"])
@login_required
@admin_user
def delete_service():
    data = request.get_json()
    service_id = data["id"]

    service = Service.query.get(service_id)
    service.name = f"Service not found"
    service.price = 0
    service.duration = 0
    service.period = "hours"
    service.description = "Service no longer available"
    service.is_available = False
    db.session.commit()

    flash("Service deleted successfully")
    return redirect(url_for("user.dashboard"))


# Check whether the service can be deleted. Service can be deleted if there is not open service request for the service
@admin.route("/user/admin/service/delete/check", methods=["POST"])
@login_required
@admin_user
def delete_service_check():
    data = request.get_json()
    service_id = data["id"]
    service_request_requested = ServiceRequest.query.filter_by(
        service=service_id, status="requested"
    ).first()
    service_request_accepted = ServiceRequest.query.filter_by(
        service=service_id, status="accepted"
    ).first()

    response = {}

    if service_request_requested is None or service_request_accepted is None:
        response["can_delete"] = True
        response["message"] = (
            "Service can be deleted, as there are no open service requests for the service"
        )
    else:
        response["can_delete"] = False
        response["message"] = (
            "The service cannot be deleted, since there are open service requests for the service"
        )

    return jsonify(response)


@admin.route("/user/admin/professional/view", methods=["GET"])
@login_required
@admin_user
def view_professional():
    professional_id = request.args.get("professional_id")
    professional = Professional.query.get(professional_id)
    user = User.query.get(professional_id)

    user_data = {
        "id": professional.id,
        "name": user.name,
        "phone": user.phone,
        "email": user.email,
        "address": user.address,
        "pincode": user.pincode,
        "experience": professional.experience,
        "service": Service.query.get(professional.service).name,
        "description": professional.description,
        "status": professional.approval.capitalize(),
        "avg_rating": professional.avg_rating,
        "tot_reviews": professional.tot_reviews,
    }

    reviews = Review.query.filter_by(professional=professional_id).all()
    reviews_modified = []
    for review in reviews:
        review_modified = {
            "id": review.id,
            "customer": User.query.get(review.customer).name,
            "date": review.date,
            "request_id": review.service_request,
            "rating": review.rating,
            "comment": review.comment,
        }
        reviews_modified.append(review_modified)

    return render_template(
        "professional_view.html", user=user_data, reviews=reviews_modified
    )


@admin.route("/user/admin/professional/approve", methods=["POST"])
@login_required
@admin_user
def approve_professional():
    professional_id = request.args.get("professional_id")
    professional = Professional.query.get(professional_id)
    professional.approval = "approved"
    db.session.commit()
    flash("Professional marked approved")
    return redirect(url_for("user.dashboard"))


@admin.route("/user/admin/professional/reject", methods=["POST"])
@login_required
@admin_user
def reject_professional():
    professional_id = request.args.get("professional_id")
    professional = Professional.query.get(professional_id)
    professional.approval = "rejected"
    db.session.commit()
    flash("Professional marked rejected")
    return redirect(url_for("user.dashboard"))


@admin.route("/user/admin/search", methods=["GET", "POST"])
@login_required
@admin_user
def search():
    if request.method == "POST":
        data = request.get_json()
        search_by = data["search_by"]
        search_text = data["search_text"]

        result = {"status": "success", "data": []}
        if search_by == "Customer":
            users = User.query.filter_by(role="customer").all()
            if users:
                for user in users:
                    if search_text.lower() in user.name.lower():
                        user_data = {
                            "id": user.id,
                            "name": user.name,
                            "email": user.email,
                            "phone": user.phone,
                            "address": user.address,
                            "pincode": user.pincode,
                            "role": user.role,
                        }
                        result["data"].append(user_data)
        elif search_by == "Service Professional":
            users = User.query.filter_by(role="professional").all()
            if users:
                for user in users:
                    professional = Professional.query.get(user.id)
                    if search_text.lower() in user.name.lower():
                        professional_data = {
                            "id": user.id,
                            "name": user.name,
                            "email": user.email,
                            "phone": user.phone,
                            "address": user.address,
                            "pincode": user.pincode,
                            "experience": professional.experience,
                            "service": Service.query.get(professional.service).name,
                            "description": professional.description,
                            "rating": professional.avg_rating,
                            "tot_reviews": professional.tot_reviews,
                        }
                        result["data"].append(professional_data)
        elif search_by == "Service Request":
            service_requests = ServiceRequest.query.all()
            for service_request in service_requests:
                customer = User.query.get(service_request.customer)
                professional = User.query.get(service_request.professional)
                service = Service.query.get(service_request.service)
                if (
                    search_text.lower() in customer.name.lower()
                    or search_text.lower() in professional.name.lower()
                    or search_text.lower() in service.name.lower()
                ):
                    service_request_data = {
                        "id": service_request.id,
                        "service": service.name,
                        "customer": customer.name,
                        "professional": professional.name,
                        "date_requested": service_request.date_requested,
                        "date_accepted": service_request.date_accepted,
                        "date_completed": service_request.date_completed,
                        "status": service_request.status,
                    }
                    result["data"].append(service_request_data)

        return jsonify(result)

    search_by_options = ["Customer", "Service Professional", "Service Request"]

    return render_template(
        "search.html",
        role="admin",
        options=search_by_options,
        fetch_url=url_for("admin.search"),
    )


@admin.route("/user/admin/user-details", methods=["GET", "POST"])
@login_required
@admin_user
def get_user_details():
    user_id = request.args.get("id")
    user = User.query.get(user_id)
    user_data = {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "address": user.address,
        "pincode": user.pincode,
        "role": (user.role).capitalize(),
        "date_created": user.date_created,
        "status": "Active" if not user.is_blocked else "Inactive",
        "is_blocked": user.is_blocked,
    }
    if user.role == "professional":
        professional = Professional.query.get(user.id)
        user_data["experience"] = professional.experience
        user_data["service"] = Service.query.get(professional.service).name
        user_data["description"] = professional.description
        user_data["avg_rating"] = professional.avg_rating
        user_data["tot_reviews"] = professional.tot_reviews
        user_data["approval"] = (professional.approval).capitalize()

        reviews = Review.query.filter_by(professional=user_id).all()
        reviews_modified = []
        for review in reviews:
            review_modified = {
                "id": review.id,
                "customer": User.query.get(review.customer).name,
                "date": review.date,
                "request_id": review.service_request,
                "rating": review.rating,
                "comment": review.comment,
            }
            reviews_modified.append(review_modified)
    elif user.role == "customer":
        reviews = Review.query.filter_by(customer=user_id).all()
        reviews_modified = []
        for review in reviews:
            review_modified = {
                "id": review.id,
                "professional": User.query.get(review.professional).name,
                "date": review.date,
                "request_id": review.service_request,
                "rating": review.rating,
                "comment": review.comment,
            }
            reviews_modified.append(review_modified)

    return render_template(
        "user_details.html", user=user_data, reviews=reviews_modified
    )


@admin.route("/user/admin/service-request-details", methods=["GET"])
@login_required
@admin_user
def get_service_request_details():
    id = request.args.get("id")
    service_request = ServiceRequest.query.get(id)
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
        "rating": review.rating if review else "Not rated yet",
        "review_comment": review.comment if review else "Not rated yet",
    }
    return render_template(
        "service_request_details.html", service_request=service_request_data
    )


@admin.route("/user/admin/block-user", methods=["POST"])
@login_required
@admin_user
def block_user():
    data = request.get_json()
    user_id = data["id"]

    response = {}
    try:
        user = User.query.get(user_id)
        user.is_blocked = True
        db.session.commit()
        flash("User blocked successfully")
        response["status"] = "success"
    except:
        flash("Error when blocking user")
        response["status"] = "error"

    return jsonify(response)


@admin.route("/user/admin/unblock-user", methods=["POST"])
@login_required
@admin_user
def unblock_user():
    data = request.get_json()
    user_id = data["id"]

    response = {}
    try:
        user = User.query.get(user_id)
        user.is_blocked = False
        db.session.commit()
        flash("User unblocked successfully")
        response["status"] = "success"
    except:
        flash("Error when unblocking user")
        response["status"] = "error"

    return jsonify(response)


@admin.route("/user/admin/summary", methods=["GET"])
@login_required
@admin_user
def summary():
    return render_template(
        "summary.html", role="admin", fetch_url=url_for("admin.get_summary")
    )


@admin.route("/user/admin/get-summary", methods=["GET"])
@login_required
@admin_user
def get_summary():
    data = {
        "graph1": {
            "labels": ["Poor", "Fair", "Good", "Great", "Excellent"],
            "data": [0, 0, 0, 0, 0],
            "total": 0,
        },
        "graph2": {"labels": ["Completed", "Requested", "Accepted"], "data": [0, 0, 0]},
    }

    reviews = Review.query.all()

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
        data["graph1"]["total"] += 1

    data["graph2"]["data"][0] = len(
        ServiceRequest.query.filter(ServiceRequest.status == "closed").all()
    )
    data["graph2"]["data"][1] = len(
        ServiceRequest.query.filter(ServiceRequest.status == "requested").all()
    )
    data["graph2"]["data"][2] = len(
        ServiceRequest.query.filter(ServiceRequest.status == "accepted").all()
    )

    return jsonify(data)
