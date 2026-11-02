'use strict';

const cache = new Map();
let lastRequestedId = null;

async function loadPrice(productId, fetchPrice) {
  if (cache.has(productId)) return cache.get(productId);
  lastRequestedId = productId;
  const price = await fetchPrice(productId);
  cache.set(lastRequestedId, price);
  return price;
}

function cachedPrice(productId) {
  return cache.get(productId);
}

function clearCache() {
  cache.clear();
  lastRequestedId = null;
}

module.exports = { loadPrice, cachedPrice, clearCache };
