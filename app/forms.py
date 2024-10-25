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
from datetime import date
from flask_babel import lazy_gettext as _l
from .models import User


def validate_future_date(form, field):
    """Validate that date is not in the past"""
    if field.data and field.data < date.today():
        raise ValidationError(_l("Date cannot be in the past"))


def validate_return_date(form, field):
    """Validate return date is not before delivery date"""
    if field.data and form.delivery_date.data and field.data < form.delivery_date.data:
        raise ValidationError(_l("Return date cannot be before delivery date"))


class RegistrationForm(FlaskForm):
    username = StringField(
        _l("Username"),
        validators=[
            DataRequired(),
            Length(min=3, max=80),
            Regexp(
                r"^[\w.]+$",
                message=_l(
                    "Username can only contain letters, numbers, dots and underscores"
                ),
            ),
        ],
    )
    email = StringField(
        _l("Email"), validators=[DataRequired(), Email(), Length(max=120)]
    )
    password = PasswordField(
        _l("Password"),
        validators=[
            DataRequired(),
            Length(min=8, message=_l("Password must be at least 8 characters long")),
            Regexp(
                r".*[A-Z]",
                message=_l("Password must contain at least one uppercase letter"),
            ),
            Regexp(
                r".*[a-z]",
                message=_l("Password must contain at least one lowercase letter"),
            ),
            Regexp(r".*[0-9]", message=_l("Password must contain at least one number")),
            Regexp(
                r'.*[!@#$%^&*(),.?":{}|<>]',
                message=_l("Password must contain at least one special character"),
            ),
        ],
    )
    confirm_password = PasswordField(
        _l("Confirm Password"),
        validators=[
            DataRequired(),
            EqualTo("password", message=_l("Passwords must match")),
        ],
    )
    submit = SubmitField(_l("Register"))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data.lower()).first()
        if user:
            raise ValidationError(
                _l("Username already taken. Please choose a different one.")
            )

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user:
            raise ValidationError(
                _l("Email already registered. Please use a different one.")
            )


class LoginForm(FlaskForm):
    email = StringField(
        _l("Email"), validators=[DataRequired(), Email(), Length(max=120)]
    )
    password = PasswordField(_l("Password"), validators=[DataRequired()])
    remember_me = BooleanField(_l("Remember Me"))
    submit = SubmitField(_l("Login"))


class EmptyForm(FlaskForm):
    submit = SubmitField(_l("Submit"))


class ProductForm(FlaskForm):
    product_id = SelectField(_l("Product"), coerce=int, validators=[DataRequired()])
    quantity = IntegerField(
        _l("Quantity"),
        validators=[
            DataRequired(),
            NumberRange(min=1, message=_l("Quantity must be greater than 0")),
        ],
    )
    price = DecimalField(
        _l("Price"),
        places=2,
        validators=[
            DataRequired(),
            NumberRange(min=0.01, message=_l("Price must be greater than 0")),
        ],
    )

    def validate_price(self, price):
        if price.data and price.data <= 0:
            raise ValidationError(_l("Price must be greater than 0"))


class DeliveryForm(FlaskForm):
    delivery_date = DateField(
        _l("Delivery Date"), validators=[DataRequired(), validate_future_date]
    )
    supermarket_id = SelectField(
        _l("Supermarket"), coerce=int, validators=[DataRequired()]
    )
    subchain = SelectField(_l("Subchain"), coerce=int, validators=[Optional()])
    products = FieldList(FormField(ProductForm), min_entries=1)
    submit = SubmitField(_l("Create Delivery"))

    def validate_products(self, products):
        if not products.data:
            raise ValidationError(_l("At least one product is required"))
        product_ids = set()
        for product in products.data:
            if product["product_id"] in product_ids:
                raise ValidationError(_l("Duplicate products are not allowed"))
            product_ids.add(product["product_id"])


class ReturnForm(FlaskForm):
    supermarket_id = SelectField(
        _l("Supermarket"), coerce=int, validators=[DataRequired()]
    )
    subchain_id = SelectField(_l("Subchain"), coerce=int, validators=[Optional()])
    delivery_date = DateField(
        _l("Delivery Date"), validators=[DataRequired()], default=date.today
    )
    return_date = DateField(
        _l("Return Date"),
        validators=[DataRequired(), validate_return_date],
        default=date.today,
    )
    products = FieldList(FormField(ProductForm), min_entries=1)
    submit = SubmitField(_l("Create Return"))

    def validate_products(self, products):
        if not products.data:
            raise ValidationError(_l("At least one product is required"))
        product_ids = set()
        for product in products.data:
            if product["product_id"] in product_ids:
                raise ValidationError(_l("Duplicate products are not allowed"))
            product_ids.add(product["product_id"])


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(
        _l("Email"), validators=[DataRequired(), Email(), Length(max=120)]
    )
    submit = SubmitField(_l("Request Password Reset"))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(
        _l("New Password"),
        validators=[
            DataRequired(),
            Length(min=8, message=_l("Password must be at least 8 characters long")),
            Regexp(
                r".*[A-Z]",
                message=_l("Password must contain at least one uppercase letter"),
            ),
            Regexp(
                r".*[a-z]",
                message=_l("Password must contain at least one lowercase letter"),
            ),
            Regexp(r".*[0-9]", message=_l("Password must contain at least one number")),
            Regexp(
                r'.*[!@#$%^&*(),.?":{}|<>]',
                message=_l("Password must contain at least one special character"),
            ),
        ],
    )
    password_confirm = PasswordField(
        _l("Confirm Password"),
        validators=[
            DataRequired(),
            EqualTo("password", message=_l("Passwords must match")),
        ],
    )
    submit = SubmitField(_l("Reset Password"))
