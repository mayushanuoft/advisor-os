import pdfParse from "pdf-parse";
import { parseTransactionsFromText } from "../utils/transactionParser.js";
import { runOcrOnPdfBuffer } from "../ocr/ocrPipeline.js";
import { summarizeTransactions } from "../utils/transactionSummary.js";

const MIN_ROWS_FOR_CONFIDENCE = 8;

export async function processPdfFiles(files, options = {}) {
  const { useOcr = true } = options;
  let allTransactions = [];
  const warnings = [];
  let ocrUsed = false;
  let lowConfidence = false;

  for (const file of files) {
    const textResult = await tryTextExtraction(file);
    let extracted = textResult.transactions;
    let usedOcrForFile = false;

    if (useOcr && (textResult.confidence === "low" || extracted.length < MIN_ROWS_FOR_CONFIDENCE)) {
      const ocrResult = await tryOcrExtraction(file);
      if (ocrResult.used) {
        usedOcrForFile = true;
        ocrUsed = true;
        extracted = ocrResult.transactions;
        if (ocrResult.warning) {
          warnings.push(ocrResult.warning);
        }
      }
    } else if (!useOcr && (textResult.confidence === "low" || extracted.length < MIN_ROWS_FOR_CONFIDENCE)) {
      warnings.push(`OCR disabled for ${file.originalname}.`);
    }

    if (extracted.length === 0) {
      warnings.push(
        `No transactions parsed from ${file.originalname}. Try exporting a text-based statement.`
      );
    }

    allTransactions = allTransactions.concat(extracted.map((item) => ({
      ...item,
      source_file: file.originalname,
      ocr_used: usedOcrForFile,
    })));
  }

  const summary = summarizeTransactions(allTransactions);
  const confidence = computeConfidence(allTransactions.length, warnings.length, ocrUsed);
  if (confidence === "low") {
    lowConfidence = true;
  }

  return {
    transactions: allTransactions,
    metrics: summary.metrics,
    top_categories: summary.topCategories,
    top_anomalies: summary.topAnomalies,
    data_quality: {
      extracted_rows: allTransactions.length,
      confidence,
      ocr_used: ocrUsed,
      warnings,
      low_confidence: lowConfidence,
    },
  };
}

async function tryTextExtraction(file) {
  try {
    const parsed = await pdfParse(file.buffer);
    const rawText = parsed.text || "";
    const transactions = parseTransactionsFromText(rawText);
    const confidence = transactions.length >= MIN_ROWS_FOR_CONFIDENCE ? "medium" : "low";
    return { transactions, confidence };
  } catch (error) {
    console.warn("Text extraction failed", error);
    return { transactions: [], confidence: "low" };
  }
}

async function tryOcrExtraction(file) {
  try {
    const { text, warning } = await runOcrOnPdfBuffer(file.buffer, file.originalname);
    if (!text) {
      return { transactions: [], used: false, warning };
    }
    const transactions = parseTransactionsFromText(text);
    return { transactions, used: true, warning };
  } catch (error) {
    console.warn("OCR extraction failed", error);
    return {
      transactions: [],
      used: false,
      warning: "OCR failed for one or more files. Try a clearer scan.",
    };
  }
}

function computeConfidence(rowCount, warningCount, ocrUsed) {
  if (rowCount >= 20 && warningCount === 0 && !ocrUsed) {
    return "high";
  }
  if (rowCount >= 10 && warningCount <= 1) {
    return "medium";
  }
  return "low";
}
