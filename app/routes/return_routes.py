"""Return management routes."""
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models import Return, ReturnItem, Supermarket
from app.forms import ReturnForm

return_bp = Blueprint('return', __name__, url_prefix='/return')


@return_bp.route('/')
@login_required
def index():
    """List all returns."""
    returns = Return.query.order_by(Return.return_date.desc()).all()
    return render_template('return/index.html', returns=returns)


@return_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new return."""
    form = ReturnForm()
    form.supermarket_id.choices = [
        (s.id, s.name) for s in Supermarket.query.order_by('name')
    ]
    
    if form.validate_on_submit():
        return_record = Return(
            return_date=form.return_date.data,
            delivery_date=form.delivery_date.data,
            supermarket_id=form.supermarket_id.data,
            subchain_id=form.subchain_id.data if form.subchain_id.data else None
        )
        
        for product_form in form.products:
            item = ReturnItem(
                product_id=product_form.product_id.data,
                quantity=product_form.quantity.data,
                price=product_form.price.data
            )
            return_record.items.append(item)
        
        db.session.add(return_record)
        db.session.commit()
        flash('Return created successfully', 'success')
        return redirect(url_for('return.index'))
    
    return render_template('return/create.html', form=form)
