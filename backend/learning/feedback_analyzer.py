import json

FEEDBACK_FILE = "feedback_logs.json"


def analyze_feedback():

    with open(FEEDBACK_FILE, "r") as f:
        data = json.load(f)

    negative_queries = []

    for record in data:

        if record["feedback"] == "negative":
            negative_queries.append(record["query"])

    return negative_queries