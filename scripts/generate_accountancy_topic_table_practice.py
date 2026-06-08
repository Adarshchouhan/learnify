from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BOOK = "Accountancy - Financial Accounting - 1"
PDF_PATH = r"C:\Users\acer\Downloads\all class pdf\all class pdf\Class 12\Commerce\Accountancy - Financial Accounting - 1\leac101.pdf"

REFERENCES = [
    {
        "title": "NCERT Class 12 Accountancy, Accounting for Partnership: Basic Concepts",
        "url": "https://cbseportal.com/ncert-books/class-12-accountancy-not-for-profit-organisation-and-partnership-accounts",
    },
    {
        "title": "Learn CBSE: Change in Profit Sharing Ratio Important Questions",
        "url": "https://www.learncbse.in/class-12-accountancy-reconstitution-of-a-partnership-firm-change-in-profit-sharing-ratio-among-the-existing-partners-important-questions-and-answers/",
    },
    {
        "title": "iCBSE: Fundamentals of Partnership and Goodwill CBSE Questions",
        "url": "https://www.icbse.com/answers/4yg2.html",
    },
]

RUBRIC = [
    {"criterion": "Correct calculation", "marks": 2},
    {"criterion": "Correct account/treatment", "marks": 1},
    {"criterion": "Correct ratio or partner-wise allocation", "marks": 1},
    {"criterion": "No irrelevant option placed", "marks": 1},
]


def slot(slot_id: str, label: str = "Drop calculated value") -> dict[str, str]:
    return {"slotId": slot_id, "label": label}


def item(prefix: str, suffix: str, text: str) -> dict[str, str]:
    return {"id": f"{prefix}-{suffix}", "text": text}


def activity(prefix: str, number: int, chapter: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    activity_id = f"{prefix}-{number:02d}"
    slots = []
    correct_items = []
    for index, answer in enumerate(spec["answers"], start=1):
        slot_id = f"{activity_id}-slot-{index}"
        slots.append({"id": slot_id, "label": answer["label"]})
        correct_items.append(item(activity_id, f"c{index}", answer["value"]))

    rows = []
    answer_index = 0
    for row in spec["rows"]:
        rendered_row = []
        for cell in row:
            if cell == "__":
                rendered_row.append(slot(slots[answer_index]["id"], slots[answer_index]["label"]))
                answer_index += 1
            else:
                rendered_row.append(cell)
        rows.append(rendered_row)

    distractors = [item(activity_id, f"x{index}", value) for index, value in enumerate(spec["distractors"], start=1)]
    answer_key = {slot_data["id"]: [correct_items[index]["id"]] for index, slot_data in enumerate(slots)}
    answer_text = ", ".join(f"{answer['label']}: {answer['value']}" for answer in spec["answers"])

    return {
        "id": activity_id,
        "type": "data_chart_table",
        "difficulty": spec.get("difficulty", "numerical-table"),
        "classLevel": 12,
        "stream": "Commerce",
        "subject": "Accountancy",
        "book": BOOK,
        "chapter": chapter["chapter"],
        "chapterNumber": chapter["chapterNumber"],
        "marks": spec.get("marks", 5),
        "question": spec["question"],
        "instructions": "Calculate the missing values, then drag the correct value chips directly into the blank cells of the table.",
        "structureHelp": ["Read data", "Calculate", "Place values in table", "Check treatment"],
        "sourceTextSummary": f"Original Class 12 Accountancy table practice for {chapter['chapter']}.",
        "sourceChapter": chapter["chapter"],
        "sourcePdf": PDF_PATH,
        "correctItems": correct_items,
        "distractors": distractors,
        "answerSlots": slots,
        "answerKey": answer_key,
        "hints": spec.get("hints", ["Use the ratio named in the row.", "Place only the calculated value that matches the blank."]),
        "modelAnswer": answer_text,
        "scoringRubric": RUBRIC,
        "tableData": {
            "title": spec["title"],
            "dropMode": "table-cells",
            "headers": spec["headers"],
            "rows": rows,
            "question": spec["question"],
        },
        "questionStyle": "class-12-accountancy-numerical-table-drag-drop",
        "questionDesignReferences": REFERENCES,
    }


def dataset(chapter: dict[str, Any], specs: list[dict[str, Any]], relative_path: str) -> dict[str, Any]:
    prefix = chapter["prefix"]
    activities = [activity(prefix, index, chapter, spec) for index, spec in enumerate(specs, start=1)]
    return {
        "version": 2,
        "generatedBy": "scripts/generate_accountancy_topic_table_practice.py",
        "generatedAt": int(time.time()),
        "source": {
            "root": r"C:\Users\acer\Downloads\all class pdf\all class pdf\Class 12\Commerce",
            "pdfPath": PDF_PATH,
            "classLevel": 12,
            "stream": "Commerce",
            "subject": "Accountancy",
            "book": BOOK,
            "chapter": chapter["chapter"],
            "chapterNumber": chapter["chapterNumber"],
            "pageCount": None,
            "extractedCharacterCount": None,
            "extractionPreview": f"Topic-wise table practice for {chapter['chapter']}.",
            "questionDesignReferences": REFERENCES,
        },
        "coverage": {
            "classes": [12],
            "streams": ["Commerce"],
            "questionTypeCount": 1,
            "activityCount": len(activities),
            "tablePracticeMode": "continuous-table-drag-drop",
            "topicFocus": chapter["chapter"],
        },
        "chapterQuestions": [
            {
                "number": index,
                "groupId": f"{prefix}-q{index:02d}",
                "question": spec["question"],
                "questionIdentifier": {
                    "label": "Accountancy Table Drag Drop",
                    "primaryType": "data_chart_table",
                    "slotStrategy": "drop-values-in-table-cells",
                    "layout": "calculation table with direct blank cells",
                    "id": "accountancy_table_drag_drop",
                },
            }
            for index, spec in enumerate(specs, start=1)
        ],
        "activities": activities,
    }


FUNDAMENTALS = [
    {
        "title": "Profit and Loss Appropriation Account",
        "question": "Complete the P and L Appropriation table for partners A and B sharing profits 3:2.",
        "headers": ["Particular", "Given data", "Working / blank", "Treatment"],
        "rows": [
            ["Net profit", "Rs 1,20,000", "__", "Start with profit before appropriations"],
            ["Interest on capital", "A Rs 50,000 at 10%; B Rs 40,000 at 10%", "__", "Debit appropriation account"],
            ["Partner salary", "A salary Rs 12,000", "__", "Debit appropriation account"],
            ["Residual profit", "Profit after above appropriations", "__", "Divide in 3:2"],
            ["A share of residual profit", "Residual profit in 3:2", "__", "Credit A capital/current account"],
            ["B share of residual profit", "Residual profit in 3:2", "__", "Credit B capital/current account"],
        ],
        "answers": [
            {"label": "Net profit", "value": "Rs 1,20,000"},
            {"label": "Interest on capital", "value": "Rs 9,000"},
            {"label": "Salary", "value": "Rs 12,000"},
            {"label": "Residual profit", "value": "Rs 99,000"},
            {"label": "A share", "value": "Rs 59,400"},
            {"label": "B share", "value": "Rs 39,600"},
        ],
        "distractors": ["Rs 1,29,000", "Rs 21,000", "Rs 60,000", "Rs 40,000", "Rs 96,000"],
    },
    {
        "title": "Interest on Drawings Product Method",
        "question": "Use the product method to complete the interest on drawings table for partner C.",
        "headers": ["Date", "Drawings", "Months to year end", "Product", "Interest blank"],
        "rows": [
            ["1 Apr", "Rs 6,000", "12", "__", "Use amount x months"],
            ["1 Jul", "Rs 4,000", "9", "__", "Use amount x months"],
            ["1 Oct", "Rs 5,000", "6", "__", "Use amount x months"],
            ["Total product", "Rate 10% p.a.", "__", "__", "Interest = product x 10 / 12 / 100"],
        ],
        "answers": [
            {"label": "Product 1", "value": "72,000"},
            {"label": "Product 2", "value": "36,000"},
            {"label": "Product 3", "value": "30,000"},
            {"label": "Total product", "value": "1,38,000"},
            {"label": "Interest on drawings", "value": "Rs 1,150"},
        ],
        "distractors": ["Rs 13,800", "1,50,000", "54,000", "Rs 1,250", "1,08,000"],
    },
    {
        "title": "Fixed Capital Accounts",
        "question": "Complete the fixed capital system table and decide which account records each item.",
        "headers": ["Item", "Amount", "Account to use", "Effect"],
        "rows": [
            ["Opening capital A", "Rs 2,00,000", "__", "Fixed balance normally unchanged"],
            ["Interest on capital A", "Rs 20,000", "__", "Record in current account"],
            ["Drawings A", "Rs 15,000", "__", "Record in current account"],
            ["Share of profit A", "Rs 45,000", "__", "Record in current account"],
            ["A current account net credit", "20,000 - 15,000 + 45,000", "__", "Closing current account balance"],
        ],
        "answers": [
            {"label": "Capital account", "value": "Capital A/c"},
            {"label": "Interest account", "value": "Current A/c"},
            {"label": "Drawings account", "value": "Current A/c"},
            {"label": "Profit account", "value": "Current A/c"},
            {"label": "Net credit", "value": "Rs 50,000"},
        ],
        "distractors": ["Revaluation A/c", "Rs 30,000", "Bank A/c", "Rs 65,000", "Goodwill A/c"],
    },
    {
        "title": "Fluctuating Capital Accounts",
        "question": "Complete the fluctuating capital account table for partner D.",
        "headers": ["Particular", "Amount", "Blank to fill", "Capital account effect"],
        "rows": [
            ["Opening capital", "Rs 1,80,000", "__", "Credit balance brought down"],
            ["Interest on capital", "Rs 18,000", "__", "Credit partner"],
            ["Drawings", "Rs 25,000", "__", "Debit partner"],
            ["Interest on drawings", "Rs 1,500", "__", "Debit partner"],
            ["Share of profit", "Rs 36,000", "__", "Credit partner"],
            ["Closing capital", "Compute", "__", "Final credit balance"],
        ],
        "answers": [
            {"label": "Opening", "value": "Rs 1,80,000"},
            {"label": "Interest capital", "value": "Rs 18,000"},
            {"label": "Drawings", "value": "Rs 25,000"},
            {"label": "Interest drawings", "value": "Rs 1,500"},
            {"label": "Profit share", "value": "Rs 36,000"},
            {"label": "Closing capital", "value": "Rs 2,07,500"},
        ],
        "distractors": ["Rs 1,72,500", "Rs 2,22,500", "Rs 43,000", "Rs 26,500", "Rs 1,98,500"],
    },
    {
        "title": "Guarantee of Profit",
        "question": "Complete the guarantee table where A guarantees B a minimum profit of Rs 40,000. Profit is Rs 90,000 shared 2:1.",
        "headers": ["Partner", "Normal share", "Guarantee adjustment", "Final share"],
        "rows": [["A", "__", "__", "__"], ["B", "__", "__", "__"]],
        "answers": [
            {"label": "A normal", "value": "Rs 60,000"},
            {"label": "A adjustment", "value": "Debit Rs 10,000"},
            {"label": "A final", "value": "Rs 50,000"},
            {"label": "B normal", "value": "Rs 30,000"},
            {"label": "B adjustment", "value": "Credit Rs 10,000"},
            {"label": "B final", "value": "Rs 40,000"},
        ],
        "distractors": ["Rs 45,000", "Credit Rs 5,000", "Debit Rs 20,000", "Rs 55,000", "Rs 35,000"],
    },
    {
        "title": "Past Adjustment",
        "question": "Complete the past adjustment table when interest on capital was omitted. A and B share profits 3:2; capitals Rs 1,00,000 and Rs 80,000; interest 10%.",
        "headers": ["Partner", "Interest omitted", "Already profit effect", "Net adjustment"],
        "rows": [["A", "__", "__", "__"], ["B", "__", "__", "__"]],
        "answers": [
            {"label": "A interest", "value": "Rs 10,000"},
            {"label": "A profit effect", "value": "Rs 10,800 debit"},
            {"label": "A net", "value": "Debit Rs 800"},
            {"label": "B interest", "value": "Rs 8,000"},
            {"label": "B profit effect", "value": "Rs 7,200 debit"},
            {"label": "B net", "value": "Credit Rs 800"},
        ],
        "distractors": ["Credit Rs 800", "Rs 9,000", "Debit Rs 1,800", "Rs 18,000", "Rs 6,000"],
    },
    {
        "title": "Average Profit Method of Goodwill",
        "question": "Complete the goodwill valuation table using 3 years' purchase of average profit.",
        "headers": ["Year / step", "Profit", "Blank", "Rule"],
        "rows": [["2021", "Rs 80,000", "__", "Include in total"], ["2022", "Rs 1,00,000", "__", "Include in total"], ["2023", "Rs 1,20,000", "__", "Include in total"], ["Average profit", "Total / 3", "__", "Calculate average"], ["Goodwill", "Average profit x 3", "__", "3 years' purchase"]],
        "answers": [
            {"label": "2021", "value": "Rs 80,000"},
            {"label": "2022", "value": "Rs 1,00,000"},
            {"label": "2023", "value": "Rs 1,20,000"},
            {"label": "Average", "value": "Rs 1,00,000"},
            {"label": "Goodwill", "value": "Rs 3,00,000"},
        ],
        "distractors": ["Rs 2,00,000", "Rs 90,000", "Rs 3,60,000", "Rs 1,50,000"],
    },
    {
        "title": "Weighted Average Profit Method",
        "question": "Complete the weighted average goodwill table using weights 1, 2 and 3 and 2 years' purchase.",
        "headers": ["Year", "Profit", "Weight", "Weighted profit"],
        "rows": [["2021", "Rs 60,000", "1", "__"], ["2022", "Rs 75,000", "2", "__"], ["2023", "Rs 90,000", "3", "__"], ["Weighted average", "Total weighted profit / 6", "__", "Goodwill = weighted average x 2"], ["Goodwill", "2 years' purchase", "__", "Final value"]],
        "answers": [
            {"label": "Weighted 2021", "value": "Rs 60,000"},
            {"label": "Weighted 2022", "value": "Rs 1,50,000"},
            {"label": "Weighted 2023", "value": "Rs 2,70,000"},
            {"label": "Weighted average", "value": "Rs 80,000"},
            {"label": "Goodwill", "value": "Rs 1,60,000"},
        ],
        "distractors": ["Rs 75,000", "Rs 2,25,000", "Rs 1,80,000", "Rs 4,80,000"],
    },
    {
        "title": "Super Profit Method",
        "question": "Complete the super profit goodwill table. Capital employed Rs 5,00,000, normal return 12%, average profit Rs 90,000, goodwill at 4 years' purchase.",
        "headers": ["Step", "Given / formula", "Blank", "Meaning"],
        "rows": [["Normal profit", "5,00,000 x 12%", "__", "Expected profit"], ["Super profit", "Average profit - normal profit", "__", "Excess profit"], ["Goodwill", "Super profit x 4", "__", "Value of goodwill"]],
        "answers": [
            {"label": "Normal profit", "value": "Rs 60,000"},
            {"label": "Super profit", "value": "Rs 30,000"},
            {"label": "Goodwill", "value": "Rs 1,20,000"},
        ],
        "distractors": ["Rs 90,000", "Rs 3,60,000", "Rs 50,000", "Rs 1,50,000"],
    },
    {
        "title": "Capitalisation of Average Profit",
        "question": "Complete the capitalisation of average profit table. Average profit Rs 96,000; normal rate 12%; actual capital Rs 6,20,000.",
        "headers": ["Step", "Formula", "Blank", "Rule"],
        "rows": [["Capitalised value", "Average profit x 100 / normal rate", "__", "Value of business"], ["Actual capital", "Given", "__", "Capital employed"], ["Goodwill", "Capitalised value - actual capital", "__", "Final goodwill"]],
        "answers": [
            {"label": "Capitalised value", "value": "Rs 8,00,000"},
            {"label": "Actual capital", "value": "Rs 6,20,000"},
            {"label": "Goodwill", "value": "Rs 1,80,000"},
        ],
        "distractors": ["Rs 1,20,000", "Rs 7,16,000", "Rs 2,00,000", "Rs 96,000"],
    },
    {
        "title": "Capitalisation of Super Profit",
        "question": "Complete the capitalisation of super profit table. Average profit Rs 1,10,000; normal profit Rs 80,000; normal rate 10%.",
        "headers": ["Step", "Formula", "Blank", "Rule"],
        "rows": [["Super profit", "1,10,000 - 80,000", "__", "Excess profit"], ["Goodwill", "Super profit x 100 / 10", "__", "Capitalised super profit"]],
        "answers": [
            {"label": "Super profit", "value": "Rs 30,000"},
            {"label": "Goodwill", "value": "Rs 3,00,000"},
        ],
        "distractors": ["Rs 1,90,000", "Rs 80,000", "Rs 30,00,000", "Rs 1,10,000"],
    },
    {
        "title": "Hidden Goodwill",
        "question": "Complete the hidden goodwill table. New partner C brings Rs 1,20,000 for 1/4 share of capital; total actual capital after admission is Rs 4,20,000.",
        "headers": ["Step", "Formula", "Blank", "Meaning"],
        "rows": [["Capitalised value of firm", "C's capital x 4", "__", "Implied total value"], ["Actual total capital", "Given", "__", "Capital after admission"], ["Hidden goodwill", "Capitalised value - actual capital", "__", "Goodwill not directly stated"]],
        "answers": [
            {"label": "Capitalised value", "value": "Rs 4,80,000"},
            {"label": "Actual capital", "value": "Rs 4,20,000"},
            {"label": "Hidden goodwill", "value": "Rs 60,000"},
        ],
        "distractors": ["Rs 30,000", "Rs 5,40,000", "Rs 1,20,000", "Rs 90,000"],
    },
]

CHANGE_RATIO = [
    {
        "title": "Sacrificing and Gaining Ratio",
        "question": "Complete the ratio table. A, B and C share 5:3:2 and will now share equally.",
        "headers": ["Partner", "Old share", "New share", "Sacrifice / gain", "Goodwill adjustment on Rs 2,40,000"],
        "rows": [["A", "5/10", "1/3", "__", "__"], ["B", "3/10", "1/3", "__", "__"], ["C", "2/10", "1/3", "__", "__"]],
        "answers": [
            {"label": "A ratio", "value": "Sacrifice 5/30"},
            {"label": "A goodwill", "value": "Credit Rs 40,000"},
            {"label": "B ratio", "value": "Gain 1/30"},
            {"label": "B goodwill", "value": "Debit Rs 8,000"},
            {"label": "C ratio", "value": "Gain 4/30"},
            {"label": "C goodwill", "value": "Debit Rs 32,000"},
        ],
        "distractors": ["Debit Rs 40,000", "Sacrifice 1/30", "Credit Rs 32,000", "Gain 5/30"],
    },
    {
        "title": "Goodwill Adjustment without Opening Goodwill Account",
        "question": "Complete the goodwill adjustment table when X, Y and Z change ratio from 3:2:1 to 2:2:2. Goodwill Rs 1,80,000.",
        "headers": ["Partner", "Old share", "New share", "Change", "Capital adjustment"],
        "rows": [["X", "3/6", "2/6", "__", "__"], ["Y", "2/6", "2/6", "__", "__"], ["Z", "1/6", "2/6", "__", "__"]],
        "answers": [
            {"label": "X change", "value": "Sacrifice 1/6"},
            {"label": "X adjustment", "value": "Credit Rs 30,000"},
            {"label": "Y change", "value": "No change"},
            {"label": "Y adjustment", "value": "No adjustment"},
            {"label": "Z change", "value": "Gain 1/6"},
            {"label": "Z adjustment", "value": "Debit Rs 30,000"},
        ],
        "distractors": ["Debit Rs 30,000", "Credit Rs 60,000", "Gain 2/6", "Sacrifice 2/6"],
    },
    {
        "title": "Existing Goodwill Written Off",
        "question": "Complete the table for writing off old goodwill of Rs 90,000 before change in ratio. Old ratio A:B:C = 4:3:2.",
        "headers": ["Partner", "Old ratio share", "Goodwill written off", "Capital account effect"],
        "rows": [["A", "4/9", "__", "__"], ["B", "3/9", "__", "__"], ["C", "2/9", "__", "__"]],
        "answers": [
            {"label": "A amount", "value": "Rs 40,000"},
            {"label": "A effect", "value": "Debit A capital"},
            {"label": "B amount", "value": "Rs 30,000"},
            {"label": "B effect", "value": "Debit B capital"},
            {"label": "C amount", "value": "Rs 20,000"},
            {"label": "C effect", "value": "Debit C capital"},
        ],
        "distractors": ["Credit A capital", "Rs 45,000", "Rs 10,000", "Revaluation A/c"],
    },
    {
        "title": "General Reserve on Change in Ratio",
        "question": "Complete the general reserve distribution table. Reserve Rs 1,20,000, old ratio 5:3:2.",
        "headers": ["Partner", "Old ratio", "Reserve share", "Treatment"],
        "rows": [["A", "5/10", "__", "__"], ["B", "3/10", "__", "__"], ["C", "2/10", "__", "__"]],
        "answers": [
            {"label": "A reserve", "value": "Rs 60,000"},
            {"label": "A treatment", "value": "Credit capital/current"},
            {"label": "B reserve", "value": "Rs 36,000"},
            {"label": "B treatment", "value": "Credit capital/current"},
            {"label": "C reserve", "value": "Rs 24,000"},
            {"label": "C treatment", "value": "Credit capital/current"},
        ],
        "distractors": ["Debit capital/current", "Rs 40,000", "Rs 30,000", "New ratio"],
    },
    {
        "title": "Accumulated Loss on Change in Ratio",
        "question": "Complete the accumulated loss table. Profit and Loss debit balance Rs 75,000, old ratio 3:2.",
        "headers": ["Partner", "Old ratio", "Loss share", "Treatment"],
        "rows": [["P", "3/5", "__", "__"], ["Q", "2/5", "__", "__"]],
        "answers": [
            {"label": "P loss", "value": "Rs 45,000"},
            {"label": "P treatment", "value": "Debit P capital"},
            {"label": "Q loss", "value": "Rs 30,000"},
            {"label": "Q treatment", "value": "Debit Q capital"},
        ],
        "distractors": ["Credit P capital", "Rs 37,500", "Rs 15,000", "New ratio"],
    },
    {
        "title": "Revaluation Profit",
        "question": "Complete the revaluation profit table. Revaluation profit Rs 48,000, old ratio A:B:C = 2:1:1.",
        "headers": ["Partner", "Old share", "Revaluation profit share", "Capital effect"],
        "rows": [["A", "2/4", "__", "__"], ["B", "1/4", "__", "__"], ["C", "1/4", "__", "__"]],
        "answers": [
            {"label": "A profit", "value": "Rs 24,000"},
            {"label": "A effect", "value": "Credit A capital"},
            {"label": "B profit", "value": "Rs 12,000"},
            {"label": "B effect", "value": "Credit B capital"},
            {"label": "C profit", "value": "Rs 12,000"},
            {"label": "C effect", "value": "Credit C capital"},
        ],
        "distractors": ["Debit A capital", "Rs 16,000", "Rs 18,000", "New ratio"],
    },
    {
        "title": "Average Profit Method for Change in Ratio",
        "question": "Complete the goodwill method table: profits Rs 70,000, Rs 90,000, Rs 1,10,000; goodwill = 2 years' purchase of average profit.",
        "headers": ["Step", "Given / formula", "Blank", "Use"],
        "rows": [["Total profit", "70,000 + 90,000 + 1,10,000", "__", "Average calculation"], ["Average profit", "Total / 3", "__", "Goodwill base"], ["Goodwill", "Average x 2", "__", "Adjustment value"]],
        "answers": [
            {"label": "Total profit", "value": "Rs 2,70,000"},
            {"label": "Average profit", "value": "Rs 90,000"},
            {"label": "Goodwill", "value": "Rs 1,80,000"},
        ],
        "distractors": ["Rs 1,35,000", "Rs 3,60,000", "Rs 80,000", "Rs 2,00,000"],
    },
    {
        "title": "Weighted Average Method for Goodwill",
        "question": "Complete the weighted average method table: profits Rs 50,000, Rs 70,000, Rs 1,00,000 with weights 1, 2, 3; goodwill at 3 years' purchase.",
        "headers": ["Year", "Profit", "Weight", "Weighted profit"],
        "rows": [["Year 1", "Rs 50,000", "1", "__"], ["Year 2", "Rs 70,000", "2", "__"], ["Year 3", "Rs 1,00,000", "3", "__"], ["Weighted average", "Total / 6", "__", "Use for goodwill"], ["Goodwill", "Weighted average x 3", "__", "Final value"]],
        "answers": [
            {"label": "Weighted 1", "value": "Rs 50,000"},
            {"label": "Weighted 2", "value": "Rs 1,40,000"},
            {"label": "Weighted 3", "value": "Rs 3,00,000"},
            {"label": "Weighted average", "value": "Rs 81,667"},
            {"label": "Goodwill", "value": "Rs 2,45,001"},
        ],
        "distractors": ["Rs 73,333", "Rs 2,20,000", "Rs 4,90,000", "Rs 2,45,000"],
    },
    {
        "title": "Super Profit Goodwill Adjustment",
        "question": "Complete the super profit method table. Average profit Rs 1,50,000; capital employed Rs 10,00,000; normal rate 12%; goodwill at 3 years' purchase.",
        "headers": ["Step", "Formula", "Blank", "Use"],
        "rows": [["Normal profit", "10,00,000 x 12%", "__", "Expected return"], ["Super profit", "1,50,000 - normal profit", "__", "Excess profit"], ["Goodwill", "Super profit x 3", "__", "Adjustment value"]],
        "answers": [
            {"label": "Normal profit", "value": "Rs 1,20,000"},
            {"label": "Super profit", "value": "Rs 30,000"},
            {"label": "Goodwill", "value": "Rs 90,000"},
        ],
        "distractors": ["Rs 1,50,000", "Rs 3,60,000", "Rs 2,70,000", "Rs 12,000"],
    },
    {
        "title": "Capitalisation of Average Profit for Goodwill",
        "question": "Complete the capitalisation table. Average profit Rs 1,25,000; normal rate 10%; actual capital Rs 10,50,000.",
        "headers": ["Step", "Formula", "Blank", "Use"],
        "rows": [["Capitalised value", "1,25,000 x 100 / 10", "__", "Value of firm"], ["Actual capital", "Given", "__", "Capital employed"], ["Goodwill", "Capitalised value - actual capital", "__", "Adjustment value"]],
        "answers": [
            {"label": "Capitalised value", "value": "Rs 12,50,000"},
            {"label": "Actual capital", "value": "Rs 10,50,000"},
            {"label": "Goodwill", "value": "Rs 2,00,000"},
        ],
        "distractors": ["Rs 1,25,000", "Rs 1,50,000", "Rs 11,75,000", "Rs 2,50,000"],
    },
    {
        "title": "Capitalisation of Super Profit for Goodwill",
        "question": "Complete the capitalisation of super profit table. Average profit Rs 1,40,000; normal profit Rs 1,00,000; normal rate 10%.",
        "headers": ["Step", "Formula", "Blank", "Use"],
        "rows": [["Super profit", "1,40,000 - 1,00,000", "__", "Excess profit"], ["Goodwill", "Super profit x 100 / 10", "__", "Adjustment value"]],
        "answers": [
            {"label": "Super profit", "value": "Rs 40,000"},
            {"label": "Goodwill", "value": "Rs 4,00,000"},
        ],
        "distractors": ["Rs 2,40,000", "Rs 1,40,000", "Rs 14,00,000", "Rs 1,00,000"],
    },
    {
        "title": "Workmen Compensation Fund",
        "question": "Complete the workmen compensation fund table. Fund Rs 60,000, claim Rs 42,000, old ratio 3:2.",
        "headers": ["Step / partner", "Amount", "Blank", "Treatment"],
        "rows": [["Claim", "Rs 42,000", "__", "Create liability"], ["Surplus fund", "60,000 - 42,000", "__", "Distribute in old ratio"], ["A share", "3/5 of surplus", "__", "Credit capital"], ["B share", "2/5 of surplus", "__", "Credit capital"]],
        "answers": [
            {"label": "Claim", "value": "Rs 42,000"},
            {"label": "Surplus", "value": "Rs 18,000"},
            {"label": "A share", "value": "Rs 10,800"},
            {"label": "B share", "value": "Rs 7,200"},
        ],
        "distractors": ["Rs 60,000", "Rs 30,000", "Rs 12,000", "Rs 6,000"],
    },
    {
        "title": "Investment Fluctuation Fund",
        "question": "Complete the investment fluctuation table. Fund Rs 25,000; investments book value Rs 1,00,000; market value Rs 82,000; old ratio 2:3.",
        "headers": ["Step / partner", "Given", "Blank", "Treatment"],
        "rows": [["Fall in investment value", "1,00,000 - 82,000", "__", "Use fund first"], ["Surplus fund", "25,000 - fall", "__", "Distribute in old ratio"], ["A share", "2/5 of surplus", "__", "Credit capital"], ["B share", "3/5 of surplus", "__", "Credit capital"]],
        "answers": [
            {"label": "Fall", "value": "Rs 18,000"},
            {"label": "Surplus", "value": "Rs 7,000"},
            {"label": "A share", "value": "Rs 2,800"},
            {"label": "B share", "value": "Rs 4,200"},
        ],
        "distractors": ["Rs 25,000", "Rs 10,000", "Rs 3,500", "Rs 5,000"],
    },
]

SPECS = [
    (
        "data/practice/class-12/accountancy-financial-accounting-1/fundamentals-of-partnership-and-goodwill-table-practice.json",
        {
            "prefix": "c12-acc-fundamentals-goodwill-table",
            "chapter": "Fundamentals of Partnership and Goodwill",
            "chapterNumber": 102,
        },
        FUNDAMENTALS,
    ),
    (
        "data/practice/class-12/accountancy-financial-accounting-1/change-in-profit-ratio-goodwill-methods-table-practice.json",
        {
            "prefix": "c12-acc-change-ratio-goodwill-table",
            "chapter": "Change in Profit Ratio - Methods of Goodwill",
            "chapterNumber": 103,
        },
        CHANGE_RATIO,
    ),
]


def upsert_catalog_entry(path: str, payload: dict[str, Any]) -> None:
    catalog_path = ROOT / "data/catalog/content-catalog.json"
    if not catalog_path.exists():
        return
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
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
        "relativePath": "Accountancy - Financial Accounting - 1\\leac101.pdf",
        "status": "active",
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


def upsert_active_entry(path: str) -> None:
    active_path = ROOT / "data/catalog/active-datasets.json"
    payload = {"activeDatasets": []}
    if active_path.exists():
        payload = json.loads(active_path.read_text(encoding="utf-8"))
    entry = {
        "id": path.removesuffix(".json"),
        "jsonPath": path,
        "status": "active",
        "approvedBy": "accountancy-topic-table-build",
        "notes": "Class 12 Accountancy topic-wise numerical table practice with direct table drag/drop.",
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
    for relative, chapter, specs in SPECS:
        payload = dataset(chapter, specs, relative)
        output_path = ROOT / relative
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        upsert_catalog_entry(relative, payload)
        upsert_active_entry(relative)
        print(f"Wrote {relative} ({len(payload['activities'])} table activities)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
