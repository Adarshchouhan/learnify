from __future__ import annotations

import json
import re
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

QUESTION_TYPES = [
    "explain",
    "compare_contrast",
    "cause_effect",
    "process_sequence",
    "pros_cons",
    "problem_solution",
    "fill_blanks",
    "true_false_not_given",
    "short_answer_key_points",
    "match_following",
    "data_chart_table",
    "paragraph_essay_structure",
    "definition_term",
    "timeline_chronological_order",
    "identify_main_idea",
    "evidence_support_statement",
    "sequencing_steps_process",
    "choose_correct_ending",
    "multiple_correct_answers",
    "formulate_question",
    "assertion_reason",
]

STANDARD_QUESTION_ROUNDS = 3

COMMON_RUBRIC = [
    {"criterion": "Accurate Class 12 concept", "marks": 2},
    {"criterion": "Logical answer structure", "marks": 1},
    {"criterion": "Relevant commerce terminology", "marks": 1},
    {"criterion": "Application or conclusion without distractors", "marks": 1},
]

QUESTION_DESIGN_REFERENCES = [
    {
        "title": "CBSE Class XII Sample Question Paper and Marking Scheme 2025-26",
        "url": "https://cbseacademic.nic.in/sqp_classxii_2025-26.html",
    },
    {
        "title": "CBSE Previous Years' Question Papers for Class XII",
        "url": "https://www.cbse.gov.in/cbsenew/question-paper.html",
    },
    {
        "title": "CBSE Question Bank Class XII",
        "url": "https://cbseacademic.nic.in/qbclass12.html",
    },
    {
        "title": "CBSE Accountancy Class XII SQP 2025-26",
        "url": "https://cbseacademic.nic.in/web_material/SQP/ClassXII_2025_26/Accountancy-SQP.pdf",
    },
    {
        "title": "CBSE Economics Class XII SQP 2025-26",
        "url": "https://cbseacademic.nic.in/web_material/SQP/ClassXII_2025_26/Economics-SQP.pdf",
    },
    {
        "title": "CBSE Business Studies Class XII Marking Scheme 2025-26",
        "url": "https://cbseacademic.nic.in/web_material/SQP/ClassXII_2025_26/BusinessStudies-MS.pdf",
    },
]

PREVIOUS_YEAR_STYLE_NOTE = (
    "Questions are original Learnify practice items modelled on CBSE Class XII "
    "previous-year and sample-paper patterns: competency-based cases, tables, "
    "assertion-reason, source/data interpretation and short analytical answers."
)


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "item"


def chunk(item_id: str, text: str, order: int | None = None, section: str | None = None) -> dict[str, Any]:
    item: dict[str, Any] = {"id": item_id, "text": text}
    if order is not None:
        item["order"] = order
    if section:
        item["section"] = section
    return item


def distractor(item_id: str, text: str) -> dict[str, str]:
    return {"id": item_id, "text": text, "misconception": "Looks relevant but is not accepted for this answer."}


def evidence_support_activity(meta: dict[str, Any], topic: dict[str, Any], index: int, prefix: str) -> dict[str, Any]:
    points = topic["points"]
    claim = points[0].rstrip(".")
    evidence = points[1].rstrip(".") if len(points) > 1 else topic["title"].rstrip(".")
    context = points[2].rstrip(".") if len(points) > 2 else meta["chapter"].rstrip(".")
    correct = [
        chunk(f"{prefix}-c1", f"Claim: {claim}.", 1),
        chunk(f"{prefix}-c2", f"Evidence: {evidence}.", 2),
        chunk(f"{prefix}-c3", "Support: this evidence is specific and directly proves the claim.", 3),
        chunk(f"{prefix}-c4", f"Link: {context}.", 4),
    ]
    wrong = [
        distractor(f"{prefix}-x1", f"Repeat only: {claim}."),
        distractor(f"{prefix}-x2", f"Unclear support: {context}."),
        distractor(f"{prefix}-x3", "No evidence is needed because the claim is already obvious."),
        distractor(f"{prefix}-x4", "A strong answer can ignore the link between claim and evidence."),
    ]
    return base_activity(
        activity_id=prefix,
        activity_type="evidence_support_statement",
        difficulty="standard",
        meta=meta,
        marks=4,
        question=(
            "Quiz & Worksheet - Evidence and Support\n"
            f"Claim: {claim}.\n"
            f"Evidence: {evidence}.\n\n"
            "Build the full evidence-support answer by selecting the correct parts in order."
        ),
        instructions="Click the correct parts in order. They will join into one answer. Leave the wrong lines outside.",
        structure_help=["Claim", "Evidence", "Support", "Link"],
        correct_items=correct,
        distractors=wrong,
        answer_slots=[{"id": "answer", "label": "Answer"}],
        answer_key={"orderedItemIds": [item["id"] for item in correct]},
        model_answer=" ".join(item["text"] for item in correct),
        hints=["Select the claim, evidence, support and link in order.", "Do not use lines that only repeat or avoid evidence."],
        correct_sequence=[item["id"] for item in correct],
    )


def base_activity(
    *,
    activity_id: str,
    activity_type: str,
    difficulty: str,
    meta: dict[str, Any],
    marks: int,
    question: str,
    instructions: str,
    structure_help: list[str],
    correct_items: list[dict[str, Any]],
    distractors: list[dict[str, Any]],
    answer_slots: list[dict[str, Any]],
    answer_key: dict[str, Any],
    model_answer: str,
    hints: list[str],
    question_group_id: str | None = None,
    chapter_question_number: int | None = None,
    correct_sequence: list[str] | None = None,
) -> dict[str, Any]:
    activity: dict[str, Any] = {
        "id": activity_id,
        "type": activity_type,
        "difficulty": difficulty,
        "classLevel": meta["classLevel"],
        "stream": meta.get("stream"),
        "subject": meta["subject"],
        "book": meta["book"],
        "chapter": meta["chapter"],
        "chapterNumber": meta["chapterNumber"],
        "marks": marks,
        "question": question,
        "instructions": instructions,
        "structureHelp": structure_help,
        "sourceTextSummary": f"Class 12 Commerce board-style practice for {meta['book']}: {meta['chapter']}.",
        "sourceChapter": meta["chapter"],
        "sourcePdf": meta["pdfPath"],
        "correctItems": correct_items,
        "distractors": distractors,
        "answerSlots": answer_slots,
        "answerKey": answer_key,
        "hints": hints,
        "modelAnswer": model_answer,
        "scoringRubric": COMMON_RUBRIC,
    }
    if question_group_id:
        activity["questionGroupId"] = question_group_id
    if chapter_question_number is not None:
        activity["chapterQuestionNumber"] = chapter_question_number
    if correct_sequence:
        activity["correctSequence"] = correct_sequence
    return activity


def split_clause(sentence: str) -> tuple[str, str]:
    words = sentence.split()
    midpoint = max(3, len(words) // 2)
    return " ".join(words[:midpoint]), " ".join(words[midpoint:])


def make_answer_builder(meta: dict[str, Any], topic: dict[str, Any], number: int) -> list[dict[str, Any]]:
    prefix = f"c12-{slugify(meta['subject'])}-{meta['chapterNumber']}-q{number:02d}"
    group_id = f"chapter-q{number:02d}-{slugify(topic['title'])}"
    points = topic["points"]
    distractors = [distractor(f"{prefix}-x{i}", text) for i, text in enumerate(topic["distractors"], start=1)]
    scenario = topic.get("case", f"A Class 12 Commerce student is revising {topic['title']} for a board-style answer.")

    easy_items = [chunk(f"{prefix}-easy-{i}", text, i, label) for i, (text, label) in enumerate(zip(points[:4], ["Concept", "Reason", "Application", "Conclusion"]), start=1)]
    easy_ids = [item["id"] for item in easy_items]

    moderate_parts: list[dict[str, Any]] = []
    for index, sentence in enumerate(points[:4], start=1):
        first, second = split_clause(sentence)
        moderate_parts.append(chunk(f"{prefix}-moderate-{index}a", first, index * 2 - 1))
        moderate_parts.append(chunk(f"{prefix}-moderate-{index}b", second, index * 2))
    moderate_ids = [item["id"] for item in moderate_parts]

    difficult_phrases = topic.get("phrases") or [
        topic["title"],
        "board-style application",
        "reasoned analysis",
        "financial or managerial implication",
        "exam conclusion",
    ]
    difficult_items = [chunk(f"{prefix}-difficult-{i}", text, i) for i, text in enumerate(difficult_phrases[:6], start=1)]

    return [
        base_activity(
            activity_id=f"{prefix}-easy-answer-builder",
            activity_type="answer_builder",
            difficulty="easy",
            meta=meta,
            marks=3,
            question=f"Build a direct Class 12 answer: {topic['easyQuestion']}",
            instructions="Arrange full answer sentences in the correct order.",
            structure_help=["Concept", "Reason", "Application", "Conclusion"],
            correct_items=easy_items,
            distractors=distractors,
            answer_slots=[{"id": f"slot-{i}", "label": label} for i, label in enumerate(["Concept", "Reason", "Application", "Conclusion"], start=1)],
            answer_key={"orderedItemIds": easy_ids},
            model_answer=" ".join(points[:4]),
            hints=["Start with the concept.", "Add a reason, then the exam-relevant application."],
            question_group_id=group_id,
            chapter_question_number=number,
            correct_sequence=easy_ids,
        ),
        base_activity(
            activity_id=f"{prefix}-moderate-answer-builder",
            activity_type="answer_builder",
            difficulty="moderate",
            meta=meta,
            marks=4,
            question=f"Build an analytical answer: {topic['moderateQuestion']}",
            instructions="Pair half-sentence chunks and arrange them into a coherent 4-mark answer.",
            structure_help=["Opening", "Explanation", "Application", "Conclusion"],
            correct_items=moderate_parts,
            distractors=distractors,
            answer_slots=[{"id": f"slot-{i}", "label": f"Part {i}"} for i in range(1, len(moderate_parts) + 1)],
            answer_key={"orderedItemIds": moderate_ids},
            model_answer=" ".join(points[:4]),
            hints=["Look for halves that complete one idea.", "Keep the reasoning in board-answer order."],
            question_group_id=group_id,
            chapter_question_number=number,
            correct_sequence=moderate_ids,
        ),
        base_activity(
            activity_id=f"{prefix}-difficult-answer-builder",
            activity_type="answer_builder",
            difficulty="difficult",
            meta=meta,
            marks=6,
            question=f"Apply the concept in a case: {scenario} What should the answer include?",
            instructions="Select all essential key phrases and leave the misleading options out.",
            structure_help=["Identify", "Analyse", "Apply", "Conclude"],
            correct_items=difficult_items,
            distractors=distractors,
            answer_slots=[
                {"id": "identify", "label": "Identify concept"},
                {"id": "analyse", "label": "Analyse"},
                {"id": "apply", "label": "Apply"},
                {"id": "conclude", "label": "Conclusion"},
            ],
            answer_key={"requiredConceptIds": [item["id"] for item in difficult_items]},
            model_answer=" ".join(points),
            hints=["Use Class 12 keywords.", "Connect the fact with the situation before concluding."],
            question_group_id=group_id,
            chapter_question_number=number,
            correct_sequence=[item["id"] for item in difficult_items],
        ),
    ]


def standard_activity(meta: dict[str, Any], topic: dict[str, Any], activity_type: str, index: int) -> dict[str, Any]:
    prefix = f"c12-{slugify(meta['subject'])}-{meta['chapterNumber']}-{activity_type}-{index:02d}"
    points = topic["points"]
    if activity_type == "evidence_support_statement":
        return evidence_support_activity(meta, topic, index, prefix)

    correct = [chunk(f"{prefix}-c{i}", text, i) for i, text in enumerate(points[:4], start=1)]
    wrong = [distractor(f"{prefix}-x{i}", text) for i, text in enumerate(topic["distractors"][:2], start=1)]
    slots = [{"id": "answer", "label": "Answer"}]
    key: dict[str, Any] = {"requiredItemIds": [item["id"] for item in correct]}
    question = f"Use {meta['chapter']} to answer: {topic['easyQuestion']}"
    structure = ["Point 1", "Point 2", "Point 3", "Point 4"]

    if activity_type in {"explain", "definition_term"}:
        wrong = [distractor(f"{prefix}-x{i}", text) for i, text in enumerate(topic["distractors"][:3], start=1)]
        wrong.extend(
            [
                distractor(f"{prefix}-x4", "Only a copied keyword is enough for full marks."),
                distractor(f"{prefix}-x5", "A correct answer can ignore the order of ideas."),
            ]
        )
        slots = [{"id": "answer", "label": "Answer"}]
        key = {"orderedItemIds": [item["id"] for item in correct]}
        question = f"Use {meta['chapter']} to answer: {topic['easyQuestion']}"
        structure = ["Definition", "Key point", "Support", "Conclusion"] if activity_type == "definition_term" else ["Opening", "Key point", "Support", "Conclusion"]
    elif activity_type in {"process_sequence", "sequencing_steps_process", "timeline_chronological_order", "paragraph_essay_structure", "fill_blanks"}:
        slots = [{"id": f"slot-{i}", "label": label} for i, label in enumerate(["Start", "Develop", "Apply", "Conclude"], start=1)]
        key = {"orderedItemIds": [item["id"] for item in correct]}
        question = f"Arrange the answer sequence for: {topic['moderateQuestion']}"
    elif activity_type == "compare_contrast":
        slots = [{"id": "basis-a", "label": "Idea A"}, {"id": "basis-b", "label": "Idea B"}, {"id": "conclusion", "label": "Conclusion"}]
        question = f"Compare related ideas in {topic['title']}."
        structure = ["Basis", "Difference", "Link", "Conclusion"]
    elif activity_type == "cause_effect":
        key = {"pairs": [[correct[0]["id"], correct[1]["id"]], [correct[2]["id"], correct[3]["id"]]]}
        question = f"Connect cause and effect for {topic['title']}."
    elif activity_type == "assertion_reason":
        question = f"Build an assertion-reason response on {topic['title']}."
        structure = ["Assertion", "Reason", "Relationship"]
    elif activity_type == "data_chart_table":
        question = f"Interpret a small business/accounting/economics data point related to {topic['title']}."
        structure = ["Data", "Meaning", "Inference", "Conclusion"]
        if topic.get("table"):
            question = topic["table"]["question"]
    elif activity_type == "formulate_question":
        question = f"Formulate the board-style question that this answer would solve: {points[0]}"
        structure = ["Question stem", "Command word", "Scope"]
    elif activity_type == "multiple_correct_answers":
        question = f"Select all valid statements about {topic['title']}."
    elif activity_type == "true_false_not_given":
        question = f"Classify statements using the concept of {topic['title']}."

    activity = base_activity(
        activity_id=prefix,
        activity_type=activity_type,
        difficulty="standard",
        meta=meta,
        marks=4 if activity_type not in {"definition_term", "identify_main_idea"} else 3,
        question=question,
        instructions="Click the correct parts in order. They will join into one answer. Leave the wrong lines outside."
        if activity_type in {"explain", "definition_term"}
        else "Choose only the options supported by the chapter and arrange them where needed.",
        structure_help=structure,
        correct_items=correct,
        distractors=wrong,
        answer_slots=slots,
        answer_key=key,
        model_answer=" ".join(points[:4]),
        hints=["Use precise Class 12 terminology.", "Reject options that overstate or contradict the concept."],
        correct_sequence=key.get("orderedItemIds"),
    )
    if activity_type == "data_chart_table" and topic.get("table"):
        activity["tableData"] = topic["table"]
        activity["questionStyle"] = "previous-year-board-table-case-inspired"
    if activity_type in {"data_chart_table", "assertion_reason", "case_study"}:
        activity["questionDesignNote"] = PREVIOUS_YEAR_STYLE_NOTE
    return activity


def topic_table(meta: dict[str, Any], topic: dict[str, Any], serial: int) -> dict[str, Any]:
    subject = meta["subject"]
    points = topic["points"]
    if subject == "Accountancy":
        headers = ["Accounting item", "Amount / Status", "Student working space", "Treatment / Reason"]
        rows = [
            [topic["title"].title(), "Given in question", "Calculate / classify here: ________", points[0]],
            ["Adjustment", "Use the adjustment figure", "Working: ________", points[1]],
            ["Report impact", "Transfer to final statement", "Amount to post: ________", points[2]],
            ["Control/check", "Recheck debit-credit effect", "Final balance / reason: ________", points[3]],
        ]
        input_answers = {
            "table-blank-0-2": ["correct calculation", "correct classification", "calculated amount"],
            "table-blank-1-2": ["working shown", "correct working", "calculation shown"],
            "table-blank-2-2": ["amount posted", "correct amount", "posted amount"],
            "table-blank-3-2": ["balance verified", "correct reason", "final balance checked"],
        }
    elif subject == "Business Studies":
        headers = ["Business situation", "Concept", "Managerial implication"]
        rows = [
            [f"Situation {serial}A", topic["title"].title(), points[0]],
            ["Managerial response", "Application", points[1]],
            ["Expected result", "Outcome", points[2]],
            ["Exam focus", "Justification", points[3]],
        ]
    elif subject == "Economics":
        headers = ["Indicator", "Observation", "Economic inference"]
        rows = [
            ["Concept", topic["title"].title(), points[0]],
            ["Change 1", "Variable changes", points[1]],
            ["Change 2", "Related effect", points[2]],
            ["Conclusion", "Policy/market meaning", points[3]],
        ]
    else:
        headers = ["Evidence/feature", "Meaning", "Use in answer"]
        rows = [
            [topic["title"].title(), points[0], "Opening idea"],
            ["Textual/writing clue", points[1], "Support"],
            ["Interpretation", points[2], "Analysis"],
            ["Conclusion", points[3], "Final response"],
        ]
    return {
        "title": f"{topic['title']} table practice",
        "headers": headers,
        "rows": rows,
        **({"inputAnswers": input_answers} if subject == "Accountancy" else {}),
        "question": f"Study the table on {topic['title']} and choose the best board-style interpretation.",
    }


def table_activity(meta: dict[str, Any], topic: dict[str, Any], index: int) -> dict[str, Any]:
    table = topic.get("table") or topic_table(meta, topic, index)
    table_topic_payload = {
        **topic,
        "table": table,
        "easyQuestion": table["question"],
        "moderateQuestion": f"Analyse the table on {topic['title']} and write a reasoned Class 12 answer.",
        "points": [
            f"The table is about {topic['title']} and must be interpreted, not copied.",
            topic["points"][0],
            topic["points"][1],
            topic["points"][2],
            "A complete answer links the table evidence with the correct commerce concept.",
        ],
        "distractors": [
            "Copy the table headings without interpretation.",
            "Ignore the given figures or situations.",
            "Write an unrelated definition that does not use the table.",
        ],
    }
    return standard_activity(meta, table_topic_payload, "data_chart_table", index)


def expanded_topics(topics: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for topic in topics:
        result.append(topic)
        result.append(
            {
                **topic,
                "title": f"{topic['title']} case application",
                "easyQuestion": f"List the essential board-answer points for {topic['title']}.",
                "moderateQuestion": f"Apply {topic['title']} to a practical Class 12 Commerce situation.",
                "case": f"An examiner frames a competency-based question on {topic['title']}. Build a precise answer with concept, reason and implication.",
                "points": [
                    topic["points"][0],
                    topic["points"][1],
                    topic["points"][2],
                    "In a case answer, connect the concept with the given business or economic situation.",
                    topic["points"][-1],
                ],
                "phrases": [
                    topic["title"],
                    "concept identification",
                    "case evidence",
                    "reasoned application",
                    "commerce terminology",
                    "exam conclusion",
                ],
            }
        )
        result.append(
            {
                **topic,
                "title": f"{topic['title']} calculation and data drill",
                "easyQuestion": f"Use a calculation/data table to answer a board-style question on {topic['title']}.",
                "moderateQuestion": f"Interpret figures or case data connected with {topic['title']} and present the working.",
                "case": f"A Class 12 Commerce paper gives data for {topic['title']} with blanks for working. Complete the calculation, interpretation and conclusion.",
                "points": [
                    topic["points"][0],
                    "Read the given data, table headings and command word before writing the answer.",
                    "Show the required calculation, classification or matching step clearly.",
                    topic["points"][1],
                    "Conclude with the exact treatment, concept or inference asked in the question.",
                ],
                "distractors": [
                    "Skip the working space and write only a memorised definition.",
                    "Use figures from a different row of the table.",
                    "Treat every debit balance as a liability and every credit balance as an asset.",
                ],
                "phrases": [
                    topic["title"],
                    "given data",
                    "student working",
                    "calculation step",
                    "correct treatment",
                    "board-style conclusion",
                ],
            }
        )
    return result


def table_topic(meta: dict[str, Any]) -> dict[str, Any]:
    subject = meta["subject"]
    if subject == "Accountancy":
        if meta["chapterNumber"] == 101:
            table = {
                "title": "Partnership balance sheet calculation table",
                "headers": ["Liabilities / Assets item", "Amount Rs", "Student calculation space", "Accounting treatment"],
                "rows": [
                    ["Partners' capital: A, B and C", "1,80,000; 1,50,000; 1,20,000", "Total capital: ________", "Show under capital accounts or partners' capital"],
                    ["Current accounts: A debit, B credit", "6,000 debit; 9,000 credit", "Net current account effect: ________", "Debit balance appears on assets side, credit balance on liabilities side"],
                    ["General reserve to be distributed", "30,000; ratio 3:2:1", "A: ________ B: ________ C: ________", "Credit partners' capital or current accounts in old ratio"],
                    ["Revaluation profit", "18,000; ratio 3:2:1", "A: ________ B: ________ C: ________", "Transfer profit to partners' capital/current accounts"],
                    ["Balance sheet total check", "Assets and liabilities after adjustments", "Both sides total: ________", "Final totals must agree after all postings"],
                ],
                "inputAnswers": {
                    "table-blank-0-2": ["450000", "4 50 000", "4,50,000", "rs 450000"],
                    "table-blank-1-2": ["3000 credit", "credit 3000", "net credit 3000", "rs 3000 credit"],
                    "table-blank-2-2": ["a 15000 b 10000 c 5000", "15000 10000 5000", "a:15000 b:10000 c:5000"],
                    "table-blank-3-2": ["a 9000 b 6000 c 3000", "9000 6000 3000", "a:9000 b:6000 c:3000"],
                    "table-blank-4-2": ["both sides agree", "assets equal liabilities", "balanced"],
                },
                "question": "Complete the partnership balance sheet working table: calculate partner-wise reserve/revaluation shares and identify where debit/credit current balances appear.",
            }
        elif meta["chapterNumber"] == 201:
            table = {
                "title": "Company accounts and analysis calculation table",
                "headers": ["Company accounts item", "Amount Rs", "Student calculation space", "Accounting treatment"],
                "rows": [
                    ["Equity shares issued", "20,000 shares at Rs 10, Rs 8 called", "Called-up capital: ________", "Show called-up amount under share capital"],
                    ["Calls in arrears", "1,200", "Paid-up capital: ________", "Deduct from called-up share capital"],
                    ["Securities premium", "Rs 2 per share on 20,000 shares", "Premium amount: ________", "Show under reserves and surplus"],
                    ["Current ratio data", "Current assets Rs 4,80,000; current liabilities Rs 2,40,000", "Current ratio: ________", "Use current assets divided by current liabilities"],
                    ["Debt-equity data", "Debt Rs 3,00,000; equity Rs 6,00,000", "Debt-equity ratio: ________", "Use debt divided by shareholders' funds"],
                ],
                "inputAnswers": {
                    "table-blank-0-2": ["160000", "1 60 000", "1,60,000", "rs 160000"],
                    "table-blank-1-2": ["158800", "1 58 800", "1,58,800", "rs 158800"],
                    "table-blank-2-2": ["40000", "40 000", "40,000", "rs 40000"],
                    "table-blank-3-2": ["2:1", "2", "2 to 1"],
                    "table-blank-4-2": ["0.5:1", "0.5", "1:2", "0.5 to 1"],
                },
                "question": "Complete the company accounts table by calculating share capital, premium and ratios in the blank working spaces.",
            }
        else:
            table = {
                "title": "Computerised accounting calculation and control table",
                "headers": ["Accounting software item", "Given data", "Student calculation / check space", "Accounting treatment"],
                "rows": [
                    ["Voucher total", "Debit Rs 18,500; credit Rs 17,900", "Difference to trace: ________", "Voucher should not be posted until debit equals credit"],
                    ["GST field", "Taxable value Rs 50,000; GST 18%", "GST amount: ________", "Validate tax calculation before posting"],
                    ["Receivable ageing", "Invoice Rs 24,000 unpaid for 62 days", "Ageing bucket: ________", "Classify for collection follow-up"],
                    ["Bank reconciliation", "Book balance Rs 80,000; unpresented cheque Rs 12,000", "Adjusted balance: ________", "Use reconciliation logic before reporting cash position"],
                    ["Access control", "Cashier requests master-data edit rights", "Approval needed: ________", "Restrict rights according to role and segregation of duties"],
                ],
                "inputAnswers": {
                    "table-blank-0-2": ["600", "rs 600"],
                    "table-blank-1-2": ["9000", "9 000", "9,000", "rs 9000"],
                    "table-blank-2-2": ["60 plus days", "over 60 days", "61-90 days", "62 days"],
                    "table-blank-3-2": ["68000", "68 000", "68,000", "rs 68000"],
                    "table-blank-4-2": ["manager approval", "authorised approval", "admin approval", "supervisor approval"],
                },
                "question": "Use the computerised accounting table to calculate missing checks and decide the correct control treatment.",
            }
        points = [
            "The table should be analysed item by item before filling the calculation space.",
            "Each blank requires the student to compute or classify the accounting effect.",
            "Debit and credit effects must be posted to the correct side or account.",
            "The answer must show working before giving the final treatment.",
            "This is a board-style calculation table task, not a memorised definition question.",
        ]
    elif subject == "Business Studies":
        table = {
            "title": "Business Studies case table",
            "headers": ["Situation", "Management concept", "Expected action"],
            "rows": [
                ["Sales targets missed", "Controlling", "Compare actual with standards"],
                ["Departments working separately", "Coordination", "Integrate efforts"],
                ["New product launch", "Planning", "Set objectives and strategy"],
                ["Employee skill gap", "Staffing", "Train or recruit suitable people"],
            ],
            "question": "Read the management case table and match each situation with the correct concept.",
        }
        points = [
            "Each situation must be linked with the relevant management function or concept.",
            "Missed targets indicate controlling because actual performance is compared with standards.",
            "Separate departmental efforts show the need for coordination.",
            "Skill gaps are solved through staffing activities such as training or recruitment.",
            "The answer should justify the concept, not only name it.",
        ]
    elif subject == "Economics":
        table = {
            "title": "Economics data table",
            "headers": ["Income (Rs crore)", "Consumption (Rs crore)", "Saving (Rs crore)"],
            "rows": [
                ["0", "40", "-40"],
                ["100", "120", "-20"],
                ["200", "200", "0"],
                ["300", "280", "20"],
            ],
            "question": "Use the income-consumption table to infer saving and break-even income.",
        }
        points = [
            "The table shows consumption, saving and income relationship.",
            "Saving is income minus consumption.",
            "Break-even income occurs where saving is zero.",
            "Here break-even income is Rs 200 crore because income equals consumption.",
            "The answer should explain the calculation and the economic meaning.",
        ]
    else:
        table = {
            "title": "English evidence table",
            "headers": ["Evidence", "What it suggests", "Answer use"],
            "rows": [
                ["Repeated image of silence", "Isolation or hesitation", "Theme support"],
                ["Contrast between hope and fear", "Internal conflict", "Character analysis"],
                ["Formal public tone", "Purposeful communication", "Writing task style"],
                ["Specific incident from text", "Concrete evidence", "Long-answer support"],
            ],
            "question": "Use the evidence table to build a literature or writing-skills answer.",
        }
        points = [
            "A table-based English answer should convert evidence into interpretation.",
            "The evidence must be connected with the theme, character or writing purpose.",
            "Unsupported summary should be avoided.",
            "A board-style answer uses concise explanation after each evidence point.",
            "The conclusion should directly answer the question.",
        ]
    return make_topic(
        table["title"],
        table["question"],
        f"Analyse the table and write a board-style answer for {meta['chapter']}.",
        f"A previous-year style question gives a table from {meta['subject']} and asks for interpretation.",
        points,
        [
            "Copy the table without explaining it.",
            "Ignore the figures or concepts given in the table.",
            "Write an unrelated definition instead of interpreting the data.",
        ],
        ["table reading", "data interpretation", "concept identification", "calculation or matching", "board-style inference", "conclusion"],
    ) | {"table": table}


def dataset(meta: dict[str, Any], topics: list[dict[str, Any]], output_path: Path) -> dict[str, Any]:
    subject_table_topic = table_topic(meta)
    topics = topics + [subject_table_topic]
    topics = expanded_topics(topics)
    activities: list[dict[str, Any]] = []
    for number, topic in enumerate(topics, start=1):
        activities.extend(make_answer_builder(meta, topic, number))
    standard_index = 1
    for round_number in range(STANDARD_QUESTION_ROUNDS):
        for activity_type in QUESTION_TYPES:
            topic_index = (standard_index + round_number - 1) % len(topics)
            activities.append(standard_activity(meta, topics[topic_index], activity_type, standard_index))
            standard_index += 1
    for table_index, topic in enumerate(topics, start=standard_index):
        activities.append(table_activity(meta, topic, table_index))

    chapter_questions = [
        {
            "number": index,
            "groupId": f"chapter-q{index:02d}-{slugify(topic['title'])}",
            "question": topic["easyQuestion"],
            "questionIdentifier": {
                "label": "Class 12 Commerce Answer Builder",
                "primaryType": "answer_builder",
                "slotStrategy": "difficulty-specific-answer-construction",
                "layout": "easy full sentences, moderate half sentences, difficult case phrases",
                "id": "commerce_answer_builder",
            },
        }
        for index, topic in enumerate(topics, start=1)
    ]
    return {
        "version": 2,
        "generatedBy": "scripts/generate_class12_commerce_practice.py",
        "generatedAt": int(time.time()),
        "source": {
            **meta,
            "pageCount": None,
            "extractedCharacterCount": None,
            "extractionPreview": f"Board-style practice generated for {meta['book']}, {meta['chapter']}.",
            "questionDesignReferences": QUESTION_DESIGN_REFERENCES,
            "previousYearStyleNote": PREVIOUS_YEAR_STYLE_NOTE,
        },
        "coverage": {
            "classes": [12],
            "streams": ["Commerce"],
            "questionTypeCount": len(QUESTION_TYPES),
            "standardQuestionRounds": STANDARD_QUESTION_ROUNDS,
            "answerBuilderModes": ["easy", "moderate", "difficult"],
            "activityCount": len(activities),
            "chapterQuestionCount": len(chapter_questions),
            "generationMode": "class-12-commerce-board-style-v2",
        },
        "chapterQuestions": chapter_questions,
        "activities": activities,
    }


def make_topic(title: str, easy: str, moderate: str, case: str, points: list[str], distractors: list[str], phrases: list[str] | None = None) -> dict[str, Any]:
    return {
        "title": title,
        "easyQuestion": easy,
        "moderateQuestion": moderate,
        "case": case,
        "points": points,
        "distractors": distractors,
        "phrases": phrases,
    }


ACCOUNTING_SOFTWARE = [
    make_topic("data validation", "Why is data validation important in accounting software?", "How does validation improve reliability of accounting reports?", "A firm finds wrong GST and ledger codes in vouchers entered by trainees.", ["Data validation checks whether entered values follow predefined rules.", "It reduces posting errors, wrong codes and incomplete vouchers.", "Reliable validation improves ledgers, trial balance and financial statements.", "It supports internal control but does not replace human review.", "A good answer should mention accuracy, reliability and control."], ["It deletes all transactions automatically.", "It proves that every transaction is legal.", "It removes the need for audit evidence."], ["validation rules", "posting accuracy", "reliable ledgers", "internal control", "human review", "audit trail"]),
    make_topic("accounting information system", "What is an accounting information system?", "Explain how AIS converts business transactions into useful reports.", "A retail store wants daily sales, inventory and receivable reports from one system.", ["An accounting information system collects, processes and stores financial data.", "It records transactions through vouchers, journals and ledgers.", "It produces summaries such as trial balance, reports and statements.", "The usefulness depends on correct data, controls and relevant report design.", "AIS links accounting records with managerial decision-making."], ["AIS records only cash purchases.", "AIS is useful only after final accounts are prepared.", "AIS hides information from managers."], ["collect data", "process vouchers", "store ledgers", "produce reports", "managerial decisions", "controls"]),
    make_topic("report generation", "How does accounting software support decision-making?", "Explain the role of generated reports in performance analysis.", "Management asks for receivable ageing, cash position and sales trend before a credit policy meeting.", ["Accounting software organises transactions in a database.", "It generates timely reports such as ledgers, ageing schedules and statements.", "Managers compare reports to identify trends, variances and risk areas.", "Decisions improve when reports are accurate, relevant and timely.", "Reports support judgement but do not make business decisions by themselves."], ["It records only non-cash transactions.", "It hides financial information from users.", "It makes judgement unnecessary."], ["database", "timely reports", "trend analysis", "variance analysis", "relevance", "managerial judgement"]),
    make_topic("security and access control", "Why are passwords and access rights needed in accounting software?", "Analyse how access control protects accounting data.", "A cashier can edit supplier master data and payment vouchers without approval.", ["Access control restricts users to authorised functions.", "It protects confidential accounting data from misuse or unauthorised changes.", "Segregation of duties reduces the risk of fraud and error.", "Audit trails help trace who entered or changed information.", "Strong security includes passwords, roles, backups and review."], ["Every employee should get administrator rights.", "Passwords remove the need for backups.", "Audit trails are useful only for sales invoices."], ["authorised access", "confidential data", "segregation of duties", "audit trail", "fraud prevention", "backup"]),
    make_topic("backup and recovery", "Why should accounting data be backed up?", "Explain backup and recovery as a control in computerised accounting.", "A system crash happens one day before final accounts are to be prepared.", ["Backup creates a copy of accounting data for protection.", "Recovery restores records after system failure, corruption or accidental loss.", "Regular backups reduce disruption in reporting and compliance work.", "Backup controls must be tested and stored securely.", "They support continuity but cannot correct wrong original entries."], ["Backup means deleting old vouchers.", "Recovery creates new sales automatically.", "Backups replace all internal controls."], ["data backup", "disaster recovery", "business continuity", "secure storage", "testing", "reporting continuity"]),
    make_topic("audit trail", "What is an audit trail in accounting software?", "How does an audit trail strengthen accountability?", "The owner wants to know who changed a purchase voucher after approval.", ["An audit trail records the sequence of accounting actions in the system.", "It can show user identity, date, time and nature of changes.", "This improves accountability and supports verification.", "It discourages unauthorised alteration of accounting records.", "An audit trail is useful only when reviewed and protected from tampering."], ["It is a decorative report.", "It removes the need to record transactions.", "It changes wrong balances automatically."], ["sequence of actions", "user identity", "date and time", "verification", "accountability", "tamper protection"]),
    make_topic("voucher entry controls", "How do voucher entry controls improve accounting accuracy?", "Explain the importance of voucher controls in a computerised system.", "Sales invoices are posted without customer codes and tax classifications.", ["Voucher controls ensure important fields are complete before posting.", "They link transactions with accounts, parties and tax details.", "They reduce incomplete, duplicate or misclassified entries.", "Correct voucher design improves reports and statutory compliance.", "Controls need periodic review when business rules change."], ["Voucher controls stop all credit sales.", "They are needed only in manual accounting.", "They prepare bank reconciliation automatically."], ["complete fields", "party codes", "tax details", "duplicate check", "compliance", "periodic review"]),
    make_topic("limitations of computerised accounting", "State limitations of computerised accounting systems.", "Why can computerised accounting still produce wrong results?", "A company relies on software reports even though opening balances were entered wrongly.", ["Computerised accounting depends on accurate input data.", "Wrong configuration or master data can produce misleading reports.", "Technical failure, cyber risk and unauthorised access are possible limitations.", "Users still need accounting knowledge to interpret outputs.", "The system improves speed but not the truthfulness of incorrect input."], ["Software guarantees profit.", "Computerised systems never require trained users.", "All errors are impossible after automation."], ["input accuracy", "configuration risk", "cyber risk", "trained users", "interpretation", "misleading output"]),
]

PARTNERSHIP = [
    make_topic("partnership deed", "Why is a partnership deed important?", "Explain how a deed prevents disputes among partners.", "Two partners disagree about interest on drawings because no written terms exist.", ["A partnership deed records the agreed terms among partners.", "It may specify profit sharing, interest, salary, drawings and admission terms.", "Written terms reduce ambiguity and disputes.", "In absence of agreement, Partnership Act provisions may apply.", "The deed supports fair accounting treatment among partners."], ["A deed is needed only for companies.", "It fixes market price of goods.", "It removes the need to maintain capital accounts."], ["written agreement", "profit sharing ratio", "interest and salary", "drawings", "Partnership Act", "fair accounting"]),
    make_topic("fixed and fluctuating capital", "Differentiate fixed and fluctuating capital accounts.", "How does the capital method affect partner account presentation?", "A firm changes from fluctuating capital to fixed capital for clearer reporting.", ["Under fixed capital, partner capital normally remains unchanged.", "Adjustments such as salary, interest and drawings go to current accounts.", "Under fluctuating capital, all such adjustments affect capital accounts directly.", "The chosen method changes presentation, not the underlying partner rights.", "Clear method disclosure helps partners interpret balances."], ["Fixed capital means no drawings are allowed.", "Fluctuating capital is used only by companies.", "Current accounts record only cash sales."], ["fixed capital", "current account", "fluctuating capital", "drawings", "presentation", "partner balances"]),
    make_topic("goodwill on admission", "Why is goodwill adjusted on admission of a partner?", "Analyse the accounting logic behind sacrificing ratio and goodwill.", "A new partner gets share in future profits contributed by old partners.", ["Goodwill represents the value of reputation and expected earning capacity.", "On admission, the new partner compensates old partners for the share sacrificed.", "Sacrificing ratio identifies how old partners give up profit share.", "Goodwill adjustment ensures equitable treatment among partners.", "The accounting entry depends on the method specified in the question."], ["Goodwill is always a liability.", "Sacrificing ratio is always equal to old ratio.", "Goodwill is ignored when a new partner joins."], ["reputation value", "future profits", "sacrificing ratio", "compensation", "equitable treatment", "admission entry"]),
    make_topic("revaluation account", "What is the purpose of a revaluation account?", "Explain why assets and liabilities are revalued on admission or retirement.", "Before admitting a partner, land value increased and a provision for claims is required.", ["Revaluation account records changes in asset and liability values.", "It identifies profit or loss arising from revaluation.", "Existing partners bear the effect in their old profit-sharing ratio.", "It prevents a new or continuing partner from receiving unfair benefit or burden.", "Revaluation brings books closer to agreed values at reconstitution."], ["Revaluation records daily sales.", "New partner alone bears all old revaluation effects.", "It is used only for cash transactions."], ["asset revaluation", "liability reassessment", "old ratio", "profit or loss", "fairness", "reconstitution"]),
    make_topic("retirement of partner", "What accounting issues arise on retirement of a partner?", "Explain settlement of a retiring partner's claim.", "A retiring partner must be paid capital, goodwill share and revaluation profit.", ["Retirement requires calculation of the outgoing partner's final claim.", "Goodwill, reserves, accumulated profits and revaluation are adjusted.", "The gaining partners compensate the retiring partner for acquired share.", "The balance may be paid immediately or transferred to loan account.", "Accurate settlement protects both the retiring and continuing partners."], ["The retiring partner loses all accumulated profit.", "Only cash balance is considered.", "Gaining ratio is irrelevant."], ["retiring partner", "goodwill share", "revaluation", "gaining ratio", "loan account", "settlement"]),
    make_topic("dissolution of firm", "What happens on dissolution of a partnership firm?", "Explain how realisation account is used at dissolution.", "The firm sells assets, pays liabilities and distributes remaining cash.", ["Dissolution closes the business of the partnership firm.", "Realisation account records sale of assets and payment of liabilities.", "Realisation profit or loss is shared by partners in profit-sharing ratio.", "Partner capital accounts are settled after outside liabilities.", "Cash or bank account is finally closed after payments."], ["Dissolution means only a partner changes.", "Realisation account records credit sales for the year.", "Partners are paid before outside liabilities."], ["close business", "realisation account", "asset sale", "liability payment", "profit-sharing ratio", "capital settlement"]),
    make_topic("interest on capital", "Why is interest on capital allowed only when agreed?", "Explain treatment of interest on capital under profit or loss.", "Partners claim interest on capital although the firm has inadequate profit.", ["Interest on capital is an appropriation of profit unless the deed states otherwise.", "It is allowed only if authorised by agreement.", "If profit is insufficient, treatment depends on the deed's wording.", "It rewards partners for capital invested in the firm.", "It must be distinguished from a charge against profit."], ["Interest on capital is compulsory in every firm.", "It is always paid even without agreement.", "It is the same as drawings."], ["appropriation of profit", "partnership deed", "insufficient profit", "capital contribution", "charge vs appropriation", "partner reward"]),
    make_topic("profit sharing ratio", "Why is profit sharing ratio central to partnership accounting?", "How does a change in profit-sharing ratio affect reserves and goodwill?", "Partners change their ratio from 3:2 to 1:1 after expansion.", ["Profit sharing ratio determines how profits and losses are divided.", "A change in ratio creates gaining and sacrificing partners.", "Goodwill is adjusted to compensate sacrifice in future profits.", "Accumulated reserves may be distributed in the old ratio unless retained with adjustment.", "Ratio analysis prevents unfair transfer of partner wealth."], ["Ratio affects only sales invoices.", "Goodwill is never considered when ratio changes.", "All reserves are shared in new ratio automatically."], ["old ratio", "new ratio", "sacrifice", "gain", "goodwill adjustment", "reserves"]),
]

COMPANY_ACCOUNTS = [
    make_topic("share capital disclosure", "Why is share capital disclosed carefully in company accounts?", "Explain authorised, issued, subscribed and paid-up capital.", "A company has authorised capital of Rs 10 lakh but issued only part of it.", ["Authorised capital is the maximum capital permitted by the memorandum.", "Issued capital is offered to the public or selected investors.", "Subscribed capital is taken up by applicants.", "Paid-up capital is the amount actually received on subscribed shares.", "Clear disclosure helps users understand ownership financing."], ["Authorised capital is always fully paid.", "Subscribed capital means loan from bank.", "Paid-up capital is an expense."], ["authorised capital", "issued capital", "subscribed capital", "paid-up capital", "ownership financing", "disclosure"]),
    make_topic("debentures", "What are debentures?", "Explain debentures as a source of long-term finance.", "A company raises funds through 10 percent debentures instead of issuing shares.", ["Debentures are written acknowledgements of debt by a company.", "Debenture holders are creditors, not owners.", "Interest on debentures is generally a charge against profit.", "They provide long-term finance without diluting ownership control.", "The company must consider interest burden and redemption obligations."], ["Debenture holders get voting rights like shareholders.", "Debenture interest is paid only after dividend.", "Debentures are always donations."], ["company debt", "creditor status", "interest charge", "no ownership dilution", "redemption", "fixed obligation"]),
    make_topic("cash flow statement", "Why is a cash flow statement useful?", "Analyse how operating, investing and financing activities are classified.", "Profit increased but cash balance fell due to equipment purchase and loan repayment.", ["A cash flow statement explains changes in cash and cash equivalents.", "Operating activities show cash from main revenue-generating operations.", "Investing activities include purchase and sale of long-term assets.", "Financing activities show changes in owner capital and borrowings.", "It helps users evaluate liquidity beyond accounting profit."], ["Cash flow statement replaces balance sheet.", "Depreciation is a cash payment.", "All asset purchases are operating activities."], ["cash equivalents", "operating activities", "investing activities", "financing activities", "liquidity", "profit vs cash"]),
    make_topic("financial statement analysis", "What is financial statement analysis?", "How does analysis help stakeholders evaluate a company?", "A lender compares profitability, liquidity and solvency before granting a loan.", ["Financial statement analysis studies accounting data to assess performance and position.", "It uses tools such as ratios, comparative statements and common-size statements.", "Stakeholders evaluate profitability, liquidity, solvency and efficiency.", "Analysis supports decisions but depends on quality of accounting data.", "It should be interpreted with industry and economic context."], ["Analysis guarantees future profit.", "Only owners use financial statements.", "Ratios have meaning without context."], ["profitability", "liquidity", "solvency", "efficiency", "ratios", "context"]),
    make_topic("ratio analysis", "Why is ratio analysis useful?", "Explain liquidity and solvency ratios in decision-making.", "Current ratio is high but quick ratio is weak because inventory is slow moving.", ["Ratio analysis expresses relationships between financial statement figures.", "Liquidity ratios assess short-term payment ability.", "Solvency ratios assess long-term financial risk.", "Ratios help comparison across years or firms.", "They require interpretation because one ratio alone can mislead."], ["A single ratio gives final proof.", "Liquidity ratio measures only profit.", "Solvency ratio is unrelated to debt."], ["relationship of figures", "liquidity", "solvency", "comparison", "interpretation", "limitations"]),
    make_topic("issue of shares at premium", "Why may shares be issued at premium?", "Explain accounting treatment of securities premium.", "A reputed company issues shares above face value due to strong investor demand.", ["Share premium arises when shares are issued above face value.", "The excess over face value is credited to securities premium reserve.", "Premium reflects reputation, demand or expected earning capacity.", "Its use is restricted by company law provisions.", "It is a capital reserve, not a normal trading profit."], ["Premium is credited to sales account.", "Premium is a loss on issue.", "It can be freely distributed as normal dividend."], ["above face value", "securities premium reserve", "capital reserve", "restricted use", "reputation", "investor demand"]),
    make_topic("redemption of debentures", "What is redemption of debentures?", "Explain why planning for redemption is important.", "A company must repay debentures at maturity while maintaining liquidity.", ["Redemption means repayment of debentures to debenture holders.", "It may be at par, premium or discount depending on terms.", "The company must arrange funds without harming liquidity.", "Proper accounting recognises redemption obligation and related entries.", "Planning protects creditworthiness and investor confidence."], ["Redemption means issuing more equity shares only.", "Debentures never mature.", "Repayment has no effect on cash planning."], ["repayment", "maturity", "premium or par", "liquidity planning", "creditworthiness", "investor confidence"]),
    make_topic("comparative statements", "How do comparative statements help analysis?", "Explain trend interpretation using comparative financial statements.", "Sales rose by 20 percent but expenses rose by 35 percent in the same year.", ["Comparative statements show financial data for two or more periods.", "They reveal absolute and percentage changes.", "Users can identify trends in income, expenses, assets and liabilities.", "A rise in sales may be weak if costs rise faster.", "Comparative analysis supports deeper ratio and cause analysis."], ["Comparative statements show only one year.", "Percentage change is never calculated.", "Higher sales always means higher profit."], ["two periods", "absolute change", "percentage change", "cost trend", "profit impact", "cause analysis"]),
]

BUSINESS_1 = [
    make_topic("principles of management", "Why are principles of management useful?", "Explain how management principles guide decision-making.", "A manager adapts Fayol's principle of unity of command to a project team.", ["Management principles are broad guidelines for managerial action.", "They are flexible and can be adapted to business situations.", "They improve efficiency by guiding planning, organising and control.", "They are formed through observation, practice and experimentation.", "They are not rigid rules and must be applied with judgement."], ["Principles are mathematical formulas.", "They are identical in every situation.", "They remove the need for managerial judgement."], ["broad guidelines", "flexibility", "efficiency", "practice", "experimentation", "judgement"]),
    make_topic("business environment", "Why should managers scan the business environment?", "Analyse the impact of economic and technological changes on business.", "A digital payment rule changes customer expectations in a retail chain.", ["Business environment includes external forces affecting performance.", "Economic, social, technological, political and legal factors create opportunities and threats.", "Scanning helps managers adapt plans and strategies.", "Early response can improve competitiveness.", "Environment is dynamic and uncertain, so monitoring must be continuous."], ["Environment includes only employees.", "External changes never affect strategy.", "Scanning is needed only after losses."], ["external forces", "opportunities", "threats", "strategy adaptation", "dynamic environment", "continuous scanning"]),
    make_topic("planning", "Why is planning called a primary function of management?", "Explain how planning reduces uncertainty but does not eliminate it.", "A firm sets sales targets before launching a new product.", ["Planning decides in advance what is to be done and how.", "It provides direction and sets objectives.", "It reduces uncertainty by anticipating future conditions.", "It does not eliminate risk because the future can change.", "Good planning coordinates departments and supports control."], ["Planning guarantees success.", "Planning is done after control.", "Planning is useful only in small firms."], ["objectives", "advance decision", "direction", "uncertainty", "coordination", "control"]),
    make_topic("organising", "What is organising in management?", "Explain how organising creates role clarity.", "A growing business creates separate purchase, sales and finance departments.", ["Organising identifies and groups activities needed to achieve objectives.", "It assigns duties and delegates authority.", "It establishes relationships among positions.", "Clear structure reduces duplication and confusion.", "It helps coordination and accountability."], ["Organising means only hiring employees.", "Authority is never delegated.", "Structure increases confusion by design."], ["group activities", "assign duties", "delegate authority", "relationships", "coordination", "accountability"]),
    make_topic("staffing", "Why is staffing important?", "Explain staffing as a human resource function.", "A company selects trained accountants for a new ERP implementation.", ["Staffing ensures the right people are placed in the right jobs.", "It includes recruitment, selection, training and development.", "Effective staffing improves productivity and morale.", "It supports future human resource needs.", "Poor staffing can weaken even well-designed plans."], ["Staffing is only salary payment.", "Training is unrelated to staffing.", "Any person can perform any job without fit."], ["right person", "right job", "recruitment", "selection", "training", "productivity"]),
    make_topic("directing", "What is directing?", "Explain the role of leadership, motivation and communication in directing.", "A supervisor guides employees during a new workflow rollout.", ["Directing initiates action by guiding and influencing employees.", "Leadership provides direction and example.", "Motivation encourages employees to work willingly.", "Communication transfers instructions, feedback and information.", "Directing links plans with actual performance."], ["Directing is done only at year end.", "Motivation means punishment only.", "Communication is not needed after planning."], ["guide employees", "leadership", "motivation", "communication", "initiate action", "performance"]),
    make_topic("controlling", "Why is controlling necessary?", "Explain the steps in controlling.", "Actual sales are lower than standard sales for three consecutive months.", ["Controlling compares actual performance with standards.", "It measures deviations and analyses their causes.", "Corrective action is taken when deviations are significant.", "It ensures plans are implemented effectively.", "Control is closely linked with planning."], ["Controlling means avoiding standards.", "Every small deviation needs the same action.", "Control is unrelated to planning."], ["standards", "actual performance", "deviation", "cause analysis", "corrective action", "planning link"]),
    make_topic("coordination", "Why is coordination called the essence of management?", "Explain coordination across departments.", "Production, marketing and finance must align before a festival launch.", ["Coordination integrates efforts of different departments.", "It ensures unity of action toward organisational objectives.", "It is needed at all levels and in all functions.", "Coordination reduces conflict and duplication.", "It is a continuous responsibility of managers."], ["Coordination belongs only to finance.", "It is required only once.", "It increases conflict intentionally."], ["integrate efforts", "unity of action", "all levels", "reduce conflict", "continuous", "managerial responsibility"]),
]

BUSINESS_2 = [
    make_topic("financial management", "What is financial management?", "Explain the objective of financial management.", "A company must choose between a high-risk project and stable returns.", ["Financial management deals with procurement and use of funds.", "Its primary objective is to maximise shareholders' wealth.", "It considers investment, financing and dividend decisions.", "Sound decisions balance risk, return and liquidity.", "Financial management supports long-term survival and growth."], ["It only records daily cash sales.", "Its objective is to maximise expenses.", "Dividend decision is unrelated to finance."], ["procurement of funds", "use of funds", "wealth maximisation", "investment decision", "financing decision", "risk-return"]),
    make_topic("capital structure", "What is capital structure?", "Analyse factors affecting debt-equity choice.", "A profitable firm considers debt because interest is tax deductible.", ["Capital structure is the mix of debt and equity used by a company.", "Debt may increase return on equity when earnings exceed interest cost.", "High debt also increases financial risk and fixed obligations.", "Factors include cost, risk, control, flexibility and market conditions.", "An optimum structure balances return and risk."], ["Capital structure means only current assets.", "Debt never creates risk.", "Equity interest is tax deductible."], ["debt-equity mix", "financial risk", "trading on equity", "cost of capital", "control", "optimum structure"]),
    make_topic("working capital", "Why is working capital needed?", "Explain factors affecting working capital requirement.", "A seasonal business stocks inventory before peak demand.", ["Working capital is needed for day-to-day operations.", "It finances inventory, receivables and cash needs.", "Requirement depends on operating cycle, scale, credit policy and seasonality.", "Too little working capital can disrupt operations.", "Too much working capital may reduce profitability."], ["Working capital is only fixed assets.", "More working capital is always best.", "Credit policy has no effect."], ["day-to-day operations", "inventory", "receivables", "operating cycle", "seasonality", "profitability"]),
    make_topic("marketing management", "What is marketing management?", "Explain how marketing creates customer value.", "A company redesigns packaging and after-sale service for a premium product.", ["Marketing management involves planning and implementing marketing activities.", "It identifies customer needs and designs value offerings.", "Product, price, place and promotion decisions shape the market response.", "Customer satisfaction supports repeat purchase and brand loyalty.", "Marketing should align company objectives with consumer value."], ["Marketing means only advertising.", "Customer value is irrelevant.", "Price is not part of marketing mix."], ["customer needs", "value offering", "product", "price", "place", "promotion"]),
    make_topic("consumer protection", "Why is consumer protection important?", "Explain consumer rights and business responsibilities.", "A customer receives a defective product and misleading warranty information.", ["Consumer protection safeguards buyers against unfair trade practices.", "Consumers have rights such as safety, information, choice and redressal.", "Businesses must provide truthful information and fair treatment.", "Protection builds confidence and ethical markets.", "Responsible firms handle complaints and quality issues promptly."], ["Consumers have no right to information.", "Misleading labels improve ethics.", "Complaint handling is never a business responsibility."], ["consumer rights", "safety", "information", "redressal", "fair trade", "ethical market"]),
    make_topic("stock exchange", "What is the role of a stock exchange?", "Explain how stock exchanges support liquidity and price discovery.", "An investor sells listed shares quickly through an organised market.", ["A stock exchange provides a market for buying and selling securities.", "It gives liquidity to investors holding listed securities.", "Trading helps price discovery through demand and supply.", "It supports capital formation and investor confidence.", "Regulation is needed to ensure fair and transparent trading."], ["Stock exchange sells only goods.", "It guarantees profit on every share.", "Price is fixed permanently by one seller."], ["securities market", "liquidity", "price discovery", "capital formation", "investor confidence", "regulation"]),
    make_topic("SEBI", "Why was SEBI established?", "Explain SEBI's protective and regulatory role.", "Investors complain about misleading issue documents and insider trading.", ["SEBI regulates the securities market in India.", "It protects investor interests and promotes fair dealing.", "It regulates intermediaries, listed companies and market practices.", "It can act against unfair trade practices and insider trading.", "Effective regulation supports confidence in capital markets."], ["SEBI manages school exams.", "SEBI guarantees every investor's profit.", "Insider trading is encouraged by regulation."], ["securities regulation", "investor protection", "intermediaries", "fair dealing", "insider trading", "market confidence"]),
    make_topic("entrepreneurship and risk", "How does entrepreneurship involve risk and innovation?", "Explain entrepreneurial decision-making in a new venture.", "A founder launches an eco-friendly product with uncertain demand.", ["Entrepreneurship involves identifying opportunities and mobilising resources.", "Innovation helps create new products, processes or markets.", "Entrepreneurs bear risk because outcomes are uncertain.", "They coordinate finance, people and operations to implement ideas.", "Sound planning and market study can reduce but not remove risk."], ["Entrepreneurship has no uncertainty.", "Innovation means copying exactly.", "Risk can be fully eliminated."], ["opportunity", "innovation", "risk bearing", "resource mobilisation", "market study", "venture planning"]),
]

MACRO = [
    make_topic("aggregate demand", "What is aggregate demand?", "Explain components of aggregate demand in an economy.", "Households increase consumption while firms postpone investment.", ["Aggregate demand is planned expenditure on final goods and services at a given income level.", "Its components include consumption, investment, government expenditure and net exports.", "Consumption depends on income and propensity to consume.", "Investment is affected by expectations and interest rates.", "Changes in aggregate demand influence output and employment."], ["Aggregate demand is demand for one firm's product.", "Imports are always added without adjustment.", "Investment is unrelated to expectations."], ["planned expenditure", "consumption", "investment", "government expenditure", "net exports", "output"]),
    make_topic("money supply", "What is money supply?", "Explain components of money supply used in macroeconomics.", "A student confuses currency held by public with cash held by banks.", ["Money supply refers to the stock of money available with the public at a point of time.", "Currency held by the public and demand deposits are key components.", "Cash held by banks is not counted as money held by the public.", "Money supply affects liquidity and monetary policy.", "Accurate definition avoids double counting."], ["Money supply means only gold reserves.", "Cash with banks is counted as public currency.", "It is measured only once in ten years."], ["stock of money", "public", "currency", "demand deposits", "liquidity", "double counting"]),
    make_topic("central bank", "What are the functions of a central bank?", "Explain how the central bank controls credit.", "Inflation rises and the central bank wants to reduce excess credit.", ["The central bank is the apex monetary authority.", "It issues currency and acts as banker to the government and banks.", "It controls credit through tools such as bank rate, repo rate, CRR and open market operations.", "Credit control influences money supply and inflation.", "Policy must balance price stability and growth."], ["Central bank is a private shop.", "CRR increases commercial bank lending capacity always.", "Credit control has no effect on inflation."], ["apex bank", "currency issue", "banker to banks", "repo rate", "CRR", "price stability"]),
    make_topic("national income", "Why is national income measured?", "Explain precautions in national income accounting.", "A calculation includes second-hand sale and intermediate goods by mistake.", ["National income measures the value of final goods and services produced by residents.", "Only final goods are counted to avoid double counting.", "Transfer payments and second-hand sales are generally excluded from current production.", "Domestic and national aggregates differ due to net factor income from abroad.", "Accurate measurement helps policy and comparison."], ["Intermediate goods are always counted separately.", "Transfer payments are payment for current production.", "Second-hand sale adds new production."], ["final goods", "residents", "double counting", "transfer payments", "NFIA", "policy comparison"]),
    make_topic("government budget", "What is a government budget?", "Explain revenue and capital receipts.", "The government receives tax revenue and also raises a loan.", ["A government budget is an annual statement of estimated receipts and expenditure.", "Revenue receipts do not create liability or reduce assets.", "Capital receipts create liability or reduce assets.", "Taxes are revenue receipts, while borrowings are capital receipts.", "Budget classification helps analyse fiscal position."], ["Borrowing is a revenue receipt.", "Taxes always create liability.", "Budget is prepared only by households."], ["annual statement", "revenue receipt", "capital receipt", "tax", "borrowing", "fiscal position"]),
    make_topic("balance of payments", "What is balance of payments?", "Differentiate current account and capital account.", "A country earns export revenue and receives foreign investment in the same year.", ["Balance of payments records economic transactions between residents and the rest of the world.", "Current account records goods, services, income and transfers.", "Capital account records capital flows and changes in assets and liabilities.", "Exports are current account receipts.", "Foreign investment is generally recorded in capital account."], ["BOP records only domestic sales.", "Exports are capital account only.", "Foreign investment is a transfer payment."], ["residents", "rest of world", "current account", "capital account", "exports", "foreign investment"]),
    make_topic("excess demand", "What is excess demand?", "Explain measures to correct inflationary pressure.", "Planned expenditure exceeds output at full employment.", ["Excess demand occurs when aggregate demand exceeds aggregate supply at full employment.", "It creates inflationary pressure in the economy.", "Fiscal measures may include reducing government expenditure or increasing taxes.", "Monetary measures may include reducing credit availability.", "The aim is to bring aggregate demand closer to output capacity."], ["Excess demand means unemployment gap.", "Increasing government spending always corrects inflation.", "Credit expansion reduces demand."], ["aggregate demand", "full employment", "inflationary gap", "taxes", "government expenditure", "credit control"]),
    make_topic("foreign exchange rate", "What is foreign exchange rate?", "Explain how currency depreciation affects imports and exports.", "The rupee depreciates against the dollar before an import payment.", ["Foreign exchange rate is the price of one currency in terms of another.", "Depreciation means domestic currency loses value against foreign currency.", "Imports become costlier in domestic currency.", "Exports may become more competitive for foreign buyers.", "The effect depends on demand elasticity and other market conditions."], ["Depreciation makes imports cheaper.", "Exchange rate is unrelated to trade.", "Exports always fall after depreciation."], ["currency price", "depreciation", "costlier imports", "export competitiveness", "elasticity", "trade impact"]),
]

MICRO = [
    make_topic("demand elasticity", "What is price elasticity of demand?", "Explain factors affecting elasticity of demand.", "A small price rise sharply reduces demand for a luxury product.", ["Price elasticity of demand measures responsiveness of quantity demanded to price change.", "Elastic demand changes proportionately more than price.", "Availability of substitutes increases elasticity.", "Necessities tend to have inelastic demand.", "Elasticity helps firms and government predict revenue effects."], ["Elasticity measures only supply.", "Necessities always have perfectly elastic demand.", "Substitutes reduce responsiveness."], ["responsiveness", "quantity demanded", "price change", "substitutes", "necessities", "revenue effect"]),
    make_topic("consumer equilibrium", "What is consumer equilibrium?", "Explain equilibrium using marginal utility and price.", "A consumer reallocates spending between two goods to maximise satisfaction.", ["Consumer equilibrium is the point where a consumer maximises satisfaction subject to budget.", "Under utility analysis, marginal utility per rupee guides choice.", "The consumer reallocates spending until no further gain is possible.", "Budget constraint limits choices.", "Equilibrium assumes rational behaviour and given prices."], ["Equilibrium means buying everything available.", "Budget constraint is irrelevant.", "Marginal utility never changes."], ["maximum satisfaction", "budget constraint", "marginal utility", "price", "rational choice", "allocation"]),
    make_topic("production function", "What is a production function?", "Explain short-run production with variable factors.", "A factory adds workers while machines remain fixed.", ["A production function shows the relation between inputs and output.", "In the short run, at least one factor is fixed.", "Adding variable factors can initially raise output at an increasing rate.", "Eventually diminishing returns may appear due to fixed factors.", "It helps firms plan input use."], ["All factors are variable in short run.", "Output is unrelated to inputs.", "Diminishing returns means output is always zero."], ["input-output relation", "short run", "fixed factor", "variable factor", "diminishing returns", "input planning"]),
    make_topic("cost concepts", "Differentiate fixed cost and variable cost.", "Explain total, average and marginal cost relationships.", "Rent remains constant while raw material cost changes with output.", ["Fixed cost does not change with output in the short run.", "Variable cost changes directly with output level.", "Total cost is the sum of fixed and variable cost.", "Average cost is cost per unit, while marginal cost is extra cost of one more unit.", "Cost concepts help pricing and production decisions."], ["Fixed cost changes with every unit.", "Variable cost is zero at all output levels.", "Marginal cost is total profit."], ["fixed cost", "variable cost", "total cost", "average cost", "marginal cost", "pricing"]),
    make_topic("market equilibrium", "What is market equilibrium?", "Explain how demand and supply determine equilibrium price.", "At the current price, quantity supplied is greater than quantity demanded.", ["Market equilibrium occurs where demand equals supply.", "Equilibrium price balances buyers' willingness and sellers' offers.", "Excess supply puts downward pressure on price.", "Excess demand puts upward pressure on price.", "Market forces move price toward equilibrium under competitive conditions."], ["Equilibrium occurs when only sellers decide price.", "Excess supply raises price automatically.", "Demand and supply never interact."], ["demand", "supply", "equilibrium price", "excess supply", "excess demand", "competitive market"]),
    make_topic("perfect competition", "What are features of perfect competition?", "Explain why firms are price takers under perfect competition.", "A wheat farmer sells in a market with many buyers and sellers.", ["Perfect competition has many buyers and sellers.", "The product is homogeneous.", "Individual firms cannot influence market price.", "Firms are price takers because price is determined by market demand and supply.", "Free entry and exit are assumed in the long run."], ["Each firm sets any price independently.", "Products are strongly differentiated.", "Only one seller exists."], ["many buyers", "many sellers", "homogeneous product", "price taker", "market price", "free entry"]),
    make_topic("monopoly", "What is monopoly?", "Explain price-making power of a monopolist.", "A single supplier controls a patented product with no close substitute.", ["Monopoly is a market with a single seller and no close substitutes.", "The monopolist faces the market demand curve.", "It has price-making power but is constrained by demand.", "Barriers to entry protect monopoly power.", "Regulation may be needed to protect consumer welfare."], ["Monopoly has many identical sellers.", "A monopolist can sell unlimited quantity at any price.", "There are no entry barriers."], ["single seller", "no close substitutes", "price maker", "demand constraint", "entry barriers", "regulation"]),
    make_topic("supply elasticity", "What is price elasticity of supply?", "Explain factors affecting elasticity of supply.", "A manufacturer cannot increase output quickly due to limited capacity.", ["Price elasticity of supply measures responsiveness of quantity supplied to price change.", "Supply is more elastic when firms can expand output quickly.", "Spare capacity and time period affect elasticity.", "Perishable goods often have less elastic supply in the short run.", "Elasticity helps understand producer response to price incentives."], ["Supply elasticity measures consumer income.", "Limited capacity makes supply perfectly elastic.", "Time period has no role."], ["quantity supplied", "price change", "spare capacity", "time period", "perishability", "producer response"]),
]

ENGLISH = [
    make_topic("central idea", "How should a Class 12 English answer present the central idea?", "Explain how evidence supports interpretation in literature answers.", "A student writes a theme but gives no textual support.", ["A strong English answer states the central idea clearly.", "It supports interpretation with relevant incidents, images or lines from the text.", "The explanation should connect evidence with theme.", "Language must be concise, formal and coherent.", "A conclusion should answer the question directly."], ["A literary answer should avoid the text.", "Only decorative language is needed.", "Evidence and theme are unrelated."], ["central idea", "textual evidence", "interpretation", "theme", "coherence", "direct conclusion"]),
    make_topic("character analysis", "What makes a character analysis effective?", "Explain how actions and dialogue reveal character.", "A question asks whether a character is courageous, conflicted or selfish.", ["Character analysis explains traits using actions and dialogue.", "It avoids unsupported judgement.", "Evidence from situations shows motivation and conflict.", "The answer links character traits with the larger theme.", "Balanced analysis recognises complexity where relevant."], ["Character analysis is only a summary.", "No evidence is required.", "A character can have only one trait."], ["traits", "actions", "dialogue", "motivation", "theme", "balanced analysis"]),
    make_topic("poetic devices", "Why are poetic devices important?", "Explain how imagery or contrast deepens meaning.", "A poem uses visual images to show loss and hope.", ["Poetic devices shape the reader's understanding of meaning.", "Imagery creates sensory effect and emotional response.", "Contrast can highlight conflict, change or irony.", "The answer should name the device and explain its effect.", "Device analysis must connect with the poem's theme."], ["Device names alone are enough.", "Imagery has no emotional effect.", "Poetry does not use theme."], ["imagery", "contrast", "effect", "emotion", "theme", "interpretation"]),
    make_topic("notice writing", "What should a notice include?", "Arrange the components of a formal notice.", "The school commerce club announces a seminar on financial literacy.", ["A notice must include issuing authority, date and heading.", "It should state event, date, time, venue and eligibility clearly.", "The content must be brief and formal.", "Name and designation of the issuer should be included.", "Accuracy and format carry marks in board-style writing."], ["A notice should be a long story.", "Venue and date can be omitted.", "Informal slang improves format."], ["authority", "date", "heading", "event details", "formal tone", "issuer"]),
    make_topic("letter to editor", "How is a letter to the editor structured?", "Explain persuasive argument in a formal letter.", "A citizen writes about wasteful plastic use in markets.", ["A letter to the editor follows formal address, subject, salutation and body.", "The issue should be introduced clearly.", "Arguments must be logical and supported by examples.", "The tone should be polite and persuasive.", "The closing should suggest practical action."], ["Subject line is unnecessary.", "Personal attacks improve persuasion.", "The letter should not suggest solutions."], ["formal format", "subject", "logical argument", "examples", "polite tone", "solution"]),
    make_topic("article writing", "What makes an article effective?", "Explain organisation of ideas in article writing.", "A student writes an article on responsible online learning.", ["An article needs a clear title and focused introduction.", "Ideas should be organised into connected paragraphs.", "Examples and facts strengthen the argument.", "The language should suit the audience and purpose.", "A strong conclusion reinforces the main message."], ["Article writing has no title.", "Ideas can be random.", "Audience is irrelevant."], ["title", "introduction", "paragraphs", "examples", "audience", "conclusion"]),
    make_topic("reading comprehension", "How should inference questions be answered?", "Explain difference between stated fact and inference.", "A passage suggests the speaker is anxious without directly saying it.", ["A stated fact is directly present in the passage.", "An inference is a logical conclusion drawn from clues.", "The answer should use evidence from the passage.", "It should avoid assumptions not supported by the text.", "Inference answers must be precise and linked to context."], ["Inference means guessing freely.", "Evidence is not needed.", "Stated facts are never written directly."], ["stated fact", "inference", "clues", "evidence", "context", "precision"]),
    make_topic("long answer structure", "How should a long literature answer be organised?", "Build a 120-150 word answer with analysis and conclusion.", "A board question asks to justify a theme using two incidents.", ["Begin with a direct response to the question.", "Develop two or three relevant points with textual support.", "Explain how each point proves the theme or argument.", "Use transitions to keep the answer coherent.", "End with a concise conclusion that returns to the question."], ["Begin with unrelated biography.", "List incidents without explanation.", "End without answering the question."], ["direct response", "textual support", "theme", "analysis", "transitions", "conclusion"]),
]


SPECS = [
    ("data/practice/class-12/accountancy-computerised-accounting-system/computerised-accounting-practice-3332e8d9.json", {"root": r"C:\Users\acer\Downloads\all class pdf\all class pdf\Class 12\Commerce", "pdfPath": r"C:\Users\acer\Downloads\all class pdf\all class pdf\Class 12\Commerce\Accountancy - Computerised Accounting System\leca101.pdf", "classLevel": 12, "stream": "Commerce", "subject": "Accountancy", "book": "Accountancy - Computerised Accounting System", "chapter": "Computerised Accounting Practice", "chapterNumber": 301}, ACCOUNTING_SOFTWARE),
    ("data/practice/class-12/accountancy-financial-accounting-1/partnership-accounting-practice-1ddc2781.json", {"root": r"C:\Users\acer\Downloads\all class pdf\all class pdf\Class 12\Commerce", "pdfPath": r"C:\Users\acer\Downloads\all class pdf\all class pdf\Class 12\Commerce\Accountancy - Financial Accounting - 1\leac101.pdf", "classLevel": 12, "stream": "Commerce", "subject": "Accountancy", "book": "Accountancy - Financial Accounting - 1", "chapter": "Partnership Accounting Practice", "chapterNumber": 101}, PARTNERSHIP),
    ("data/practice/class-12/accountancy-financial-accounting-2/company-accounts-and-analysis-practice-76eb6c97.json", {"root": r"C:\Users\acer\Downloads\all class pdf\all class pdf\Class 12\Commerce", "pdfPath": r"C:\Users\acer\Downloads\all class pdf\all class pdf\Class 12\Commerce\Accountancy - Financial Accounting - 2\leac201.pdf", "classLevel": 12, "stream": "Commerce", "subject": "Accountancy", "book": "Accountancy - Financial Accounting - 2", "chapter": "Company Accounts and Analysis Practice", "chapterNumber": 201}, COMPANY_ACCOUNTS),
    ("data/practice/class-12/business-studies-part-1/management-functions-practice-141fa764.json", {"root": r"C:\Users\acer\Downloads\all class pdf\all class pdf\Class 12\Commerce", "pdfPath": r"C:\Users\acer\Downloads\all class pdf\all class pdf\Class 12\Commerce\Business Studies Part 1\lebs101.pdf", "classLevel": 12, "stream": "Commerce", "subject": "Business Studies", "book": "Business Studies Part 1", "chapter": "Management Functions Practice", "chapterNumber": 101}, BUSINESS_1),
    ("data/practice/class-12/business-studies-part-2/finance-marketing-and-consumer-practice-05d9c4f0.json", {"root": r"C:\Users\acer\Downloads\all class pdf\all class pdf\Class 12\Commerce", "pdfPath": r"C:\Users\acer\Downloads\all class pdf\all class pdf\Class 12\Commerce\Business Studies Part 2\lebs201.pdf", "classLevel": 12, "stream": "Commerce", "subject": "Business Studies", "book": "Business Studies Part 2", "chapter": "Finance Marketing and Consumer Practice", "chapterNumber": 201}, BUSINESS_2),
    ("data/practice/class-12/economics-introductory-macroeconomics/macroeconomics-practice-08391c21.json", {"root": r"C:\Users\acer\Downloads\all class pdf\all class pdf\Class 12\Commerce", "pdfPath": r"C:\Users\acer\Downloads\all class pdf\all class pdf\Class 12\Commerce\Economics - Introductory Macroeconomics\leec201.pdf", "classLevel": 12, "stream": "Commerce", "subject": "Economics", "book": "Economics - Introductory Macroeconomics", "chapter": "Macroeconomics Practice", "chapterNumber": 201}, MACRO),
    ("data/practice/class-12/economics-introductory-microeconomics/microeconomics-practice-f6fb2797.json", {"root": r"C:\Users\acer\Downloads\all class pdf\all class pdf\Class 12\Commerce", "pdfPath": r"C:\Users\acer\Downloads\all class pdf\all class pdf\Class 12\Commerce\Economics - Introductory Microeconomics\leec101.pdf", "classLevel": 12, "stream": "Commerce", "subject": "Economics", "book": "Economics - Introductory Microeconomics", "chapter": "Microeconomics Practice", "chapterNumber": 101}, MICRO),
    ("data/practice/class-12/english-flamingo-and-vistas/class-12-english-practice-f5cd2640.json", {"root": r"C:\Users\acer\Downloads\all class pdf\all class pdf\Class 12\Commerce", "pdfPath": r"C:\Users\acer\Downloads\all class pdf\all class pdf\Class 12\Commerce\English\lefl101.pdf", "classLevel": 12, "stream": "Commerce", "subject": "English", "book": "English - Flamingo and Vistas", "chapter": "Class 12 English Practice", "chapterNumber": 101}, ENGLISH),
]


def update_catalog(paths: list[str]) -> None:
    catalog_path = ROOT / "data/catalog/content-catalog.json"
    if not catalog_path.exists():
        return
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    generated = {path.replace("\\", "/") for path in paths}
    for entry in catalog.get("datasets", []):
        if str(entry.get("jsonPath", "")).replace("\\", "/") in generated:
            payload = json.loads((ROOT / entry["jsonPath"]).read_text(encoding="utf-8"))
            entry["activityCount"] = len(payload["activities"])
            entry["status"] = "active"
            entry["hasJson"] = True
    catalog["generatedAt"] = int(time.time())
    catalog_path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    paths: list[str] = []
    for relative, meta, topics in SPECS:
        output_path = ROOT / relative
        payload = dataset(meta, topics, output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        paths.append(relative)
        print(f"Wrote {relative} ({len(payload['activities'])} activities)")
    update_catalog(paths)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
