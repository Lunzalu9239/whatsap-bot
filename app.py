from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from openai import OpenAI

app = Flask(__name__)

# 🔑 GROQ API (FREE LLM)
client = OpenAI(
    api_key="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",
    base_url="https://api.groq.com/openai/v1"
)

# 🧠 MEMORY STORE (per user)
sessions = {}

# 🤖 AI FUNCTION WITH MEMORY
def smart_ai(user, msg):

    # create session if new user
    if user not in sessions:
        sessions[user] = []

    # store message
    sessions[user].append(f"User: {msg}")

    # keep last 6 messages only (avoid overload)
    history = sessions[user][-6:]

    context = "\n".join(history)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a smart WhatsApp AI tutor. You remember conversation context and explain things simply for students."
            },
            {
                "role": "user",
                "content": context
            }
        ]
    )

    answer = response.choices[0].message.content

    # store AI reply too
    sessions[user].append(f"AI: {answer}")

    return answer


# 📲 WHATSAPP WEBHOOK
@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    msg = request.form.get("Body", "").strip()
    user = request.form.get("From", "")

    response = MessagingResponse()
    reply = response.message()

    try:
        answer = smart_ai(user, msg)
        reply.body("Lunzalu's AI Tutor:\n\n" + answer)

    except Exception as e:
        print("ERROR:", e)
        reply.body("AI error. Please try again.")

    return str(response)


# 🚀 RUN SERVER
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
