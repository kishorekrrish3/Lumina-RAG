import json
import os
from datetime import datetime

FEEDBACK_FILE = "feedback_logs.json"


def log_feedback(query, answer, feedback):

    record = {
        "query": query,
        "answer": answer,
        "feedback": feedback,
        "timestamp": str(datetime.now())
    }

    if os.path.exists(FEEDBACK_FILE):

        with open(FEEDBACK_FILE, "r") as f:
            data = json.load(f)

    else:
        data = []

    data.append(record)

    with open(FEEDBACK_FILE, "w") as f:
        json.dump(data, f, indent=4)