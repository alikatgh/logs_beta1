document.addEventListener("DOMContentLoaded", function () {
  const supermarketSelect = document.getElementById("supermarket_id");
  const subchainSelect = document.getElementById("subchain_id");
  const productsContainer = document.getElementById("products-container");
  const addProductBtn = document.getElementById("add-product-btn");
  const totalAmountInput = document.getElementById("total_amount");

  let products = [];

  // Load products on page load
  fetch("/delivery/get_products")
    .then((response) => response.json())
    .then((data) => {
      products = data;
      updateAllProductSelects();
    });

  // Handle supermarket change
  supermarketSelect.addEventListener("change", function () {
    const supermarketId = this.value;
    updateSubchains(supermarketId);
  });

  // Update subchains dropdown
  function updateSubchains(supermarketId) {
    subchainSelect.innerHTML = '<option value="0">Select Subchain</option>';
    if (supermarketId && supermarketId !== "0") {
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
  }

  // Add product row
  addProductBtn.addEventListener("click", function () {
    const index = document.querySelectorAll(".product-row").length;
    const row = createProductRow(index);
    productsContainer.appendChild(row);
    updateTotalAmount();
  });

  // Create product row
  function createProductRow(index) {
    const div = document.createElement("div");
    div.className = "product-row row mb-3";
    div.innerHTML = `
      <div class="col-md-3">
        <label class="form-label">Product</label>
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
      <div class="col-md-2">
        <label class="form-label">Quantity</label>
        <input type="number" name="products-${index}-quantity" class="form-control quantity-input" required min="1">
      </div>
      <div class="col-md-2">
        <label class="form-label">Price</label>
        <input type="number" name="products-${index}-price" class="form-control price-input" required step="0.01" min="0.01">
      </div>
      <div class="col-md-2">
        <label class="form-label">Total</label>
        <input type="number" name="products-${index}-total" class="form-control total-input" readonly>
      </div>
      <div class="col-md-2">
        <button type="button" class="btn btn-danger remove-product mt-4">
          <i class="fas fa-trash"></i> Remove
        </button>
      </div>
    `;

    setupRowEventListeners(div);
    return div;
  }

  // Setup event listeners for a row
  function setupRowEventListeners(row) {
    const productSelect = row.querySelector(".product-select");
    const quantityInput = row.querySelector(".quantity-input");
    const priceInput = row.querySelector(".price-input");
    const totalInput = row.querySelector(".total-input");
    const removeBtn = row.querySelector(".remove-product");

    productSelect.addEventListener("change", function () {
      const option = this.options[this.selectedIndex];
      if (option.dataset.price) {
        priceInput.value = option.dataset.price;
        updateRowTotal(row);
      }
    });

    quantityInput.addEventListener("input", function () {
      updateRowTotal(row);
    });

    priceInput.addEventListener("input", function () {
      updateRowTotal(row);
    });

    removeBtn.addEventListener("click", function () {
      row.remove();
      updateTotalAmount();
    });
  }

  // Update row total
  function updateRowTotal(row) {
    const quantity =
      parseFloat(row.querySelector(".quantity-input").value) || 0;
    const price = parseFloat(row.querySelector(".price-input").value) || 0;
    const total = quantity * price;
    row.querySelector(".total-input").value = total.toFixed(2);
    updateTotalAmount();
  }

  // Update total amount
  function updateTotalAmount() {
    const totals = Array.from(document.querySelectorAll(".total-input")).map(
      (input) => parseFloat(input.value) || 0
    );
    const total = totals.reduce((sum, value) => sum + value, 0);
    totalAmountInput.value = total.toFixed(2);
  }

  // Update all existing product selects
  function updateAllProductSelects() {
    document.querySelectorAll(".product-row").forEach((row) => {
      setupRowEventListeners(row);
    });
  }
});
