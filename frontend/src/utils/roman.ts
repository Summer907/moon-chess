const ROMAN_NUMERALS: Record<number, string> = {
  1: "Ⅰ",
  2: "Ⅱ",
  3: "Ⅲ",
  4: "Ⅳ",
  5: "Ⅴ",
  6: "Ⅵ",
  7: "Ⅶ",
  8: "Ⅷ",
  9: "Ⅸ",
};

export function toRoman(value: number): string {
  return ROMAN_NUMERALS[value] ?? String(value);
}
