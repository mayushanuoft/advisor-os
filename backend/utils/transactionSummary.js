const ESSENTIAL_VARIABLE = new Set(["Groceries", "Transport", "Utilities"]);

export function summarizeTransactions(transactions) {
  const spendTx = transactions.filter((tx) => tx.amount < 0);
  const incomeTx = transactions.filter((tx) => tx.amount > 0);

  const totalSpend = sum(spendTx.map((tx) => Math.abs(tx.amount)));
  const fixedSpend = sum(
    spendTx.filter((tx) => tx.fixed_or_variable === "Fixed").map((tx) => Math.abs(tx.amount))
  );
  const variableSpend = totalSpend - fixedSpend;
  const essentialVariableProxy = sum(
    spendTx
      .filter((tx) => ESSENTIAL_VARIABLE.has(tx.category))
      .map((tx) => Math.abs(tx.amount))
  );
  const incomeDetected = sum(incomeTx.map((tx) => Math.abs(tx.amount)));

  const metrics = {
    total_spend: round(totalSpend),
    fixed_spend: round(fixedSpend),
    variable_spend: round(variableSpend),
    essential_variable_proxy: round(essentialVariableProxy),
    income_detected: round(incomeDetected),
    true_free_cash_flow: round(incomeDetected - fixedSpend - essentialVariableProxy),
  };

  const topCategories = getTopCategories(spendTx);
  const topAnomalies = getTopAnomalies(spendTx);

  return { metrics, topCategories, topAnomalies };
}

function getTopCategories(spendTx) {
  const totals = spendTx.reduce((acc, tx) => {
    const key = tx.category || "Other";
    acc[key] = (acc[key] || 0) + Math.abs(tx.amount);
    return acc;
  }, {});
  return Object.entries(totals)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3)
    .map(([category, amount]) => ({ category, amount: round(amount) }));
}

function getTopAnomalies(spendTx) {
  return [...spendTx]
    .sort((a, b) => Math.abs(b.amount) - Math.abs(a.amount))
    .slice(0, 3)
    .map((tx) => ({
      date: tx.date,
      merchant: tx.merchant_normalized,
      amount: round(Math.abs(tx.amount)),
      category: tx.category,
    }));
}

function sum(values) {
  return values.reduce((total, value) => total + value, 0);
}

function round(value) {
  return Number(value.toFixed(2));
}
