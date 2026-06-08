from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BOOK = "Accountancy Syllabus Question Bank 2025-26 - Numerical Tables"
PDF_PATH = r"C:\Users\acer\Downloads\Accountancy_SrSec_2025-26.pdf"

RUBRIC = [
    {"criterion": "Correct calculation", "marks": 2},
    {"criterion": "Correct account or treatment", "marks": 1},
    {"criterion": "Correct table placement", "marks": 1},
    {"criterion": "No irrelevant option placed", "marks": 1},
]


def chip(prefix: str, suffix: str, text: str) -> dict[str, str]:
    return {"id": f"{prefix}-{suffix}", "text": text}


def blank(slot_id: str, label: str) -> dict[str, str]:
    return {"slotId": slot_id, "label": label}


def activity(prefix: str, chapter: dict[str, Any], number: int, spec: dict[str, Any]) -> dict[str, Any]:
    activity_id = f"{prefix}-{number:02d}"
    slots: list[dict[str, str]] = []
    correct_items: list[dict[str, str]] = []
    for index, answer in enumerate(spec["answers"], start=1):
        slot_id = f"{activity_id}-slot-{index}"
        slots.append({"id": slot_id, "label": answer["label"]})
        correct_items.append(chip(activity_id, f"c{index}", answer["value"]))

    answer_index = 0
    rows = []
    for row in spec["rows"]:
        rendered = []
        for cell in row:
            if cell == "__":
                rendered.append(blank(slots[answer_index]["id"], slots[answer_index]["label"]))
                answer_index += 1
            else:
                rendered.append(cell)
        rows.append(rendered)

    return {
        "id": activity_id,
        "type": "data_chart_table",
        "difficulty": "numerical-table",
        "classLevel": 12,
        "stream": "Commerce",
        "subject": "Accountancy",
        "book": BOOK,
        "chapter": chapter["chapter"],
        "chapterNumber": chapter["chapterNumber"],
        "marks": spec.get("marks", 5),
        "question": spec["question"],
        "instructions": "Calculate the missing amounts, then drag the correct value chips into the blank table cells.",
        "structureHelp": ["Read given data", "Calculate amount", "Choose chip", "Drop in blank cell"],
        "sourceTextSummary": f"Class 12 Accountancy numerical table practice for {chapter['chapter']}.",
        "sourceChapter": chapter["chapter"],
        "sourcePdf": PDF_PATH,
        "correctItems": correct_items,
        "distractors": [chip(activity_id, f"x{index}", value) for index, value in enumerate(spec["distractors"], start=1)],
        "answerSlots": slots,
        "answerKey": {slot["id"]: [correct_items[index]["id"]] for index, slot in enumerate(slots)},
        "hints": spec.get("hints", ["Use the formula shown in the row.", "Match each blank with the exact calculated amount."]),
        "modelAnswer": ", ".join(f"{answer['label']}: {answer['value']}" for answer in spec["answers"]),
        "scoringRubric": RUBRIC,
        "tableData": {
            "title": spec["title"],
            "dropMode": "table-cells",
            "headers": spec["headers"],
            "rows": rows,
            "question": spec["question"],
        },
        "questionStyle": "class-12-accountancy-numerical-table-drag-drop",
    }


def dataset(chapter: dict[str, Any], specs: list[dict[str, Any]], relative: str) -> dict[str, Any]:
    prefix = f"c12-acc-num-ch{chapter['chapterNumber']:02d}"
    activities = [activity(prefix, chapter, index, spec) for index, spec in enumerate(specs, start=1)]
    return {
        "version": 2,
        "generatedBy": "scripts/generate_accountancy_all_chapter_numerical_tables.py",
        "generatedAt": int(time.time()),
        "source": {
            "root": r"C:\Users\acer\Downloads",
            "pdfPath": PDF_PATH,
            "classLevel": 12,
            "stream": "Commerce",
            "subject": "Accountancy",
            "book": BOOK,
            "chapter": chapter["chapter"],
            "chapterNumber": chapter["chapterNumber"],
            "pageCount": None,
            "extractedCharacterCount": None,
            "extractionPreview": f"Chapter-wise numerical table practice for {chapter['chapter']}.",
        },
        "coverage": {
            "classes": [12],
            "streams": ["Commerce"],
            "questionTypeCount": 1,
            "activityCount": len(activities),
            "tablePracticeMode": "continuous-table-drag-drop",
            "generationMode": "class-12-accountancy-all-chapter-numerical-tables",
        },
        "chapterQuestions": [
            {
                "number": index,
                "groupId": f"{prefix}-q{index:02d}",
                "question": spec["question"],
                "questionIdentifier": {
                    "label": "Accountancy Numerical Table",
                    "primaryType": "data_chart_table",
                    "slotStrategy": "drop-values-in-table-cells",
                    "layout": "calculation table with direct blank cells",
                    "id": "accountancy_numerical_table",
                },
            }
            for index, spec in enumerate(specs, start=1)
        ],
        "activities": activities,
    }


def spec(title: str, question: str, headers: list[str], rows: list[list[str]], answers: list[tuple[str, str]], distractors: list[str]) -> dict[str, Any]:
    return {
        "title": title,
        "question": question,
        "headers": headers,
        "rows": rows,
        "answers": [{"label": label, "value": value} for label, value in answers],
        "distractors": distractors,
    }


CHAPTERS: list[dict[str, Any]] = [
    {
        "chapterNumber": 1,
        "chapter": "Fundamentals of Partnership and Goodwill",
        "slug": "fundamentals-of-partnership-and-goodwill",
        "specs": [
            spec("P and L Appropriation", "Complete the appropriation table for A and B sharing profits 3:2.", ["Item", "Given", "Blank", "Treatment"], [["Net profit", "Rs 1,20,000", "__", "Starting balance"], ["Interest on capital", "A Rs 50,000 at 10%; B Rs 40,000 at 10%", "__", "Appropriation"], ["Salary to A", "Rs 12,000", "__", "Appropriation"], ["Residual profit", "Balance", "__", "Divide 3:2"], ["A share", "3/5 of residual", "__", "Credit A"], ["B share", "2/5 of residual", "__", "Credit B"]], [("Net profit", "Rs 1,20,000"), ("Interest", "Rs 9,000"), ("Salary", "Rs 12,000"), ("Residual", "Rs 99,000"), ("A share", "Rs 59,400"), ("B share", "Rs 39,600")], ["Rs 1,29,000", "Rs 21,000", "Rs 60,000", "Rs 40,000"]),
            spec("Goodwill Average Profit", "Calculate goodwill at 3 years' purchase of average profit.", ["Year / step", "Profit / formula", "Blank", "Rule"], [["2021", "Rs 80,000", "__", "Include"], ["2022", "Rs 1,00,000", "__", "Include"], ["2023", "Rs 1,20,000", "__", "Include"], ["Average profit", "Total / 3", "__", "Base"], ["Goodwill", "Average x 3", "__", "Final"]], [("2021", "Rs 80,000"), ("2022", "Rs 1,00,000"), ("2023", "Rs 1,20,000"), ("Average", "Rs 1,00,000"), ("Goodwill", "Rs 3,00,000")], ["Rs 2,00,000", "Rs 90,000", "Rs 3,60,000"]),
            spec("Interest on Drawings", "Use product method at 10% p.a. to calculate interest on drawings.", ["Date", "Drawings", "Months", "Blank"], [["1 Apr", "Rs 6,000", "12", "__"], ["1 Jul", "Rs 4,000", "9", "__"], ["1 Oct", "Rs 5,000", "6", "__"], ["Total product", "Rate 10%", "", "__"], ["Interest", "Product x 10 / 12 / 100", "", "__"]], [("Product 1", "72,000"), ("Product 2", "36,000"), ("Product 3", "30,000"), ("Total product", "1,38,000"), ("Interest", "Rs 1,150")], ["Rs 13,800", "1,50,000", "Rs 1,250"]),
        ],
    },
    {
        "chapterNumber": 2,
        "chapter": "Change in Profit Sharing Ratio - Methods of Goodwill",
        "slug": "change-in-profit-sharing-ratio-methods-of-goodwill",
        "specs": [
            spec("Sacrificing and Gaining Ratio", "A, B and C change from 5:3:2 to equal shares. Goodwill is Rs 2,40,000.", ["Partner", "Old", "New", "Change", "Goodwill adjustment"], [["A", "5/10", "1/3", "__", "__"], ["B", "3/10", "1/3", "__", "__"], ["C", "2/10", "1/3", "__", "__"]], [("A change", "Sacrifice 5/30"), ("A adjustment", "Credit Rs 40,000"), ("B change", "Gain 1/30"), ("B adjustment", "Debit Rs 8,000"), ("C change", "Gain 4/30"), ("C adjustment", "Debit Rs 32,000")], ["Debit Rs 40,000", "Sacrifice 1/30", "Credit Rs 32,000"]),
            spec("Reserve Distribution", "Distribute general reserve of Rs 1,20,000 in old ratio 5:3:2.", ["Partner", "Old ratio", "Reserve share", "Treatment"], [["A", "5/10", "__", "__"], ["B", "3/10", "__", "__"], ["C", "2/10", "__", "__"]], [("A reserve", "Rs 60,000"), ("A treatment", "Credit capital/current"), ("B reserve", "Rs 36,000"), ("B treatment", "Credit capital/current"), ("C reserve", "Rs 24,000"), ("C treatment", "Credit capital/current")], ["Debit capital/current", "Rs 40,000", "Rs 30,000"]),
            spec("Revaluation Profit", "Distribute revaluation profit of Rs 48,000 in old ratio 2:1:1.", ["Partner", "Old ratio", "Profit share", "Capital effect"], [["A", "2/4", "__", "__"], ["B", "1/4", "__", "__"], ["C", "1/4", "__", "__"]], [("A profit", "Rs 24,000"), ("A effect", "Credit A capital"), ("B profit", "Rs 12,000"), ("B effect", "Credit B capital"), ("C profit", "Rs 12,000"), ("C effect", "Credit C capital")], ["Debit A capital", "Rs 16,000", "Rs 18,000"]),
        ],
    },
    {
        "chapterNumber": 3,
        "chapter": "Admission of a Partner",
        "slug": "admission-of-a-partner",
        "specs": [
            spec("New Ratio on Admission", "A and B share 3:2. C is admitted for 1/5 share, taken by A and B in old ratio.", ["Partner", "Old share", "Sacrifice", "New share"], [["A", "3/5", "__", "__"], ["B", "2/5", "__", "__"], ["C", "-", "__", "__"]], [("A sacrifice", "3/25"), ("A new", "12/25"), ("B sacrifice", "2/25"), ("B new", "8/25"), ("C sacrifice", "5/25"), ("C new", "5/25")], ["10/25", "1/5 gain", "3/20"]),
            spec("Goodwill Premium", "C brings Rs 60,000 as premium for 1/4 share. A and B sacrifice 3:1.", ["Partner", "Sacrificing ratio", "Goodwill share", "Treatment"], [["A", "3/4", "__", "__"], ["B", "1/4", "__", "__"], ["C", "Brings cash", "__", "__"]], [("A share", "Rs 45,000"), ("A treatment", "Credit A capital"), ("B share", "Rs 15,000"), ("B treatment", "Credit B capital"), ("C cash", "Rs 60,000"), ("C treatment", "Debit Cash/Bank")], ["Rs 30,000", "Debit A capital", "Credit C capital"]),
            spec("Revaluation on Admission", "Assets rise by Rs 50,000 and liabilities rise by Rs 14,000. Old ratio A:B = 3:2.", ["Step / partner", "Given", "Blank", "Treatment"], [["Asset increase", "Rs 50,000", "__", "Credit revaluation"], ["Liability increase", "Rs 14,000", "__", "Debit revaluation"], ["Revaluation profit", "Net", "__", "Old partners"], ["A share", "3/5", "__", "Credit A"], ["B share", "2/5", "__", "Credit B"]], [("Asset increase", "Rs 50,000"), ("Liability increase", "Rs 14,000"), ("Profit", "Rs 36,000"), ("A share", "Rs 21,600"), ("B share", "Rs 14,400")], ["Rs 64,000", "Rs 18,000", "Rs 20,000"]),
        ],
    },
    {
        "chapterNumber": 4,
        "chapter": "Retirement and Death of a Partner",
        "slug": "retirement-and-death-of-a-partner",
        "specs": [
            spec("Gaining Ratio", "A, B and C share 4:3:2. B retires; A and C share 5:4.", ["Partner", "Old share", "New share", "Gain"], [["A", "4/9", "5/9", "__"], ["C", "2/9", "4/9", "__"], ["B", "3/9", "-", "__"]], [("A gain", "1/9"), ("C gain", "2/9"), ("B retired share", "3/9")], ["3/9", "1/3 gain", "No gain"]),
            spec("Retiring Partner Settlement", "Retiring partner B has capital Rs 1,40,000, goodwill share Rs 30,000, revaluation profit Rs 12,000 and drawings Rs 8,000.", ["Item", "Amount", "Blank", "Effect"], [["Capital", "Rs 1,40,000", "__", "Credit"], ["Goodwill", "Rs 30,000", "__", "Credit"], ["Revaluation profit", "Rs 12,000", "__", "Credit"], ["Drawings", "Rs 8,000", "__", "Debit"], ["Amount due", "Net", "__", "Transfer/pay"]], [("Capital", "Rs 1,40,000"), ("Goodwill", "Rs 30,000"), ("Revaluation", "Rs 12,000"), ("Drawings", "Rs 8,000"), ("Amount due", "Rs 1,74,000")], ["Rs 1,90,000", "Rs 1,50,000", "Debit goodwill"]),
            spec("Profit Till Death", "Deceased partner's last year profit was Rs 1,20,000. Death after 3 months. Share 1/4.", ["Step", "Formula", "Blank", "Meaning"], [["Estimated annual profit", "Rs 1,20,000", "__", "Base"], ["Time proportion", "3/12", "__", "Till death"], ["Firm profit till death", "1,20,000 x 3/12", "__", "Period profit"], ["Partner share", "1/4", "__", "Credit deceased partner"]], [("Annual profit", "Rs 1,20,000"), ("Time", "3/12"), ("Period profit", "Rs 30,000"), ("Partner share", "Rs 7,500")], ["Rs 10,000", "Rs 37,500", "Rs 30,000 share"]),
        ],
    },
    {
        "chapterNumber": 5,
        "chapter": "Dissolution of Partnership Firm",
        "slug": "dissolution-of-partnership-firm",
        "specs": [
            spec("Realisation Account", "Assets book value Rs 2,80,000 realised Rs 2,50,000; liabilities Rs 90,000 paid at Rs 86,000; expenses Rs 6,000.", ["Item", "Given", "Blank", "Realisation effect"], [["Assets transferred", "Book value", "__", "Debit"], ["Cash from assets", "Realised", "__", "Credit"], ["Liabilities transferred", "Book value", "__", "Credit"], ["Liabilities paid", "Paid", "__", "Debit"], ["Expenses", "Paid", "__", "Debit"], ["Realisation result", "Net", "__", "Profit/Loss"]], [("Assets", "Rs 2,80,000"), ("Realised", "Rs 2,50,000"), ("Liabilities", "Rs 90,000"), ("Paid", "Rs 86,000"), ("Expenses", "Rs 6,000"), ("Loss", "Rs 42,000")], ["Profit Rs 42,000", "Rs 36,000", "Rs 2,86,000"]),
            spec("Partner Capital Settlement", "Realisation loss Rs 42,000 shared 3:2. Capitals A Rs 1,20,000 and B Rs 80,000.", ["Partner", "Capital before loss", "Loss share", "Amount payable"], [["A", "Rs 1,20,000", "__", "__"], ["B", "Rs 80,000", "__", "__"]], [("A loss", "Rs 25,200"), ("A payable", "Rs 94,800"), ("B loss", "Rs 16,800"), ("B payable", "Rs 63,200")], ["Rs 21,000", "Rs 99,000", "Rs 60,000"]),
            spec("Cash Bank Account", "Cash balance Rs 20,000; assets realised Rs 2,50,000; liabilities paid Rs 86,000; expenses Rs 6,000; partners paid A Rs 94,800 and B Rs 63,200.", ["Receipt/payment", "Amount", "Blank", "Side"], [["Opening cash", "Rs 20,000", "__", "Receipt"], ["Assets realised", "Rs 2,50,000", "__", "Receipt"], ["Liabilities paid", "Rs 86,000", "__", "Payment"], ["Expenses paid", "Rs 6,000", "__", "Payment"], ["Partners paid", "A + B", "__", "Payment"], ["Closing balance", "Should close", "__", "Check"]], [("Opening", "Rs 20,000"), ("Assets", "Rs 2,50,000"), ("Liabilities", "Rs 86,000"), ("Expenses", "Rs 6,000"), ("Partners", "Rs 1,58,000"), ("Closing", "Nil")], ["Rs 1,80,000", "Rs 2,70,000", "Rs 20,000"]),
        ],
    },
    {
        "chapterNumber": 6,
        "chapter": "Accounting for Share Capital",
        "slug": "accounting-for-share-capital",
        "specs": [
            spec("Share Issue at Premium", "10,000 shares of Rs 10 issued at Rs 12. Application Rs 5, allotment Rs 5 including premium, first call Rs 2.", ["Stage", "Formula", "Blank", "Account"], [["Application", "10,000 x 5", "__", "Share application"], ["Share capital on application", "10,000 x 5", "__", "Share capital"], ["Allotment due", "10,000 x 5", "__", "Share allotment"], ["Securities premium", "10,000 x 2", "__", "Premium reserve"], ["First call", "10,000 x 2", "__", "Share first call"]], [("Application", "Rs 50,000"), ("Capital application", "Rs 50,000"), ("Allotment", "Rs 50,000"), ("Premium", "Rs 20,000"), ("First call", "Rs 20,000")], ["Rs 1,20,000", "Rs 30,000", "Rs 10,000"]),
            spec("Forfeiture", "1,000 shares of Rs 10, Rs 8 called, Rs 6 received, forfeited.", ["Step", "Formula", "Blank", "Effect"], [["Share capital debit", "1,000 x 8", "__", "Debit"], ["Share forfeiture credit", "1,000 x 6", "__", "Credit"], ["Calls in arrears credit", "1,000 x 2", "__", "Credit"], ["Amount unpaid", "Difference", "__", "Arrears"]], [("Capital debit", "Rs 8,000"), ("Forfeiture", "Rs 6,000"), ("Calls arrears", "Rs 2,000"), ("Unpaid", "Rs 2,000")], ["Rs 10,000", "Rs 4,000", "Rs 6,000 debit"]),
            spec("Reissue and Capital Reserve", "Forfeited 1,000 shares with Rs 6 received are reissued at Rs 9 fully paid.", ["Step", "Formula", "Blank", "Treatment"], [["Bank received", "1,000 x 9", "__", "Debit bank"], ["Share capital", "1,000 x 10", "__", "Credit capital"], ["Discount on reissue", "1,000 x 1", "__", "Debit forfeiture"], ["Capital reserve", "Forfeiture balance", "__", "Transfer"]], [("Bank", "Rs 9,000"), ("Capital", "Rs 10,000"), ("Discount", "Rs 1,000"), ("Capital reserve", "Rs 5,000")], ["Rs 6,000", "Rs 4,000", "Rs 1,000 reserve"]),
        ],
    },
    {
        "chapterNumber": 7,
        "chapter": "Accounting for Debentures",
        "slug": "accounting-for-debentures",
        "specs": [
            spec("Issue of Debentures at Discount", "5,000 debentures of Rs 100 issued at 95%.", ["Item", "Formula", "Blank", "Treatment"], [["Bank received", "5,000 x 95", "__", "Debit bank"], ["Discount/loss", "5,000 x 5", "__", "Debit loss"], ["Debentures", "5,000 x 100", "__", "Credit liability"]], [("Bank", "Rs 4,75,000"), ("Discount", "Rs 25,000"), ("Debentures", "Rs 5,00,000")], ["Rs 4,50,000", "Rs 5,25,000", "Rs 50,000"]),
            spec("Debenture Interest", "Rs 8,00,000 10% debentures; interest for 6 months.", ["Step", "Formula", "Blank", "Meaning"], [["Annual interest", "8,00,000 x 10%", "__", "Full year"], ["Half-year interest", "Annual x 6/12", "__", "Expense"], ["Debenture holders", "Amount payable", "__", "Liability"]], [("Annual interest", "Rs 80,000"), ("Half-year", "Rs 40,000"), ("Payable", "Rs 40,000")], ["Rs 8,000", "Rs 48,000", "Rs 80,000 payable"]),
            spec("Debentures as Collateral Security", "Debentures Rs 2,00,000 issued as collateral for bank loan Rs 1,50,000.", ["Item", "Given", "Blank", "Disclosure"], [["Bank loan", "Rs 1,50,000", "__", "Primary liability"], ["Debentures collateral", "Rs 2,00,000", "__", "Secondary security"], ["Balance sheet note", "Collateral issue", "__", "Shown by note"]], [("Bank loan", "Rs 1,50,000"), ("Collateral debentures", "Rs 2,00,000"), ("Disclosure", "By way of note")], ["Rs 50,000", "Primary capital", "Sales revenue"]),
        ],
    },
    {
        "chapterNumber": 8,
        "chapter": "Financial Statements of a Company",
        "slug": "financial-statements-of-a-company",
        "specs": [
            spec("Balance Sheet Classification", "Classify company balance sheet items and compute total current assets.", ["Item", "Amount", "Blank", "Heading"], [["Inventory", "Rs 1,20,000", "__", "Current asset"], ["Trade receivables", "Rs 80,000", "__", "Current asset"], ["Cash", "Rs 30,000", "__", "Current asset"], ["Total current assets", "Sum", "__", "Balance sheet"], ["Long-term borrowings", "Rs 2,00,000", "__", "Non-current liability"]], [("Inventory", "Rs 1,20,000"), ("Receivables", "Rs 80,000"), ("Cash", "Rs 30,000"), ("Current assets", "Rs 2,30,000"), ("Borrowings", "Rs 2,00,000")], ["Rs 2,00,000 assets", "Rs 1,50,000", "Current liability"]),
            spec("Statement of Profit and Loss", "Revenue Rs 5,00,000; purchases Rs 2,20,000; expenses Rs 90,000; tax Rs 38,000.", ["Item", "Formula", "Blank", "Meaning"], [["Revenue", "Given", "__", "Income"], ["Cost/expenses", "2,20,000 + 90,000", "__", "Total expenses"], ["Profit before tax", "Revenue - expenses", "__", "PBT"], ["Tax", "Given", "__", "Deduct"], ["Profit after tax", "PBT - tax", "__", "PAT"]], [("Revenue", "Rs 5,00,000"), ("Expenses", "Rs 3,10,000"), ("PBT", "Rs 1,90,000"), ("Tax", "Rs 38,000"), ("PAT", "Rs 1,52,000")], ["Rs 1,14,000", "Rs 2,80,000", "Rs 4,10,000"]),
            spec("Shareholders Funds", "Share capital Rs 4,00,000; securities premium Rs 60,000; surplus Rs 90,000.", ["Component", "Amount", "Blank", "Heading"], [["Share capital", "Rs 4,00,000", "__", "Equity"], ["Securities premium", "Rs 60,000", "__", "Reserves"], ["Surplus", "Rs 90,000", "__", "Reserves"], ["Shareholders funds", "Total", "__", "Balance sheet"]], [("Capital", "Rs 4,00,000"), ("Premium", "Rs 60,000"), ("Surplus", "Rs 90,000"), ("Funds", "Rs 5,50,000")], ["Rs 4,60,000", "Rs 4,90,000", "Current asset"]),
        ],
    },
    {
        "chapterNumber": 9,
        "chapter": "Financial Statement Analysis",
        "slug": "financial-statement-analysis",
        "specs": [
            spec("Comparative Statement", "Sales increased from Rs 4,00,000 to Rs 5,00,000; expenses from Rs 2,80,000 to Rs 3,70,000.", ["Item", "Previous", "Current", "Blank"], [["Sales increase", "4,00,000", "5,00,000", "__"], ["Sales % change", "Increase / previous", "", "__"], ["Expense increase", "2,80,000", "3,70,000", "__"], ["Expense % change", "Increase / previous", "", "__"]], [("Sales increase", "Rs 1,00,000"), ("Sales change", "25%"), ("Expense increase", "Rs 90,000"), ("Expense change", "32.14%")], ["20%", "Rs 80,000", "35%"]),
            spec("Common Size Balance Sheet", "Total assets Rs 10,00,000; fixed assets Rs 6,50,000; current assets Rs 3,50,000.", ["Item", "Amount", "% of total", "Blank"], [["Fixed assets", "Rs 6,50,000", "__", "Non-current"], ["Current assets", "Rs 3,50,000", "__", "Current"], ["Total assets", "Rs 10,00,000", "__", "Base"]], [("Fixed assets", "65%"), ("Current assets", "35%"), ("Total", "100%")], ["60%", "40%", "10%"]),
            spec("Trend Analysis", "Base year sales Rs 2,00,000. Current sales Rs 2,60,000; current profit Rs 52,000 vs base profit Rs 40,000.", ["Item", "Base", "Current", "Trend index"], [["Sales", "Rs 2,00,000", "Rs 2,60,000", "__"], ["Profit", "Rs 40,000", "Rs 52,000", "__"], ["Base index", "Base year", "", "__"]], [("Sales index", "130"), ("Profit index", "130"), ("Base index", "100")], ["120", "125", "150"]),
        ],
    },
    {
        "chapterNumber": 10,
        "chapter": "Accounting Ratios",
        "slug": "accounting-ratios",
        "specs": [
            spec("Liquidity Ratios", "Current assets Rs 3,00,000; inventory Rs 80,000; prepaid expenses Rs 20,000; current liabilities Rs 1,50,000.", ["Ratio", "Formula", "Blank", "Meaning"], [["Current ratio", "CA / CL", "__", "Liquidity"], ["Quick assets", "CA - inventory - prepaid", "__", "Liquid assets"], ["Quick ratio", "Quick assets / CL", "__", "Immediate liquidity"]], [("Current ratio", "2:1"), ("Quick assets", "Rs 2,00,000"), ("Quick ratio", "1.33:1")], ["1.5:1", "Rs 2,20,000", "2.5:1"]),
            spec("Solvency Ratios", "Debt Rs 5,00,000; equity Rs 8,00,000; EBIT Rs 2,40,000; interest Rs 60,000.", ["Ratio", "Formula", "Blank", "Meaning"], [["Debt-equity ratio", "Debt / equity", "__", "Solvency"], ["Interest coverage", "EBIT / interest", "__", "Debt service"], ["Proprietary ratio", "Equity / total assets Rs 13,00,000", "__", "Owners' funds"]], [("Debt-equity", "0.625:1"), ("Interest coverage", "4 times"), ("Proprietary", "0.615:1")], ["1.6:1", "3 times", "0.5:1"]),
            spec("Profitability Ratios", "Revenue Rs 10,00,000; gross profit Rs 3,00,000; net profit Rs 1,20,000; capital employed Rs 8,00,000.", ["Ratio", "Formula", "Blank", "Meaning"], [["Gross profit ratio", "GP / revenue x 100", "__", "Trading margin"], ["Net profit ratio", "NP / revenue x 100", "__", "Net margin"], ["ROI", "NP / capital employed x 100", "__", "Return"]], [("GP ratio", "30%"), ("NP ratio", "12%"), ("ROI", "15%")], ["20%", "18%", "25%"]),
        ],
    },
    {
        "chapterNumber": 11,
        "chapter": "Cash Flow Statement",
        "slug": "cash-flow-statement",
        "specs": [
            spec("Cash from Operations", "Net profit before tax Rs 2,00,000; depreciation Rs 40,000; profit on sale of asset Rs 10,000; increase in current assets Rs 25,000; increase in current liabilities Rs 15,000.", ["Step", "Formula", "Blank", "Classification"], [["Net profit", "Given", "__", "Start"], ["Add depreciation", "Non-cash", "__", "Add"], ["Less profit on sale", "Non-operating", "__", "Deduct"], ["Working capital adjustment", "-25,000 + 15,000", "__", "Adjust"], ["Cash from operations", "Net", "__", "Operating"]], [("Net profit", "Rs 2,00,000"), ("Depreciation", "Rs 40,000"), ("Profit sale", "Rs 10,000"), ("WC adjustment", "Minus Rs 10,000"), ("CFO", "Rs 2,20,000")], ["Rs 2,40,000", "Plus Rs 10,000", "Rs 1,80,000"]),
            spec("Investing Activities", "Machinery purchased Rs 1,50,000; old machinery sold Rs 35,000; interest received Rs 8,000.", ["Item", "Amount", "Blank", "Activity"], [["Purchase machinery", "Rs 1,50,000", "__", "Outflow"], ["Sale machinery", "Rs 35,000", "__", "Inflow"], ["Interest received", "Rs 8,000", "__", "Inflow"], ["Net investing cash flow", "35,000 + 8,000 - 1,50,000", "__", "Net"]], [("Purchase", "Minus Rs 1,50,000"), ("Sale", "Plus Rs 35,000"), ("Interest", "Plus Rs 8,000"), ("Net investing", "Minus Rs 1,07,000")], ["Plus Rs 1,50,000", "Minus Rs 43,000", "Plus Rs 1,07,000"]),
            spec("Financing Activities", "Issue of shares Rs 2,00,000; debenture redemption Rs 80,000; dividend paid Rs 30,000.", ["Item", "Amount", "Blank", "Activity"], [["Issue shares", "Rs 2,00,000", "__", "Inflow"], ["Redeem debentures", "Rs 80,000", "__", "Outflow"], ["Dividend paid", "Rs 30,000", "__", "Outflow"], ["Net financing", "2,00,000 - 80,000 - 30,000", "__", "Net"]], [("Shares", "Plus Rs 2,00,000"), ("Debentures", "Minus Rs 80,000"), ("Dividend", "Minus Rs 30,000"), ("Net financing", "Plus Rs 90,000")], ["Minus Rs 2,00,000", "Plus Rs 1,10,000", "Minus Rs 90,000"]),
        ],
    },
    {
        "chapterNumber": 12,
        "chapter": "Computerised Accounting System",
        "slug": "computerised-accounting-system",
        "specs": [
            spec("Spreadsheet BRS", "Cash book balance Rs 48,000; cheque issued not presented Rs 12,000; cheque deposited not cleared Rs 7,000; bank charges Rs 500.", ["Item", "Given amount / effect", "Blank", "Bank statement balance"], [["Cash book balance", "Start with Rs 48,000", "__", "Base"], ["Cheque issued not presented", "Add Rs 12,000", "__", "Bank higher"], ["Cheque deposited not cleared", "Less Rs 7,000", "__", "Bank lower"], ["Bank charges", "Less Rs 500", "__", "Bank lower"], ["Pass book balance", "48,000 + 12,000 - 7,000 - 500", "__", "Final"]], [("Cash book", "Rs 48,000"), ("Add cheque", "Rs 12,000"), ("Less deposit", "Rs 7,000"), ("Charges", "Rs 500"), ("Pass book", "Rs 52,500")], ["Rs 40,500", "Rs 53,000", "Rs 60,000"]),
            spec("Loan Schedule in Spreadsheet", "Loan Rs 1,00,000; annual interest 12%; repayment Rs 30,000 at year end.", ["Step", "Given / formula", "Blank", "Meaning"], [["Opening loan", "Given Rs 1,00,000", "__", "Principal"], ["Interest", "Rs 1,00,000 x 12%", "__", "Finance cost"], ["Amount due", "Rs 1,00,000 + Rs 12,000", "__", "Before repayment"], ["Repayment", "Given Rs 30,000", "__", "Cash outflow"], ["Closing loan", "Rs 1,12,000 - Rs 30,000", "__", "Balance"]], [("Opening", "Rs 1,00,000"), ("Interest", "Rs 12,000"), ("Amount due", "Rs 1,12,000"), ("Repayment", "Rs 30,000"), ("Closing", "Rs 82,000")], ["Rs 88,000", "Rs 70,000", "Rs 10,000"]),
            spec("Spreadsheet Ratio Analysis", "Current assets Rs 2,40,000; inventory Rs 60,000; current liabilities Rs 1,20,000.", ["Spreadsheet cell", "Formula", "Blank", "Output"], [["B2 Current assets", "Input", "__", "Data"], ["B3 Inventory", "Input", "__", "Data"], ["B4 Current liabilities", "Input", "__", "Data"], ["B5 Current ratio", "=B2/B4", "__", "Formula"], ["B6 Quick ratio", "=(B2-B3)/B4", "__", "Formula"]], [("CA", "Rs 2,40,000"), ("Inventory", "Rs 60,000"), ("CL", "Rs 1,20,000"), ("Current ratio", "2:1"), ("Quick ratio", "1.5:1")], ["1:1", "Rs 1,80,000 liabilities", "2.5:1"]),
        ],
    },
]


def upsert_catalog(path: str, payload: dict[str, Any]) -> None:
    catalog_path = ROOT / "data/catalog/content-catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8")) if catalog_path.exists() else {"datasets": []}
    source = payload["source"]
    entry = {
        "id": path.removesuffix(".json"),
        "jsonPath": path,
        "hasJson": True,
        "activityCount": len(payload["activities"]),
        "classLevel": source["classLevel"],
        "stream": source["stream"],
        "subject": source["subject"],
        "book": source["book"],
        "chapter": source["chapter"],
        "chapterNumber": source["chapterNumber"],
        "pdfPath": source["pdfPath"],
        "status": "active",
        "approvedBy": "accountancy-all-chapter-numerical-tables",
        "notes": "Class 12 Accountancy chapter-wise numerical table drag/drop practice.",
    }
    datasets = catalog.setdefault("datasets", [])
    for index, existing in enumerate(datasets):
        if existing.get("jsonPath") == path:
            datasets[index] = {**existing, **entry}
            break
    else:
        datasets.append(entry)
    catalog["generatedAt"] = int(time.time())
    catalog_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def upsert_active(path: str) -> None:
    active_path = ROOT / "data/catalog/active-datasets.json"
    payload = json.loads(active_path.read_text(encoding="utf-8")) if active_path.exists() else {"activeDatasets": []}
    entry = {
        "id": path.removesuffix(".json"),
        "jsonPath": path,
        "status": "active",
        "approvedBy": "accountancy-all-chapter-numerical-tables",
        "notes": "Class 12 Accountancy numerical table practice for all chapters.",
    }
    active = payload.setdefault("activeDatasets", [])
    for index, existing in enumerate(active):
        if existing.get("jsonPath") == path:
            active[index] = entry
            break
    else:
        active.append(entry)
    active_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    for chapter in CHAPTERS:
        relative = f"data/practice/class-12/accountancy-syllabus-question-bank/{chapter['chapterNumber']:02d}-{chapter['slug']}-numerical-tables.json"
        payload = dataset(chapter, chapter["specs"], relative)
        output = ROOT / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        upsert_catalog(relative, payload)
        upsert_active(relative)
        print(f"Wrote {relative} ({len(payload['activities'])} numerical table activities)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
