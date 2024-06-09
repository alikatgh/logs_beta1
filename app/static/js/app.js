$(document).ready(function() {
  $('#add-product').click(function() {
      var productFields = $('#product-fields');
      var newFields = productFields.children().first().clone();
      newFields.find('input').val('');
      productFields.append(newFields);
  });

  $(document).on('click', '.remove-row', function() {
      $(this).closest('.form-row').remove();
  });
});