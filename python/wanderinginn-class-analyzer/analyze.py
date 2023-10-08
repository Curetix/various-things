import sys
import os
import re
import json
import bs4
from PyInquirer import prompt

PATTERNS = {
    "class_obtained": re.compile(r"\[(?P<class_name>.+)\sClass\s[Oo]btained!\]"),
    "class_level_up": re.compile(r"\[(?P<class_name>.+)\sLevel\s(?P<level>\d{1,2})!\]"),
    "class_change": re.compile(r"\[Conditions\s[Mm]et:\s(?P<old_class>.+)\s→\s(?P<new_class>.+)\sClass!\]"),
    "class_consolidation": re.compile(r"\[Class\sConsolidation:\s(?P<removed_class>.+)\sremoved.\]"),
    "skill_obtained": re.compile(r"\[Skill\s–\s(?P<skill_name>.+)\s[Oo]btained!\]"),
    "skill_learned": re.compile(r"\[Skill\s–\s(?P<skill_name>.+)\s[Ll]earned.\]"),
    "skill_change": re.compile(r"\[Skill\sChange\s–\s(?P<old_skill>.+)\s→\s(?P<new_skill>.+)!\]")
}


def main():
    questions = [
        {
            "type": "checkbox",
            "message": "Which folder in data/ should be processed?",
            "name": "source_folders",
            "choices": [{"name": f} for f in os.listdir("data/") if os.path.isdir("data/%s" % f)],
        },
        {
            "type": "confirm",
            "message": "Do you want to load the report saved on the disk?",
            "name": "load_report",
            "when": lambda _: os.path.isfile("data/report.json")
        }
    ]

    answers = prompt(questions)

    if not answers or len(answers.get("source_folders")) == 0:
        return

    report = {}

    if answers.get("load_report", False):
        with open("data/report.json", "r") as file:
            report = json.load(file)

    # Process folders
    for folder in answers.get("source_folders"):
        volume_changes = process_volume_folder(folder)

        with open("data/%s.json" % folder, "w") as file:
            json.dump(volume_changes, file, indent=4)

        report = create_class_report(volume_changes, report)

        with open("data/report.json", "w") as file:
            json.dump(report, file, indent=4)


def process_volume_folder(folder):
    print("Processing %s" % folder)

    volume_changes = []

    # Process files in folders
    for file in os.listdir("data/%s" % folder):
        if file.endswith(".html") or file.endswith(".xhtml"):
            with open("data/%s/%s" % (folder, file), "r", encoding="utf-8") as html:
                soup = bs4.BeautifulSoup(str(html.read()), features="html.parser")

            volume_changes += process_chapter(soup)

    return volume_changes


def process_chapter(soup):
    chapter_name = soup.h1.get_text().strip()
    chapter_changes = []

    # Process regex patterns
    for (pattern_name, pattern) in PATTERNS.items():
        search = pattern.finditer(soup.get_text())

        # Process matches
        for m in search:
            d = {
                "type": pattern_name,
                "chapter": chapter_name
            }
            d.update(m.groupdict())
            chapter_changes.append(d)

    if len(chapter_changes) > 0:
        print("Found %s changes in %s chapters" % (len(chapter_changes), chapter_name))

    return chapter_changes


def create_class_report(changes, report):
    while len(changes) > 0:
        questions = [
            {
                "type": "checkbox",
                "message": "Which changes do you want to associate?",
                "name": "changes",
                "choices": [{"name": create_choice(i, c)} for (i, c) in enumerate(changes)]
            },
            {
                "type": "list",
                "message": "Which character do these changes belong to?",
                "name": "character",
                "choices": ["Erin", "Toren", "Rags", "Pawn", "Lyonette", "other"],
                "when": lambda a: len(a.get("changes", [])) > 0
            },
            {
                "type": "input",
                "message": "Which character do these changes belong to?",
                "name": "character_manual",
                "when": lambda a: a.get("character", "") == "other"
            }
        ]

        answers = prompt(questions)

        if not answers:
            sys.exit()

        indexes = [int(c.split(")")[0]) for c in answers.get("changes", [])]

        if len(indexes) == 0:
            break

        selected_changes = []

        for i in indexes:
            selected_changes.append(changes[i])

        for i in sorted(indexes, reverse=True):
            changes.pop(i)

        character = answers.get("character")
        if character == "other":
            character = answers.get("character_manual")
            if not character:
                continue

        cs = report.get(character, {
            "classes": {},
            "skills": []
        })

        for (i, c) in enumerate(selected_changes):
            t = c["type"]

            if t == "skill_obtained" or t == "skill_learned":
                cs["skills"].append(c["skill_name"])
            elif t == "skill_change":
                if c["old_skill"] in cs["skills"]:
                    cs["skills"].remove(c["old_skill"])
                if not c["new_skill"] in cs["skills"]:
                    cs["skills"].append(c["new_skill"])
            elif t == "class_obtained":
                if not cs["classes"].get(c["class_name"]):
                    cs["classes"][c["class_name"]] = 1
            elif t == "class_level_up":
                cs["classes"][c["class_name"]] = int(c["level"])
            elif t == "class_change":
                if len([cl for cl in selected_changes[i:] if cl["type"] == "class_level_up" and cl["class_name"] == c["old_class"]]) > 0:
                    selected_changes.append(c)
                    continue

                cs["classes"][c["new_class"]] = int(cs["classes"][c["old_class"]])
                cs["classes"].pop(c["old_class"])
            elif t == "class_consolidation":
                if cs["classes"].get(c["removed_class"]):
                    cs["classes"].pop(c["removed_class"])

        report[character] = cs

    return report


def create_choice(index, change):
    t = change["type"]

    if t == "class_obtained":
        return "%s) Class %s obtained" % (index, change["class_name"])
    if t == "class_level_up":
        return "%s) Class %s level %s gained" % (index, change["class_name"], change["level"])
    if t == "class_consolidation":
        return "%s) Class Consolidation, %s removed" % (index, change["removed_class"])
    if t == "class_change":
        return "%s) Class %s changed to %s" % (index, change["old_class"], change["new_class"])
    if t == "skill_obtained" or t == "skill_learned":
        return "%s) Skill %s obtained" % (index, change["skill_name"])
    if t == "skill_change":
        return "%s) Skill %s changed to %s" % (index, change["old_skill"], change["new_skill"])


if __name__ == "__main__":
    main()
