from flask import render_template, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload

from app.routes import delivery
from app.models import Delivery, DeliveryItem, Supermarket, Product, db
from app.forms import DeliveryForm, EmptyForm
from app.utils.decorators import log_action


@delivery.route("/", methods=["GET"])
@login_required
@log_action("viewed_deliveries")
def index():
    """
    List all deliveries with optimized queries

    Returns:
        rendered template with deliveries list
    """
    deliveries = (
        Delivery.query.options(
            joinedload(Delivery.supermarket),
            joinedload(Delivery.subchain),
            joinedload(Delivery.items).joinedload(DeliveryItem.product),
        )
        .order_by(Delivery.delivery_date.desc())
        .all()
    )
    return render_template(
        "deliveries/index.html", deliveries=deliveries, form=EmptyForm()
    )


@delivery.route("/create", methods=["GET", "POST"])
@login_required
@log_action("create_delivery")
def create():
    """
    Create a new delivery

    Returns:
        On GET: rendered create form
        On POST success: redirect to index
        On POST error: rendered form with errors
    """
    form = DeliveryForm()

    # Fetch data with optimized queries
    supermarkets = Supermarket.query.filter_by(is_active=True).all()
    products = Product.query.filter_by(is_active=True).all()

    # Populate form choices
    form.supermarket_id.choices = [(s.id, s.name) for s in supermarkets]
    for product_form in form.products:
        product_form.product_id.choices = [(p.id, p.name) for p in products]

    if form.validate_on_submit():
        try:
            # Create new delivery
            new_delivery = Delivery(
                supermarket_id=form.supermarket_id.data,
                subchain_id=form.subchain.data,
                delivery_date=form.delivery_date.data,
                created_by_id=current_user.id,
            )
            db.session.add(new_delivery)
            db.session.flush()

            # Add delivery items
            for product_form in form.products:
                new_item = DeliveryItem(
                    delivery_id=new_delivery.id,
                    product_id=product_form.product_id.data,
                    quantity=product_form.quantity.data,
                    price=product_form.price.data,
                )
                db.session.add(new_item)

            db.session.commit()
            flash("Delivery created successfully", "success")
            return redirect(url_for("delivery.index"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error creating delivery: {str(e)}", "danger")
            current_app.logger.error(
                f"Error creating delivery: {str(e)}", exc_info=True
            )

    return render_template(
        "deliveries/create.html",
        form=form,
        supermarkets=supermarkets,
        products=products,
        products_serialized=[p.to_dict() for p in products],
    )


@delivery.route("/<int:delivery_id>", methods=["GET"])
@login_required
@log_action("view_delivery")
def view(delivery_id):
    """
    View delivery details

    Args:
        delivery_id: ID of the delivery to view

    Returns:
        rendered template with delivery details
    """
    delivery = Delivery.query.options(
        joinedload(Delivery.supermarket),
        joinedload(Delivery.subchain),
        joinedload(Delivery.items).joinedload(DeliveryItem.product),
    ).get_or_404(delivery_id)
    return render_template("deliveries/view.html", delivery=delivery)


@delivery.route("/<int:delivery_id>/delete", methods=["POST"])
@login_required
@log_action("delete_delivery")
def delete(delivery_id):
    """
    Delete a delivery

    Args:
        delivery_id: ID of the delivery to delete

    Returns:
        redirect to index page
    """
    form = EmptyForm()
    if form.validate_on_submit():
        try:
            delivery = Delivery.query.get_or_404(delivery_id)
            db.session.delete(delivery)
            db.session.commit()
            flash("Delivery deleted successfully", "success")

        except Exception as e:
            db.session.rollback()
            flash(f"Error deleting delivery: {str(e)}", "danger")
            current_app.logger.error(
                f"Error deleting delivery: {str(e)}", exc_info=True
            )

    return redirect(url_for("delivery.index"))
