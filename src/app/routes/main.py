from . import main
from flask import render_template, flash

#### Create the database and add some sample data
@main.before_app_request
def create_tables():
    from app.models import db
    db.create_all()

    from app.models import User, Professional, Customer, Service, Review, ServiceRequest
    from datetime import datetime
    from . import bcrypt

    # Create Deleted User if its not in the database, when user deletes the account it will be marked as this deleted user
    if User.query.filter_by(role="deleted").count() == 0:
        deleted_user_password = "Password123"
        hashed_password = bcrypt.generate_password_hash(deleted_user_password).decode("utf-8")
        deleted_user = User(
            id = 0,
            email="deleted_user@email.com",
            password=hashed_password,
            name="Deleted User",
            phone="1234567890",
            address="Deleted User's Address",
            pincode="123456",
            date_created=None,
            role="deleted",
            is_blocked=True
        )

        db.session.add(deleted_user)
        db.session.commit()


        deleted_professional = Professional(
            id=0,
            experience=0,
            service=0,
            description="service PRofessional has deleted the account",
            approval="deleted",
            avg_rating = 0.0,
            tot_reviews = 0
        )

        db.session.add(deleted_professional)
        db.session.commit()

        deleted_customer = Customer(id=0)
        db.session.add(deleted_customer)
        db.session.commit()


    # Create Admin User if its not in the database
    if User.query.filter_by(role="admin").count() == 0:
        admin_password = "Password123"
        hashed_password = bcrypt.generate_password_hash(admin_password).decode("utf-8")
        admin_user = User(
            email="admin@email.com",
            password=hashed_password,
            name="Admin",
            phone="1234567890",
            address="Admin Address",
            pincode="123456",
            date_created=None,
            role="admin",
        )
        db.session.add(admin_user)
        db.session.commit()

    # Testing: create some sample data if the database only has the admin
    # if User.query.count() == 2:
    #     password = "Password123"
    #     hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")


    #     # normal service
    #     new_service = Service(
    #         name="Service 1",
    #         price=100,
    #         duration=1,
    #         period="hours",
    #         date_created = None,
    #         description="Service 1 Description",
    #     )
    #     db.session.add(new_service)
    #     db.session.commit()

    #     new_service1 = Service(
    #         name="Service 2",
    #         price=2000,
    #         duration=2,
    #         period="days",
    #         date_created = None,
    #         description="Service 2 Description",
    #     )
    #     db.session.add(new_service1)
    #     db.session.commit()


    #     # normal customer user
    #     customer_user = User(
    #         email="charlie@email.com",
    #         password=hashed_password,
    #         name="Charlie Doe",
    #         phone="1478523690",
    #         address="123 IVN Street",
    #         pincode="147852",
    #         date_created=None,
    #         role="customer",
    #     )
    #     db.session.add(customer_user)
    #     db.session.commit()

    #     new_customer = Customer(id=customer_user.id)
    #     db.session.add(new_customer)
    #     db.session.commit()


    #     # customer who is blocked
    #     customer_user1 = User(
    #         email="harry@email.com",
    #         password=hashed_password,
    #         name="Harry Doe",
    #         phone="9897456210",
    #         address="123 LOP Street",
    #         pincode="989745",
    #         date_created=None,
    #         role="customer",
    #         is_blocked=True
    #     )
    #     db.session.add(customer_user1)
    #     db.session.commit()

    #     new_customer1 = Customer(id=customer_user1.id)
    #     db.session.add(new_customer1)
    #     db.session.commit()


    #     # normal professional user
    #     professional_user = User(
    #         email="bob@email.com",
    #         password=hashed_password,
    #         name="Bob Doe",
    #         phone="9632587410",
    #         address="123 EDF Street",
    #         pincode="963258",
    #         date_created=None,
    #         role="professional",
    #     )
    #     db.session.add(professional_user)
    #     db.session.commit()

    #     new_professional = Professional(
    #         id=professional_user.id,
    #         experience=5,
    #         service=1,
    #         description="Trained Professional skilled in Service 1",
    #         approval="approved",
    #         avg_rating = 5.0,
    #         tot_reviews = 1
    #     )
    #     db.session.add(new_professional)
    #     db.session.commit()


    #     # professional user with approval pending
    #     professional_user1 = User(
    #         email="denise@email.com",
    #         password=hashed_password,
    #         name="Denise Doe",
    #         phone="3698521470",
    #         address="123 FRT Street",
    #         pincode="369852",
    #         date_created=None,
    #         role="professional"
    #     )
    #     db.session.add(professional_user1)
    #     db.session.commit()

    #     new_professional1 = Professional(
    #         id=professional_user1.id,
    #         experience=3,
    #         service=1,
    #         description="Professional with 3 years experience in Service 1",
    #         approval="pending",
    #     )
    #     db.session.add(new_professional1)
    #     db.session.commit()


    #     # professional user with approval rejected
    #     professional_user2 = User(
    #         email="frank@email.com",
    #         password=hashed_password,
    #         name="Frank Doe",
    #         phone="7894561230",
    #         address="123 FER Street",
    #         pincode="789456",
    #         date_created=None,
    #         role="professional"
    #     )
    #     db.session.add(professional_user2)
    #     db.session.commit()

    #     new_professional2 = Professional(
    #         id=professional_user2.id,
    #         experience=2,
    #         service=1,
    #         description="Does Service 1 works",
    #         approval="rejected",
    #     )
    #     db.session.add(new_professional2)
    #     db.session.commit()


    #     # professional user who is blocked
    #     professional_user3 = User(
    #         email="george@email.com",
    #         password=hashed_password,
    #         name="George Doe",
    #         phone="3214569870",
    #         address="123 EFT Street",
    #         pincode="321456",
    #         date_created=None,
    #         role="professional",
    #         is_blocked=True
    #     )
    #     db.session.add(professional_user3)
    #     db.session.commit()


    #     new_professional3 = Professional(
    #         id=professional_user3.id,
    #         experience=4,
    #         service=2,
    #         description="Does Service 2 perfectly",
    #         approval="approved",
    #     )
    #     db.session.add(new_professional3)
    #     db.session.commit()


    #     # completed service request
    #     new_service_request = ServiceRequest(
    #         service=new_service.id,
    #         customer=customer_user.id,
    #         professional=professional_user.id,
    #         date_requested=datetime.now(),
    #         status="closed"
    #     )
    #     db.session.add(new_service_request)
    #     db.session.commit()

    #     new_service_request.date_accepted=datetime.now()
    #     db.session.commit()


    #     # requested service request
    #     new_service_request1 = ServiceRequest(
    #         service=new_service.id,
    #         customer=customer_user.id,
    #         professional=professional_user.id,
    #         date_requested=datetime.now(),
    #         status="requested"
    #     )
    #     db.session.add(new_service_request1)
    #     db.session.commit()

    #     new_service_request1.date_accepted=datetime.now()
    #     db.session.commit()


    #     # accepted service request
    #     new_service_request2 = ServiceRequest(
    #         service=new_service.id,
    #         customer=customer_user1.id,
    #         professional=professional_user.id,
    #         date_requested=datetime.now(),
    #         status="accepted"
    #     )
    #     db.session.add(new_service_request2)
    #     db.session.commit()

    #     new_service_request2.date_accepted=datetime.now()
    #     db.session.commit()


    #     # Create a review
    #     new_review = Review(
    #         comment="Great service!",
    #         rating=5,
    #         customer=customer_user.id,
    #         professional=professional_user.id,
    #         service_request=new_service_request.id
    #     )
    #     db.session.add(new_review)
    #     db.session.commit()

    #     new_service_request.date_completed=datetime.now()
    #     new_service_request.review=new_review.id
    #     db.session.commit()


@main.route("/")
def index():
    return render_template("index.html")

def page_not_found(e):
    return render_template('404.html'), 404

def internal_server_error(e):
    return render_template('500.html'), 500

@main.route("/test")
def test():
    flash("Test Message")
    return render_template("index.html")