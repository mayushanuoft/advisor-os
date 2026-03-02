import path from "path";
import os from "os";
import fs from "fs/promises";
import { createWorker } from "tesseract.js";
import pdfPoppler from "pdf-poppler";

export async function runOcrOnPdfBuffer(buffer, originalName) {
  const tempDir = await fs.mkdtemp(path.join(os.tmpdir(), "prism-ocr-"));
  const pdfPath = path.join(tempDir, sanitizeFilename(originalName));
  await fs.writeFile(pdfPath, buffer);

  try {
    const outputPrefix = path.join(tempDir, "page");
    await pdfPoppler.convert(pdfPath, {
      format: "png",
      out_dir: tempDir,
      out_prefix: "page",
      page: null,
    });

    const files = await fs.readdir(tempDir);
    const imageFiles = files
      .filter((file) => file.startsWith("page") && file.endsWith(".png"))
      .map((file) => path.join(tempDir, file));

    if (imageFiles.length === 0) {
      return { text: "", warning: "OCR conversion produced no images." };
    }

    const worker = await createWorker("eng");
    let text = "";

    for (const imagePath of imageFiles) {
      const result = await worker.recognize(imagePath);
      text += `\n${result.data.text || ""}`;
    }

    await worker.terminate();
    return { text, warning: "OCR used (experimental)." };
  } catch (error) {
    return {
      text: "",
      warning:
        "OCR is experimental and requires Poppler installed. Install Poppler if scans fail.",
    };
  } finally {
    await fs.rm(tempDir, { recursive: true, force: true });
  }
}

function sanitizeFilename(name) {
  return name.replace(/[^a-z0-9.\-_]/gi, "_");
}
