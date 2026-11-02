'use strict';

// Day label shown on the order history screen (YYYY-MM-DD).
function formatOrderDay(placedAtIso) {
  return new Date(placedAtIso).toISOString().slice(0, 10);
}

function groupOrdersByDay(orders) {
  const groups = new Map();
  for (const order of orders) {
    const day = formatOrderDay(order.placedAt);
    if (!groups.has(day)) groups.set(day, []);
    groups.get(day).push(order.id);
  }
  return groups;
}

module.exports = { formatOrderDay, groupOrdersByDay };
