@app.template_filter('currency')
def currency_filter(value):
    """Format value as Mongolian currency."""
    return f"₮{value:,.2f}" 