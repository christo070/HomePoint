from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import ForeignKey
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    phone: Mapped[str] = mapped_column(nullable=False)
    address: Mapped[str] = mapped_column(nullable=False)
    pincode: Mapped[str] = mapped_column(nullable=False)
    date_created: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.now()
    )
    # customer/professional/admin(only 1)/deleted(only 1)
    role: Mapped[str] = mapped_column(nullable=False, default="customer")
    is_blocked: Mapped[bool] = mapped_column(nullable=False, default=False)


class Professional(db.Model):
    __tablename__ = "professionals"
    id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), primary_key=True, nullable=False
    )
    # Work Experience in Years
    experience: Mapped[int] = mapped_column(nullable=False)
    service: Mapped[int] = mapped_column(ForeignKey("services.id"), nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    # Pending/Approved/Rejected/Deleted
    approval: Mapped[str] = mapped_column(nullable=False, default="pending")
    avg_rating: Mapped[float] = mapped_column(nullable=True, default=0.0)
    tot_reviews: Mapped[int] = mapped_column(nullable=True, default=0)


class Admin(db.Model):
    __tablename__ = "admin"
    id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), primary_key=True, nullable=False
    )


class Customer(db.Model):
    __tablename__ = "customers"
    id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), primary_key=True, nullable=False
    )


class Service(db.Model):
    __tablename__ = "services"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    duration: Mapped[int] = mapped_column(nullable=False)
    # hours/days/weeks/months
    period: Mapped[str] = mapped_column(nullable=False, default="hours")
    description: Mapped[str] = mapped_column(nullable=False)
    date_created: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.now()
    )
    is_available: Mapped[bool] = mapped_column(nullable=False, default=True)


class Review(db.Model):
    __tablename__ = "reviews"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now())
    comment: Mapped[str] = mapped_column(nullable=True)
    rating: Mapped[int] = mapped_column(nullable=True, default=-1)
    customer: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    professional: Mapped[int] = mapped_column(
        ForeignKey("professionals.id"), nullable=False
    )
    service_request: Mapped[int] = mapped_column(
        ForeignKey("service_requests.id"), nullable=False
    )


class ServiceRequest(db.Model):
    __tablename__ = "service_requests"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    service: Mapped[int] = mapped_column(ForeignKey("services.id"), nullable=False)
    customer: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    professional: Mapped[int] = mapped_column(
        ForeignKey("professionals.id"), nullable=False, default="Not Assigned"
    )
    date_requested: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.now()
    )
    date_accepted: Mapped[datetime] = mapped_column(nullable=True)
    date_completed: Mapped[datetime] = mapped_column(nullable=True)
    # Requested/Accepted/Closed/Cancelled
    status: Mapped[str] = mapped_column(nullable=False, default="requested")
    review: Mapped[int] = mapped_column(ForeignKey("reviews.id"), nullable=True)
