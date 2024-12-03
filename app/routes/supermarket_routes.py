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
            name=form.name.data
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
            address=form.address.data,
            contact_person=form.contact_person.data,
            phone=form.phone.data,
            email=form.email.data,
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


@supermarket_bp.route('/<int:id>/subchains/<int:subchain_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_subchain(id, subchain_id):
    """Edit a subchain."""
    supermarket = Supermarket.query.get_or_404(id)
    subchain = Subchain.query.get_or_404(subchain_id)
    
    if subchain.supermarket_id != id:
        flash('Invalid subchain for this supermarket', 'error')
        return redirect(url_for('supermarket.subchains', id=id))
    
    form = SubchainForm(obj=subchain)
    
    if form.validate_on_submit():
        subchain.name = form.name.data
        db.session.commit()
        flash('Subchain updated successfully', 'success')
        return redirect(url_for('supermarket.subchains', id=id))
    
    return render_template(
        'supermarket/edit_subchain.html',
        form=form,
        supermarket=supermarket,
        subchain=subchain
    )


@supermarket_bp.route('/<int:id>/subchains/<int:subchain_id>/delete', methods=['POST'])
@login_required
def delete_subchain(id, subchain_id):
    """Delete a subchain."""
    supermarket = Supermarket.query.get_or_404(id)
    subchain = Subchain.query.get_or_404(subchain_id)
    
    if subchain.supermarket_id != id:
        flash('Invalid subchain for this supermarket', 'error')
        return redirect(url_for('supermarket.subchains', id=id))
    
    try:
        name = subchain.name
        db.session.delete(subchain)
        db.session.commit()
        flash(f'Subchain "{name}" has been deleted', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting subchain: {str(e)}', 'error')
    
    return redirect(url_for('supermarket.subchains', id=id))


@supermarket_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete a supermarket and all its subchains."""
    supermarket = Supermarket.query.get_or_404(id)
    name = supermarket.name
    try:
        db.session.delete(supermarket)
        db.session.commit()
        flash(f'Supermarket "{name}" and all its subchains have been deleted', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting supermarket: {str(e)}', 'error')
    return redirect(url_for('supermarket.index'))
  