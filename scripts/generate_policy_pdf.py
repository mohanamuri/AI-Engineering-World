"""
Generate data/loan_policy.pdf using only Python built-ins.
Run: python scripts/generate_policy_pdf.py
"""

import struct
import zlib
from pathlib import Path


# ---------------------------------------------------------------------------
# Loan policy content — pages of text
# ---------------------------------------------------------------------------

PAGES = [
    {
        "title": "LOAN ELIGIBILITY POLICY",
        "subtitle": "FinCorp Bank — Credit Division | Version 3.2 | Effective: January 2024",
        "lines": [
            "",
            "SECTION 1 — PURPOSE AND SCOPE",
            "",
            "This policy establishes the criteria, processes, and standards for evaluating",
            "personal and business loan applications at FinCorp Bank. It applies to all",
            "loan officers, credit analysts, and automated decision systems. All decisions",
            "must comply with applicable fair lending laws including the Equal Credit",
            "Opportunity Act (ECOA) and the Fair Housing Act (FHA).",
            "",
            "SECTION 2 — LOAN PRODUCTS COVERED",
            "",
            "2.1  Personal Loans        — USD 1,000 to USD 50,000",
            "2.2  Home Improvement Loans — USD 5,000 to USD 150,000",
            "2.3  Auto Loans             — USD 3,000 to USD 80,000",
            "2.4  Small Business Loans  — USD 10,000 to USD 500,000",
            "2.5  Education Loans        — USD 2,000 to USD 100,000",
            "",
            "SECTION 3 — MINIMUM ELIGIBILITY CRITERIA",
            "",
            "3.1  Age: Applicant must be at least 21 years of age.",
            "3.2  Citizenship: Must be a citizen or permanent resident.",
            "3.3  Employment: Minimum 12 months of continuous employment.",
            "     Self-employed applicants must provide 2 years of ITR.",
            "3.4  Income: Minimum monthly net income of USD 2,000.",
            "3.5  Credit Score: Minimum FICO score of 620 for standard loans.",
            "     Premium rates apply for scores above 750.",
            "3.6  Debt-to-Income Ratio: Must not exceed 43%.",
        ],
    },
    {
        "title": "SECTION 4 — CREDIT SCORE BANDS",
        "subtitle": "",
        "lines": [
            "",
            "The bank uses the following credit score classification:",
            "",
            "  Score 300 – 579  :  Poor       — Loan declined. Refer to credit counselling.",
            "  Score 580 – 619  :  Fair        — Conditional approval with collateral required.",
            "  Score 620 – 659  :  Acceptable  — Standard approval. Higher interest rate tier.",
            "  Score 660 – 699  :  Good        — Standard approval. Mid interest rate tier.",
            "  Score 700 – 749  :  Very Good   — Preferred approval. Lower interest rate.",
            "  Score 750 – 850  :  Excellent   — Priority approval. Best available rate.",
            "",
            "SECTION 5 — INCOME AND EMPLOYMENT VERIFICATION",
            "",
            "5.1  Salaried Employees:",
            "     - Last 3 months payslips",
            "     - Latest Form 16 or W-2",
            "     - 6 months bank statement",
            "     - Employment confirmation letter",
            "",
            "5.2  Self-Employed / Business Owners:",
            "     - Last 2 years Income Tax Returns (ITR)",
            "     - Business registration certificate",
            "     - 12 months business bank statement",
            "     - Profit and Loss statement (CA certified)",
            "",
            "5.3  Retired / Pensioners:",
            "     - Pension slip or Social Security statement",
            "     - 6 months bank statement showing regular credit",
            "     - Proof of any additional income sources",
        ],
    },
    {
        "title": "SECTION 6 — DEBT-TO-INCOME RATIO (DTI)",
        "subtitle": "",
        "lines": [
            "",
            "DTI = (Total Monthly Debt Payments) / (Gross Monthly Income) x 100",
            "",
            "  DTI below 28%  :  Excellent — Strongly preferred for approval.",
            "  DTI 28% – 36%  :  Good      — Standard approval criteria met.",
            "  DTI 37% – 43%  :  Marginal  — Requires additional review and documentation.",
            "  DTI above 43%  :  Declined  — Does not meet minimum policy requirements.",
            "",
            "Note: Housing expense ratio (mortgage/rent to income) must not exceed 28%.",
            "",
            "SECTION 7 — LOAN-TO-VALUE RATIO (LTV)",
            "",
            "For secured loans, the maximum LTV ratios are:",
            "",
            "  Home Improvement Loans : Maximum 80% LTV",
            "  Auto Loans             : Maximum 85% LTV",
            "  Small Business Loans   : Maximum 70% LTV",
            "",
            "SECTION 8 — INTEREST RATE STRUCTURE",
            "",
            "8.1  Personal Loans:",
            "     Credit score 620-659 : 16% – 18% per annum",
            "     Credit score 660-699 : 13% – 15% per annum",
            "     Credit score 700-749 : 10% – 12% per annum",
            "     Credit score 750+    :  8% – 9.5% per annum",
            "",
            "8.2  Rate Review: Rates are reviewed quarterly by the Credit Committee.",
            "8.3  Fixed vs Variable: Loans under USD 25,000 may be fixed rate only.",
        ],
    },
    {
        "title": "SECTION 9 — REQUIRED DOCUMENTS",
        "subtitle": "",
        "lines": [
            "",
            "All applicants must submit the following:",
            "",
            "  (a) Completed loan application form (Form LA-01)",
            "  (b) Government-issued photo ID (passport, driving licence)",
            "  (c) Proof of address not older than 3 months",
            "  (d) PAN card or Social Security Number",
            "  (e) Income proof (as per Section 5)",
            "  (f) Bank statements for last 6 months",
            "  (g) Existing loan statements (if any)",
            "",
            "For secured loans, additionally:",
            "  (h) Property documents / vehicle RC book",
            "  (i) Insurance documents",
            "  (j) Valuation report from approved valuer",
            "",
            "SECTION 10 — LOAN TENURE",
            "",
            "  Personal Loans        :  12 to 60 months",
            "  Home Improvement Loans:  12 to 180 months",
            "  Auto Loans            :  12 to 84 months",
            "  Small Business Loans  :  12 to 120 months",
            "  Education Loans       :  12 to 84 months (moratorium during study)",
            "",
            "SECTION 11 — AUTOMATIC DECLINE CONDITIONS",
            "",
            "Applications are automatically declined if any of the following apply:",
            "  - Credit score below 580",
            "  - Active bankruptcy proceedings",
            "  - Loan default in the last 24 months",
            "  - DTI exceeds 50%",
            "  - Undischarged insolvency",
            "  - Fraud flag on any credit bureau report",
        ],
    },
    {
        "title": "SECTION 12 — APPROVAL AUTHORITY",
        "subtitle": "",
        "lines": [
            "",
            "  Loans up to USD 10,000        : Branch Loan Officer",
            "  Loans USD 10,001 – USD 50,000 : Senior Credit Analyst",
            "  Loans USD 50,001 – USD 200,000: Regional Credit Manager",
            "  Loans above USD 200,000       : Credit Committee (quorum of 3)",
            "",
            "SECTION 13 — TURNAROUND TIME",
            "",
            "  Pre-approval decision    :  24 hours from complete application",
            "  Final sanction letter    :  3 – 5 business days",
            "  Loan disbursement        :  2 – 3 business days after sanction",
            "",
            "SECTION 14 — REPAYMENT AND DEFAULT",
            "",
            "14.1 EMI must be received by the 5th of each month.",
            "14.2 Grace period of 10 days applies before late fee is charged.",
            "14.3 Late fee: 2% of overdue EMI amount per month.",
            "14.4 Loans overdue by 90+ days are classified as NPA (Non-Performing Asset).",
            "14.5 Prepayment allowed after 6 EMIs. Prepayment charge: 2% of outstanding.",
            "",
            "SECTION 15 — APPEALS PROCESS",
            "",
            "Declined applicants may appeal within 30 days by submitting:",
            "  - Appeal form (Form LA-02)",
            "  - Additional supporting documents",
            "  - Written explanation of changed circumstances",
            "",
            "Appeals are reviewed by the Regional Credit Manager within 10 business days.",
            "",
            "SECTION 16 — POLICY REVIEW",
            "",
            "This policy is reviewed annually by the Credit Committee and approved by",
            "the Board Risk Committee. Interim revisions may be made as required by",
            "regulatory changes. All staff must complete annual policy training.",
            "",
            "Last reviewed  : December 2023",
            "Next review    : December 2024",
            "Policy owner   : Head of Credit Risk, FinCorp Bank",
        ],
    },
]


# ---------------------------------------------------------------------------
# Minimal PDF writer (no dependencies)
# ---------------------------------------------------------------------------

def _encode_text(text: str) -> bytes:
    """Escape special PDF characters."""
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)").encode("latin-1", errors="replace")


def generate_pdf(output_path: str) -> None:
    objects = []
    offsets = []

    def add_object(content: bytes) -> int:
        idx = len(objects) + 1
        objects.append(content)
        return idx

    # Object 1: Catalog (written later after pages)
    # Object 2: Page tree (written later)

    page_obj_ids = []

    font_obj_id = add_object(
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"
    )
    bold_font_obj_id = add_object(
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>"
    )

    def build_page_stream(page_data: dict) -> bytes:
        lines_out = []
        y = 760
        margin = 60

        lines_out.append(b"BT")

        # Title
        title = page_data["title"]
        lines_out.append(b"/F2 14 Tf")
        lines_out.append(f"{margin} {y} Td".encode())
        lines_out.append(b"(" + _encode_text(title) + b") Tj")
        y -= 20

        # Subtitle
        if page_data.get("subtitle"):
            lines_out.append(b"/F1 8 Tf")
            lines_out.append(f"{margin} {y} Td".encode())
            lines_out.append(b"(" + _encode_text(page_data["subtitle"]) + b") Tj")
            y -= 18

        y -= 6

        # Body lines
        for line in page_data["lines"]:
            if y < 60:
                break
            if line == "":
                y -= 8
                continue
            # Section headers (ALL CAPS lines)
            if line.isupper() or (line.startswith("SECTION") and "—" in line):
                lines_out.append(b"/F2 10 Tf")
                lines_out.append(f"{margin} {y} Td".encode())
            else:
                lines_out.append(b"/F1 9 Tf")
                lines_out.append(f"{margin} {y} Td".encode())
            lines_out.append(b"(" + _encode_text(line) + b") Tj")
            y -= 13

        lines_out.append(b"ET")
        return b"\n".join(lines_out)

    # After fonts, we add len(PAGES) stream objects + len(PAGES) page objects,
    # so the page tree object ends up at: current_count + 2*len(PAGES) + 1
    page_tree_id = len(objects) + 2 * len(PAGES) + 1
    page_ids_placeholder = []

    # Pre-compute all page stream objects
    stream_ids = []
    for page_data in PAGES:
        stream_content = build_page_stream(page_data)
        compressed = zlib.compress(stream_content)
        stream_obj = (
            f"<< /Filter /FlateDecode /Length {len(compressed)} >>".encode()
            + b"\nstream\n"
            + compressed
            + b"\nendstream"
        )
        sid = add_object(stream_obj)
        stream_ids.append(sid)

    # Page objects
    for sid in stream_ids:
        page_obj = (
            f"<< /Type /Page /Parent {page_tree_id} 0 R "
            f"/MediaBox [0 0 595 842] "
            f"/Contents {sid} 0 R "
            f"/Resources << /Font << /F1 {font_obj_id} 0 R /F2 {bold_font_obj_id} 0 R >> >> >>"
        ).encode()
        pid = add_object(page_obj)
        page_ids_placeholder.append(pid)

    # Page tree object
    kids = " ".join(f"{pid} 0 R" for pid in page_ids_placeholder)
    page_tree_obj = f"<< /Type /Pages /Kids [{kids}] /Count {len(PAGES)} >>".encode()
    actual_page_tree_id = add_object(page_tree_obj)

    # Catalog
    catalog_obj = f"<< /Type /Catalog /Pages {actual_page_tree_id} 0 R >>".encode()
    catalog_id = add_object(catalog_obj)

    # Write PDF
    buf = bytearray()
    buf.extend(b"%PDF-1.4\n")

    for i, obj_content in enumerate(objects):
        offsets.append(len(buf))
        buf.extend(f"{i + 1} 0 obj\n".encode())
        buf.extend(obj_content)
        buf.extend(b"\nendobj\n")

    xref_offset = len(buf)
    buf.extend(b"xref\n")
    buf.extend(f"0 {len(objects) + 1}\n".encode())
    buf.extend(b"0000000000 65535 f \n")
    for off in offsets:
        buf.extend(f"{off:010d} 00000 n \n".encode())

    buf.extend(b"trailer\n")
    buf.extend(f"<< /Size {len(objects) + 1} /Root {catalog_id} 0 R >>\n".encode())
    buf.extend(b"startxref\n")
    buf.extend(f"{xref_offset}\n".encode())
    buf.extend(b"%%EOF\n")

    Path(output_path).write_bytes(bytes(buf))
    print(f"Generated: {output_path} ({len(buf):,} bytes, {len(PAGES)} pages)")


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "data" / "loan_policy.pdf"
    out.parent.mkdir(exist_ok=True)
    generate_pdf(str(out))
