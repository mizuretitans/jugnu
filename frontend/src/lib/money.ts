const currency = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  minimumFractionDigits: 0,
  maximumFractionDigits: 2,
});

export const money = (paise: number) => currency.format(paise / 100);

export const DURATIONS = [30, 60, 90, 120];

/** For display only. The server computes the price that is actually charged. */
export const priceFor = (hourlyPaise: number, minutes: number) =>
  Math.round((hourlyPaise * minutes) / 60);
