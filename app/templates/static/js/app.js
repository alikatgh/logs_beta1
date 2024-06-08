$(document).ready(function() {
    $('#add-row').click(function() {
      var row = `
        <tr>
          <td>
            <select class="form-control product-select" name="product_id[]" required>
              {% for product in products %}
                <option value="{{ product.id }}">{{ product.name }}</option>
              {% endfor %}
            </select>
          </td>
          <td><input type="number" class="form-control quantity-input" name="quantity[]" required></td>
          <td><input type="number" step="0.01" class="form-control price-input" name="price[]" required></td>
          <td><button type="button" class="btn btn-danger remove-row">Remove</button></td>
        </tr>
      `;
      $('#products-table tbody').append(row);
    });
  
    $(document).on('click', '.remove-row', function() {
      $(this).closest('tr').remove();
    });
  });