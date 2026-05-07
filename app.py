
def home_screen():
    return (
        "╔════════════════════╗\n"
        "     🤖 NOVA AI APP\n"
        "╚════════════════════╝\n\n"
        "📱 Main Menu:\n\n"
        "1️⃣ Ask AI\n"
        "2️⃣ Study Help\n"
        "3️⃣ Business Ideas\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "Reply with a number"
    )


def format_ai(answer):
    return (
        "╭───────────────╮\n"
        "   🤖 NOVA AI\n"
        "╰───────────────╯\n\n"
        f"{answer}\n\n"
        "────────────────\n"
        "💡 Ask anything anytime"
    )

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

    msg = request.form.get("Body", "").strip().lower()
    user = request.form.get("From", "")

    response = MessagingResponse()
    reply = response.message()

    # 🟢 MENU
    if msg in ["hi", "hello", "start", "menu"]:
        reply.body(home_screen())
        return str(response)

    if msg == "1":
        reply.body("💬 Ask me anything and I will respond like an AI assistant.")
        return str(response)

    if msg == "2":
        reply.body("📚 Study Help Mode:\nAsk any school question.")
        return str(response)

    if msg == "3":
        reply.body("💡 Business Ideas Mode:\nTell me your skills or budget.")
        return str(response)

    # 🤖 AI RESPONSE
    answer = smart_ai(user, msg)
    reply.body(format_ai(answer))

    return str(response)
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
