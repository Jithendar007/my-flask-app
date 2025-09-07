from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Load CSV and normalize column names
df = pd.read_csv("QUESTIONPAPER.csv", encoding="ISO-8859-1")
df.columns = df.columns.str.lower()

# Fix year: handle decimals and NaN safely
df["year"] = df["year"].astype(str)

# Format questions for response
def format_questions(questions, limit):
    if questions.empty:
        return "No questions found for your request."
    if limit:
        questions = questions.head(limit)
    return "\n\n".join(   # double line break between questions
    f"[{row.year}] {row.sub} ({row.examtype})\nQ: {row.question}"
    for row in questions.itertuples(index=False)
)


@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json()
    print("RAW REQUEST:", req, flush=True)

    intent = req.get("queryResult", {}).get("intent", {}).get("displayName", "")
    params = req.get("queryResult", {}).get("parameters", {})

    print("INTENT:", intent, flush=True)
    print("PARAMS:", params, flush=True)

    response_text = "Sorry, I didn't understand that."

    if intent.lower() == "get_questions_by_intent":
        # Extract params safely with normalization
        year = str(params.get("Year"))
        limit = int(params.get("number", 2)) if params.get("number") else 2
        exam_type = str(params.get("Exam_Type"))
        subject = str(params.get("Subject"))
        topic =str(params.get("any")).upper()

        # Apply filters
        filtered = df.copy()
        if year:
            filtered = filtered[filtered["year"] == year]
        if exam_type:
            filtered = filtered[filtered["examtype"] == exam_type]
        if subject:
           filtered = filtered[filtered["sub"]== subject]
        if topic:
           filtered = filtered[filtered["topic"]== topic]

        # Prepare response
        if filtered.empty:
            response_text = "No questions found ."
        else:
            response_text = format_questions(filtered, limit)

    return jsonify({"fulfillmentText": response_text})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
