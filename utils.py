import re

def detect_time(text):
    match = re.search(r'(\d{1,2}\s?(am|pm))', text.lower())
    return match.group(0) if match else "not specified"

def detect_urgency(text):
    text = text.lower()
    if "urgent" in text or "asap" in text:
        return "high"
    elif "tomorrow" in text:
        return "medium"
    return "low"

def smart_time_parser(text):
    if "morning" in text.lower():
        return "9 AM"
    if "evening" in text.lower():
        return "7 PM"
    return detect_time(text)

def assign_time_based_on_urgency(urgency):
    if urgency == "high":
        return "6 PM"
    elif urgency == "medium":
        return "8 PM"
    return "10 PM"

def generate_plan(prompt):
    prompt = prompt.lower()
    steps = []

    if "study" in prompt:
        steps += ["create_task", "schedule_study"]
    elif "meeting" in prompt:
        steps.append("schedule_meeting")
    elif "note" in prompt:
        steps.append("save_note")
    else:
        steps.append("general_task")

    return steps