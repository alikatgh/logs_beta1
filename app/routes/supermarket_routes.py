from flask import render_template, redirect, url_for, request, flash
from app import db
from app.models import Supermarket, Subchain
from . import supermarket  # Import the supermarket blueprint

# Index route to view a list of all supermarkets - renders `supermarkets/index.html`
@supermarket.route('/supermarkets/index', methods=['GET'])
def index():
    supermarkets = Supermarket.query.all()
    return render_template('supermarkets/index.html', supermarkets=supermarkets)

# View all supermarkets and subchains - renders `manage_supermarkets.html`
@supermarket.route('/supermarkets', methods=['GET', 'POST'])
def manage_supermarkets():
    supermarkets = Supermarket.query.all()
    subchains = Subchain.query.all()
    return render_template('supermarkets/manage_supermarkets.html', supermarkets=supermarkets, subchains=subchains)

# Add new supermarket
@supermarket.route('/supermarkets/add', methods=['POST'])
def add_supermarket():
    name = request.form.get('name')
    address = request.form.get('address')
    if name and address:
        supermarket = Supermarket(name=name, address=address)
        db.session.add(supermarket)
        db.session.commit()
        flash('Supermarket added successfully!', 'success')
    return redirect(url_for('supermarket.manage_supermarkets'))

# Edit supermarket
@supermarket.route('/supermarkets/edit/<int:id>', methods=['GET', 'POST'])
def edit_supermarket(id):
    supermarket = Supermarket.query.get_or_404(id)
    if request.method == 'POST':
        supermarket.name = request.form.get('name')
        supermarket.address = request.form.get('address')
        db.session.commit()
        flash('Supermarket updated successfully!', 'success')
        return redirect(url_for('supermarket.manage_supermarkets'))
    return render_template('supermarkets/edit_supermarket.html', supermarket=supermarket)

# Delete supermarket
@supermarket.route('/supermarkets/delete/<int:id>', methods=['POST'])
def delete_supermarket(id):
    supermarket = Supermarket.query.get_or_404(id)
    if supermarket.deliveries.count() == 0:
        db.session.delete(supermarket)
        db.session.commit()
        flash('Supermarket deleted successfully!', 'success')
    else:
        flash('Cannot delete supermarket with existing deliveries.', 'danger')
    return redirect(url_for('supermarket.manage_supermarkets'))

# Add subchain
@supermarket.route('/subchains/add', methods=['POST'])
def add_subchain():
    name = request.form.get('subchain_name')
    supermarket_id = request.form.get('supermarket_id')
    if name and supermarket_id:
        subchain = Subchain(name=name, supermarket_id=supermarket_id)
        db.session.add(subchain)
        db.session.commit()
        flash('Subchain added successfully!', 'success')
    return redirect(url_for('supermarket.manage_supermarkets'))

# Edit subchain
@supermarket.route('/subchains/edit/<int:id>', methods=['POST'])
def edit_subchain(id):
    subchain = Subchain.query.get_or_404(id)
    subchain.name = request.form.get('name')
    subchain.supermarket_id = request.form.get('supermarket_id')
    db.session.commit()
    flash('Subchain updated successfully!', 'success')
    return redirect(url_for('supermarket.manage_supermarkets'))

# Delete subchain
@supermarket.route('/subchains/delete/<int:id>', methods=['POST'])
def delete_subchain(id):
    subchain = Subchain.query.get_or_404(id)
    db.session.delete(subchain)
    db.session.commit()
    flash('Subchain deleted successfully!', 'success')
    return redirect(url_for('supermarket.manage_supermarkets'))
