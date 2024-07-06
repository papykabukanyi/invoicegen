function addItem() {
    const itemsDiv = document.getElementById('items');
    const newItemDiv = document.createElement('div');
    newItemDiv.className = 'item';
    newItemDiv.innerHTML = `
        <input type="text" name="description" placeholder="Description" required>
        <input type="number" name="quantity" placeholder="Quantity/Hours" required>
        <input type="number" name="unit_price" placeholder="Unit Price" step="0.01" required>
        <button type="button" onclick="removeItem(this)">Remove</button>
    `;
    itemsDiv.appendChild(newItemDiv);
}

function removeItem(button) {
    const itemDiv = button.parentElement;
    itemDiv.remove();
}
