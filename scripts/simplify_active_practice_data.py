from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ACTIVE_PATH = ROOT / "data" / "catalog" / "active-datasets.json"


TYPE_LABELS = {
    "explain": "Explain",
    "compare_contrast": "Compare",
    "cause_effect": "Cause and effect",
    "process_sequence": "Put in order",
    "pros_cons": "Good points and limits",
    "problem_solution": "Problem and solution",
    "fill_blanks": "Fill the blanks",
    "true_false_not_given": "True or false",
    "short_answer_key_points": "Short answer",
    "match_following": "Match",
    "data_chart_table": "Read the table",
    "paragraph_essay_structure": "Build a paragraph",
    "definition_term": "Definition",
    "timeline_chronological_order": "Timeline",
    "identify_main_idea": "Main idea",
    "evidence_support_statement": "Evidence",
    "sequencing_steps_process": "Steps",
    "choose_correct_ending": "Correct ending",
    "multiple_correct_answers": "Choose all correct",
    "formulate_question": "Make a question",
    "assertion_reason": "Assertion and reason",
}

SUBJECT_WORDS = {
    "science": ["observe", "question", "evidence", "reason", "conclusion", "nature"],
    "mathematics": ["count", "compare", "pattern", "shape", "number", "answer"],
    "english": ["read", "word", "sentence", "character", "meaning", "story"],
    "social": ["people", "place", "time", "map", "society", "reason"],
    "arts": ["look", "create", "colour", "shape", "rhythm", "expression"],
    "physical": ["body", "movement", "health", "practice", "game", "safety"],
    "vocational": ["skill", "tool", "work", "step", "care", "practice"],
}

CLASS_1_PROFILES = {
    "my family and me": {
        "question": "Who are the people in my family?",
        "sentences": [
            "I live with my family.",
            "My family loves me.",
            "We help one another.",
            "We are happy together.",
        ],
        "words": ["family", "mother", "father", "home"],
    },
    "greetings": {
        "question": "What do we say when we meet people?",
        "sentences": [
            "We say hello when we meet.",
            "We say good morning in the morning.",
            "We say thank you when someone helps us.",
            "We say goodbye when we leave.",
        ],
        "words": ["hello", "morning", "thank you", "goodbye"],
    },
    "life around us": {
        "question": "What living things do we see around us?",
        "sentences": [
            "We see plants around us.",
            "We see animals around us.",
            "Plants need water and sunlight.",
            "Animals need food and care.",
        ],
        "words": ["plants", "animals", "water", "care"],
    },
    "cap-seller": {
        "question": "What happened to the cap-seller?",
        "sentences": [
            "The cap-seller had many caps.",
            "He slept under a tree.",
            "The monkeys took his caps.",
            "The monkeys copied him and dropped the caps.",
        ],
        "words": ["cap", "seller", "monkeys", "tree"],
    },
    "a farm": {
        "question": "What can we see on a farm?",
        "sentences": [
            "A farm has plants.",
            "A farm has animals.",
            "Farmers grow food for us.",
            "We should care for animals and plants.",
        ],
        "words": ["farm", "plants", "animals", "farmer"],
    },
    "food we eat": {
        "question": "Why do we eat food?",
        "sentences": [
            "Food helps us grow.",
            "Food gives us energy.",
            "We eat fruits and vegetables.",
            "We should eat clean and healthy food.",
        ],
        "words": ["food", "grow", "energy", "healthy"],
    },
    "food": {
        "question": "Why do we need food?",
        "sentences": [
            "We eat food every day.",
            "Food gives us energy.",
            "Food helps us work and play.",
            "Good food keeps us healthy.",
        ],
        "words": ["food", "energy", "play", "healthy"],
    },
    "seasons": {
        "question": "What are seasons?",
        "sentences": [
            "Summer is hot.",
            "Rainy days bring rain.",
            "Winter is cold.",
            "We wear clothes for the season.",
        ],
        "words": ["summer", "rain", "winter", "clothes"],
    },
    "rainbow": {
        "question": "What do we see in a rainbow?",
        "sentences": [
            "A rainbow has many colours.",
            "We see a rainbow after rain.",
            "The colours look bright.",
            "A rainbow looks beautiful in the sky.",
        ],
        "words": ["rainbow", "rain", "colours", "sky"],
    },
    "funny cat": {
        "question": "How can we find the cat?",
        "sentences": [
            "We look carefully at the picture.",
            "We find the hidden cat.",
            "We notice shapes and places.",
            "We point to the cat when we find it.",
        ],
        "words": ["cat", "look", "find", "shape"],
    },
    "what is long what is round": {
        "question": "Which things are long or round?",
        "sentences": [
            "A stick can be long.",
            "A ball is round.",
            "We look at the shape.",
            "We sort things by shape.",
        ],
        "words": ["long", "round", "stick", "ball"],
    },
    "mango treat": {
        "question": "What can we count with mangoes?",
        "sentences": [
            "We count mangoes one by one.",
            "We compare more and less.",
            "We share mangoes with friends.",
            "Counting helps us find the answer.",
        ],
        "words": ["mango", "count", "more", "less"],
    },
    "making 10": {
        "question": "How can we make 10?",
        "sentences": [
            "We join two numbers.",
            "The numbers make 10 together.",
            "Five and five make 10.",
            "Making 10 helps us add.",
        ],
        "words": ["ten", "five", "add", "together"],
    },
    "how many": {
        "question": "How do we know how many?",
        "sentences": [
            "We count each object.",
            "We say the numbers in order.",
            "The last number tells how many.",
            "Counting carefully gives the answer.",
        ],
        "words": ["count", "number", "order", "answer"],
    },
    "vegetable farm": {
        "question": "What can we count on a vegetable farm?",
        "sentences": [
            "A vegetable farm has many vegetables.",
            "We can count the vegetables.",
            "We can compare big and small groups.",
            "Counting helps farmers know how many.",
        ],
        "words": ["vegetable", "farm", "count", "groups"],
    },
    "lina's family": {
        "question": "What can we learn from Lina's family?",
        "sentences": [
            "Lina has people in her family.",
            "We can count family members.",
            "Families can be big or small.",
            "We love and help our family.",
        ],
        "words": ["Lina", "family", "count", "help"],
    },
    "fun with numbers": {
        "question": "How do numbers help us?",
        "sentences": [
            "Numbers help us count.",
            "Numbers help us compare.",
            "Numbers help us find answers.",
            "We use numbers in games and daily life.",
        ],
        "words": ["numbers", "count", "compare", "answer"],
    },
    "utsav": {
        "question": "What can we count during Utsav?",
        "sentences": [
            "Utsav is a happy time.",
            "We can count people and things.",
            "We can make groups.",
            "Counting helps us enjoy the activity.",
        ],
        "words": ["utsav", "count", "people", "groups"],
    },
    "how do i spend my day": {
        "question": "What do I do in a day?",
        "sentences": [
            "I wake up in the morning.",
            "I eat, learn, and play.",
            "I do things at different times.",
            "I sleep at night.",
        ],
        "words": ["morning", "play", "time", "night"],
    },
    "how many times": {
        "question": "How do we count repeated actions?",
        "sentences": [
            "Some actions happen again and again.",
            "We count each time it happens.",
            "The total tells how many times.",
            "Counting repeats helps us answer.",
        ],
        "words": ["again", "count", "times", "total"],
    },
    "how much can we spend": {
        "question": "How do we use money carefully?",
        "sentences": [
            "We count the money we have.",
            "We see the price of things.",
            "We spend only what we can.",
            "Counting money helps us buy things.",
        ],
        "words": ["money", "price", "spend", "buy"],
    },
    "so many toys": {
        "question": "How can we count toys?",
        "sentences": [
            "We put toys in groups.",
            "We count the toys carefully.",
            "We compare more and less.",
            "Sorting toys helps us count.",
        ],
        "words": ["toys", "groups", "count", "sort"],
    },
}

CLASS_1_QUESTION_SETS = {
    "my family and me": [
        ("What can my hands do?", ["My hands can clap.", "My hands can hold things.", "My hands help me work.", "I keep my hands clean."]),
        ("What can my legs do?", ["My legs can tap.", "My legs help me walk.", "My legs help me run.", "I use my legs to play."]),
        ("What can my eyes and ears do?", ["My eyes help me see.", "My ears help me hear.", "My nose helps me smell.", "My mouth helps me talk."]),
        ("What are the parts of my body?", ["I have hands.", "I have legs.", "I have eyes and ears.", "I have a mouth and nose."]),
    ],
    "greetings": [
        ("What do we say when we meet?", ["We say hello.", "We smile at others.", "We speak politely.", "We make friends."]),
        ("What do we say in the morning?", ["We say good morning.", "We greet our family.", "We greet our teacher.", "We start the day happily."]),
        ("What do we say when someone helps us?", ["We say thank you.", "We speak kindly.", "We feel happy.", "We are polite."]),
        ("What do we say when we leave?", ["We say goodbye.", "We wave our hand.", "We leave politely.", "We meet again later."]),
    ],
    "life around us": [
        ("What living things do we see?", ["We see plants.", "We see animals.", "We see birds.", "We see people."]),
        ("What do plants need?", ["Plants need water.", "Plants need sunlight.", "Plants need soil.", "Plants grow around us."]),
        ("What do animals need?", ["Animals need food.", "Animals need water.", "Animals need care.", "Animals live around us."]),
        ("How should we care for living things?", ["We should be kind.", "We should not hurt animals.", "We should water plants.", "We should keep places clean."]),
    ],
    "cap-seller": [
        ("What did the cap-seller carry?", ["The cap-seller carried caps.", "He walked with the caps.", "He felt tired.", "He slept under a tree."]),
        ("What did the monkeys do?", ["The monkeys saw the caps.", "The monkeys took the caps.", "They sat in the tree.", "They copied the cap-seller."]),
        ("How did the cap-seller get his caps back?", ["He threw his cap down.", "The monkeys copied him.", "The monkeys dropped the caps.", "He picked up the caps."]),
        ("What do we learn from the story?", ["We should think calmly.", "We can solve problems.", "The cap-seller was clever.", "Copying can be funny."]),
    ],
    "a farm": [
        ("What do we see on a farm?", ["We see plants.", "We see animals.", "We see a farmer.", "We see food growing."]),
        ("Who works on a farm?", ["A farmer works on a farm.", "The farmer grows crops.", "The farmer cares for animals.", "The farmer works hard."]),
        ("What animals can live on a farm?", ["Cows can live on a farm.", "Goats can live on a farm.", "Hens can live on a farm.", "Animals need care."]),
        ("Why is a farm useful?", ["A farm gives us food.", "A farm has crops.", "A farm has animals.", "We should respect farmers."]),
    ],
    "food we eat": [
        ("Why do we eat food?", ["Food gives us energy.", "Food helps us grow.", "Food helps us play.", "Good food keeps us healthy."]),
        ("Which foods are healthy?", ["Fruits are healthy.", "Vegetables are healthy.", "Milk is good for us.", "Clean food is safe."]),
        ("When do we eat food?", ["We eat breakfast.", "We eat lunch.", "We eat dinner.", "We eat when we are hungry."]),
        ("How should we eat?", ["We wash our hands.", "We eat clean food.", "We chew food well.", "We do not waste food."]),
    ],
    "food": [
        ("Why do we need food?", ["Food gives us energy.", "Food helps us grow.", "Food helps us work.", "Good food keeps us healthy."]),
        ("What food do we eat?", ["We eat rice or roti.", "We eat fruits.", "We eat vegetables.", "We drink milk or water."]),
        ("How do we keep food clean?", ["We cover our food.", "We wash fruits.", "We wash our hands.", "We eat fresh food."]),
        ("Why should we not waste food?", ["Food is important.", "Many people work for food.", "We take only what we need.", "We share food with others."]),
    ],
    "seasons": [
        ("What happens in summer?", ["Summer is hot.", "We drink more water.", "We wear light clothes.", "We like shade."]),
        ("What happens on rainy days?", ["Rain falls from clouds.", "We use an umbrella.", "Plants get water.", "The ground becomes wet."]),
        ("What happens in winter?", ["Winter is cold.", "We wear warm clothes.", "We may drink warm milk.", "We keep ourselves warm."]),
        ("Why do seasons change our clothes?", ["Weather changes.", "We dress for the weather.", "Light clothes help in summer.", "Warm clothes help in winter."]),
    ],
    "rainbow": [
        ("What do we see in a rainbow?", ["A rainbow has many colours.", "It appears in the sky.", "It can come after rain.", "It looks beautiful."]),
        ("When can we see a rainbow?", ["We may see it after rain.", "Sunlight helps make a rainbow.", "The sky becomes colourful.", "We look up to see it."]),
        ("What colours can a rainbow have?", ["A rainbow has red.", "A rainbow has yellow.", "A rainbow has green.", "A rainbow has blue."]),
        ("Why do children like a rainbow?", ["It is bright.", "It has many colours.", "It looks pretty.", "It makes us happy."]),
    ],
    "funny cat": [
        ("Where is the furry cat?", ["The cat is on the window shed.", "The cat is under the bed.", "The cat is inside the backpack.", "The cat is outside the red rack."]),
        ("Which words tell us where the cat is?", ["On tells where something is.", "Under tells where something is.", "Inside tells where something is.", "Outside tells where something is."]),
        ("Where else did the cat go?", ["The cat hid below the mat.", "The cat hopped above the hat.", "The cat scratched the bottom of the jar.", "The cat played at the top of the car."]),
        ("How can we find hidden things?", ["We look carefully.", "We listen to clues.", "We use words like under and near.", "We check one place at a time."]),
    ],
    "what is long what is round": [
        ("Which things are long?", ["A pencil can be long.", "A stick can be long.", "A rope can be long.", "We can compare lengths."]),
        ("Which things are round?", ["A ball is round.", "A wheel is round.", "A plate can be round.", "A coin is round."]),
        ("How do we sort shapes?", ["We look at each object.", "We put long things together.", "We put round things together.", "Sorting helps us compare."]),
        ("How do we know the shape?", ["We look carefully.", "We touch the object.", "We say long or round.", "We match similar shapes."]),
    ],
    "mango treat": [
        ("How do we count mangoes?", ["We count one mango.", "Then we count the next mango.", "We say numbers in order.", "The last number tells how many."]),
        ("How do we compare mangoes?", ["One group can have more.", "One group can have less.", "We count both groups.", "Then we compare."]),
        ("How can we share mangoes?", ["We give mangoes to friends.", "We count before sharing.", "We try to share equally.", "Sharing makes everyone happy."]),
        ("Why is counting useful?", ["Counting tells how many.", "Counting helps us share.", "Counting helps us compare.", "Counting gives the answer."]),
    ],
    "making 10": [
        ("How can we make 10?", ["We join two numbers.", "The numbers make 10 together.", "Five and five make 10.", "Making 10 helps us add."]),
        ("Which pairs make 10?", ["One and nine make 10.", "Two and eight make 10.", "Three and seven make 10.", "Four and six make 10."]),
        ("Why do we learn making 10?", ["It helps us add fast.", "It helps us count better.", "It helps us solve sums.", "It makes numbers easy."]),
        ("How do we check 10?", ["We count all objects.", "We see if there are 10.", "We add the two groups.", "We check the answer."]),
    ],
    "how many": [
        ("How do we know how many?", ["We count each object.", "We say numbers in order.", "We do not skip any object.", "The last number tells how many."]),
        ("What should we do while counting?", ["We point to one object.", "We say one number.", "We count slowly.", "We check again."]),
        ("How can we compare two groups?", ["We count the first group.", "We count the second group.", "We see which has more.", "We see which has less."]),
        ("Why should we count carefully?", ["Careful counting avoids mistakes.", "It gives the correct number.", "It helps us answer.", "It helps us compare."]),
    ],
    "vegetable farm": [
        ("What is on a vegetable farm?", ["There are vegetables.", "There are plants.", "There may be baskets.", "Farmers work there."]),
        ("How can we count vegetables?", ["We count one by one.", "We make small groups.", "We count each group.", "We find the total."]),
        ("How can we compare vegetables?", ["One basket may have more.", "One basket may have less.", "We count both baskets.", "Then we compare."]),
        ("Why do farmers count?", ["Farmers count vegetables.", "Counting tells how many.", "Counting helps sell vegetables.", "Counting helps share vegetables."]),
    ],
    "lina's family": [
        ("Who is in Lina's family?", ["Lina has family members.", "Some are older.", "Some are younger.", "Family members help each other."]),
        ("How can we count family members?", ["We count each person.", "We say numbers in order.", "We do not count twice.", "The last number tells how many."]),
        ("Are all families the same?", ["Some families are small.", "Some families are big.", "Families can be different.", "All families are special."]),
        ("What do families do?", ["Families care for us.", "Families help us.", "Families eat together.", "Families love one another."]),
    ],
    "fun with numbers": [
        ("How do numbers help us?", ["Numbers help us count.", "Numbers help us compare.", "Numbers help us find answers.", "Numbers are used every day."]),
        ("Where do we see numbers?", ["We see numbers in books.", "We see numbers on clocks.", "We see numbers on houses.", "We see numbers in games."]),
        ("How do we put numbers in order?", ["We start with the small number.", "We say numbers one by one.", "We do not skip numbers.", "We stop at the last number."]),
        ("Why are numbers fun?", ["We can count toys.", "We can play number games.", "We can solve puzzles.", "We can find answers."]),
    ],
    "utsav": [
        ("What happens during Utsav?", ["People come together.", "There is joy.", "We see many things.", "We can count them."]),
        ("What can we count during Utsav?", ["We can count people.", "We can count flowers.", "We can count plates.", "We can count decorations."]),
        ("How do we make groups?", ["We put similar things together.", "We count each group.", "We compare groups.", "Groups make counting easy."]),
        ("Why is Utsav special?", ["People celebrate together.", "Everyone feels happy.", "We share things.", "We enjoy the day."]),
    ],
    "how do i spend my day": [
        ("What do I do in the morning?", ["I wake up.", "I brush my teeth.", "I eat breakfast.", "I get ready."]),
        ("What do I do in the day?", ["I learn.", "I play.", "I eat lunch.", "I help at home."]),
        ("What do I do at night?", ["I eat dinner.", "I clean up.", "I rest.", "I sleep at night."]),
        ("Why do we follow time?", ["Time tells us what to do.", "Morning has some activities.", "Day has some activities.", "Night is for rest."]),
    ],
    "how many times": [
        ("How do we count repeated actions?", ["We watch the action.", "We count each time.", "We do not skip any turn.", "The total tells how many times."]),
        ("What can happen many times?", ["We can clap many times.", "We can jump many times.", "We can tap many times.", "We can count each action."]),
        ("Why do we count repeats?", ["It tells how many times.", "It helps us compare.", "It helps us play games.", "It gives a clear answer."]),
        ("How do we check the total?", ["We count again.", "We say numbers in order.", "We match action and number.", "We check the last number."]),
    ],
    "how much can we spend": [
        ("How do we use money carefully?", ["We count the money.", "We check the price.", "We buy what we need.", "We do not spend too much."]),
        ("What should we do before buying?", ["We see what we want.", "We ask the price.", "We count our money.", "We decide if we can buy it."]),
        ("Why do we count money?", ["Money helps us buy things.", "Counting tells how much we have.", "Counting helps us pay.", "Counting helps us save."]),
        ("How can we spend less?", ["We buy only what we need.", "We compare prices.", "We save some money.", "We spend carefully."]),
    ],
    "so many toys": [
        ("How can we count toys?", ["We put toys together.", "We count one by one.", "We say numbers in order.", "The last number tells how many."]),
        ("How can we sort toys?", ["We keep same toys together.", "We make small groups.", "We count each group.", "Sorting helps us count."]),
        ("How can we compare toys?", ["One group may have more.", "One group may have less.", "We count both groups.", "Then we compare."]),
        ("Why should we keep toys properly?", ["Toys stay safe.", "We can find them easily.", "We can count them.", "Our room stays clean."]),
    ],
}

TOPIC_PROFILES = {
    "ever-evolving world of science": {
        "question": "What is science about?",
        "sentences": [
            "Science is a way to ask questions about the world.",
            "We observe things carefully.",
            "We do experiments to test our ideas.",
            "Evidence helps us make better conclusions.",
        ],
        "words": ["question", "observe", "experiment", "evidence"],
    },
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def clean_title(value: str, chapter_number: int, book: str) -> str:
    title = re.sub(r"^(Unit \d+ )?Chapter \d+:\s*", "", value).strip()
    if not title or re.fullmatch(r"[a-z]{4}\d{3}", title.lower()) or title.lower().startswith("chapter "):
        return f"Chapter {chapter_number} of {book}"
    return title


def preview_title(data: dict[str, Any]) -> str | None:
    preview = str(data.get("source", {}).get("extractionPreview", ""))
    for line in preview.splitlines():
        line = re.sub(r"\s+", " ", line).strip(" -")
        if not (5 <= len(line) <= 80):
            continue
        if re.search(r"copyright|isbn|teacher|textbook|chapter\s*\d+$", line, re.IGNORECASE):
            continue
        if len(re.findall(r"[A-Za-z]", line)) < 4:
            continue
        return line
    return None


def subject_words(subject: str, book: str) -> list[str]:
    text = f"{subject} {book}".lower()
    for key, words in SUBJECT_WORDS.items():
        if key in text:
            return words
    return ["read", "think", "choose", "explain", "check", "learn"]


def topic(data: dict[str, Any]) -> str:
    source = data.get("source", {})
    title = clean_title(str(source.get("chapter", "this chapter")), int(source.get("chapterNumber") or 1), str(source.get("book", "the book")))
    if title.lower().startswith("chapter ") and " of " in title:
        return preview_title(data) or title
    return title


def class_1_profile(data: dict[str, Any]) -> dict[str, Any] | None:
    if int(data.get("source", {}).get("classLevel") or 0) != 1:
        return None
    title = topic(data).lower().replace("’", "'")
    for key, profile in CLASS_1_PROFILES.items():
        if key in title:
            return profile
    return None


def class_1_question_set(data: dict[str, Any], group_number: int) -> tuple[str, list[str]] | None:
    if int(data.get("source", {}).get("classLevel") or 0) != 1:
        return None
    title = topic(data).lower().replace("’", "'")
    for key, question_sets in CLASS_1_QUESTION_SETS.items():
        if key in title:
            index = max(group_number - 1, 0) % len(question_sets)
            question, sentences = question_sets[index]
            return question, list(sentences)
    profile = class_1_profile(data)
    if profile:
        return str(profile["question"]), list(profile["sentences"])
    return None


def topic_profile(data: dict[str, Any]) -> dict[str, Any] | None:
    title = topic(data).lower().replace("’", "'")
    for key, profile in TOPIC_PROFILES.items():
        if key in title:
            return profile
    return None


def student_level(data: dict[str, Any]) -> str:
    class_level = int(data.get("source", {}).get("classLevel") or 0)
    return "simple" if class_level <= 2 else "clear"


def sentence_bank(data: dict[str, Any], count: int, group_number: int = 1) -> list[str]:
    source = data.get("source", {})
    topic_name = topic(data)
    subject = str(source.get("subject", "this subject"))
    book = str(source.get("book", "the book"))
    words = subject_words(subject, book)
    simple = student_level(data) == "simple"
    class_1_set = class_1_question_set(data, group_number)
    profile = class_1_profile(data) or topic_profile(data)
    if class_1_set:
        base = class_1_set[1]
    elif profile:
        base = list(profile["sentences"])
    elif simple:
        base = [
            f"{topic_name} helps us read and understand the lesson.",
            f"We look at the pictures, words, and examples carefully.",
            f"We choose the cards that match the question.",
            f"We put the cards in the correct order.",
            f"We say the answer in simple words.",
            f"We check our answer and fix mistakes.",
            f"The word '{words[0]}' helps us remember this lesson.",
            f"The word '{words[1]}' is also useful in this lesson.",
        ]
    else:
        base = [
            f"{topic_name} teaches an important idea from {subject}.",
            f"The first step is to read the question carefully.",
            f"Then we choose only the cards that match the question.",
            f"A good answer uses clear words and correct order.",
            f"Examples from the chapter help us understand the idea.",
            f"We should remove cards that do not answer the question.",
            f"The word '{words[0]}' is connected to this chapter.",
            f"The word '{words[1]}' helps explain the answer.",
            f"The word '{words[2]}' gives another clue.",
            f"The word '{words[3]}' helps complete the idea.",
        ]
    while len(base) < count:
        base.append(f"This point helps complete the answer about {topic_name}.")
    return base[:count]


def phrase_bank(data: dict[str, Any], count: int, group_number: int = 1) -> list[str]:
    source = data.get("source", {})
    class_1_set = class_1_question_set(data, group_number)
    profile = class_1_profile(data) or topic_profile(data)
    if class_1_set:
        words = re.findall(r"[A-Za-z']+", " ".join(class_1_set[1]))
        base = list(dict.fromkeys(word.lower() for word in words if len(word) > 2))
        while len(base) < count:
            base.append(topic(data).lower())
        return base[:count]
    words = list(profile["words"]) if profile else subject_words(str(source.get("subject", "")), str(source.get("book", "")))
    base = [topic(data), "read the question", "choose matching cards", "correct order", "clear answer", *words]
    while len(base) < count:
        base.append("important point")
    return base[:count]


def wrong_cards(data: dict[str, Any], count: int) -> list[str]:
    topic_name = topic(data)
    if class_1_profile(data):
        base = [
            "This does not answer the question.",
            "This is not from this lesson.",
            "This card does not fit here.",
            "Leave this card outside.",
        ]
    else:
        base = [
            "This card is not connected to the question.",
            "This card is from another idea, so leave it out.",
            "This card does not help complete the answer.",
            f"This card does not explain {topic_name}.",
        ]
    while len(base) < count:
        base.append("This card is a distractor.")
    return base[:count]


def question_for_type(activity_type: str, data: dict[str, Any], group_number: int = 1) -> str:
    label = TYPE_LABELS.get(activity_type, "Answer")
    topic_name = topic(data)
    simple = student_level(data) == "simple"
    class_1_set = class_1_question_set(data, group_number)
    profile = class_1_profile(data) or topic_profile(data)
    if class_1_set:
        return class_1_set[0]
    if profile:
        return str(profile["question"])
    if activity_type == "answer_builder":
        return f"Build a good answer about '{topic_name}'."
    if simple:
        return f"{label}: choose the cards that help answer '{topic_name}'."
    return f"{label}: answer this question about {topic_name}."


def model_answer(data: dict[str, Any], group_number: int = 1) -> str:
    pieces = sentence_bank(data, 4, group_number)
    return " ".join(pieces)


def rewrite_items(items: list[dict[str, Any]], texts: list[str]) -> None:
    for index, item in enumerate(items):
        item["text"] = texts[index % len(texts)]
        if "misconception" in item:
            item["misconception"] = "This option does not answer the question."


def answer_builder_question(data: dict[str, Any], group_number: int, difficulty: str = "easy") -> str:
    class_1_set = class_1_question_set(data, group_number)
    profile = class_1_profile(data) or topic_profile(data)
    if class_1_set:
        question = class_1_set[0]
        if int(data.get("source", {}).get("classLevel") or 0) == 1:
            if difficulty == "moderate":
                return f"Put the answer parts in order: {question}"
            if difficulty == "difficult":
                return f"Choose the key words: {question}"
        return question
    if profile:
        question = str(profile["question"])
        if int(data.get("source", {}).get("classLevel") or 0) == 1:
            if difficulty == "moderate":
                return f"Put the answer parts in order: {question}"
            if difficulty == "difficult":
                return f"Choose the key words: {question}"
        return question
    topic_name = topic(data)
    questions = [
        f"What is the main idea of '{topic_name}'?",
        f"Which cards help answer a question about '{topic_name}'?",
        f"How can we write a clear answer about '{topic_name}'?",
        f"What is the correct order for an answer about '{topic_name}'?",
    ]
    return questions[(group_number - 1) % len(questions)]


def rewrite_activity(activity: dict[str, Any], data: dict[str, Any], group_number: int) -> None:
    activity_type = activity.get("type", "")
    difficulty = activity.get("difficulty", "standard")
    topic_name = topic(data)
    correct_count = len(activity.get("correctItems", []))
    wrong_count = len(activity.get("distractors", []))

    if activity_type == "answer_builder":
        activity["question"] = answer_builder_question(data, group_number, difficulty)
        if difficulty == "difficult":
            correct_texts = phrase_bank(data, correct_count, group_number)
            activity["instructions"] = "Drag the word cards that answer the question."
            activity["structureHelp"] = ["Word 1", "Word 2", "Word 3"] if class_1_profile(data) else ["Start", "Main idea", "Finish"]
        elif difficulty == "moderate":
            full = sentence_bank(data, max(4, correct_count // 2), group_number)
            split: list[str] = []
            for sentence in full:
                words = sentence.split()
                midpoint = max(2, len(words) // 2)
                split.extend([" ".join(words[:midpoint]), " ".join(words[midpoint:])])
            correct_texts = split[:correct_count]
            activity["instructions"] = "Put the small answer parts in order."
            activity["structureHelp"] = [f"Answer part {index}" for index in range(1, correct_count + 1)]
        else:
            correct_texts = sentence_bank(data, correct_count, group_number)
            activity["instructions"] = "Drag the answer cards into the boxes. Leave the wrong cards outside."
            activity["structureHelp"] = [f"Answer {index}" for index in range(1, correct_count + 1)]
    else:
        activity["question"] = question_for_type(activity_type, data, group_number)
        correct_texts = sentence_bank(data, correct_count, group_number)
        activity["instructions"] = "Choose the answer cards. Leave the wrong cards outside."

    rewrite_items(activity.get("correctItems", []), correct_texts)
    rewrite_items(activity.get("distractors", []), wrong_cards(data, wrong_count))
    if class_1_profile(data):
        activity["hints"] = [
            "Read the question.",
            "Pick only good answer cards.",
            "Put them from first to last.",
        ]
    else:
        activity["hints"] = [
            "Read the question first.",
            "Pick cards that match the question.",
            "Put the answer in a clear order.",
        ]
    activity["modelAnswer"] = model_answer(data, group_number)
    activity["sourceTextSummary"] = f"Student-friendly practice for {topic_name}."


def simplify_dataset(path: Path) -> None:
    data = load_json(path)
    answer_group_numbers: dict[str, int] = {}
    standard_number = 0
    for activity in data.get("activities", []):
        group_number = 1
        if activity.get("type") == "answer_builder":
            group_id = activity.get("questionGroupId") or activity.get("question") or activity.get("id")
            if group_id not in answer_group_numbers:
                answer_group_numbers[group_id] = len(answer_group_numbers) + 1
            group_number = answer_group_numbers[group_id]
            if class_1_profile(data):
                mode_offset = {"easy": 0, "moderate": 1, "difficult": 2}.get(activity.get("difficulty"), 0)
                group_number += mode_offset
        else:
            standard_number += 1
            group_number = standard_number
        rewrite_activity(activity, data, group_number)
    write_json(path, data)


def main() -> int:
    active = load_json(ACTIVE_PATH).get("activeDatasets", [])
    paths = [(ROOT / item["jsonPath"]).resolve() for item in active]
    changed = 0
    for path in paths:
        if not path.exists() or ROOT not in path.parents:
            continue
        simplify_dataset(path)
        changed += 1
    print(f"Simplified {changed} active dataset(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
