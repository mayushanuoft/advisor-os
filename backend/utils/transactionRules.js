const NORMALIZATION_PATTERNS = [
  { pattern: /uber\s*trip|uber\*/i, replacement: "Uber" },
  { pattern: /starbucks|sbux/i, replacement: "Starbucks" },
  { pattern: /amazon|amzn/i, replacement: "Amazon" },
];

const CATEGORY_KEYWORDS = [
  { category: "Dining", keywords: ["restaurant", "cafe", "starbucks", "mcdonald", "uber eats", "doordash"] },
  { category: "Transport", keywords: ["uber", "lyft", "transit", "ttc", "gas", "shell", "petro"] },
  { category: "Groceries", keywords: ["loblaws", "metro", "walmart", "costco", "grocery"] },
  { category: "Utilities", keywords: ["hydro", "electricity", "internet", "phone"] },
  { category: "Shopping", keywords: ["amazon", "bestbuy", "apple"] },
  { category: "Subscriptions", keywords: ["netflix", "spotify", "prime"] },
  { category: "Housing", keywords: ["rent", "mortgage", "condo", "property"] },
];

const FIXED_CATEGORIES = new Set(["Housing", "Utilities", "Subscriptions", "Insurance"]);

export function normalizeMerchant(raw) {
  if (!raw) return "Unknown";
  let normalized = raw.toLowerCase();
  normalized = normalized.replace(/[*#0-9]/g, " ");
  normalized = normalized.replace(/\b(pos|inc|llc|bv|ltd|co|corp)\b/g, " ");
  normalized = normalized.replace(/\s+/g, " ").trim();

  let mapped = titleCase(normalized);
  for (const rule of NORMALIZATION_PATTERNS) {
    if (rule.pattern.test(normalized)) {
      mapped = rule.replacement;
      break;
    }
  }
  return mapped || "Unknown";
}

export function categorizeMerchant(normalized, raw) {
  const text = `${normalized} ${raw}`.toLowerCase();
  for (const item of CATEGORY_KEYWORDS) {
    if (item.keywords.some((keyword) => text.includes(keyword))) {
      return item.category;
    }
  }
  return "Other";
}

export function detectFixedOrVariable(transactions) {
  const grouped = groupByMerchant(transactions);
  const recurringMerchants = new Set();

  for (const [merchant, items] of Object.entries(grouped)) {
    if (items.length < 2) continue;
    const sorted = items
      .map((item) => ({ ...item, dateObj: new Date(item.date) }))
      .filter((item) => !Number.isNaN(item.dateObj.getTime()))
      .sort((a, b) => a.dateObj - b.dateObj);

    const amountMedian = median(items.map((item) => Math.abs(item.amount)));
    const stableAmount = items.every(
      (item) => Math.abs(Math.abs(item.amount) - amountMedian) / amountMedian <= 0.1
    );

    const monthlyish = sorted.some((item, idx) => {
      if (idx === 0) return false;
      const diffDays = Math.abs((item.dateObj - sorted[idx - 1].dateObj) / 86400000);
      return diffDays >= 25 && diffDays <= 35;
    });

    if (stableAmount && (monthlyish || items.length >= 3)) {
      recurringMerchants.add(merchant);
    }
  }

  return transactions.map((item) => {
    const isFixedCategory = FIXED_CATEGORIES.has(item.category);
    const isRecurring = recurringMerchants.has(item.merchant_normalized);
    const fixed = isFixedCategory || isRecurring;
    return { ...item, fixed_or_variable: fixed ? "Fixed" : "Variable" };
  });
}

function groupByMerchant(transactions) {
  return transactions.reduce((acc, item) => {
    const key = item.merchant_normalized || "Unknown";
    if (!acc[key]) acc[key] = [];
    acc[key].push(item);
    return acc;
  }, {});
}

function median(values) {
  if (!values.length) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  if (sorted.length % 2 === 0) {
    return (sorted[mid - 1] + sorted[mid]) / 2;
  }
  return sorted[mid];
}

function titleCase(value) {
  return value
    .split(" ")
    .filter(Boolean)
    .map((word) => word[0].toUpperCase() + word.slice(1))
    .join(" ");
}
