# E3 — Tooltip once per product

React Native app, React 19 with the React Compiler enabled. Styles are developer-owned: write no
style values. Fix the bug in the existing file below; write the fixed `product-tooltip.tsx`.

**Bug report:** the "Swipe to see more photos" tooltip appears only for the first product. On the
product screen the user switches colour, which calls `navigation.setParams({ productId })` — the
screen does not remount, `ProductTooltip` receives a new `productId`, and the tooltip never shows
again. **Expected:** the tooltip shows once per product id each time that product is displayed, for 3
seconds.

Existing `product-tooltip.tsx`:

```tsx
import { useEffect, useRef, useState } from 'react';
import { Trans } from '@lingui/react/macro';
import { Tooltip } from './tooltip';

const TOOLTIP_DURATION_MS = 3000;

type PropsType = { productId: string };

export const ProductTooltip: React.FC<PropsType> = ({ productId }) => {
  const [isVisible, setIsVisible] = useState(false);
  const didAnnounceRef = useRef(false);

  useEffect(() => {
    if (didAnnounceRef.current) return;

    didAnnounceRef.current = true;
    setIsVisible(true);

    const timer = setTimeout(() => setIsVisible(false), TOOLTIP_DURATION_MS);

    return () => clearTimeout(timer);
  }, []);

  if (!isVisible) return null;

  return (
    <Tooltip>
      <Trans>Swipe to see more photos</Trans>
    </Tooltip>
  );
};
```

It is rendered once, in `product-screen.tsx`, as `<ProductTooltip productId={productId} />`. You may
also say how that line should change if your fix needs it.
