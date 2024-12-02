from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    SelectField,
    DateField,
    IntegerField,
    FieldList,
    FormField,
    DecimalField,
    BooleanField,
)
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    NumberRange,
    Optional,
    Length,
    ValidationError,
    Regexp,
)
from datetime import date, datetime
from .models import User


def validate_future_date(form, field):
    """Validate that date is not in the past."""
    if field.data and field.data < date.today():
        raise ValidationError("Date cannot be in the past")


def validate_return_date(form, field):
    """Validate return date is not before delivery date."""
    if field.data and form.delivery_date.data and field.data < form.delivery_date.data:
        raise ValidationError("Return date cannot be before delivery date")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=3, max=80),
            Regexp(
                r"^[\w.]+$",
                message="Username can only contain letters, numbers, dots and underscores",
            ),
        ],
    )
    email = StringField(
        "Email", 
        validators=[DataRequired(), Email(), Length(max=120)]
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=8, message="Password must be at least 8 characters long"),
            Regexp(
                r".*[A-Z]",
                message="Password must contain at least one uppercase letter",
            ),
            Regexp(
                r".*[a-z]",
                message="Password must contain at least one lowercase letter",
            ),
            Regexp(r".*[0-9]", message="Password must contain at least one number"),
            Regexp(
                r'.*[!@#$%^&*(),.?":{}|<>]',
                message="Password must contain at least one special character",
            ),
        ],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match"),
        ],
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data.lower()).first()
        if user:
            raise ValidationError(
                "Username already taken. Please choose a different one."
            )

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError(
                "Email already registered. Please use a different one."
            )


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class EmptyForm(FlaskForm):
    submit = SubmitField("Submit")


class ProductForm(FlaskForm):
    product_id = SelectField("Product", coerce=int, validators=[DataRequired()])
    quantity = IntegerField(
        "Quantity",
        validators=[
            DataRequired(),
            NumberRange(min=1, message="Quantity must be greater than 0"),
        ],
    )
    price = DecimalField(
        "Price",
        places=2,
        validators=[
            DataRequired(),
            NumberRange(min=0.01, message="Price must be greater than 0"),
        ],
    )

    def validate_price(self, price):
        if price.data and price.data <= 0:
            raise ValidationError("Price must be greater than 0")


class DeliveryForm(FlaskForm):
    delivery_date = DateField(
        "Delivery Date", 
        validators=[DataRequired()],
        default=datetime.utcnow
    )
    supermarket_id = SelectField(
        "Supermarket", 
        coerce=int,
        validators=[DataRequired()]
    )
    subchain = SelectField(
        "Subchain", 
        coerce=int,
        validators=[Optional()]
    )
    products = FieldList(
        FormField(ProductForm),
        min_entries=1
    )
    submit = SubmitField("Create Delivery")
