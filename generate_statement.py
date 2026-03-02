import random
from datetime import datetime, timedelta
from fpdf import FPDF

# --- 1. Data Generation Rules ---
# We mix standard living expenses with high-net-worth discretionary spending
MERCHANTS = [
    # Fixed / Essential
    {"name": "TD Auto Finance", "min": 800, "max": 1200},
    {"name": "City of Toronto Property Tax", "min": 1500, "max": 2000},
    {"name": "Enbridge Gas", "min": 80, "max": 250},
    {"name": "Rogers Communications", "min": 120, "max": 200},
    {"name": "Manulife Insurance", "min": 300, "max": 600},
    # Discretionary / Lifestyle
    {"name": "Air Canada - Signature Class", "min": 2500, "max": 6000},
    {"name": "Holt Renfrew", "min": 400, "max": 3500},
    {"name": "Alo Restaurant", "min": 300, "max": 800},
    {"name": "Toronto Golf Club", "min": 1000, "max": 1500},
    {"name": "Uber Eats", "min": 40, "max": 120},
    {"name": "Equinox Fitness", "min": 200, "max": 250},
    {"name": "LCBO Vintages", "min": 100, "max": 600},
    # Ambiguous (To test the AI's reasoning)
    {"name": "Smith & Sons LLC (Contractor)", "min": 5000, "max": 15000},
    {"name": "Transfer to Acct 8842", "min": 1000, "max": 5000}
]

# Generate 50 random transactions over the last 60 days
transactions = []
start_date = datetime.now() - timedelta(days=60)

for _ in range(50):
    merchant = random.choice(MERCHANTS)
    amount = round(random.uniform(merchant["min"], merchant["max"]), 2)
    days_offset = random.randint(0, 60)
    tx_date = start_date + timedelta(days=days_offset)
    transactions.append({
        "date": tx_date.strftime("%Y-%m-%d"),
        "merchant": merchant["name"],
        "amount": f"${amount:,.2f}"
    })

# Sort transactions chronologically
transactions.sort(key=lambda x: x["date"], reverse=True)

# --- 2. PDF Generation ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'PREMIER WEALTH BANKING', 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 10, 'Statement of Account - High Net Worth Division', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

# Create PDF instance
pdf = PDF()
pdf.add_page()
pdf.set_font('Arial', 'B', 10)

# Table Header
col_width = pdf.w / 3.5
row_height = 8

pdf.cell(col_width, row_height, 'Date', border=1, align='C')
pdf.cell(col_width * 1.5, row_height, 'Description', border=1, align='C')
pdf.cell(col_width * 0.8, row_height, 'Amount', border=1, align='C')
pdf.ln(row_height)

# Table Rows
pdf.set_font('Arial', '', 9)
for tx in transactions:
    pdf.cell(col_width, row_height, tx['date'], border=1, align='C')
    pdf.cell(col_width * 1.5, row_height, tx['merchant'], border=1, align='L')
    pdf.cell(col_width * 0.8, row_height, tx['amount'], border=1, align='R')
    pdf.ln(row_height)

# Save to file
filename = "Client_Statement_Test.pdf"
pdf.output(filename, 'F')
print(f"Success! '{filename}' has been generated in your current folder.")