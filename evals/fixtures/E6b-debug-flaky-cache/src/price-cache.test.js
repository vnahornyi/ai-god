'use strict';

const test = require('node:test');
const assert = require('node:assert');
const { loadPrice, cachedPrice, clearCache } = require('./price-cache');

const PRICES = { shoes: 120, socks: 9 };

function fakeFetch(productId) {
  const latency = Math.random() * 20;
  return new Promise((resolve) => setTimeout(() => resolve(PRICES[productId]), latency));
}

test('switching products quickly keeps each price on its own product', async () => {
  clearCache();
  const shoes = loadPrice('shoes', fakeFetch);
  await new Promise((resolve) => setTimeout(resolve, Math.random() * 20));
  const socks = loadPrice('socks', fakeFetch);
  await Promise.all([shoes, socks]);
  assert.strictEqual(cachedPrice('shoes'), 120);
  assert.strictEqual(cachedPrice('socks'), 9);
});
