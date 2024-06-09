$(document).ready(function() {
  // Products
  $('#add-product').click(function() {
      var productFields = $('#product-fields');
      var newFields = productFields.children().first().clone();
      newFields.find('input').val('');
      productFields.append(newFields);
  });

  // Supermarkets
  $('#add-supermarket').click(function() {
      var supermarketFields = $('#supermarket-fields');
      var newFields = supermarketFields.children().first().clone();
      newFields.find('input').val('');
      supermarketFields.append(newFields);
  });

  // Remove row (for both products and supermarkets)
  $(document).on('click', '.remove-row', function() {
      $(this).closest('.form-row').remove();
  });
});