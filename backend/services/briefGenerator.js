import PDFDocument from "pdfkit";

export async function buildDiscoveryBriefPdf(payload) {
  const doc = new PDFDocument({ margin: 40 });
  const chunks = [];

  doc.on("data", (chunk) => chunks.push(chunk));

  const {
    metrics = {},
    top_categories: topCategories = [],
    top_anomalies: topAnomalies = [],
    advisor_notes = "",
  } = payload;

  doc.fontSize(20).text("Prism Discovery Brief", { align: "left" });
  doc.moveDown(0.5);
  doc.fontSize(10).text("Generated summary for discovery prep; not financial advice.");
  doc.moveDown(1);

  doc.fontSize(14).text("Vitals");
  doc.moveDown(0.3);
  doc.fontSize(11);
  doc.text(`Total Spend: $${formatCurrency(metrics.total_spend)}`);
  doc.text(`Fixed Spend: $${formatCurrency(metrics.fixed_spend)}`);
  doc.text(`Variable Spend: $${formatCurrency(metrics.variable_spend)}`);
  doc.text(`True Free Cash Flow: $${formatCurrency(metrics.true_free_cash_flow)}`);
  doc.moveDown(0.8);

  doc.fontSize(14).text("Top Categories");
  doc.moveDown(0.3);
  doc.fontSize(11);
  if (!topCategories.length) {
    doc.text("No category data available.");
  } else {
    topCategories.forEach((item) => {
      doc.text(`${item.category}: $${formatCurrency(item.amount)}`);
    });
  }
  doc.moveDown(0.8);

  doc.fontSize(14).text("Top Anomalies");
  doc.moveDown(0.3);
  doc.fontSize(11);
  if (!topAnomalies.length) {
    doc.text("No anomalies detected.");
  } else {
    topAnomalies.forEach((item) => {
      doc.text(`${item.merchant} (${item.date}): $${formatCurrency(item.amount)}`);
    });
  }
  doc.moveDown(0.8);

  doc.fontSize(14).text("Recommendation Scaffolds");
  doc.moveDown(0.3);
  doc.fontSize(11);
  const recommendations = buildRecommendations(metrics, topCategories, topAnomalies);
  recommendations.forEach((line) => doc.text(`• ${line}`));

  if (advisor_notes) {
    doc.moveDown(0.8);
    doc.fontSize(14).text("Advisor Notes");
    doc.moveDown(0.3);
    doc.fontSize(11).text(advisor_notes);
  }

  doc.end();

  return await new Promise((resolve) => {
    doc.on("end", () => resolve(Buffer.concat(chunks)));
  });
}

function buildRecommendations(metrics, topCategories, topAnomalies) {
  const lines = [];
  const freeCashFlow = metrics.true_free_cash_flow || 0;
  const totalSpend = metrics.total_spend || 0;

  if (freeCashFlow > 0) {
    lines.push(
      `High discretionary capacity detected → discuss redirecting ~$${formatCurrency(
        freeCashFlow
      )}/mo into investments.`
    );
  } else {
    lines.push("Cash flow looks tight → discuss areas to trim variable spend.");
  }

  const dining = topCategories.find((item) => item.category === "Dining");
  if (dining) {
    lines.push("High dining concentration → discuss a 10–20% reduction scenario.");
  }

  if (topAnomalies.length) {
    lines.push("Large one-off spend detected → ask about upcoming planned expenses.");
  }

  if (!lines.length && totalSpend) {
    lines.push("Discuss budget allocation and goals based on top spend categories.");
  }

  return lines.slice(0, 3);
}

function formatCurrency(value) {
  if (value === undefined || value === null || Number.isNaN(value)) return "0.00";
  return Number(value).toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}
