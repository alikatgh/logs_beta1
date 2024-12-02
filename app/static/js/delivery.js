document.addEventListener("DOMContentLoaded", function () {
  const supermarketSelect = document.getElementById("supermarket_id");
  const subchainSelect = document.getElementById("subchain");
  const productsContainer = document.getElementById("products-container");
  const addProductBtn = document.getElementById("add-product-btn");

  let products = [];

  // Load products on page load
  fetch("/delivery/get_products")
    .then((response) => response.json())
    .then((data) => {
      products = data;
    });

  // Handle supermarket change
  supermarketSelect.addEventListener("change", function () {
    const supermarketId = this.value;

    // Clear subchain select
    subchainSelect.innerHTML = '<option value="">Select Subchain</option>';

    if (supermarketId) {
      fetch(`/delivery/get_subchains/${supermarketId}`)
        .then((response) => response.json())
        .then((data) => {
          data.forEach((subchain) => {
            const option = document.createElement("option");
            option.value = subchain.id;
            option.textContent = subchain.name;
            subchainSelect.appendChild(option);
          });
        });
    }
  });

  // Add product row
  addProductBtn.addEventListener("click", function () {
    const index = document.querySelectorAll(".product-row").length;
    const row = createProductRow(index);
    productsContainer.appendChild(row);
  });

  function createProductRow(index) {
    const div = document.createElement("div");
    div.className = "product-row row mb-3";

    div.innerHTML = `
            <div class="col-md-4">
                <select name="products-${index}-product_id" class="form-control product-select" required>
                    <option value="">Select Product</option>
                    ${products
                      .map(
                        (p) =>
                          `<option value="${p.id}" data-price="${p.price}">${p.name}</option>`
                      )
                      .join("")}
                </select>
            </div>
            <div class="col-md-3">
                <input type="number" name="products-${index}-quantity" class="form-control quantity-input" 
                       placeholder="Quantity" required min="1">
            </div>
            <div class="col-md-3">
                <input type="number" name="products-${index}-price" class="form-control price-input" 
                       placeholder="Price" required step="0.01" min="0.01">
            </div>
            <div class="col-md-2">
                <button type="button" class="btn btn-danger remove-product">Remove</button>
            </div>
        `;

    // Handle product selection
    const productSelect = div.querySelector(".product-select");
    const priceInput = div.querySelector(".price-input");

    productSelect.addEventListener("change", function () {
      const option = this.options[this.selectedIndex];
      if (option.dataset.price) {
        priceInput.value = option.dataset.price;
      }
    });

    // Handle remove button
    div.querySelector(".remove-product").addEventListener("click", function () {
      div.remove();
    });

    return div;
  }
});
