window.addEventListener('DOMContentLoaded', () => {
  const productNameField = document.getElementById('id_product_name');
  const subcategoryField = document.getElementById('id_subcategory');

  // Definir las opciones de subcategoría para cada valor de product_name
  const subcategoryChoices = {
    'OTP': [
      ['', '---------'],  // opción vacía
      ['Resortada', 'Resortada'],
      ['Reaccion a piso', 'Reaccion a piso'],
      ['Sarmiento corto', 'Sarmiento corto'],
      ['Sarmiento articulado', 'Sarmiento articulado']
    ],
    'PLANTILLAS': [
      ['', '---------'],  // opción vacía
      ['Plantillas termoformadas', 'Termoformadas'],
      ['Plantillas Cuero', 'Cuero'],
      ['Plantillas UCBL', 'UCBL']
    ],
    // agregar más categorías y opciones de subcategoría aquí
  };

  function updateSubcategoryChoices() {
    const selectedProduct = productNameField.value;
    const options = subcategoryChoices[selectedProduct] || [];

    subcategoryField.innerHTML = '';
    for (const [value, label] of options) {
      const option = document.createElement('option');
      option.value = value;
      option.textContent = label;
      subcategoryField.appendChild(option);
    }
  }

  productNameField.addEventListener('input', updateSubcategoryChoices);

  // Actualizar las opciones inicialmente
  updateSubcategoryChoices();
});
