# E4 — "Closed today" badge

React Native app, React 19 with the React Compiler enabled. Translations use `<Trans>` from
`@lingui/react/macro`. Styles are developer-owned: write no style values. This is a small direct
request, not a planned task.

**Request:** "Add a 'Closed today' badge to the store header when the store has no opening hours for
today."

Existing `store-header.tsx` — the file to change:

```tsx
import { Text, View } from 'react-native';
import { Badge } from './badge';
import { useStoreHours } from './use-store-hours';
import type { WeekdayType } from './types';

type PropsType = { storeId: string; storeName: string; today: WeekdayType };

export const StoreHeader: React.FC<PropsType> = ({ storeId, storeName, today }) => {
  const { hours } = useStoreHours(storeId);

  return (
    <View>
      <Text>{storeName}</Text>
    </View>
  );
};
```

Existing `use-store-hours.ts` — do not edit:

```ts
import { use, useEffect, useState } from 'react';
import { StoresContext } from './stores-context';
import type { DayHoursType } from './types';

// hours is null until the request for this store has completed; [] means the store has no hours at all.
export const useStoreHours = (storeId: string) => {
  const { hours, hoursStoreId, loadHours } = use(StoresContext);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setIsLoading(true);
    loadHours(storeId).finally(() => setIsLoading(false));
  }, [storeId]);

  return { hours: hoursStoreId === storeId ? hours : null, isLoading };
};
```

```ts
// types.ts
export type WeekdayType = 'mon' | 'tue' | 'wed' | 'thu' | 'fri' | 'sat' | 'sun';
export type DayHoursType = { weekday: WeekdayType; opens: string; closes: string };
```

The store screen switches stores in place with `navigation.setParams({ storeId })`.

Write the changed `store-header.tsx`.
