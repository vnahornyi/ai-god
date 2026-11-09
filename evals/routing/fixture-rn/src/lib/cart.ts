export function cartTotal(lines: { price: number; quantity: number }[]) {
  return lines.reduce((sum, line) => sum + line.price * line.quantity, 0);
}
