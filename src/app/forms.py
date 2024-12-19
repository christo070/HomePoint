from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    SelectField,
    IntegerField,
    FloatField,
    EmailField,
    HiddenField,
    RadioField,
    TextAreaField
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
    ValidationError
)
from app.models import User, Service


def get_service_options():
    services = Service.query.all()
    options = [(service.id, service.name) for service in services if service.name != "Service not found"]
    return options


class ServiceSelectField(SelectField):
    def __init__(self, *args, **kwargs):
        super(ServiceSelectField, self).__init__(*args, **kwargs)
        self.choices = get_service_options()


class LoginForm(FlaskForm):
    email = EmailField(
        "Email",
        validators=[DataRequired(), Email()],
        render_kw={
            "class": "form-control",
            "placeholder": "name@example.com",
            "id": "floatingEmail",
            "aria-describedby": "floatingEmailFeedback",
        },
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=8, max=16)],
        render_kw={
            "class": "form-control",
            "placeholder": "Password",
            "id": "floatingPassword",
            "aria-describedby": "floatingPasswordFeedback",
        },
    )
    submit = SubmitField(
        "Submit",
        render_kw={
            "class": "btn btn-lg btn-primary w-100 py-2",
        },
    )


class UserRegistrationForm(FlaskForm):
    email = EmailField(
        "Email",
        validators=[DataRequired(), Email(message="Invalid email")],
        render_kw={
            "class": "form-control",
            "placeholder": "name@example.com",
            "id": "floatingEmail",
            "aria-describedby": "floatingEmailFeedback",
        },
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(max=16)],
        render_kw={
            "class": "form-control",
            "placeholder": "Password",
            "id": "floatingPassword",
            "aria-describedby": "floatingPasswordFeedback",
        },
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            Length(max=16),
            EqualTo("password", message="Passwords must match"),
        ],
        render_kw={
            "class": "form-control",
            "placeholder": "Confirm Password",
            "id": "floatingConfirmPassword",
            "aria-describedby": "floatingConfirmPasswordFeedback",
        },
    )
    name = StringField(
        "Full Name",
        validators=[DataRequired()],
        render_kw={
            "class": "form-control",
            "placeholder": "Name",
            "id": "floatingName",
            "aria-describedby": "floatingNameFeedback",
        },
    )
    phone = StringField(
        "Phone Number",
        validators=[DataRequired(), Length(max=10)],
        render_kw={
            "class": "form-control",
            "placeholder": "Phone",
            "id": "floatingPhone",
            "aria-describedby": "floatingPhoneFeedback",
        },
    )
    address = StringField(
        "Address",
        validators=[DataRequired(), Length(max=50)],
        render_kw={
            "class": "form-control",
            "placeholder": "Address",
            "id": "floatingAddress",
            "aria-describedby": "floatingAddressFeedback",
        },
    )
    pincode = StringField(
        "Pincode",
        validators=[DataRequired(), Length(max=6)],
        render_kw={
            "class": "form-control",
            "placeholder": "Pincode",
            "id": "floatingPincode",
            "aria-describedby": "floatingPincodeFeedback",
        },
    )
    submit = SubmitField(
        "Submit",
        render_kw={
            "class": "btn btn-primary w-100 py-2",
        },
    )

    def validate_email(form, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError("Email already registered")


class ProfessionalRegistrationForm(UserRegistrationForm):
    experience = IntegerField(
        "Experience (in Years)",
        validators=[DataRequired()],
        render_kw={
            "class": "form-control",
            "placeholder": "Experience",
            "id": "floatingExperience",
            "aria-describedby": "floatingExperienceFeedback",
        },
    )
    service = ServiceSelectField(
        "Service",
        validators=[DataRequired()],
        render_kw={
            "class": "form-control",
            "placeholder": "Service",
            "id": "floatingService",
            "aria-describedby": "floatingServiceFeedback",
        },
    )
    description = StringField(
        "Service Description",
        validators=[DataRequired()],
        render_kw={
            "class": "form-control",
            "placeholder": "Description",
            "id": "floatingDescription",
            "aria-describedby": "floatingDescriptionFeedback",
        },
    )

    def validate_service(form, service):
        options = get_service_options()
        if int(service.data) not in dict(options).keys():
            raise ValidationError("Service not available")


# Provided considering future changes in `Customer` model, which may include Customer specific fields
class CustomerRegistrationForm(UserRegistrationForm):
    pass


class UserProfileForm(FlaskForm):
    email = EmailField(
        "Email",
        validators=[DataRequired(), Email()],
        render_kw={
            "class": "form-control",
            "placeholder": "name@example.com",
            "id": "floatingEmail",
            "aria-describedby": "floatingEmailFeedback",
        },
    )
    name = StringField(
        "Full Name",
        validators=[DataRequired()],
        render_kw={
            "class": "form-control",
            "placeholder": "Name",
            "id": "floatingName",
            "aria-describedby": "floatingNameFeedback",
        },
    )
    phone = StringField(
        "Phone",
        validators=[DataRequired(), Length(max=10)],
        render_kw={
            "class": "form-control",
            "placeholder": "Phone",
            "id": "floatingPhone",
            "aria-describedby": "floatingPhoneFeedback",
        },
    )
    address = StringField(
        "Address",
        validators=[DataRequired(), Length(max=100)],
        render_kw={
            "class": "form-control",
            "placeholder": "Address",
            "id": "floatingAddress",
            "aria-describedby": "floatingAddressFeedback",
        },
    )
    pincode = StringField(
        "Pincode",
        validators=[DataRequired(), Length(max=6)],
        render_kw={
            "class": "form-control",
            "placeholder": "Pincode",
            "id": "floatingPincode",
            "aria-describedby": "floatingPincodeFeedback",
        },
    )
    submit = SubmitField(
        "Update",
        render_kw={
            "class": "btn btn-primary w-100 py-2",
        },
    )


class ProfessionalProfileForm(UserProfileForm):
    experience = IntegerField(
        "Experience (in Years)",
        validators=[DataRequired()],
        render_kw={
            "class": "form-control",
            "placeholder": "Experience",
            "id": "floatingExperience",
            "aria-describedby": "floatingExperienceFeedback",
        },
    )
    service = StringField(
        "Service",
        validators=[DataRequired()],
        render_kw={
            "readonly": True,
            "class": "form-control",
            "placeholder": "Service",
            "id": "floatingService",
            "aria-describedby": "floatingServiceFeedback",
        },
    )
    description = StringField(
        "Description",
        validators=[DataRequired()],
        render_kw={
            "class": "form-control",
            "placeholder": "Description",
            "id": "floatingDescription",
            "aria-describedby": "floatingDescriptionFeedback",
        },
    )


class CustomerProfileForm(UserProfileForm):
    pass


class AdminProfileForm(UserProfileForm):
    pass


class ServiceForm(FlaskForm):
    id = HiddenField(
        "Id",
        render_kw={
            "class": "form-control",
            "id": "floatingId",
            "aria-describedby": "floatingIdFeedback",
        },
    )
    name = StringField(
        "Service Name",
        validators=[DataRequired()],
        render_kw={
            "class": "form-control rounded-3",
            "placeholder": "Name",
            "id": "floatingName",
            "aria-describedby": "floatingNameFeedback",
        },
    )
    price = FloatField(
        "Price",
        validators=[DataRequired()],
        render_kw={
            "class": "form-control rounded-3",
            "placeholder": "Price",
            "id": "floatingPrice",
            "aria-describedby": "floatingPriceFeedback",
        },
    )
    duration = IntegerField(
        "Duration",
        validators=[DataRequired()],
        render_kw={
            "class": "form-control rounded-3",
            "placeholder": "Duration",
            "id": "floatingDuration",
            "aria-describedby": "floatingDurationFeedback",
        },
    )
    period = SelectField(
        "Duration Period",
        choices=[
            ("hours", "Hours"),
            ("days", "Days"),
            ("weeks", "Weeks"),
            ("months", "Months"),
        ],
        validators=[DataRequired()],
        render_kw={
            "class": "form-control rounded-3",
            "placeholder": "DurationPeriod",
            "id": "floatingDurationPeriod",
            "aria-describedby": "floatingDurationPeriodFeedback",
        },
    )
    description = StringField(
        "Description",
        validators=[DataRequired()],
        render_kw={
            "class": "form-control rounded-3",
            "placeholder": "Description",
            "id": "floatingDescription",
            "aria-describedby": "floatingDescriptionFeedback",
        },
    )
    submit = SubmitField(
        "Create",
        render_kw={
            "class": "w-100 mb-2 btn btn-lg rounded-3 btn-primary",
        },
    )


class ServiceRemarkForm(FlaskForm):
    id = HiddenField("Service Request Id")
    service = StringField(
        "Service",
        render_kw={
            "readonly": True,
            "class": "form-control rounded-3",
            "placeholder": "Service Name",
            "id": "floatingService",
            "aria-describedby": "floatingServiceFeedback",
        },
    )
    date_requested = StringField(
        "Service Requested Date",
        render_kw={
            "readonly": True,
            "class": "form-control rounded-3",
            "placeholder": "Service Requested Date",
            "id": "floatingRequestedDate",
            "aria-describedby": "floatingRequestedDateFeedback",
        },
    )
    date_accepted = StringField(
        "Service Accepted Date",
        render_kw={
            "readonly": True,
            "class": "form-control rounded-3",
            "placeholder": "Service Accepted Date",
            "id": "floatingAcceptedDate",
            "aria-describedby": "floatingAcceptedDateFeedback",
        },
    )
    professional = StringField(
        "Service Professional",
        render_kw={
            "readonly": True,
            "class": "form-control rounded-3",
            "placeholder": "Service Professional",
            "id": "floatingProfessional",
            "aria-describedby": "floatingProfessionalFeedback",
        },
    )
    phone = StringField(
        "Contact",
        render_kw={
            "readonly": True,
            "class": "form-control rounded-3",
            "placeholder": "Phone Number",
            "id": "floatingPhone",
            "aria-describedby": "floatingPhoneFeedback",
        },
    )
    remarks = TextAreaField(
        "Remarks",
        validators=[DataRequired()],
        render_kw={
            "readonly": False,
            "class": "form-control rounded-3",
            "placeholder": "Remarks on the service",
            "id": "floatingRemarks",
            "aria-describedby": "floatingRemarksFeedback",
        },
    )
    rating = RadioField(
        "Rating",
        choices=[(1, "Bad"), (2, "Poor"), (3, "Fair"), (4, "Satisfied"), (5, "Good")],
        validators=[DataRequired()],
        render_kw={
            "readonly": False,
            "class": "form-check-input",
            "placeholder": "Rating",
            "id": "floatingRating",
            "aria-describedby": "floatingRatingFeedback"
        },
    )
    submit = SubmitField(
        "Submit",
        render_kw={
            "class": "w-100 mb-2 btn btn-lg rounded-3 btn-primary",
        },
    )
