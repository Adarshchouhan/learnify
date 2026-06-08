from __future__ import annotations

import json
import re
import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SOURCE_ROOT = Path(r"C:\Users\acer\Downloads\all class pdf\all class pdf")
PILOT_PDF = SOURCE_ROOT / "class 7" / "Science - Curiosity" / "gecu109.pdf"
OUTPUT_PATH = (
    Path("data")
    / "practice"
    / "class-7"
    / "science-curiosity"
    / "life-processes-in-animals.json"
)


@dataclass(frozen=True)
class ChapterMeta:
    class_level: int
    stream: str | None
    subject: str
    book: str
    chapter: str
    chapter_number: int
    pdf_path: Path


PILOT_META = ChapterMeta(
    class_level=7,
    stream=None,
    subject="Science",
    book="Science - Curiosity",
    chapter="Life Processes in Animals",
    chapter_number=9,
    pdf_path=PILOT_PDF,
)

ACTIVE_META = PILOT_META


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

LAYOUT_PROFILES: dict[str, dict[str, Any]] = {
    "sequence": {
        "label": "Sequence Builder",
        "primaryType": "process_sequence",
        "slotStrategy": "ordered_placeholders",
        "layout": "numbered vertical slots with exact-order validation",
    },
    "explain": {
        "label": "Explanation Builder",
        "primaryType": "explain",
        "slotStrategy": "structured_answer",
        "layout": "introduction, key points, conclusion",
    },
    "compare": {
        "label": "Compare and Contrast Builder",
        "primaryType": "compare_contrast",
        "slotStrategy": "two_column_table",
        "layout": "similarities and differences columns",
    },
    "cause_effect": {
        "label": "Cause-Effect Builder",
        "primaryType": "cause_effect",
        "slotStrategy": "paired_connections",
        "layout": "cause column, effect column and explanation box",
    },
    "experiment": {
        "label": "Experiment/Observation Builder",
        "primaryType": "evidence_support_statement",
        "slotStrategy": "aim_observation_reason",
        "layout": "aim, materials, observation, inference",
    },
    "data": {
        "label": "Data Interpretation Builder",
        "primaryType": "data_chart_table",
        "slotStrategy": "table_or_chart_inference",
        "layout": "data table with inference slots",
    },
    "definition": {
        "label": "Definition Builder",
        "primaryType": "definition_term",
        "slotStrategy": "term_definition_parts",
        "layout": "term, key phrase slots, final definition",
    },
    "assertion_reason": {
        "label": "Assertion-Reason Builder",
        "primaryType": "assertion_reason",
        "slotStrategy": "truth_and_relationship",
        "layout": "assertion, reason, relationship choice",
    },
}


SOURCE_SUMMARY = (
    "The chapter explains nutrition and respiration in animals. It covers the "
    "human alimentary canal, digestion in the mouth, stomach and small intestine, "
    "absorption of nutrients, egestion, rumination in grass-eating animals, "
    "breathing in humans, gas exchange in alveoli, the difference between "
    "breathing and respiration, and breathing mechanisms in other animals."
)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "chapter"


def activity_prefix() -> str:
    meta = ACTIVE_META
    if meta == PILOT_META:
        return "c7-science-lpa"
    parts = [
        f"class-{meta.class_level}",
        slugify(meta.stream) if meta.stream else None,
        slugify(meta.subject),
        slugify(meta.chapter),
    ]
    return "-".join(part for part in parts if part)


def infer_output_path(meta: ChapterMeta) -> Path:
    parts = [Path("data"), Path("practice"), Path(f"class-{meta.class_level}")]
    if meta.stream:
        parts.append(Path(slugify(meta.stream)))
    parts.extend([Path(slugify(meta.book)), Path(f"{slugify(meta.chapter)}.json")])
    path = parts[0]
    for part in parts[1:]:
        path /= part
    return path


def summarize_source(extracted_text: str) -> str:
    if ACTIVE_META == PILOT_META:
        return SOURCE_SUMMARY
    cleaned = re.sub(r"\s+", " ", extracted_text).strip()
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    selected = [sentence for sentence in sentences if 60 <= len(sentence) <= 220][:3]
    if not selected:
        return f"Generated from {ACTIVE_META.book}, Chapter {ACTIVE_META.chapter}."
    return " ".join(selected)


COMMON_RUBRIC = [
    {"criterion": "Correct facts", "marks": 2},
    {"criterion": "Logical structure or matching", "marks": 1},
    {"criterion": "Relevant vocabulary", "marks": 1},
    {"criterion": "No incorrect distractors selected", "marks": 1},
]


def extract_pdf_text(pdf_path: Path) -> str:
    if not pdf_path.exists():
        raise FileNotFoundError(f"Missing source PDF: {pdf_path}")

    try:
        import fitz  # type: ignore

        with fitz.open(pdf_path) as doc:
            text = "\n".join(page.get_text() for page in doc)
    except Exception:
        import pdfplumber  # type: ignore

        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    return normalize_text(text)


def normalize_text(text: str) -> str:
    replacements = {
        "\ufb00": "ff",
        "\ufb01": "fi",
        "\ufb02": "fl",
        "\u00a0": " ",
        "\u2013": "-",
        "\u2014": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk(item_id: str, text: str, order: int | None = None, section: str | None = None) -> dict[str, Any]:
    item: dict[str, Any] = {"id": item_id, "text": text}
    if order is not None:
        item["order"] = order
    if section:
        item["section"] = section
    return item


def distractor(item_id: str, text: str, misconception: str) -> dict[str, Any]:
    return {"id": item_id, "text": text, "misconception": misconception}


def split_correct_ending(sentence: str) -> tuple[str, str]:
    clean = re.sub(r"\s+", " ", sentence).strip()
    clean = clean.rstrip(".!?")
    words = clean.split()
    if len(words) < 8:
        midpoint = max(2, len(words) // 2)
    else:
        midpoint = max(4, len(words) - min(7, max(3, len(words) // 3)))
    return " ".join(words[:midpoint]), " ".join(words[midpoint:])


def choose_correct_ending_payload(
    prefix: str,
    sentences: list[str],
    fallback_wrong: list[str] | None = None,
    limit: int = 3,
) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], str, list[str]]:
    usable = [sentence for sentence in sentences if len(sentence.split()) >= 6][:limit]
    while len(usable) < limit:
        usable.append(f"{ACTIVE_META.chapter} gives important facts that students can complete correctly.")

    correct: list[dict[str, Any]] = []
    slots: list[dict[str, Any]] = []
    stems: list[str] = []
    model_lines: list[str] = []
    for index, sentence in enumerate(usable, start=1):
        stem, ending = split_correct_ending(sentence)
        item_id = f"{prefix}-{index}"
        correct.append(chunk(item_id, ending, index))
        slots.append({"id": f"ending-{index}", "label": f"Gap {index}", "expectedItemId": item_id})
        stems.append(f"{index}. {stem} ________.")
        model_lines.append(f"{index}. {stem} {ending}.")

    wrong_source = fallback_wrong or []
    wrong_texts = [split_correct_ending(text)[1] for text in wrong_source if len(text.split()) >= 4]
    wrong_texts.extend(
        [
            "does not match the chapter idea.",
            "belongs to another topic.",
            "is not the correct ending.",
        ]
    )
    distractors = [
        distractor(f"{prefix}-x{index}", text.rstrip(".") + ".", "This ending does not complete the sentence correctly.")
        for index, text in enumerate(wrong_texts[:3], start=1)
    ]
    question = "Choose the correct ending for each sentence and fill in the gaps.\n" + "\n".join(stems)
    key = {"orderedItemIds": [item["id"] for item in correct]}
    hints = ["Read the sentence before the blank.", "Choose the ending that completes the meaning."]
    return question, correct, distractors, slots, key, " ".join(model_lines), hints


def evidence_support_quiz_payload(
    prefix: str,
    claim: str,
    evidence: str,
    context: str | None = None,
) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], str, list[str]]:
    clean_claim = re.sub(r"\s+", " ", claim).strip().rstrip(".")
    clean_evidence = re.sub(r"\s+", " ", evidence).strip().rstrip(".")
    clean_context = re.sub(r"\s+", " ", context or "").strip().rstrip(".")
    if not clean_claim:
        clean_claim = f"{ACTIVE_META.chapter} presents an important Class 12 claim"
    if not clean_evidence:
        clean_evidence = f"{ACTIVE_META.chapter} gives specific supporting information"

    correct = [
        chunk(f"{prefix}-c1", f"Claim: {clean_claim}.", 1),
        chunk(f"{prefix}-c2", f"Evidence: {clean_evidence}.", 2),
        chunk(f"{prefix}-c3", "Support: this evidence is specific and directly proves the claim.", 3),
        chunk(f"{prefix}-c4", f"Link: {clean_context or ACTIVE_META.chapter}.", 4),
    ]
    distractor_texts = [
        f"Repeat only: {clean_claim}.",
        f"Unclear support: {clean_context or ACTIVE_META.chapter}.",
        "No evidence is needed because the claim is already obvious.",
        "A strong answer can ignore the link between claim and evidence.",
    ]
    question = (
        "Quiz & Worksheet - Evidence and Support\n"
        f"Claim: {clean_claim}.\n"
        f"Evidence: {clean_evidence}.\n\n"
        "Build the full evidence-support answer by selecting the correct parts in order."
    )
    distractors = [
        distractor(f"{prefix}-x{index}", text, "This option does not use specific, direct evidence.")
        for index, text in enumerate(distractor_texts, start=1)
    ]
    slots = [{"id": "answer", "label": "Answer"}]
    key = {"orderedItemIds": [item["id"] for item in correct]}
    model = " ".join(item["text"] for item in correct)
    hints = ["Select the claim, evidence, support and link in order.", "Do not use lines that only repeat or avoid evidence."]
    return question, correct, distractors, slots, key, model, hints


def base_activity(
    index: int,
    activity_type: str,
    difficulty: str,
    question: str,
    instructions: str,
    structure_help: list[str],
    correct_items: list[dict[str, Any]],
    distractors: list[dict[str, Any]],
    answer_slots: list[dict[str, Any]],
    answer_key: Any,
    model_answer: str,
    hints: list[str],
    correct_sequence: list[str] | None = None,
    marks: int = 5,
) -> dict[str, Any]:
    meta = ACTIVE_META
    activity: dict[str, Any] = {
        "id": f"{activity_prefix()}-{index:02d}-{activity_type}-{difficulty}",
        "type": activity_type,
        "difficulty": difficulty,
        "classLevel": meta.class_level,
        "stream": meta.stream,
        "subject": meta.subject,
        "book": meta.book,
        "chapter": meta.chapter,
        "chapterNumber": meta.chapter_number,
        "marks": marks,
        "question": question,
        "instructions": instructions,
        "structureHelp": structure_help,
        "sourceTextSummary": SOURCE_SUMMARY if meta == PILOT_META else f"Generated from {meta.book}, Chapter {meta.chapter}.",
        "sourceChapter": meta.chapter,
        "sourcePdf": str(meta.pdf_path),
        "correctItems": correct_items,
        "distractors": distractors,
        "answerSlots": answer_slots,
        "answerKey": answer_key,
        "hints": hints,
        "modelAnswer": model_answer,
        "scoringRubric": COMMON_RUBRIC,
    }
    if correct_sequence is not None:
        activity["correctSequence"] = correct_sequence
    return activity


def identify_question_layout(question: str, structure: list[str]) -> dict[str, Any]:
    text = f"{question} {' '.join(structure)}".lower()
    if any(word in text for word in ["journey", "arrange", "sequence", "steps", "pathway", "during inhalation"]):
        profile = "sequence"
    elif any(word in text for word in ["compare", "different", "not the same", "breathing and respiration"]):
        profile = "compare"
    elif any(word in text for word in ["why", "reason", "possible explanations", "because"]):
        profile = "cause_effect"
    elif any(word in text for word in ["experiment", "investigating", "test", "iodine", "lime water", "observations"]):
        profile = "experiment"
    elif any(word in text for word in ["percentage", "table", "data", "chart"]):
        profile = "data"
    elif any(word in text for word in ["what is", "define", "meaning"]):
        profile = "definition"
    elif any(word in text for word in ["assertion", "reason"]):
        profile = "assertion_reason"
    else:
        profile = "explain"
    result = dict(LAYOUT_PROFILES[profile])
    result["id"] = profile
    return result


def answer_builder_variants(start_index: int) -> list[dict[str, Any]]:
    full_sentences = [
        chunk("ab-e-1", "Food enters the mouth, where teeth crush and chew it.", 1, "Mouth"),
        chunk("ab-e-2", "Saliva moistens food and begins the digestion of starch into sugar.", 2, "Mouth"),
        chunk("ab-e-3", "The food moves through the oesophagus to the stomach.", 3, "Oesophagus"),
        chunk("ab-e-4", "In the stomach, digestive juice and acid partly digest proteins.", 4, "Stomach"),
        chunk("ab-e-5", "In the small intestine, food is fully digested and nutrients are absorbed into blood.", 5, "Small intestine"),
        chunk("ab-e-6", "The large intestine absorbs water and the waste is removed through the anus.", 6, "Large intestine"),
    ]
    halves = [
        chunk("ab-m-1a", "Food enters the mouth,", 1, "Mouth"),
        chunk("ab-m-1b", "where teeth crush and chew it.", 2, "Mouth"),
        chunk("ab-m-2a", "Saliva helps break down", 3, "Mouth"),
        chunk("ab-m-2b", "starch into simple sugars.", 4, "Mouth"),
        chunk("ab-m-3a", "The oesophagus pushes food", 5, "Oesophagus"),
        chunk("ab-m-3b", "down to the stomach.", 6, "Oesophagus"),
        chunk("ab-m-4a", "The small intestine completes digestion", 7, "Small intestine"),
        chunk("ab-m-4b", "and absorbs nutrients into blood.", 8, "Small intestine"),
    ]
    phrases = [
        chunk("ab-d-1", "mouth", 1, "Sequence"),
        chunk("ab-d-2", "teeth chew food", 2, "Sequence"),
        chunk("ab-d-3", "saliva digests starch", 3, "Sequence"),
        chunk("ab-d-4", "oesophagus moves food", 4, "Sequence"),
        chunk("ab-d-5", "stomach digests proteins", 5, "Sequence"),
        chunk("ab-d-6", "small intestine absorbs nutrients", 6, "Sequence"),
        chunk("ab-d-7", "large intestine absorbs water", 7, "Sequence"),
        chunk("ab-d-8", "anus removes waste", 8, "Sequence"),
    ]
    common_slots = [
        {"id": "slot-1", "label": "Step 1"},
        {"id": "slot-2", "label": "Step 2"},
        {"id": "slot-3", "label": "Step 3"},
        {"id": "slot-4", "label": "Step 4"},
        {"id": "slot-5", "label": "Step 5"},
        {"id": "slot-6", "label": "Step 6"},
    ]

    return [
        base_activity(
            start_index,
            "answer_builder",
            "easy",
            "Build a correct answer explaining digestion in human beings.",
            "Drag full sentences into the correct sequence. Leave incorrect sentences unused.",
            ["Mouth", "Oesophagus", "Stomach", "Small intestine", "Large intestine", "Egestion"],
            full_sentences,
            [
                distractor("ab-e-x1", "The lungs absorb nutrients from digested food.", "Confuses respiration with digestion."),
                distractor("ab-e-x2", "The large intestine produces bile for fat digestion.", "Bile is produced by the liver."),
                distractor("ab-e-x3", "Food digestion starts only after food reaches the stomach.", "Digestion starts in the mouth."),
            ],
            common_slots,
            {"orderedItemIds": [item["id"] for item in full_sentences]},
            "Digestion starts in the mouth, where teeth chew food and saliva begins breaking starch into sugar. Food then moves through the oesophagus to the stomach, where proteins are partly digested. In the small intestine, digestion is completed and nutrients are absorbed into blood. The large intestine absorbs water, and waste is removed through the anus.",
            ["Start with where food first enters the body.", "End with removal of waste."],
            [item["id"] for item in full_sentences],
        ),
        base_activity(
            start_index + 1,
            "answer_builder",
            "moderate",
            "Build a correct answer about digestion using half-sentence chunks.",
            "Pair related half-sentences and arrange them in a logical order.",
            ["Complete sentence", "Correct body part", "Correct sequence"],
            halves,
            [
                distractor("ab-m-x1", "the lungs pump food", "Wrong organ and function."),
                distractor("ab-m-x2", "oxygen is absorbed by the stomach", "Gas exchange happens in alveoli."),
                distractor("ab-m-x3", "bile is secreted by the small intestine wall", "Bile is secreted by the liver."),
            ],
            [{"id": f"slot-{i}", "label": f"Half sentence {i}"} for i in range(1, 9)],
            {"orderedItemIds": [item["id"] for item in halves]},
            "Food enters the mouth, where teeth crush and chew it. Saliva helps break down starch into simple sugars. The oesophagus pushes food down to the stomach. The small intestine completes digestion and absorbs nutrients into blood.",
            ["Look for pairs that complete one idea.", "Keep the path of food in order."],
            [item["id"] for item in halves],
        ),
        base_activity(
            start_index + 2,
            "answer_builder",
            "difficult",
            "Build a short answer on digestion from key phrases.",
            "Use the phrases to form a meaningful answer in your own words.",
            ["Opening idea", "Major organs", "Absorption", "Waste removal"],
            phrases,
            [
                distractor("ab-d-x1", "gills absorb nutrients", "Gills are for gas exchange in fish."),
                distractor("ab-d-x2", "rib cage churns food", "Rib cage protects lungs."),
                distractor("ab-d-x3", "alveoli digest starch", "Alveoli exchange gases."),
            ],
            [
                {"id": "intro", "label": "Introduction"},
                {"id": "body", "label": "Main explanation"},
                {"id": "end", "label": "Conclusion"},
            ],
            {"requiredConceptIds": [item["id"] for item in phrases]},
            "Digestion is the process by which complex food is broken into simpler forms. It begins in the mouth, where teeth chew food and saliva digests starch. Food moves through the oesophagus to the stomach, where proteins are partly digested. The small intestine completes digestion and absorbs nutrients. The large intestine absorbs water and waste leaves through the anus.",
            ["Turn phrases into full sentences.", "Mention both digestion and absorption."],
            [item["id"] for item in phrases],
        ),
    ]


def core_activities(start_index: int) -> list[dict[str, Any]]:
    activities: list[dict[str, Any]] = []

    def add(activity_type: str, question: str, correct: list[dict[str, Any]], wrong: list[dict[str, Any]], slots: list[dict[str, Any]], key: Any, model: str, help_items: list[str], hints: list[str], sequence: list[str] | None = None) -> None:
        activities.append(
            base_activity(
                start_index + len(activities),
                activity_type,
                "standard",
                question,
                "Drag or select the correct options to complete the activity.",
                help_items,
                correct,
                wrong,
                slots,
                key,
                model,
                hints,
                sequence,
            )
        )

    add(
        "explain",
        "Explain why digestion is necessary in animals.",
        [
            chunk("ex-1", "Animals eat food containing complex components such as carbohydrates, proteins and fats.", 1),
            chunk("ex-2", "These complex components must be broken into simpler forms.", 2),
            chunk("ex-3", "Simpler nutrients are absorbed and transported by blood.", 3),
            chunk("ex-4", "The nutrients provide energy, support growth and help repair the body.", 4),
        ],
        [
            distractor("ex-x1", "Digestion changes oxygen into carbon dioxide.", "This describes respiration."),
            distractor("ex-x2", "Digestion happens only in the lungs.", "Digestion occurs in the alimentary canal."),
        ],
        [{"id": "answer", "label": "Explanation"}],
        {"requiredItemIds": ["ex-1", "ex-2", "ex-3", "ex-4"]},
        "Digestion is necessary because animals eat food with complex components like carbohydrates, proteins and fats. These must be broken into simpler forms before the body can absorb and use them. Absorbed nutrients are carried by blood and used for energy, growth, repair and proper body functions.",
        ["Need", "Process", "Use in body"],
        ["Ask: can the body directly use complex food?", "Include absorption and energy."],
    )
    add(
        "compare_contrast",
        "Compare breathing and respiration.",
        [
            chunk("cc-1", "Breathing is a physical process.", 1, "Breathing"),
            chunk("cc-2", "Respiration is a chemical process.", 2, "Respiration"),
            chunk("cc-3", "Breathing involves inhaling and exhaling air.", 3, "Breathing"),
            chunk("cc-4", "Respiration uses oxygen to break down glucose and release energy.", 4, "Respiration"),
            chunk("cc-5", "Both are essential for survival.", 5, "Similarity"),
        ],
        [
            distractor("cc-x1", "Breathing produces bile.", "Bile is related to digestion."),
            distractor("cc-x2", "Respiration happens only in the nose.", "Respiration occurs inside the body."),
        ],
        [{"id": "breathing", "label": "Breathing"}, {"id": "respiration", "label": "Respiration"}, {"id": "similarity", "label": "Similarity"}],
        {"breathing": ["cc-1", "cc-3"], "respiration": ["cc-2", "cc-4"], "similarity": ["cc-5"]},
        "Breathing is the physical process of taking air into the lungs and giving air out. Respiration is a chemical process in which oxygen breaks down glucose to release energy. Both are essential because breathing supplies oxygen needed for respiration.",
        ["Breathing", "Respiration", "Similarity"],
        ["One process moves air; the other releases energy."],
    )
    add(
        "cause_effect",
        "Connect each cause with its correct effect in digestion or breathing.",
        [
            chunk("ce-1", "Teeth crush and chew food", 1, "Cause"),
            chunk("ce-2", "Food is broken into smaller pieces", 1, "Effect"),
            chunk("ce-3", "Diaphragm moves downward", 2, "Cause"),
            chunk("ce-4", "Air enters the lungs", 2, "Effect"),
            chunk("ce-5", "Alveoli have thin walls and blood vessels", 3, "Cause"),
            chunk("ce-6", "Oxygen and carbon dioxide are exchanged", 3, "Effect"),
        ],
        [
            distractor("ce-x1", "Bile filters dust from air", "Nasal hair and mucus trap dust."),
            distractor("ce-x2", "Rib cage absorbs digested nutrients", "Small intestine absorbs nutrients."),
        ],
        [{"id": "pair-1", "label": "Connection 1"}, {"id": "pair-2", "label": "Connection 2"}, {"id": "pair-3", "label": "Connection 3"}],
        {"pairs": [["ce-1", "ce-2"], ["ce-3", "ce-4"], ["ce-5", "ce-6"]]},
        "Chewing breaks food into smaller pieces. When the diaphragm moves downward, the chest space increases and air enters the lungs. Thin-walled alveoli surrounded by blood vessels help oxygen enter blood and carbon dioxide leave blood.",
        ["Cause", "Effect", "Explanation"],
        ["Match an action to what immediately happens because of it."],
    )
    add(
        "process_sequence",
        "Arrange the journey of food through the alimentary canal.",
        [
            chunk("ps-1", "Mouth", 1),
            chunk("ps-2", "Oesophagus or food pipe", 2),
            chunk("ps-3", "Stomach", 3),
            chunk("ps-4", "Small intestine", 4),
            chunk("ps-5", "Large intestine", 5),
            chunk("ps-6", "Rectum", 6),
            chunk("ps-7", "Anus", 7),
        ],
        [
            distractor("ps-x1", "Lungs", "Respiratory organ."),
            distractor("ps-x2", "Rib cage", "Protects lungs."),
        ],
        [{"id": f"step-{i}", "label": f"Step {i}"} for i in range(1, 8)],
        {"orderedItemIds": ["ps-1", "ps-2", "ps-3", "ps-4", "ps-5", "ps-6", "ps-7"]},
        "Food travels from the mouth to the oesophagus, stomach, small intestine, large intestine, rectum and finally the anus.",
        ["Start", "Middle organs", "Waste removal"],
        ["Follow the path food takes, not air."],
        ["ps-1", "ps-2", "ps-3", "ps-4", "ps-5", "ps-6", "ps-7"],
    )
    add(
        "pros_cons",
        "Sort the helpful and harmful habits for digestive and respiratory health.",
        [
            chunk("pc-1", "Eating fibre-rich fruits, vegetables and whole grains", 1, "Helpful"),
            chunk("pc-2", "Maintaining oral hygiene by brushing and cleaning the tongue", 2, "Helpful"),
            chunk("pc-3", "Practising breathing exercises", 3, "Helpful"),
            chunk("pc-4", "Smoking damages lungs and causes respiratory illness", 4, "Harmful"),
            chunk("pc-5", "Overeating can disturb digestion", 5, "Harmful"),
        ],
        [
            distractor("pc-x1", "Avoiding all millets because they contain gluten", "Millets are naturally gluten-free."),
            distractor("pc-x2", "Breathing through the mouth filters dust better than the nose", "Nasal hair and mucus filter dust."),
        ],
        [{"id": "helpful", "label": "Helpful"}, {"id": "harmful", "label": "Harmful"}],
        {"helpful": ["pc-1", "pc-2", "pc-3"], "harmful": ["pc-4", "pc-5"]},
        "Helpful habits include eating fibre-rich food, maintaining oral hygiene and practising breathing exercises. Harmful habits include smoking and overeating because they damage respiratory or digestive health.",
        ["Helpful", "Harmful"],
        ["Look for habits that protect the alimentary canal or lungs."],
    )
    add(
        "problem_solution",
        "Suggest solutions for a student who often has poor digestion and bad mouth smell.",
        [
            chunk("pr-1", "Brush teeth and clean the tongue twice a day.", 1, "Solution"),
            chunk("pr-2", "Rinse the mouth with water after meals.", 2, "Solution"),
            chunk("pr-3", "Eat fibre-rich foods such as fruits, vegetables and whole grains.", 3, "Solution"),
            chunk("pr-4", "Practise mindful eating and avoid overeating.", 4, "Solution"),
        ],
        [
            distractor("pr-x1", "Skip water so the large intestine works harder.", "Water balance is important."),
            distractor("pr-x2", "Smoke to strengthen the lungs.", "Smoking damages lungs."),
        ],
        [{"id": "problem", "label": "Problem"}, {"id": "solutions", "label": "Solutions"}],
        {"solutions": ["pr-1", "pr-2", "pr-3", "pr-4"]},
        "The student should brush teeth and clean the tongue twice daily, rinse the mouth after meals, eat fibre-rich foods and avoid overeating. These habits support oral hygiene and healthy digestion.",
        ["Problem", "Practical solutions"],
        ["Use the oral hygiene and digestive health parts of the chapter."],
    )
    add(
        "fill_blanks",
        "Complete the passage about breathing.",
        [
            chunk("fb-1", "nostrils", 1),
            chunk("fb-2", "windpipe", 2),
            chunk("fb-3", "alveoli", 3),
            chunk("fb-4", "carbon dioxide", 4),
        ],
        [
            distractor("fb-x1", "oesophagus", "Food pipe, not air passage."),
            distractor("fb-x2", "bile", "Digestive secretion."),
            distractor("fb-x3", "starch", "Food component."),
        ],
        [{"id": "blank-1", "label": "Blank 1"}, {"id": "blank-2", "label": "Blank 2"}, {"id": "blank-3", "label": "Blank 3"}, {"id": "blank-4", "label": "Blank 4"}],
        {"blank-1": "fb-1", "blank-2": "fb-2", "blank-3": "fb-3", "blank-4": "fb-4"},
        "Air enters through the nostrils, passes through the windpipe and reaches the alveoli. In the alveoli, oxygen enters blood and carbon dioxide leaves blood.",
        ["Air pathway", "Gas exchange"],
        ["Food uses the oesophagus; air uses the windpipe."],
    )
    add(
        "true_false_not_given",
        "Classify each statement as True, False or Not Given based on the chapter.",
        [
            chunk("tf-1", "Breathing is a physical process.", 1, "True"),
            chunk("tf-2", "The large intestine absorbs water from undigested food.", 2, "True"),
            chunk("tf-3", "The stomach absorbs most digested nutrients into blood.", 3, "False"),
            chunk("tf-4", "Every bird can fly higher than every mammal.", 4, "Not Given"),
        ],
        [
            distractor("tf-x1", "All animals breathe through lungs.", "Fish use gills and earthworms use moist skin."),
        ],
        [{"id": "true", "label": "True"}, {"id": "false", "label": "False"}, {"id": "not-given", "label": "Not Given"}],
        {"true": ["tf-1", "tf-2"], "false": ["tf-3"], "notGiven": ["tf-4"]},
        "Breathing is physical and the large intestine absorbs water. Most nutrient absorption happens in the small intestine, not the stomach. The statement about every bird and mammal is not given.",
        ["True", "False", "Not Given"],
        ["False means contradicted by the chapter; Not Given means not stated."],
    )
    add(
        "short_answer_key_points",
        "List three key points about alveoli.",
        [
            chunk("sa-1", "Alveoli are small balloon-like sacs in the lungs.", 1),
            chunk("sa-2", "They have thin walls.", 2),
            chunk("sa-3", "They are surrounded by blood vessels.", 3),
            chunk("sa-4", "They help exchange oxygen and carbon dioxide.", 4),
        ],
        [
            distractor("sa-x1", "Alveoli secrete bile.", "Bile is secreted by the liver."),
            distractor("sa-x2", "Alveoli chew food.", "Teeth chew food."),
        ],
        [{"id": "point-1", "label": "Point 1"}, {"id": "point-2", "label": "Point 2"}, {"id": "point-3", "label": "Point 3"}],
        {"minimumRequired": 3, "acceptedItemIds": ["sa-1", "sa-2", "sa-3", "sa-4"]},
        "Alveoli are tiny balloon-like sacs in the lungs. Their thin walls and surrounding blood vessels allow oxygen to enter blood and carbon dioxide to leave blood.",
        ["What they are", "Structure", "Function"],
        ["Mention both oxygen and carbon dioxide for a stronger answer."],
    )
    add(
        "match_following",
        "Match each part of the respiratory system with its function.",
        [
            chunk("mf-1", "Nostrils", 1, "Part"),
            chunk("mf-2", "Nasal passages", 2, "Part"),
            chunk("mf-3", "Windpipe", 3, "Part"),
            chunk("mf-4", "Alveoli", 4, "Part"),
            chunk("mf-5", "Openings through which air is inhaled and exhaled", 1, "Function"),
            chunk("mf-6", "Tiny hair and mucus trap dust and dirt", 2, "Function"),
            chunk("mf-7", "Air reaches the lungs through this tube", 3, "Function"),
            chunk("mf-8", "Exchange of gases occurs here", 4, "Function"),
        ],
        [
            distractor("mf-x1", "Stores stool until removal", "Function of rectum."),
        ],
        [{"id": "match-1", "label": "Match 1"}, {"id": "match-2", "label": "Match 2"}, {"id": "match-3", "label": "Match 3"}, {"id": "match-4", "label": "Match 4"}],
        {"pairs": [["mf-1", "mf-5"], ["mf-2", "mf-6"], ["mf-3", "mf-7"], ["mf-4", "mf-8"]]},
        "Nostrils are openings for air. Nasal passages trap dust with hair and mucus. The windpipe carries air to lungs. Alveoli are the site of gas exchange.",
        ["Part", "Function"],
        ["Do not mix digestive and respiratory parts."],
    )
    add(
        "data_chart_table",
        "Use the inhaled and exhaled air data to answer the question.",
        [
            chunk("dt-1", "Inhaled air has nearly 21% oxygen.", 1),
            chunk("dt-2", "Exhaled air has nearly 16-17% oxygen.", 2),
            chunk("dt-3", "Inhaled air has nearly 0.04% carbon dioxide.", 3),
            chunk("dt-4", "Exhaled air has nearly 4-5% carbon dioxide.", 4),
        ],
        [
            distractor("dt-x1", "Exhaled air has no oxygen.", "Some oxygen remains in exhaled air."),
            distractor("dt-x2", "Inhaled air has more carbon dioxide than exhaled air.", "Exhaled air has more carbon dioxide."),
        ],
        [{"id": "oxygen", "label": "Oxygen comparison"}, {"id": "carbon-dioxide", "label": "Carbon dioxide comparison"}],
        {
            "table": [
                {"gas": "Oxygen", "inhaled": "Nearly 21%", "exhaled": "Nearly 16-17%"},
                {"gas": "Carbon dioxide", "inhaled": "Nearly 0.04%", "exhaled": "Nearly 4-5%"},
            ],
            "answers": ["dt-1", "dt-2", "dt-3", "dt-4"],
        },
        "Inhaled air has more oxygen than exhaled air, while exhaled air has much more carbon dioxide than inhaled air. This shows that the body uses some oxygen and releases carbon dioxide.",
        ["Read data", "Compare gases", "Infer"],
        ["Compare inhaled and exhaled values for each gas."],
    )
    add(
        "paragraph_essay_structure",
        "Arrange the parts of a good paragraph on human respiration.",
        [
            chunk("pe-1", "Humans need respiration to release energy from food.", 1),
            chunk("pe-2", "Air enters through nostrils and reaches the lungs through the windpipe.", 2),
            chunk("pe-3", "In alveoli, oxygen enters blood and carbon dioxide leaves blood.", 3),
            chunk("pe-4", "Oxygen helps break down glucose to release energy.", 4),
            chunk("pe-5", "Thus, breathing and respiration together help humans survive.", 5),
        ],
        [
            distractor("pe-x1", "The paragraph should start with an unrelated joke.", "Irrelevant to answer structure."),
            distractor("pe-x2", "Conclusion should introduce a new digestive organ.", "Conclusion should wrap up."),
        ],
        [{"id": f"part-{i}", "label": f"Part {i}"} for i in range(1, 6)],
        {"orderedItemIds": ["pe-1", "pe-2", "pe-3", "pe-4", "pe-5"]},
        "Humans need respiration to release energy from food. Air enters through nostrils and reaches the lungs through the windpipe. In alveoli, oxygen enters blood and carbon dioxide leaves blood. Oxygen helps break down glucose to release energy. Thus, breathing and respiration together help humans survive.",
        ["Topic sentence", "Pathway", "Gas exchange", "Energy release", "Conclusion"],
        ["A strong paragraph starts broad, explains, then concludes."],
        ["pe-1", "pe-2", "pe-3", "pe-4", "pe-5"],
    )
    add(
        "definition_term",
        "Build the correct definition of respiration.",
        [
            chunk("df-1", "Respiration is the process", 1),
            chunk("df-2", "by which nutrients are converted", 2),
            chunk("df-3", "into usable energy", 3),
            chunk("df-4", "using oxygen to break down glucose.", 4),
        ],
        [
            distractor("df-x1", "by which food moves through the oesophagus", "This is movement in alimentary canal."),
            distractor("df-x2", "into bile inside the liver", "Not respiration."),
        ],
        [{"id": "definition", "label": "Definition"}],
        {"orderedItemIds": ["df-1", "df-2", "df-3", "df-4"]},
        "Respiration is the process by which nutrients are converted into usable energy using oxygen to break down glucose.",
        ["Term", "Process", "Outcome"],
        ["The key outcome is usable energy."],
        ["df-1", "df-2", "df-3", "df-4"],
    )
    add(
        "timeline_chronological_order",
        "Arrange the breathing mechanism in order during inhalation.",
        [
            chunk("tl-1", "Ribs move up and outwards.", 1),
            chunk("tl-2", "Diaphragm moves downward.", 2),
            chunk("tl-3", "Space inside the chest increases.", 3),
            chunk("tl-4", "Air enters the lungs.", 4),
        ],
        [
            distractor("tl-x1", "Diaphragm moves upward during inhalation.", "It moves upward during exhalation."),
            distractor("tl-x2", "Air is forced out first.", "That is exhalation."),
        ],
        [{"id": f"event-{i}", "label": f"Event {i}"} for i in range(1, 5)],
        {"orderedItemIds": ["tl-1", "tl-2", "tl-3", "tl-4"]},
        "During inhalation, ribs move up and outwards, the diaphragm moves downward, chest space increases and air enters the lungs.",
        ["Inhalation sequence"],
        ["Inhalation increases chest space."],
        ["tl-1", "tl-2", "tl-3", "tl-4"],
    )
    add(
        "identify_main_idea",
        "Select the main idea of the passage: 'Different animals have different breathing mechanisms. Fish use gills, frogs can use gills, lungs or skin at different stages, and earthworms exchange gases through moist skin.'",
        [
            chunk("mi-1", "Animals have breathing mechanisms adapted to their habitats.", 1),
        ],
        [
            distractor("mi-x1", "All animals breathe through lungs.", "Contradicted by the passage."),
            distractor("mi-x2", "Only fish need oxygen.", "All animals need oxygen."),
            distractor("mi-x3", "Earthworms digest food through skin.", "Skin is used for gas exchange."),
        ],
        [{"id": "main-idea", "label": "Main idea"}],
        {"mainIdea": "mi-1"},
        "The main idea is that animals have different breathing mechanisms adapted to their habitats.",
        ["Main idea", "Supporting details"],
        ["The main idea should cover all examples, not only one animal."],
    )
    add(
        "evidence_support_statement",
        "Choose evidence that supports the statement: The small intestine is well suited for absorption.",
        [
            chunk("ev-1", "Its inner lining is thin.", 1),
            chunk("ev-2", "It has thousands of finger-like projections.", 2),
            chunk("ev-3", "The projections increase surface area for efficient absorption.", 3),
            chunk("ev-4", "Digested nutrients pass into blood vessels in its walls.", 4),
        ],
        [
            distractor("ev-x1", "It is protected by the rib cage.", "Rib cage protects lungs."),
            distractor("ev-x2", "It stores stool until removal.", "Rectum stores stool."),
        ],
        [{"id": "evidence-1", "label": "Evidence 1"}, {"id": "evidence-2", "label": "Evidence 2"}, {"id": "evidence-3", "label": "Evidence 3"}],
        {"minimumRequired": 3, "acceptedItemIds": ["ev-1", "ev-2", "ev-3", "ev-4"]},
        "The small intestine is suited for absorption because its lining is thin, has many finger-like projections that increase surface area, and contains blood vessels into which digested nutrients pass.",
        ["Statement", "Evidence"],
        ["Use structure features that explain absorption."],
    )
    add(
        "sequencing_steps_process",
        "Arrange the steps in the saliva and iodine investigation.",
        [
            chunk("sq-1", "Take boiled rice in test tube A.", 1),
            chunk("sq-2", "Take chewed boiled rice in test tube B.", 2),
            chunk("sq-3", "Add water to both test tubes.", 3),
            chunk("sq-4", "Add iodine solution to both test tubes.", 4),
            chunk("sq-5", "Observe the colour change.", 5),
        ],
        [
            distractor("sq-x1", "Blow exhaled air into lime water.", "This is a respiration activity."),
            distractor("sq-x2", "Attach balloons to a bottle.", "This is a breathing model activity."),
        ],
        [{"id": f"step-{i}", "label": f"Step {i}"} for i in range(1, 6)],
        {"orderedItemIds": ["sq-1", "sq-2", "sq-3", "sq-4", "sq-5"]},
        "The investigation compares boiled rice and chewed boiled rice. Water and iodine are added to both, and colour change is observed to test the action of saliva on starch.",
        ["Materials", "Test", "Observation"],
        ["This activity tests starch digestion by saliva."],
        ["sq-1", "sq-2", "sq-3", "sq-4", "sq-5"],
    )
    ending_question, ending_correct, ending_distractors, ending_slots, ending_key, ending_answer, ending_hints = choose_correct_ending_payload(
        "end",
        [
            "When exhaled air is blown into lime water, the lime water turns milky because exhaled air contains more carbon dioxide than inhaled air.",
            "The small intestine is well suited for absorption because it has many finger-like projections.",
            "Earthworms can exchange gases through skin when the skin remains moist.",
        ],
        [
            "Exhaled air contains bile.",
            "Oxygen turns lime water milky.",
            "The straw digests starch.",
        ],
    )
    add(
        "choose_correct_ending",
        ending_question,
        ending_correct,
        ending_distractors,
        ending_slots,
        ending_key,
        ending_answer,
        ["Sentence stems", "Endings"],
        ending_hints,
        [item["id"] for item in ending_correct],
    )
    add(
        "multiple_correct_answers",
        "Select all correct statements about animal breathing.",
        [
            chunk("mc-1", "Fish use gills for gas exchange.", 1),
            chunk("mc-2", "Adult frogs can use lungs on land and skin in water.", 2),
            chunk("mc-3", "Earthworms use moist skin for gas exchange.", 3),
            chunk("mc-4", "Birds breathe through lungs.", 4),
        ],
        [
            distractor("mc-x1", "All animals use gills.", "Only some aquatic animals such as fish use gills."),
            distractor("mc-x2", "Tadpoles breathe through lungs only.", "Tadpoles breathe through gills."),
        ],
        [{"id": "selected", "label": "Correct options"}],
        {"correctOptionIds": ["mc-1", "mc-2", "mc-3", "mc-4"]},
        "Fish use gills, adult frogs can use lungs and skin, earthworms use moist skin, and birds use lungs. These examples show adaptation to habitats.",
        ["Multiple correct facts"],
        ["More than one option is correct."],
    )
    add(
        "formulate_question",
        "Create a suitable question for the answer: 'The diaphragm moves downward during inhalation, increasing the space inside the chest so air enters the lungs.'",
        [
            chunk("fq-1", "What is the role of the diaphragm during inhalation?", 1),
            chunk("fq-2", "How does the diaphragm help air enter the lungs?", 2),
        ],
        [
            distractor("fq-x1", "Why does the liver secrete bile?", "Answer is about breathing, not bile."),
            distractor("fq-x2", "Where is stool stored?", "Answer is about rectum, not diaphragm."),
        ],
        [{"id": "question", "label": "Formulated question"}],
        {"acceptedItemIds": ["fq-1", "fq-2"]},
        "A suitable question is: What is the role of the diaphragm during inhalation?",
        ["Answer clue", "Question word"],
        ["The answer focuses on the diaphragm and inhalation."],
    )
    add(
        "assertion_reason",
        "Arrange the assertion, reason and relationship correctly.",
        [
            chunk("ar-1", "Assertion: The small intestine is the main site of nutrient absorption.", 1, "Assertion"),
            chunk("ar-2", "Reason: Its thin inner lining has many finger-like projections that increase surface area.", 2, "Reason"),
            chunk("ar-3", "Both A and R are true, and R correctly explains A.", 3, "Relationship"),
        ],
        [
            distractor("ar-x1", "A is true, but R is false.", "The reason is true."),
            distractor("ar-x2", "Both are true, but R does not explain A.", "The reason explains absorption."),
        ],
        [{"id": "assertion", "label": "Assertion"}, {"id": "reason", "label": "Reason"}, {"id": "relationship", "label": "Relationship"}],
        {"assertion": "ar-1", "reason": "ar-2", "relationship": "ar-3"},
        "The assertion and reason are both true. The reason correctly explains the assertion because a thin lining and many projections increase the surface area for absorption into blood.",
        ["Truth of A", "Truth of R", "Relationship"],
        ["First test truth, then test whether the reason explains the assertion."],
    )

    expected = set(QUESTION_TYPES)
    actual = {activity["type"] for activity in activities}
    missing = sorted(expected - actual)
    if missing:
        raise ValueError(f"Missing activities for: {missing}")
    return activities


CHAPTER_QUESTION_SETS = [
    {
        "slug": "food-journey",
        "question": "Complete the journey of food through the alimentary canal.",
        "structure": ["Mouth", "Oesophagus", "Stomach", "Small intestine", "Large intestine", "Anus"],
        "sentences": [
            "Food first enters the mouth.",
            "It then passes into the oesophagus or food pipe.",
            "The food reaches the stomach for partial digestion.",
            "It moves to the small intestine where nutrients are absorbed.",
            "Undigested food enters the large intestine where water is absorbed.",
            "Waste is finally expelled through the anus.",
        ],
        "wrong": [
            "Food moves from the mouth directly to the lungs.",
            "The rib cage absorbs digested nutrients.",
            "The windpipe carries food to the stomach.",
        ],
    },
    {
        "slug": "iodine-chapati",
        "question": "Explain the observations when iodine is added to chapati, chewed chapati and boiled potato.",
        "structure": ["Iodine test", "Unchewed food", "Chewed food", "Reason"],
        "sentences": [
            "Iodine turns blue-black when starch is present.",
            "Chapati and boiled potato contain starch, so they show a blue-black colour.",
            "Chewed chapati may show little or no blue-black colour.",
            "This is because saliva begins breaking starch into simple sugars.",
        ],
        "wrong": [
            "Iodine turns milky in the presence of carbon dioxide.",
            "Chewing adds bile to the chapati.",
            "Saliva changes starch into oxygen.",
        ],
    },
    {
        "slug": "diaphragm-role",
        "question": "What is the role of the diaphragm in breathing?",
        "structure": ["Position", "Inhalation", "Exhalation", "Function"],
        "sentences": [
            "The diaphragm is a dome-shaped muscle below the lungs.",
            "During inhalation, it moves downward and increases space in the chest.",
            "This allows air to enter the lungs.",
            "During exhalation, it moves upward and helps push air out.",
        ],
        "wrong": [
            "The diaphragm filters dust from inhaled air.",
            "The diaphragm produces sound in the throat.",
            "The diaphragm absorbs oxygen from food.",
        ],
    },
    {
        "slug": "respiratory-parts",
        "question": "Match the respiratory parts with their functions and explain the pathway of air.",
        "structure": ["Nostrils", "Nasal passages", "Windpipe", "Alveoli"],
        "sentences": [
            "Air enters and leaves the body through the nostrils.",
            "Nasal passages have hair and mucus that trap dust and dirt.",
            "The windpipe carries air towards the lungs.",
            "Alveoli are the sites where oxygen and carbon dioxide are exchanged.",
        ],
        "wrong": [
            "The oesophagus carries air to the lungs.",
            "The rectum protects the lungs.",
            "Bile traps dust in the nose.",
        ],
    },
    {
        "slug": "breathing-vs-respiration",
        "question": "How can you show that breathing and respiration are not the same process?",
        "structure": ["Breathing", "Respiration", "Difference", "Link"],
        "sentences": [
            "Breathing is the physical process of inhaling and exhaling air.",
            "Respiration is a chemical process inside the body.",
            "In respiration, oxygen helps break down glucose to release energy.",
            "Breathing supplies oxygen needed for respiration and removes carbon dioxide.",
        ],
        "wrong": [
            "Breathing and respiration both mean chewing food.",
            "Respiration happens only in the nostrils.",
            "Breathing produces bile for fat digestion.",
        ],
    },
    {
        "slug": "inhaled-air",
        "question": "Which statement is correct: we inhale air, oxygen, or air rich in oxygen?",
        "structure": ["Correct statement", "Reason", "Gas composition", "Conclusion"],
        "sentences": [
            "The most accurate statement is that we inhale air rich in oxygen.",
            "Air is a mixture of gases and not pure oxygen.",
            "Inhaled air has nearly 21 percent oxygen and very little carbon dioxide.",
            "Therefore, saying that we inhale air rich in oxygen is scientifically better.",
        ],
        "wrong": [
            "We inhale only carbon dioxide.",
            "Exhaled air has no oxygen at all.",
            "Air is made only of oxygen.",
        ],
    },
    {
        "slug": "sneezing-dust",
        "question": "Why do we often sneeze when we inhale dust-laden air?",
        "structure": ["Dust entry", "Nasal protection", "Sneezing", "Purpose"],
        "sentences": [
            "Dust-laden air may enter the nostrils during breathing.",
            "Hair and mucus in the nasal passages trap dust and dirt.",
            "Dust can irritate the inner lining of the nose.",
            "Sneezing helps force out the irritating particles and protects the respiratory system.",
        ],
        "wrong": [
            "Sneezing happens because bile enters the nose.",
            "Dust is absorbed by the small intestine.",
            "Sneezing digests starch into sugar.",
        ],
    },
    {
        "slug": "fast-breathing",
        "question": "Give possible reasons why Anusha was breathing faster after running.",
        "structure": ["Running", "Energy need", "Oxygen demand", "Individual difference"],
        "sentences": [
            "Running makes muscles work harder and need more energy.",
            "Respiration uses oxygen to release energy from glucose.",
            "Anusha may have needed more oxygen, so her breathing rate increased.",
            "She may also have run faster, been less fit, or taken less rest than Paridhi.",
        ],
        "wrong": [
            "Breathing slows down because muscles need no oxygen.",
            "Running stops respiration inside the body.",
            "The large intestine pumps air during running.",
        ],
    },
    {
        "slug": "saliva-starch-test",
        "question": "What was Yadu trying to test with rice flour, saliva and iodine solution?",
        "structure": ["Aim", "Control", "Saliva tube", "Inference"],
        "sentences": [
            "Yadu was testing the action of saliva on starch.",
            "Rice flour in water contains starch and turns blue-black with iodine.",
            "The test tube with saliva should show less blue-black colour after some time.",
            "This shows that saliva breaks starch into simpler sugars.",
        ],
        "wrong": [
            "Yadu was testing whether lungs produce bile.",
            "Iodine detects oxygen in exhaled air.",
            "Saliva turns carbon dioxide into water.",
        ],
    },
    {
        "slug": "lime-water-test",
        "question": "What was Rakshita investigating with lime water and exhaled air?",
        "structure": ["Aim", "Observation", "Reason", "Confirmation"],
        "sentences": [
            "Rakshita was investigating whether exhaled air contains more carbon dioxide.",
            "Lime water turns milky when carbon dioxide is present.",
            "The test tube receiving exhaled air should turn milky faster.",
            "This confirms that exhaled air has more carbon dioxide than inhaled air.",
        ],
        "wrong": [
            "Lime water turns milky because of starch.",
            "Inhaled air contains more carbon dioxide than exhaled air.",
            "The test proves that saliva digests proteins.",
        ],
    },
]


MAJOR_CHAPTER_QUESTION_SETS = [
    {
        "slug": "life-processes-meaning",
        "question": "Explain the meaning and importance of life processes in animals.",
        "structure": ["Definition", "Examples", "Importance", "Conclusion"],
        "sentences": [
            "Life processes are essential activities needed for the survival of living beings.",
            "Nutrition, respiration, circulation, excretion and reproduction are examples of life processes.",
            "Animals need these processes to obtain energy, transport materials and remove waste.",
            "These processes work together to keep the body alive and healthy.",
        ],
        "wrong": [
            "Life processes happen only in plants and not in animals.",
            "Respiration and reproduction are names of digestive juices.",
            "Animals can survive without nutrition or respiration.",
        ],
    },
    {
        "slug": "digestion-human-beings",
        "question": "Describe the process of digestion in human beings.",
        "structure": ["Mouth", "Food pipe", "Stomach", "Small intestine", "Large intestine"],
        "sentences": [
            "Digestion begins in the mouth where teeth chew food and saliva acts on starch.",
            "The tongue pushes softened food into the oesophagus.",
            "The oesophagus moves food to the stomach by wave-like contractions and relaxations.",
            "In the stomach, digestive juice and acid partly digest proteins.",
            "In the small intestine, food is completely digested and nutrients are absorbed into blood.",
            "The large intestine absorbs water and waste is removed through the anus.",
        ],
        "wrong": [
            "The windpipe carries food from the mouth to the stomach.",
            "Most nutrients are absorbed in the rib cage.",
            "The lungs complete digestion of carbohydrates.",
        ],
    },
    {
        "slug": "saliva-starch-role",
        "question": "Explain the role of saliva in digestion using the chapati or rice example.",
        "structure": ["Food", "Saliva", "Observation", "Inference"],
        "sentences": [
            "Chapati and rice contain starch, a type of carbohydrate.",
            "When we chew them for some time, saliva mixes with the food.",
            "The food begins to taste sweet because saliva breaks starch into simpler sugars.",
            "This shows that digestion starts in the mouth.",
        ],
        "wrong": [
            "Saliva breaks oxygen into carbon dioxide.",
            "Chapati tastes sweet because bile enters the mouth.",
            "Digestion starts only in the large intestine.",
        ],
    },
    {
        "slug": "stomach-small-intestine",
        "question": "Compare the roles of the stomach and small intestine in digestion.",
        "structure": ["Stomach", "Small intestine", "Difference", "Link"],
        "sentences": [
            "The stomach churns food and mixes it with digestive juice, acid and mucus.",
            "The stomach partly digests proteins and changes food into a semi-liquid mass.",
            "The small intestine receives bile, pancreatic juice and intestinal juice.",
            "The small intestine completes digestion and absorbs nutrients into blood.",
            "Thus, the stomach mainly prepares and partly digests food while the small intestine completes digestion and absorption.",
        ],
        "wrong": [
            "The stomach is the main site of gas exchange.",
            "The small intestine filters dust from inhaled air.",
            "The stomach absorbs most oxygen into blood.",
        ],
    },
    {
        "slug": "absorption-small-intestine",
        "question": "Why is the small intestine suitable for absorption of nutrients?",
        "structure": ["Thin lining", "Finger-like projections", "Blood vessels", "Absorption"],
        "sentences": [
            "The inner lining of the small intestine is thin.",
            "It has thousands of finger-like projections.",
            "These projections increase the surface area for absorption.",
            "Digested nutrients pass into blood vessels in the walls of the small intestine.",
        ],
        "wrong": [
            "The small intestine is suitable because it has alveoli.",
            "The small intestine absorbs dust from air.",
            "The small intestine stores stool until removal.",
        ],
    },
    {
        "slug": "rumination",
        "question": "Explain rumination in grass-eating animals.",
        "structure": ["Animal type", "Partial chewing", "Return to mouth", "Further digestion"],
        "sentences": [
            "Grass-eating animals such as cows and buffaloes are called ruminants.",
            "They partially chew grass and swallow it into the stomach.",
            "The partially digested food is brought back to the mouth for gradual chewing.",
            "The thoroughly chewed food again passes down the alimentary canal for further digestion.",
        ],
        "wrong": [
            "Rumination is the exchange of gases in alveoli.",
            "Ruminants use gills to chew food.",
            "Rumination means birds swallow stones for breathing.",
        ],
    },
    {
        "slug": "breathing-mechanism",
        "question": "Describe the mechanism of breathing in humans.",
        "structure": ["Inhalation", "Chest movement", "Diaphragm", "Exhalation"],
        "sentences": [
            "During inhalation, the ribs move up and outwards.",
            "The diaphragm moves downward and increases space inside the chest.",
            "Because of this, air enters the lungs.",
            "During exhalation, ribs move down and inwards and the diaphragm moves upward.",
            "This reduces chest space and pushes air out of the lungs.",
        ],
        "wrong": [
            "During inhalation, the diaphragm moves upward first.",
            "Air enters the stomach during breathing.",
            "The oesophagus controls inhalation and exhalation.",
        ],
    },
    {
        "slug": "gas-exchange-alveoli",
        "question": "Explain how gas exchange takes place in the alveoli.",
        "structure": ["Alveoli", "Oxygen", "Carbon dioxide", "Transport"],
        "sentences": [
            "Alveoli are small balloon-like sacs in the lungs.",
            "They have thin walls and are surrounded by blood vessels.",
            "Oxygen from the alveoli passes into the blood.",
            "Carbon dioxide from the blood passes into the alveoli and is breathed out.",
            "Blood then transports oxygen to different parts of the body.",
        ],
        "wrong": [
            "Alveoli secrete bile to digest fats.",
            "Carbon dioxide enters blood from food in the stomach.",
            "Oxygen is absorbed by the large intestine.",
        ],
    },
    {
        "slug": "respiration-equation",
        "question": "Explain respiration with the word equation.",
        "structure": ["Glucose", "Oxygen", "Products", "Energy"],
        "sentences": [
            "Respiration uses oxygen to break down glucose inside the body.",
            "The word equation is glucose plus oxygen gives carbon dioxide, water and energy.",
            "The released energy helps us walk, run, play and think.",
            "Breathing supplies oxygen and removes carbon dioxide, but respiration releases energy.",
        ],
        "wrong": [
            "Respiration converts bile into starch.",
            "The equation for respiration produces only oxygen.",
            "Respiration is the same as chewing food.",
        ],
    },
    {
        "slug": "breathing-in-animals",
        "question": "How do different animals breathe according to their habitats?",
        "structure": ["Lungs", "Gills", "Frogs", "Moist skin"],
        "sentences": [
            "Many animals such as birds, elephants, lions, cows and snakes breathe through lungs.",
            "Most aquatic animals like fish use gills for gas exchange in water.",
            "Tadpoles breathe through gills, while adult frogs use lungs on land and skin in water.",
            "Earthworms exchange oxygen and carbon dioxide through their moist skin.",
            "These examples show that breathing mechanisms are adapted to habitats.",
        ],
        "wrong": [
            "All animals breathe only through lungs.",
            "Fish breathe through the large intestine.",
            "Earthworms use dry skin for gas exchange.",
        ],
    },
]


ALL_CHAPTER_QUESTION_SETS = CHAPTER_QUESTION_SETS + MAJOR_CHAPTER_QUESTION_SETS


def extract_key_sentences(extracted_text: str, count: int = 12) -> list[str]:
    cleaned = re.sub(r"\s+", " ", extracted_text)
    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    skip_patterns = re.compile(r"(copyright|isbn|rationalised|chapter|figure|activity|exercise|page)", re.IGNORECASE)
    picked: list[str] = []
    for sentence in sentences:
        sentence = sentence.strip(" -")
        if not (55 <= len(sentence) <= 190):
            continue
        if skip_patterns.search(sentence):
            continue
        if sentence in picked:
            continue
        picked.append(sentence)
        if len(picked) >= count:
            break
    while len(picked) < count:
        picked.append("The lesson includes an important idea that students should explain clearly.")
    return picked


def display_chapter_title() -> str:
    chapter = str(ACTIVE_META.chapter or "").strip()
    if re.fullmatch(r"[a-z]{3,6}\d{2,4}", chapter, flags=re.IGNORECASE):
        return f"Lesson {ACTIVE_META.chapter_number}"
    return chapter or f"Lesson {ACTIVE_META.chapter_number}"


def generic_question_sets(extracted_text: str) -> list[dict[str, Any]]:
    sentences = extract_key_sentences(extracted_text, 24)
    chapter_title = display_chapter_title()
    groups: list[dict[str, Any]] = []
    templates = [
        ("chapter-overview", f"What are the main ideas in {chapter_title}?", ["Introduction", "Key idea 1", "Key idea 2", "Conclusion"], sentences[0:4]),
        ("important-process", f"Put the events or ideas from {chapter_title} in the correct order.", ["First", "Next", "Then", "Finally"], sentences[4:8]),
        ("cause-effect", f"What happens in {chapter_title}, and why does it happen?", ["Cause", "Effect", "Reason", "Result"], sentences[8:12]),
        ("definition-and-example", f"What important word or idea do we learn in {chapter_title}?", ["Term", "Meaning", "Example", "Use"], sentences[12:16]),
        ("short-answer", f"Write a short answer using key points from {chapter_title}.", ["Point 1", "Point 2", "Point 3", "Closing"], sentences[16:20]),
    ]
    for slug, question, structure, selected in templates:
        groups.append(
            {
                "slug": slug,
                "question": question,
                "structure": structure,
                "sentences": selected,
                "wrong": [
                    f"This option does not match {chapter_title}.",
                    "The answer should ignore the facts given in the lesson.",
                    "Only one random word is enough for a complete answer.",
                ],
            }
        )
    return groups


def class_1_question_sets(extracted_text: str) -> list[dict[str, Any]]:
    sentences = extract_key_sentences(extracted_text, 18)
    chapter = ACTIVE_META.chapter
    simple_title = re.sub(r"^(Unit \d+ )?Chapter \d+:\s*", "", chapter).strip()
    if ACTIVE_META.subject == "Mathematics" and "Finding the Funny Cat" in chapter:
        return [
            {
                "slug": "cat-room-places",
                "question": "Where can we see the cat in the room?",
                "structure": ["On", "Under", "Inside", "Outside"],
                "sentences": [
                    "The cat is on the window shed.",
                    "The cat is under the bed.",
                    "The cat is inside the backpack.",
                    "The cat is outside the red rack.",
                ],
                "wrong": [
                    "The cat is sleeping in the sky.",
                    "Count the mangoes only.",
                    "This tells a different story.",
                ],
                "visualArt": "assets/question-art/class1-math-ai/cat-room-places.png",
            },
            {
                "slug": "position-words",
                "question": "Which position words tell where the cat is?",
                "structure": ["On", "Under", "Inside", "Outside"],
                "sentences": [
                    "On means above and touching.",
                    "Under means below something.",
                    "Inside means in something.",
                    "Outside means not in something.",
                ],
                "wrong": [
                    "Blue is a colour word.",
                    "Seven is a number word.",
                    "Run is an action word.",
                ],
                "visualArt": "assets/question-art/class1-math-ai/position-words.png",
            },
            {
                "slug": "cat-movement",
                "question": "How did the cat move in the song?",
                "structure": ["Below", "Above", "Bottom", "Top"],
                "sentences": [
                    "The cat hid below the mat.",
                    "The cat hopped above the hat.",
                    "The cat scratched the bottom of the jar.",
                    "The cat played at the top of the car.",
                ],
                "wrong": [
                    "The cat counted ten pencils.",
                    "The cat wrote a long sentence.",
                    "The cat became a big tree.",
                ],
                "visualArt": "assets/question-art/class1-math-ai/cat-movement.png",
            },
            {
                "slug": "find-hidden-cat",
                "question": "How can we find the hidden cat?",
                "structure": ["Look", "Listen", "Check", "Say"],
                "sentences": [
                    "Look around the room.",
                    "Listen to the position words.",
                    "Check each place carefully.",
                    "Say where the cat is.",
                ],
                "wrong": [
                    "Close your eyes and guess.",
                    "Look only at the ceiling.",
                    "Forget the position words.",
                ],
                "visualArt": "assets/question-art/class1-math-ai/find-hidden-cat.png",
            },
        ]
    simple_words = [
        word.lower()
        for word in re.findall(r"[A-Za-z]{3,}", extracted_text)
        if word.lower()
        not in {
            "chapter",
            "unit",
            "page",
            "copyright",
            "national",
            "education",
            "textbook",
            "children",
            "teacher",
            "students",
        }
    ]
    unique_words = list(dict.fromkeys(simple_words))[:8]
    if len(unique_words) < 4:
        unique_words = [word.lower() for word in re.findall(r"[A-Za-z]{3,}", simple_title)] or ["learn", "read", "say", "write"]

    return [
        {
            "slug": "read-and-arrange",
            "question": f"Read the chapter '{simple_title}'. Arrange the lines to make a small answer.",
            "structure": ["First line", "Next line", "Last line"],
            "sentences": sentences[:3],
            "wrong": [
                "This line is not about the chapter.",
                "This answer does not match the story or lesson.",
                "This line should not come in the answer.",
            ],
        },
        {
            "slug": "word-meaning",
            "question": f"Which words help us talk about '{simple_title}'?",
            "structure": ["Word 1", "Word 2", "Word 3", "Word 4"],
            "sentences": [f"The word '{word}' is used in this lesson." for word in unique_words[:4]],
            "wrong": [
                "The word is not connected to this lesson.",
                "This option is only a random sentence.",
                "This does not help us answer the question.",
            ],
        },
        {
            "slug": "short-answer",
            "question": f"Make a short answer about '{simple_title}'.",
            "structure": ["Who or what", "What happens", "What we learn"],
            "sentences": sentences[3:6],
            "wrong": [
                "A short answer should ignore the chapter.",
                "The answer can be only one random word.",
                "The answer should be about a different book.",
            ],
        },
        {
            "slug": "listen-and-tell",
            "question": f"Tell one clear thing from '{simple_title}'.",
            "structure": ["Start", "Detail", "Finish"],
            "sentences": sentences[6:9],
            "wrong": [
                "This detail is not from the lesson.",
                "This sentence does not make a clear answer.",
                "This belongs to another chapter.",
            ],
        },
    ]


def generic_answer_builder_activities(start_index: int, question_sets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    original_sets = ALL_CHAPTER_QUESTION_SETS
    globals()["ALL_CHAPTER_QUESTION_SETS"] = question_sets
    try:
        return chapter_answer_builder_activities(start_index)
    finally:
        globals()["ALL_CHAPTER_QUESTION_SETS"] = original_sets


def class_1_core_activities(start_index: int, extracted_text: str) -> list[dict[str, Any]]:
    sentences = extract_key_sentences(extracted_text, 16)
    chapter = re.sub(r"^(Unit \d+ )?Chapter \d+:\s*", "", ACTIVE_META.chapter).strip()
    words = list(dict.fromkeys(re.findall(r"[A-Za-z]{3,}", extracted_text.lower())))[:10]
    if len(words) < 6:
        words = ["read", "listen", "tell", "write", "count", "learn"]

    activities: list[dict[str, Any]] = []

    def add(activity_type: str, question: str, selected: list[str], structure: list[str], ordered: bool = False) -> None:
        correct = [chunk(f"c1-{activity_type}-{index}", text, index) for index, text in enumerate(selected, start=1)]
        answer_key: dict[str, Any] = {"requiredItemIds": [item["id"] for item in correct]}
        sequence = None
        if ordered:
            sequence = [item["id"] for item in correct]
            answer_key = {"orderedItemIds": sequence}
        activities.append(
            base_activity(
                start_index + len(activities),
                activity_type,
                "standard",
                question,
                "Choose the correct cards for this Class 1 activity.",
                structure,
                correct,
                [
                    distractor(f"c1-{activity_type}-x1", "This card is not about the chapter.", "Unrelated card."),
                    distractor(f"c1-{activity_type}-x2", "This card does not complete the answer.", "Incomplete answer."),
                ],
                [{"id": f"slot-{index}", "label": label} for index, label in enumerate(structure, start=1)],
                answer_key,
                " ".join(selected),
                ["Read the question first.", "Pick only the cards that match the lesson."],
                sequence,
                marks=3,
            )
        )

    add("short_answer_key_points", f"What is '{chapter}' about?", sentences[:3], ["Point 1", "Point 2", "Point 3"])
    add("fill_blanks", f"Complete simple lines from '{chapter}'.", sentences[3:6], ["Line 1", "Line 2", "Line 3"], ordered=True)
    add("match_following", f"Match words from '{chapter}'.", [f"{word} is an important word." for word in words[:4]], ["Word 1", "Word 2", "Word 3", "Word 4"])
    add("sequencing_steps_process", f"Put the answer about '{chapter}' in order.", sentences[6:9], ["First", "Next", "Last"], ordered=True)
    ending_question, ending_correct, ending_distractors, ending_slots, ending_key, ending_answer, ending_hints = choose_correct_ending_payload(
        "c1-choose_correct_ending",
        sentences[:3],
        [
            "This card is not about the chapter.",
            "This sentence does not make a correct ending.",
            "This belongs to another lesson.",
        ],
    )
    activities.append(
        base_activity(
            start_index + len(activities),
            "choose_correct_ending",
            "standard",
            ending_question,
            "Choose the correct ending for each blank.",
            ["Sentence", "Ending"],
            ending_correct,
            ending_distractors,
            ending_slots,
            ending_key,
            ending_answer,
            ending_hints,
            [item["id"] for item in ending_correct],
            marks=3,
        )
    )
    return activities


def generic_core_activities(start_index: int, extracted_text: str) -> list[dict[str, Any]]:
    sentences = extract_key_sentences(extracted_text, 30)
    activities: list[dict[str, Any]] = []

    def items(prefix: str, selected: list[str]) -> list[dict[str, Any]]:
        return [chunk(f"{prefix}-{index}", text, index) for index, text in enumerate(selected, start=1)]

    def wrong(prefix: str) -> list[dict[str, Any]]:
        return [
            distractor(f"{prefix}-x1", f"{ACTIVE_META.chapter} should be answered without using chapter facts.", "Rejects source evidence."),
            distractor(f"{prefix}-x2", "An unrelated statement can replace a factual answer.", "Irrelevant distractor."),
        ]

    def add(activity_type: str, question: str, selected: list[str], structure: list[str], key: Any | None = None) -> None:
        correct = items(activity_type, selected)
        if key is None:
            key = {"requiredItemIds": [item["id"] for item in correct]}
        activities.append(
            base_activity(
                start_index + len(activities),
                activity_type,
                "standard",
                question,
                "Use the source-based options to complete this activity.",
                structure,
                correct,
                wrong(activity_type),
                [{"id": f"slot-{index}", "label": label} for index, label in enumerate(structure, start=1)],
                key,
                " ".join(selected),
                ["Use only statements supported by the chapter.", "Ignore unrelated distractors."],
                key.get("orderedItemIds") if isinstance(key, dict) and "orderedItemIds" in key else None,
            )
        )

    if ACTIVE_META.class_level == 12:
        explain_correct = items("explain", sentences[0:4])
        explain_wrong = wrong("explain") + [
            distractor("explain-x3", "A correct answer can ignore the order of ideas.", "Order matters in an explain answer."),
            distractor("explain-x4", "Only a copied keyword is enough for full marks.", "A Class 12 answer needs connected explanation."),
        ]
        activities.append(
            base_activity(
                start_index + len(activities),
                "explain",
                "standard",
                f"Use {ACTIVE_META.chapter} to answer: Explain the main idea in ordered subparts.",
                "Click the correct parts in order. They will join into one answer. Leave the wrong lines outside.",
                ["Opening", "Key point", "Support", "Conclusion"],
                explain_correct,
                explain_wrong,
                [{"id": "answer", "label": "Answer"}],
                {"orderedItemIds": [item["id"] for item in explain_correct]},
                " ".join(sentences[0:4]),
                ["Start with the main idea.", "Then add supporting details in logical order.", "Do not use lines that are unrelated or too vague."],
                [item["id"] for item in explain_correct],
            )
        )
    else:
        add("explain", f"Explain the main idea of {ACTIVE_META.chapter}.", sentences[0:4], ["Opening", "Key point", "Support", "Conclusion"])
    add("compare_contrast", f"Compare two important ideas from {ACTIVE_META.chapter}.", sentences[4:8], ["Idea A", "Idea B", "Similarity", "Difference"])
    add("cause_effect", f"Connect causes and effects from {ACTIVE_META.chapter}.", sentences[8:12], ["Cause 1", "Effect 1", "Cause 2", "Effect 2"], {"pairs": [["cause_effect-1", "cause_effect-2"], ["cause_effect-3", "cause_effect-4"]]})
    add("process_sequence", f"Arrange key steps or ideas from {ACTIVE_META.chapter} in order.", sentences[12:16], ["Step 1", "Step 2", "Step 3", "Step 4"], {"orderedItemIds": [f"process_sequence-{i}" for i in range(1, 5)]})
    add("pros_cons", f"Sort useful and less useful statements about {ACTIVE_META.chapter}.", sentences[16:20], ["Useful", "Less useful"])
    add("problem_solution", f"Identify a problem and solution connected to {ACTIVE_META.chapter}.", sentences[20:24], ["Problem", "Evidence", "Solution", "Result"])
    add("fill_blanks", f"Complete a passage from {ACTIVE_META.chapter}.", sentences[0:4], ["Blank 1", "Blank 2", "Blank 3", "Blank 4"], {"orderedItemIds": [f"fill_blanks-{i}" for i in range(1, 5)]})
    add("true_false_not_given", f"Classify statements based on {ACTIVE_META.chapter}.", sentences[4:8], ["True", "False", "Not Given"])
    add("short_answer_key_points", f"List key points from {ACTIVE_META.chapter}.", sentences[8:12], ["Point 1", "Point 2", "Point 3"])
    add("match_following", f"Match ideas and meanings from {ACTIVE_META.chapter}.", sentences[12:16], ["Match 1", "Match 2", "Match 3", "Match 4"])
    add("data_chart_table", f"Use chapter information from {ACTIVE_META.chapter} to make inferences.", sentences[16:20], ["Data", "Inference 1", "Inference 2"])
    add("paragraph_essay_structure", f"Arrange a paragraph about {ACTIVE_META.chapter}.", sentences[20:25], ["Topic", "Support 1", "Support 2", "Support 3", "Conclusion"], {"orderedItemIds": [f"paragraph_essay_structure-{i}" for i in range(1, 6)]})
    if ACTIVE_META.class_level == 12:
        definition_correct = items("definition_term", sentences[0:4])
        definition_wrong = wrong("definition_term") + [
            distractor("definition_term-x3", "A definition can skip the key features of the concept.", "Definition answers need key features."),
            distractor("definition_term-x4", "An example alone is a complete definition.", "An example supports but does not replace the definition."),
        ]
        activities.append(
            base_activity(
                start_index + len(activities),
                "definition_term",
                "standard",
                f"Use {ACTIVE_META.chapter} to answer: Build the definition in correct order.",
                "Click the correct parts in order. They will join into one answer. Leave the wrong lines outside.",
                ["Definition", "Meaning", "Example", "Conclusion"],
                definition_correct,
                definition_wrong,
                [{"id": "answer", "label": "Answer"}],
                {"orderedItemIds": [item["id"] for item in definition_correct]},
                " ".join(sentences[0:4]),
                ["Start with the definition.", "Add meaning and support in order.", "Leave vague or unrelated lines outside."],
                [item["id"] for item in definition_correct],
            )
        )
    else:
        add("definition_term", f"Build a definition from {ACTIVE_META.chapter}.", sentences[0:4], ["Term", "Meaning", "Example"])
    add("timeline_chronological_order", f"Arrange chronological or logical ideas from {ACTIVE_META.chapter}.", sentences[4:9], ["1", "2", "3", "4", "5"], {"orderedItemIds": [f"timeline_chronological_order-{i}" for i in range(1, 6)]})
    add("identify_main_idea", f"Identify the main idea of a passage from {ACTIVE_META.chapter}.", sentences[9:12], ["Main idea"])
    if ACTIVE_META.class_level == 12:
        evidence_question, evidence_correct, evidence_distractors, evidence_slots, evidence_key, evidence_model, evidence_hints = evidence_support_quiz_payload(
            "evidence_support_statement",
            sentences[12],
            sentences[13],
            sentences[14],
        )
        activities.append(
            base_activity(
                start_index + len(activities),
                "evidence_support_statement",
                "standard",
                evidence_question,
                "Click the correct parts in order. They will join into one answer. Leave the wrong lines outside.",
                ["Claim", "Evidence", "Support", "Link"],
                evidence_correct,
                evidence_distractors,
                evidence_slots,
                evidence_key,
                evidence_model,
                evidence_hints,
                evidence_key.get("orderedItemIds"),
            )
        )
    else:
        add("evidence_support_statement", f"Choose evidence that supports a statement from {ACTIVE_META.chapter}.", sentences[12:15], ["Evidence"])
    add("sequencing_steps_process", f"Sequence a process from {ACTIVE_META.chapter}.", sentences[15:19], ["Step 1", "Step 2", "Step 3", "Step 4"], {"orderedItemIds": [f"sequencing_steps_process-{i}" for i in range(1, 5)]})
    ending_question, ending_correct, ending_distractors, ending_slots, ending_key, ending_answer, ending_hints = choose_correct_ending_payload(
        "choose_correct_ending",
        sentences[19:22],
        [item["text"] for item in wrong("choose_correct_ending")],
    )
    activities.append(
        base_activity(
            start_index + len(activities),
            "choose_correct_ending",
            "standard",
            ending_question,
            "Choose the correct ending for each blank.",
            ["Sentence", "Ending"],
            ending_correct,
            ending_distractors,
            ending_slots,
            ending_key,
            ending_answer,
            ending_hints,
            [item["id"] for item in ending_correct],
        )
    )
    add("multiple_correct_answers", f"Select all correct statements from {ACTIVE_META.chapter}.", sentences[22:26], ["Correct statements"])
    add("formulate_question", f"Formulate a question for an answer from {ACTIVE_META.chapter}.", sentences[26:28], ["Question"])
    add("assertion_reason", f"Build an assertion-reason answer from {ACTIVE_META.chapter}.", sentences[28:30] + sentences[0:1], ["Assertion", "Reason", "Relationship"])
    return activities


def split_sentence(sentence: str) -> tuple[str, str]:
    words = sentence.split()
    midpoint = max(2, len(words) // 2)
    return " ".join(words[:midpoint]), " ".join(words[midpoint:])


def chapter_answer_builder_activities(start_index: int) -> list[dict[str, Any]]:
    activities: list[dict[str, Any]] = []
    for question_number, question_set in enumerate(ALL_CHAPTER_QUESTION_SETS, start=1):
        slug = question_set["slug"]
        group_id = f"chapter-q{question_number:02d}-{slug}"
        sentences = question_set["sentences"]
        wrong = question_set["wrong"]
        layout_profile = identify_question_layout(question_set["question"], question_set["structure"])
        easy_items = [chunk(f"{group_id}-e-{index}", sentence, index, question_set["structure"][min(index - 1, len(question_set["structure"]) - 1)]) for index, sentence in enumerate(sentences, start=1)]
        moderate_items: list[dict[str, Any]] = []
        for index, sentence in enumerate(sentences, start=1):
            first, second = split_sentence(sentence)
            moderate_items.append(chunk(f"{group_id}-m-{index}a", first, (index * 2) - 1))
            moderate_items.append(chunk(f"{group_id}-m-{index}b", second, index * 2))
        phrase_items = [
            chunk(f"{group_id}-d-{index}", phrase, index)
            for index, phrase in enumerate([part.lower() for part in question_set["structure"]] + [sentence.split()[0].lower() for sentence in sentences[:2]], start=1)
        ]

        mode_specs = [
            ("easy", easy_items, [distractor(f"{group_id}-e-x{index}", text, "Distractor from the same chapter but not correct for this answer.") for index, text in enumerate(wrong, start=1)], [{"id": f"slot-{index}", "label": f"Sentence {index}"} for index in range(1, len(easy_items) + 1)], {"orderedItemIds": [item["id"] for item in easy_items]}, [item["id"] for item in easy_items]),
            ("moderate", moderate_items, [distractor(f"{group_id}-m-x{index}", text, "Incorrect half-sentence distractor.") for index, text in enumerate(wrong, start=1)], [{"id": f"slot-{index}", "label": f"Part {index}"} for index in range(1, len(moderate_items) + 1)], {"orderedItemIds": [item["id"] for item in moderate_items]}, [item["id"] for item in moderate_items]),
            ("difficult", phrase_items, [distractor(f"{group_id}-d-x{index}", text, "Incorrect phrase distractor.") for index, text in enumerate(wrong, start=1)], [{"id": "intro", "label": "Opening"}, {"id": "body", "label": "Main explanation"}, {"id": "end", "label": "Conclusion"}], {"requiredConceptIds": [item["id"] for item in phrase_items]}, [item["id"] for item in phrase_items]),
        ]

        for mode, correct_items, wrong_items, slots, answer_key, sequence in mode_specs:
            activity = base_activity(
                start_index + len(activities),
                "answer_builder",
                mode,
                question_set["question"],
                "Place the options in the correct placeholders. The sentence order must match the answer key.",
                question_set["structure"],
                correct_items,
                wrong_items,
                slots,
                answer_key,
                " ".join(sentences),
                ["Follow the sequence of the concept.", "Leave distractors unused until you submit."],
                sequence,
            )
            activity["questionGroupId"] = group_id
            activity["chapterQuestionNumber"] = question_number
            activity["questionIdentifier"] = {
                "layoutProfileId": layout_profile["id"],
                "layoutLabel": layout_profile["label"],
                "primaryPracticeType": layout_profile["primaryType"],
                "slotStrategy": layout_profile["slotStrategy"],
                "recommendedLayout": layout_profile["layout"],
            }
            if question_set.get("visualArt"):
                activity["visualArt"] = question_set["visualArt"]
            activities.append(activity)
    return activities


def build_dataset(meta: ChapterMeta = PILOT_META) -> dict[str, Any]:
    global ACTIVE_META
    ACTIVE_META = meta
    extracted_text = extract_pdf_text(meta.pdf_path)
    if meta == PILOT_META:
        question_sets = ALL_CHAPTER_QUESTION_SETS
        seed_builders = answer_builder_variants(1)
        for activity in seed_builders:
            activity["questionGroupId"] = "chapter-q00-digestion-overview"
            activity["chapterQuestionNumber"] = 0
        activities = seed_builders + core_activities(4) + chapter_answer_builder_activities(25)
    elif meta.class_level == 1:
        question_sets = class_1_question_sets(extracted_text)
        activities = (
            class_1_core_activities(1, extracted_text)
            + generic_core_activities(6, extracted_text)
            + generic_answer_builder_activities(27, question_sets)
        )
    else:
        question_sets = generic_question_sets(extracted_text)
        activities = generic_core_activities(1, extracted_text) + generic_answer_builder_activities(22, question_sets)
    return {
        "version": 1,
        "generatedBy": "scripts/build_practice_data.py",
        "source": {
            "root": str(SOURCE_ROOT),
            "pdfPath": str(meta.pdf_path),
            "classLevel": meta.class_level,
            "stream": meta.stream,
            "subject": meta.subject,
            "book": meta.book,
            "chapter": meta.chapter,
            "chapterNumber": meta.chapter_number,
            "pageCount": None,
            "extractedCharacterCount": len(extracted_text),
            "extractionPreview": extracted_text[:500],
        },
        "coverage": {
            "classes": [meta.class_level],
            "questionTypeCount": len(QUESTION_TYPES),
            "answerBuilderModes": ["easy", "moderate", "difficult"],
            "activityCount": len(activities),
            "chapterQuestionCount": len(question_sets),
            "layoutProfileCount": len(LAYOUT_PROFILES),
            "generationMode": "pilot-reviewed" if meta == PILOT_META else "source-derived-draft",
        },
        "layoutProfiles": LAYOUT_PROFILES,
        "chapterQuestions": [
            {
                "number": index,
                "groupId": f"chapter-q{index:02d}-{item['slug']}",
                "question": item["question"],
                "questionIdentifier": identify_question_layout(item["question"], item["structure"]),
            }
            for index, item in enumerate(question_sets, start=1)
        ],
        "activities": activities,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Learnify practice JSON from a chapter PDF.")
    parser.add_argument("--pdf", type=Path, default=PILOT_META.pdf_path)
    parser.add_argument("--class-level", type=int, default=PILOT_META.class_level)
    parser.add_argument("--stream", default=PILOT_META.stream)
    parser.add_argument("--subject", default=PILOT_META.subject)
    parser.add_argument("--book", default=PILOT_META.book)
    parser.add_argument("--chapter", default=PILOT_META.chapter)
    parser.add_argument("--chapter-number", type=int, default=PILOT_META.chapter_number)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    meta = ChapterMeta(
        class_level=args.class_level,
        stream=args.stream,
        subject=args.subject,
        book=args.book,
        chapter=args.chapter,
        chapter_number=args.chapter_number,
        pdf_path=args.pdf,
    )
    output_path = args.output or infer_output_path(meta)
    dataset = build_dataset(meta)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(dataset, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {output_path}")
    print(f"Activities: {len(dataset['activities'])}")


if __name__ == "__main__":
    main()
