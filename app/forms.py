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
    """Form for creating and editing products."""
    name = StringField(
        "Name",
        validators=[DataRequired(), Length(max=100)]
    )
    price = DecimalField(
        "Price",
        places=2,
        validators=[
            DataRequired(),
            NumberRange(min=0.01, message="Price must be greater than 0"),
        ],
    )
    weight = DecimalField(
        "Weight (kg)",
        places=3,
        validators=[
            DataRequired(),
            NumberRange(min=0.001, message="Weight must be greater than 0"),
        ],
    )
    submit = SubmitField("Save Product")


class DeliveryProductForm(FlaskForm):
    """Form for products in a delivery."""
    product_id = SelectField(
        "Product", 
        coerce=int,
        choices=[]  # Initialize with empty choices
    )
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
    total = DecimalField("Total", places=2, render_kw={'readonly': True})

    class Meta:
        csrf = False  # Disable CSRF for nested form

    def __init__(self, *args, **kwargs):
        super(DeliveryProductForm, self).__init__(*args, **kwargs)
        # Set default choices
        self.product_id.choices = [(0, 'Select Product')]


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
    subchain_id = SelectField(
        "Subchain", 
        coerce=int,
        validators=[Optional()],
        choices=[]
    )
    products = FieldList(
        FormField(DeliveryProductForm),
        min_entries=1
    )
    total_amount = DecimalField("Total Amount", places=2, render_kw={'readonly': True})
    submit = SubmitField("Create Delivery")

    def __init__(self, *args, **kwargs):
        super(DeliveryForm, self).__init__(*args, **kwargs)
        self.subchain_id.choices = [(0, 'Select Subchain')]

    def validate_products(self, field):
        valid_products = [f for f in field if f.product_id.data and f.product_id.data != 0]
        if not valid_products:
            raise ValidationError('Please add at least one product')


class ReturnForm(FlaskForm):
    """Form for creating and editing returns."""
    delivery_date = DateField(
        "Delivery Date",
        validators=[DataRequired()],
        default=datetime.utcnow
    )
    return_date = DateField(
        "Return Date",
        validators=[DataRequired()],
        default=datetime.utcnow
    )
    supermarket_id = SelectField(
        "Supermarket", 
        coerce=int,
        validators=[DataRequired()]
    )
    subchain_id = SelectField(
        "Subchain", 
        coerce=int,
        validators=[Optional()],
        choices=[]
    )
    products = FieldList(
        FormField(DeliveryProductForm),
        min_entries=1
    )
    total_amount = DecimalField("Total Amount", places=2, render_kw={'readonly': True})
    submit = SubmitField("Create Return")

    def __init__(self, *args, **kwargs):
        super(ReturnForm, self).__init__(*args, **kwargs)
        self.subchain_id.choices = [(0, 'Select Subchain')]

    def validate_products(self, field):
        valid_products = [f for f in field if f.product_id.data and f.product_id.data != 0]
        if not valid_products:
            raise ValidationError('Please add at least one product')


class SupermarketForm(FlaskForm):
    """Form for creating and editing supermarkets."""
    name = StringField(
        "Name", 
        validators=[DataRequired(), Length(max=100)]
    )
    submit = SubmitField("Save Supermarket")


class SubchainForm(FlaskForm):
    """Form for creating and editing subchains."""
    name = StringField(
        "Name", 
        validators=[DataRequired(), Length(max=100)]
    )
    address = StringField(
        "Address", 
        validators=[Optional(), Length(max=200)]
    )
    contact_person = StringField(
        "Contact Person", 
        validators=[Optional(), Length(max=100)]
    )
    phone = StringField(
        "Phone", 
        validators=[Optional(), Length(max=20)]
    )
    email = StringField(
        "Email", 
        validators=[Optional(), Email(), Length(max=120)]
    )
    submit = SubmitField("Save Subchain")
