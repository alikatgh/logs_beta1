from flask import render_template, flash, redirect, url_for, send_file, request
from flask_login import login_required
import pandas as pd
import io

from app.routes import report
from app.models import Delivery
from app.forms import EmptyForm


@report.route("/", methods=["GET", "POST"])
@login_required
def generate_report():
    """Handle report generation"""
    if request.method == "POST":
        try:
            # Get deliveries and returns
            deliveries = Delivery.query.filter_by(is_return=False).all()
            returns = Delivery.query.filter_by(is_return=True).all()

            # Prepare data for export
            data = []

            # Add delivery data
            for delivery in deliveries:
                for item in delivery.items:
                    data.append(
                        [
                            "Delivery",
                            delivery.delivery_date.strftime("%Y-%m-%d"),
                            delivery.supermarket.name,
                            delivery.subchain.name if delivery.subchain else "N/A",
                            item.product.name,
                            item.quantity,
                            item.price,
                        ]
                    )

            # Add return data
            for return_item in returns:
                for item in return_item.items:
                    data.append(
                        [
                            "Return",
                            (
                                return_item.return_date.strftime("%Y-%m-%d")
                                if return_item.return_date
                                else return_item.delivery_date.strftime("%Y-%m-%d")
                            ),
                            return_item.supermarket.name,
                            (
                                return_item.subchain.name
                                if return_item.subchain
                                else "N/A"
                            ),
                            item.product.name,
                            item.quantity,
                            item.price,
                        ]
                    )

            # Create DataFrame and export to Excel
            df = pd.DataFrame(
                data,
                columns=[
                    "Type",
                    "Date",
                    "Supermarket",
                    "Subchain",
                    "Product",
                    "Quantity",
                    "Price",
                ],
            )

            # Create Excel file in memory
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Report")
            output.seek(0)

            return send_file(
                output,
                download_name="report.xlsx",
                as_attachment=True,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        except Exception as e:
            flash(f"Error generating report: {str(e)}", "danger")
            return redirect(url_for("report.generate_report"))

    # GET request - show report form
    deliveries = Delivery.query.filter_by(is_return=False).all()
    returns = Delivery.query.filter_by(is_return=True).all()
    form = EmptyForm()

    return render_template(
        "reports/report.html", deliveries=deliveries, returns=returns, form=form
    )
