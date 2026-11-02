'use strict';

// Keeps the first occurrence of every product id, in the original order.
function dedupeById(items) {
  const unique = [];
  for (const item of items) {
    if (!unique.some((kept) => kept.id === item.id)) unique.push(item);
  }
  return unique;
}

function visibleProducts(pages) {
  return dedupeById(pages.flat()).filter((product) => product.isVisible);
}

module.exports = { dedupeById, visibleProducts };
