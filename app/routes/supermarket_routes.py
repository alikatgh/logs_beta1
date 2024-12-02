"""Supermarket management routes."""
from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask_login import login_required
from app.extensions import db
from app.models import Supermarket, Subchain
from app.forms import SupermarketForm, SubchainForm

# Create the blueprint
supermarket_bp = Blueprint('supermarket', __name__, url_prefix='/supermarket')


@supermarket_bp.route('/')
@login_required
def index():
    """List all supermarkets."""
    supermarkets = Supermarket.query.order_by(Supermarket.name).all()
    return render_template('supermarket/index.html', supermarkets=supermarkets)


@supermarket_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new supermarket."""
    form = SupermarketForm()
    if form.validate_on_submit():
        supermarket = Supermarket(
            name=form.name.data,
            address=form.address.data,
            contact_person=form.contact_person.data,
            phone=form.phone.data,
            email=form.email.data
        )
        db.session.add(supermarket)
        db.session.commit()
        flash('Supermarket created successfully', 'success')
        return redirect(url_for('supermarket.index'))
    return render_template('supermarket/create.html', form=form)


@supermarket_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit a supermarket."""
    supermarket = Supermarket.query.get_or_404(id)
    form = SupermarketForm(obj=supermarket)
    
    if form.validate_on_submit():
        supermarket.name = form.name.data
        supermarket.address = form.address.data
        supermarket.contact_person = form.contact_person.data
        supermarket.phone = form.phone.data
        supermarket.email = form.email.data
        db.session.commit()
        flash('Supermarket updated successfully', 'success')
        return redirect(url_for('supermarket.index'))
    
    return render_template('supermarket/edit.html', form=form, supermarket=supermarket)


@supermarket_bp.route('/<int:id>/subchains')
@login_required
def subchains(id):
    """List subchains for a supermarket."""
    supermarket = Supermarket.query.get_or_404(id)
    return render_template('supermarket/subchains.html', supermarket=supermarket)


@supermarket_bp.route('/<int:id>/subchains/create', methods=['GET', 'POST'])
@login_required
def create_subchain(id):
    """Create a new subchain for a supermarket."""
    supermarket = Supermarket.query.get_or_404(id)
    form = SubchainForm()
    
    if form.validate_on_submit():
        subchain = Subchain(
            name=form.name.data,
            supermarket_id=id
        )
        db.session.add(subchain)
        db.session.commit()
        flash('Subchain created successfully', 'success')
        return redirect(url_for('supermarket.subchains', id=id))
    
    return render_template(
        'supermarket/create_subchain.html',
        form=form,
        supermarket=supermarket
    )


@supermarket_bp.route('/get_subchains/<int:supermarket_id>')
@login_required
def get_subchains(supermarket_id):
    """Get subchains for a supermarket (AJAX endpoint)."""
    subchains = Subchain.query.filter_by(supermarket_id=supermarket_id).all()
    return jsonify([{'id': s.id, 'name': s.name} for s in subchains])
  