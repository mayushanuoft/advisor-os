import express from "express";
import cors from "cors";
import multer from "multer";
import { processPdfFiles } from "./services/pdfProcessor.js";
import { buildDiscoveryBriefPdf } from "./services/briefGenerator.js";

const app = express();
const upload = multer({ storage: multer.memoryStorage() });

app.use(cors());
app.use(express.json({ limit: "10mb" }));

app.get("/api/health", (req, res) => {
  res.json({ ok: true });
});

app.post("/api/process-pdfs", upload.array("files"), async (req, res) => {
  try {
    if (!req.files || req.files.length === 0) {
      return res.status(400).json({ error: "No PDF files received." });
    }

    const useOcr = req.body?.use_ocr !== "false";
    const results = await processPdfFiles(req.files, { useOcr });
    return res.json(results);
  } catch (error) {
    console.error("process-pdfs failed", error);
    return res.status(500).json({
      error:
        "We couldn't process these PDFs yet. Try another statement or export to a text-based PDF.",
    });
  }
});

app.post("/api/generate-brief", async (req, res) => {
  try {
    const payload = req.body || {};
    const pdfBuffer = await buildDiscoveryBriefPdf(payload);
    res.setHeader("Content-Type", "application/pdf");
    res.setHeader("Content-Disposition", "attachment; filename=discovery-brief.pdf");
    return res.send(pdfBuffer);
  } catch (error) {
    console.error("generate-brief failed", error);
    return res.status(500).json({
      error: "Could not generate the Discovery Brief. Please try again.",
    });
  }
});

const PORT = process.env.PORT || 5050;
app.listen(PORT, () => {
  console.log(`Prism backend running on http://localhost:${PORT}`);
});
