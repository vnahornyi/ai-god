'use strict';

// Builds catalogue pages like the API returns them: 40 pages, overlapping by a few items.
function makePages(pageCount = 40, pageSize = 500, overlap = 5) {
  const pages = [];
  for (let p = 0; p < pageCount; p += 1) {
    const start = p * (pageSize - overlap);
    pages.push(
      Array.from({ length: pageSize }, (_, i) => ({
        id: `sku-${start + i}`,
        isVisible: (start + i) % 7 !== 0,
      })),
    );
  }
  return pages;
}

module.exports = { makePages };
