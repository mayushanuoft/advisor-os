import {
  categorizeMerchant,
  normalizeMerchant,
  detectFixedOrVariable,
} from "./transactionRules.js";

const DATE_REGEX = /^(\d{1,2}[\/\-]\d{1,2}(?:[\/\-]\d{2,4})?)\s+/;
const AMOUNT_REGEX = /(-?\$?\d[\d,]*\.\d{2})(?:\s|$)/;

export function parseTransactionsFromText(text) {
  if (!text) return [];
  const lines = text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);

  const rawTransactions = [];
  let current = null;

  for (const line of lines) {
    const dateMatch = line.match(DATE_REGEX);
    if (dateMatch) {
      if (current) {
        rawTransactions.push(current);
      }
      current = { raw: line };
      continue;
    }

    if (current) {
      current.raw = `${current.raw} ${line}`.trim();
    }
  }

  if (current) {
    rawTransactions.push(current);
  }

  const transactions = rawTransactions
    .map((entry) => parseTransactionLine(entry.raw))
    .filter(Boolean);

  const withFixed = detectFixedOrVariable(transactions);
  return withFixed;
}

function parseTransactionLine(line) {
  const dateMatch = line.match(DATE_REGEX);
  const amountMatch = line.match(AMOUNT_REGEX);
  if (!dateMatch || !amountMatch) return null;

  const date = normalizeDate(dateMatch[1]);
  const amount = parseAmount(amountMatch[1], line);

  const merchantRaw = line
    .replace(DATE_REGEX, "")
    .replace(amountMatch[1], "")
    .replace(/\s+/g, " ")
    .trim();

  const merchantNormalized = normalizeMerchant(merchantRaw);
  const category = categorizeMerchant(merchantNormalized, merchantRaw);

  return {
    date,
    merchant_raw: merchantRaw,
    merchant_normalized: merchantNormalized,
    amount,
    category,
    fixed_or_variable: "Variable",
  };
}

function normalizeDate(raw) {
  const parts = raw.split(/[\/\-]/);
  if (parts.length < 2) return raw;
  const [p1, p2, p3] = parts;
  const month = p1.padStart(2, "0");
  const day = p2.padStart(2, "0");
  const year = p3 ? normalizeYear(p3) : "";
  return year ? `${year}-${month}-${day}` : `${month}/${day}`;
}

function normalizeYear(year) {
  if (year.length === 2) {
    return `20${year}`;
  }
  return year;
}

function parseAmount(amountRaw, fullLine) {
  const cleaned = amountRaw.replace(/[$,]/g, "");
  let value = Number.parseFloat(cleaned);
  if (Number.isNaN(value)) {
    value = 0;
  }

  const hasCreditHint = /credit|cr\b|deposit|payroll/i.test(fullLine);
  if (fullLine.includes("-")) {
    value = -Math.abs(value);
  } else if (hasCreditHint) {
    value = Math.abs(value);
  } else {
    value = -Math.abs(value);
  }

  return value;
}
