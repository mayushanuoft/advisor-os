import React, { useMemo, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE || "";

const initialMetrics = {
  total_spend: 0,
  fixed_spend: 0,
  variable_spend: 0,
  essential_variable_proxy: 0,
  income_detected: 0,
  true_free_cash_flow: 0,
};

export default function App() {
  const [files, setFiles] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState("");
  const [results, setResults] = useState(null);
  const [manualIncome, setManualIncome] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const [useOcr, setUseOcr] = useState(true);

  const effectiveMetrics = useMemo(() => {
    if (!results) return initialMetrics;
    const metrics = { ...results.metrics };
    const manualValue = Number.parseFloat(manualIncome);
    if (!Number.isNaN(manualValue) && manualValue > 0) {
      metrics.income_detected = manualValue;
      metrics.true_free_cash_flow =
        manualValue - metrics.fixed_spend - metrics.essential_variable_proxy;
    }
    return metrics;
  }, [results, manualIncome]);

  const handleFiles = (incoming) => {
    setError("");
    const list = Array.from(incoming || []).filter((file) => file.type === "application/pdf");
    setFiles(list);
  };

  const onProcess = async () => {
    if (!files.length) {
      setError("Please upload at least one PDF statement.");
      return;
    }
    setProcessing(true);
    setError("");
    setResults(null);

    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 60000);
      const formData = new FormData();
      files.forEach((file) => formData.append("files", file));
      formData.append("use_ocr", useOcr ? "true" : "false");
      const response = await fetch(`${API_BASE}/api/process-pdfs`, {
        method: "POST",
        body: formData,
        signal: controller.signal,
      });
      clearTimeout(timeout);
      if (!response.ok) {
        const payload = await safeReadJson(response);
        throw new Error(payload?.error || "Processing failed.");
      }
      const payload = await safeReadJson(response);
      setResults(payload);
    } catch (err) {
      if (err.name === "AbortError") {
        setError("Processing timed out. Try disabling OCR or uploading fewer pages.");
      } else {
        setError(err.message || "Something went wrong.");
      }
    } finally {
      setProcessing(false);
    }
  };

  const onDownloadBrief = async () => {
    if (!results) return;
    try {
      const response = await fetch(`${API_BASE}/api/generate-brief`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          metrics: effectiveMetrics,
          top_categories: results.top_categories,
          top_anomalies: results.top_anomalies,
        }),
      });
      if (!response.ok) {
        const payload = await safeReadJson(response);
        throw new Error(payload?.error || "Failed to generate PDF.");
      }
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "discovery-brief.pdf";
      link.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message || "PDF generation failed.");
    }
  };

  return (
    <div className="app">
      <header className="hero">
        <div>
          <h1>Prism</h1>
          <p>AI Financial Discovery Copilot</p>
        </div>
      </header>

      <section className="card">
        <h2>1) Upload Statements</h2>
        <div
          className={`dropzone ${isDragging ? "active" : ""}`}
          onDragOver={(event) => {
            event.preventDefault();
            setIsDragging(true);
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={(event) => {
            event.preventDefault();
            setIsDragging(false);
            handleFiles(event.dataTransfer.files);
          }}
        >
          <p>Drag & drop PDFs here</p>
          <span>or</span>
          <label className="file-input">
            Browse files
            <input type="file" multiple accept="application/pdf" onChange={(e) => handleFiles(e.target.files)} />
          </label>
        </div>

        <div className="file-list">
          {files.length ? (
            files.map((file) => (
              <div key={file.name} className="file-pill">
                {file.name}
              </div>
            ))
          ) : (
            <p className="muted">No PDFs selected.</p>
          )}
        </div>

        <label className="toggle">
          <input
            type="checkbox"
            checked={useOcr}
            onChange={(event) => setUseOcr(event.target.checked)}
          />
          Use OCR for scanned PDFs (experimental, slower)
        </label>

        <button className="primary" onClick={onProcess} disabled={processing}>
          {processing ? "Processing..." : "Process"}
        </button>
        {error && <p className="error">{error}</p>}
      </section>

      {results && (
        <>
          <section className="card">
            <h2>2) Results</h2>
            <div className="metrics-grid">
              <Metric label="Total Spend" value={effectiveMetrics.total_spend} />
              <Metric label="Fixed Spend" value={effectiveMetrics.fixed_spend} />
              <Metric label="Variable Spend" value={effectiveMetrics.variable_spend} />
              <Metric label="True Free Cash Flow" value={effectiveMetrics.true_free_cash_flow} />
            </div>

            <div className="income-input">
              <label>
                Estimated Income (override)
                <input
                  type="number"
                  min="0"
                  placeholder="Optional manual income"
                  value={manualIncome}
                  onChange={(event) => setManualIncome(event.target.value)}
                />
              </label>
              <p className="muted">
                Detected income: ${results.metrics.income_detected?.toFixed(2) || "0.00"}
              </p>
            </div>

            <div className="quality-panel">
              <h3>Data Quality</h3>
              <div className="quality-grid">
                <span>Extracted Rows</span>
                <strong>{results.data_quality.extracted_rows}</strong>
                <span>Confidence</span>
                <strong className={`pill ${results.data_quality.confidence}`}>
                  {results.data_quality.confidence}
                </strong>
                <span>OCR Used</span>
                <strong>{results.data_quality.ocr_used ? "Yes (experimental)" : "No"}</strong>
              </div>
              {results.data_quality.warnings?.length ? (
                <ul className="warnings">
                  {results.data_quality.warnings.map((warning, idx) => (
                    <li key={`${warning}-${idx}`}>{warning}</li>
                  ))}
                </ul>
              ) : null}
            </div>

            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Merchant (Raw)</th>
                    <th>Merchant (Normalized)</th>
                    <th>Amount</th>
                    <th>Category</th>
                    <th>Fixed/Variable</th>
                  </tr>
                </thead>
                <tbody>
                  {results.transactions.map((tx, idx) => (
                    <tr key={`${tx.date}-${tx.merchant_raw}-${idx}`}>
                      <td>{tx.date}</td>
                      <td>{tx.merchant_raw}</td>
                      <td>{tx.merchant_normalized}</td>
                      <td className={tx.amount < 0 ? "negative" : "positive"}>
                        {formatCurrency(tx.amount)}
                      </td>
                      <td>{tx.category}</td>
                      <td>{tx.fixed_or_variable}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className="muted">
                {results.transactions.length} transactions extracted.
              </p>
            </div>
          </section>

          <section className="card">
            <h2>3) Export</h2>
            <button className="secondary" onClick={onDownloadBrief}>
              Download Discovery Brief PDF
            </button>
          </section>
        </>
      )}
    </div>
  );
}

function Metric({ label, value }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>${Number(value || 0).toFixed(2)}</strong>
    </div>
  );
}

function formatCurrency(amount) {
  const absolute = Math.abs(amount);
  const formatted = absolute.toLocaleString("en-US", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
  return amount < 0 ? `-$${formatted}` : `$${formatted}`;
}

async function safeReadJson(response) {
  const contentType = response.headers.get("content-type") || "";
  if (!contentType.includes("application/json")) {
    return null;
  }
  try {
    return await response.json();
  } catch {
    return null;
  }
}
