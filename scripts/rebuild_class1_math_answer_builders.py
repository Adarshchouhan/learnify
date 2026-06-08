from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "practice" / "class-1" / "mathematics-joyful-mathematics"


VISUALS = {
    1: ["ch01-cat-room-places.png", "ch01-position-words.png", "ch01-cat-movement.png", "ch01-find-hidden-cat.png"],
    2: ["ch02-long-things.png", "ch02-round-things.png", "ch02-shape-sort.png", "ch02-shape-check.png"],
    3: ["ch03-count-mangoes.png", "ch03-compare-mangoes.png", "ch03-share-mangoes.png", "ch03-counting-useful.png"],
    4: ["ch04-make-10.png", "ch04-pairs-make-10.png", "ch04-learn-making-10.png", "ch04-check-10.png"],
    5: ["ch05-know-how-many.png", "ch05-count-carefully.png", "ch05-compare-groups.png", "ch05-count-carefully-why.png"],
    6: ["ch06-farm-things.png", "ch06-count-vegetables.png", "ch06-compare-vegetables.png", "ch06-farmers-count.png"],
    7: ["ch07-family-members.png", "ch07-count-family.png", "ch07-compare-families.png", "ch07-family-do.png"],
    8: ["ch08-numbers-help.png", "ch08-see-numbers.png", "ch08-number-order.png", "ch08-numbers-fun.png"],
    9: ["ch09-utsav-happens.png", "ch09-count-utsav.png", "ch09-make-groups.png", "ch09-utsav-special.png"],
    10: ["ch10-morning.png", "ch10-day.png", "ch10-night.png", "ch10-follow-time.png"],
    11: ["ch11-know-how-many.png", "ch11-counting.png", "ch11-compare-groups.png", "ch11-count-carefully.png"],
    12: ["ch12-use-money.png", "ch12-before-buying.png", "ch12-count-money.png", "ch12-spend-less.png"],
    13: ["ch13-count-toys.png", "ch13-sort-toys.png", "ch13-compare-toys.png", "ch13-keep-toys.png"],
}


QUESTIONS = {
    1: [
        ("Where can the cat be in the room?", ["The cat can be on the mat.", "It can be under the chair.", "It can be inside the basket.", "Position words tell where the cat is."], ["The cat is a fruit.", "The mat is counting money.", "All shapes are mangoes."]),
        ("Which words tell where the cat is?", ["Words like on and under tell position.", "Inside tells that the cat is in something.", "Above tells that the cat is higher.", "These words help us describe place."], ["Heavy and light tell position.", "Morning and night are shapes.", "Coins show where the cat is."]),
        ("How did the cat move in the song?", ["The cat moved from one place to another.", "It went up and down.", "We can use position words for its movement.", "Movement changes where the cat is."], ["The cat became a coin.", "The cat counted vegetables.", "The cat made ten mangoes."]),
        ("How can we find the hidden cat?", ["We look carefully at each place.", "We check under and behind things.", "We use position words as clues.", "Then we can say where the cat is."], ["We close our eyes first.", "We buy the cat with coins.", "We sort the cat with shapes."]),
    ],
    2: [
        ("Which things are long?", ["A rope is long.", "A pencil can be long.", "A stick can be long.", "Long things stretch from one end to the other."], ["A ball is always long.", "A plate is a position word.", "A mango tells the time."]),
        ("Which things are round?", ["A ball is round.", "A plate is round.", "A wheel is round.", "Round things can roll or have a curved edge."], ["A rope is round like a wheel.", "A stick is a coin.", "A clock is a vegetable."]),
        ("How do we sort shapes?", ["We look at each shape.", "We put same shapes together.", "Circles go with circles.", "Sorting helps us see groups."], ["We mix all shapes without looking.", "We count only mangoes.", "We spend less to sort."]),
        ("How do we know a shape?", ["We look at its sides and corners.", "A circle has a curved edge.", "A square has equal sides.", "The shape name comes from what we see."], ["A shape is known by smell.", "A triangle is a morning time.", "Coins make every shape long."]),
    ],
    3: [
        ("How do we count mangoes?", ["We point to one mango at a time.", "We say number names in order.", "We count every mango once.", "The last number tells how many mangoes."], ["We skip some mangoes.", "We count the basket only.", "We say the numbers backwards first."]),
        ("How do we compare mangoes?", ["We count mangoes in each group.", "We look at the two counts.", "The bigger count means more mangoes.", "The smaller count means fewer mangoes."], ["We compare by color only.", "We hide the mangoes first.", "We use a clock to compare."]),
        ("How can we share mangoes?", ["We count the mangoes first.", "We give mangoes to each child.", "We try to give the same amount.", "Equal sharing is fair."], ["We keep all mangoes in one hand.", "We sort mangoes by position words.", "We spend coins to make ten."]),
        ("Why is counting useful?", ["Counting tells how many things we have.", "It helps us share fairly.", "It helps us compare groups.", "Counting helps us solve small problems."], ["Counting hides the answer.", "Counting is only for night.", "Counting changes a circle into a square."]),
    ],
    4: [
        ("How can we make 10?", ["We join two small groups.", "We count the objects together.", "If the total is ten, we made 10.", "Making 10 helps in addition."], ["We remove all objects.", "We count only one group and stop.", "We use position words only."]),
        ("Which pairs make 10?", ["One and nine make ten.", "Two and eight make ten.", "Four and six make ten.", "Five and five also make ten."], ["One and two make ten.", "Seven and one make ten.", "A rope and a chair make ten."]),
        ("Why do we learn making 10?", ["Ten is an easy number to use.", "Making 10 helps us add quickly.", "It helps us see number pairs.", "It makes counting easier."], ["Making 10 tells where the cat is.", "Making 10 means spending all money.", "Making 10 is only about vegetables."]),
        ("How do we check 10?", ["We count all the objects.", "We do not skip any object.", "We stop when the count reaches ten.", "If there are ten objects, the answer is correct."], ["We guess without counting.", "We count the same object twice.", "We check by color only."]),
    ],
    5: [
        ("How do we know how many?", ["We count the objects one by one.", "We touch or point to each object.", "We say numbers in order.", "The last number gives the total."], ["We look away while counting.", "We count only the box.", "We say any number we like."]),
        ("What should we do while counting?", ["We start from one.", "We count each object once.", "We keep the number order.", "We check that no object is missed."], ["We count one object many times.", "We mix morning and night.", "We sort coins by smell."]),
        ("How can we compare two groups?", ["We count the first group.", "We count the second group.", "We compare the two numbers.", "Then we say more, fewer, or same."], ["We compare without looking.", "We count the floor only.", "We share before counting."]),
        ("Why should we count carefully?", ["Careful counting avoids mistakes.", "It stops us from missing objects.", "It stops us from counting twice.", "It gives the correct total."], ["Careful counting makes fewer objects.", "Careful counting hides shapes.", "Careful counting is only for toys."]),
    ],
    6: [
        ("What is on a vegetable farm?", ["A vegetable farm has plants.", "It has vegetables like carrots and brinjals.", "Farmers care for the plants.", "We can count vegetables on the farm."], ["A farm has only coins.", "A farm is inside a clock.", "A farm sorts cats by shape."]),
        ("How can we count vegetables?", ["We look at one basket first.", "We count each vegetable once.", "We say the numbers in order.", "The final number tells the total."], ["We count only leaves.", "We count the same carrot twice.", "We close the basket before counting."]),
        ("How can we compare vegetables?", ["We count vegetables in each basket.", "We see which basket has more.", "We see which basket has fewer.", "Comparison helps farmers plan."], ["We compare by hiding baskets.", "We use night and day only.", "We make every vegetable round."]),
        ("Why do farmers count?", ["Farmers count seeds and plants.", "They count vegetables after harvest.", "Counting helps them share and sell.", "Counting helps them know their crop."], ["Farmers count to find a cat.", "Farmers count to change shapes.", "Farmers count only toys."]),
    ],
    7: [
        ("Who is in Lina's family?", ["Lina's family has different members.", "Parents and children can be in a family.", "Grandparents can also be in a family.", "Family members live with care and love."], ["A family is a group of coins.", "Only toys can be family members.", "A clock is Lina's uncle."]),
        ("How can we count family members?", ["We look at each person.", "We count every family member once.", "We say numbers in order.", "The last number tells the family size."], ["We count chairs instead of people.", "We count one person again and again.", "We sort family by shape only."]),
        ("Are all families the same?", ["Families can be small or big.", "Some families have grandparents.", "Some families have fewer members.", "Every family is special."], ["All families must have ten people.", "Families are always round.", "Families are counted with coins only."]),
        ("What do families do together?", ["Families eat together.", "They help each other.", "They play and work together.", "Families care for one another."], ["Families become number blocks.", "Families only count mangoes.", "Families live inside a basket."]),
    ],
    8: [
        ("How do numbers help us?", ["Numbers help us count things.", "They help us know order.", "They help us compare groups.", "Numbers help us in daily life."], ["Numbers hide all objects.", "Numbers are only for cats.", "Numbers make vegetables grow."]),
        ("Where do we see numbers?", ["We see numbers on pages.", "We see numbers on doors.", "We see numbers on clocks.", "We see numbers in many places."], ["We see numbers only inside mangoes.", "Numbers are never in books.", "Numbers are only under chairs."]),
        ("How do we put numbers in order?", ["We start with the smaller number.", "We say the next number after it.", "We keep going step by step.", "This makes a number order."], ["We jump to any number first.", "We put all numbers in a basket.", "We compare by color only."]),
        ("Why are numbers fun?", ["Numbers help us play games.", "They help us count toys.", "They help us make patterns.", "Numbers make learning interesting."], ["Numbers stop us from playing.", "Numbers are only for night.", "Numbers are not used in games."]),
    ],
    9: [
        ("What happens during Utsav?", ["People decorate the place.", "Children help and celebrate.", "There can be lamps, flowers, and sweets.", "We can count many things during Utsav."], ["Utsav means hiding all things.", "Utsav is only about clocks.", "Utsav has no groups."]),
        ("What can we count during Utsav?", ["We can count lamps.", "We can count flowers.", "We can count sweets.", "Counting helps us arrange them neatly."], ["We count only shadows.", "We count without looking.", "We count one sweet many times."]),
        ("How do we make groups?", ["We put some objects together.", "We keep the same number in each group.", "We check each group carefully.", "Equal groups are easy to count."], ["We mix all objects randomly.", "We hide one group.", "We use a rope to tell time."]),
        ("Why is Utsav special?", ["Utsav brings people together.", "Everyone shares and helps.", "We arrange things in beautiful groups.", "It is a happy time to learn and count."], ["Utsav is special because it has no people.", "Utsav means counting backwards only.", "Utsav changes circles into cats."]),
    ],
    10: [
        ("What do I do in the morning?", ["I wake up in the morning.", "I brush my teeth.", "I eat breakfast.", "Morning activities start the day."], ["I sleep for the whole day.", "I count only coins in bed.", "I keep toys under the sun."]),
        ("What do I do in the day?", ["I go to school in the day.", "I study with my class.", "I play with friends.", "Daytime has many activities."], ["I see the moon at noon.", "I sleep under the table all day.", "I buy mangoes in every lesson."]),
        ("What do I do at night?", ["I eat dinner at night.", "I get ready for bed.", "I sleep and rest.", "Night comes after the day."], ["I go to school at midnight.", "I count sunlight at night.", "I sort shapes while sleeping."]),
        ("Why do we follow time?", ["Time tells when to do things.", "It helps us follow a routine.", "It tells morning, day, and night.", "Following time keeps our day in order."], ["Time tells the shape of a mango.", "Time is only for toys.", "Time makes all groups equal."]),
    ],
    11: [
        ("How do we know how many times?", ["We count each action.", "We count every repeat once.", "We keep track as it happens.", "The total tells how many times."], ["We count only the first action.", "We guess without watching.", "We count vegetables instead."]),
        ("What should we do while counting repeated actions?", ["We watch the action carefully.", "We count one each time it happens.", "We do not skip a repeat.", "Then the count is correct."], ["We close our eyes.", "We count the same clap twice.", "We sort actions by color."]),
        ("How can we compare repeated groups?", ["We count repeats in the first group.", "We count repeats in the second group.", "We compare the two totals.", "The larger total happened more times."], ["We compare without counting.", "We count only one group.", "We use a plate to tell position."]),
        ("Why should we count repeats carefully?", ["Repeats can happen quickly.", "Careful counting stops mistakes.", "It helps us know the correct number.", "It helps us compare actions."], ["Careful counting makes actions disappear.", "Repeats are never counted.", "Counting repeats is only for money."]),
    ],
    12: [
        ("How do we use money carefully?", ["We look at the coins we have.", "We think about what we need.", "We pay the correct amount.", "Careful spending saves money."], ["We spend without counting.", "We throw coins away.", "We buy every toy at once."]),
        ("What should we do before buying?", ["We check what we want to buy.", "We look at the money we have.", "We think if we need it.", "Then we decide carefully."], ["We buy before looking.", "We count cats instead of coins.", "We spend more for no reason."]),
        ("Why do we count money?", ["Counting money tells how much we have.", "It helps us pay correctly.", "It helps us know what we can buy.", "It helps us avoid mistakes."], ["Counting money changes coins into toys.", "Counting money is only for night.", "We count money by shape words."]),
        ("How can we spend less?", ["We choose only what we need.", "We compare the cost.", "We buy the cheaper useful item.", "Then some money is saved."], ["We buy everything in the shop.", "We never look at the cost.", "We count vegetables instead of coins."]),
    ],
    13: [
        ("How can we count toys?", ["We place the toys where we can see them.", "We count one toy at a time.", "We count every toy once.", "The last number tells how many toys."], ["We hide the toys first.", "We count the shelf only.", "We count one toy many times."]),
        ("How can we sort toys?", ["We look at each toy.", "We put similar toys together.", "Cars can go with cars.", "Sorting keeps toys neat."], ["We mix all toys again.", "We sort toys by morning and night.", "We spend coins to sort."]),
        ("How can we compare toys?", ["We count toys in each group.", "We compare the two counts.", "One group may have more toys.", "Another group may have fewer toys."], ["We compare with closed eyes.", "We count only the box.", "We make every toy a circle."]),
        ("Why should we keep toys properly?", ["Keeping toys properly makes them easy to find.", "It keeps the room neat.", "It stops toys from getting lost.", "It helps us count and sort them again."], ["We keep toys properly by hiding them outside.", "Toys become coins when sorted.", "A clock keeps toys properly."]),
    ],
}


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def easy_activity(activity: dict, question: str, sentences: list[str], distractors: list[str], base: str) -> None:
    parts = sentences[:3]
    activity["difficulty"] = "easy"
    activity["question"] = question
    activity["instructions"] = "Drag the answer cards into the boxes in the correct order."
    activity["structureHelp"] = ["Start", "Next", "Finish"]
    activity["correctItems"] = [
        {"id": f"{base}-easy-{index}", "text": text, "order": index, "section": label}
        for index, (text, label) in enumerate(zip(parts, activity["structureHelp"]), start=1)
    ]
    activity["distractors"] = [
        {"id": f"{base}-easy-x{index}", "text": text, "misconception": "This card does not answer this maths question."}
        for index, text in enumerate(distractors, start=1)
    ]
    activity["answerSlots"] = [{"id": f"slot-{index}", "label": label} for index, label in enumerate(activity["structureHelp"], start=1)]
    ordered = [item["id"] for item in activity["correctItems"]]
    activity["answerKey"] = {"orderedItemIds": ordered}
    activity["correctSequence"] = ordered


def moderate_activity(activity: dict, question: str, sentences: list[str], distractors: list[str], base: str) -> None:
    activity["difficulty"] = "moderate"
    activity["question"] = question
    activity["instructions"] = "Drag the answer parts in order to build the full maths answer."
    activity["structureHelp"] = ["Idea 1", "Idea 2", "Idea 3", "Idea 4"]
    activity["correctItems"] = [
        {"id": f"{base}-mod-{index}", "text": text, "order": index, "section": f"Part {index}"}
        for index, text in enumerate(sentences, start=1)
    ]
    activity["distractors"] = [
        {"id": f"{base}-mod-x{index}", "text": text, "misconception": "This part belongs to a different maths idea."}
        for index, text in enumerate(distractors, start=1)
    ]
    activity["answerSlots"] = [{"id": f"slot-{index}", "label": label} for index, label in enumerate(activity["structureHelp"], start=1)]
    ordered = [item["id"] for item in activity["correctItems"]]
    activity["answerKey"] = {"orderedItemIds": ordered}
    activity["correctSequence"] = ordered


def key_phrases(question: str, sentences: list[str]) -> list[str]:
    words = re.findall(r"[A-Za-z]+", " ".join([question, *sentences]).lower())
    skip = {"the", "and", "are", "can", "with", "this", "that", "how", "why", "what", "which", "when", "where", "there", "each", "then", "they", "them", "into", "from", "have", "has"}
    seen: list[str] = []
    for word in words:
        if len(word) < 4 or word in skip:
            continue
        if word not in seen:
            seen.append(word)
    return seen[:5] or ["count", "order", "compare", "same", "total"]


def difficult_activity(activity: dict, question: str, sentences: list[str], distractors: list[str], base: str) -> None:
    phrases = key_phrases(question, sentences)
    activity["difficulty"] = "difficult"
    activity["question"] = question
    activity["instructions"] = "Drag only the key idea cards that belong in this answer."
    activity["structureHelp"] = ["Key idea", "Maths word", "Useful detail"]
    activity["correctItems"] = [
        {"id": f"{base}-hard-{index}", "text": text, "order": index}
        for index, text in enumerate(phrases, start=1)
    ]
    activity["distractors"] = [
        {"id": f"{base}-hard-x{index}", "text": text, "misconception": "This key idea is for another question."}
        for index, text in enumerate(distractors, start=1)
    ]
    activity["answerSlots"] = [
        {"id": "intro", "label": "Key facts"},
        {"id": "body", "label": "Maths idea"},
        {"id": "end", "label": "Final check"},
    ]
    required = [item["id"] for item in activity["correctItems"]]
    activity["answerKey"] = {"requiredConceptIds": required}
    activity["correctSequence"] = required


def rebuild_file(path: Path) -> bool:
    data = json.loads(path.read_text(encoding="utf-8"))
    chapter = int(data["source"]["chapterNumber"])
    chapter_questions = QUESTIONS.get(chapter)
    if not chapter_questions:
        return False

    builders_by_q: dict[int, list[dict]] = {}
    for activity in data["activities"]:
        if activity.get("type") == "answer_builder":
            builders_by_q.setdefault(int(activity.get("chapterQuestionNumber") or 0), []).append(activity)

    for qnum, (question, sentences, distractors) in enumerate(chapter_questions, start=1):
        group_id = f"chapter-q{qnum:02d}-{slug(question)}"
        base = f"ch{chapter:02d}-q{qnum:02d}"
        visual = f"assets/question-art/class1-math-question-ai/{VISUALS[chapter][qnum - 1]}"
        modes = sorted(builders_by_q.get(qnum, []), key=lambda item: {"easy": 0, "moderate": 1, "difficult": 2}.get(item.get("difficulty"), 9))
        if len(modes) != 3:
            continue
        easy_activity(modes[0], question, sentences, distractors, base)
        moderate_activity(modes[1], question, sentences, distractors, base)
        difficult_activity(modes[2], question, sentences, distractors, base)
        for activity in modes:
            activity["questionGroupId"] = group_id
            activity["chapterQuestionNumber"] = qnum
            activity["visualArt"] = visual
            activity["hints"] = [
                "Read the maths question first.",
                "Choose cards that match only this question.",
                "Put answer parts from first idea to final idea.",
            ]
            activity["modelAnswer"] = " ".join(sentences)
            activity["scoringRubric"] = [
                {"criterion": "Maths idea matches the question", "marks": 2},
                {"criterion": "Answer parts are in the correct order", "marks": 1},
                {"criterion": "Uses useful maths words", "marks": 1},
                {"criterion": "Leaves wrong cards outside", "marks": 1},
            ]
            activity["questionIdentifier"] = {
                "layoutProfileId": "answer_builder",
                "layoutLabel": "Answer Builder",
                "primaryPracticeType": "answer_builder",
                "slotStrategy": "ordered_answer_parts" if activity["difficulty"] != "difficult" else "key_idea_cards",
                "recommendedLayout": "drag answer parts into slots",
            }

    data["chapterQuestions"] = [
        {
            "number": index,
            "groupId": f"chapter-q{index:02d}-{slug(question)}",
            "question": question,
            "questionIdentifier": {
                "label": "Answer Builder",
                "primaryType": "answer_builder",
                "slotStrategy": "ordered_answer_parts",
                "layout": "drag answer parts into slots",
                "id": "answer_builder",
            },
        }
        for index, (question, _sentences, _distractors) in enumerate(chapter_questions, start=1)
    ]
    data.setdefault("coverage", {})["chapterQuestionCount"] = len(chapter_questions)
    data["coverage"]["answerBuilderMode"] = "math-question-specific-answer-parts"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return True


def main() -> int:
    changed = []
    for path in sorted(DATA_DIR.glob("*.json")):
        if rebuild_file(path):
            changed.append(path.name)
    print(f"Rebuilt answer-builder maths content in {len(changed)} files.")
    for name in changed:
        print(name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
