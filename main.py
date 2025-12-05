
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

ALLOWED_USERS = [1214273889, 718173097]  # replace with your IDs

# ---------------- LOAD OR CREATE USER DATA ----------------
def load_data():
    try:
        with open("user_data.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open("user_data.json", "w") as f:
        json.dump(data, f, indent=4)

userdb = load_data()

def restricted(func):
    def wrapper(update, context):
        user = update.effective_user.id
        if user not in ALLOWED_USERS:
            update.message.reply_text("❌ Access denied")
            return
        return func(update, context)
    return wrapper

# ---------------- START ----------------
@restricted
def start(update, context):
    user = update.effective_user.id
    if str(user) not in userdb:
        userdb[str(user)] = {"weak": {}, "tests": []}
        save_data(userdb)

    keyboard = [
        [InlineKeyboardButton("📘 Physics", callback_data="subject_physics")],
        [InlineKeyboardButton("📗 Chemistry", callback_data="subject_chemistry")],
        [InlineKeyboardButton("📙 Biology", callback_data="subject_biology")],
        [InlineKeyboardButton("📊 My Weak Topics", callback_data="weak_topics")]
    ]
    update.message.reply_text("Welcome! Select a subject:", reply_markup=InlineKeyboardMarkup(keyboard))

# ---------------- SUBJECT SELECT ----------------
def button(update, context):
    query = update.callback_query
    user_id = str(query.from_user.id)
    data = query.data

    if data.startswith("subject_"):
        subject = data.split("_")[1]
        query.edit_message_text(
            f"Choose chapter from {subject.title()}:\n\n(Temporary demo — chapters will be added)",
            reply_markup=chapter_keyboard(subject)
        )

    elif data.startswith("chapter_"):
        chap = data.split("_")[1]
        send_mcq(query, user_id, chap)

    elif data.startswith("ans_"):
        _, correct, chosen, chapter = data.split("_")
        handle_answer(query, user_id, correct, chosen, chapter)

    elif data == "weak_topics":
        show_weak_topics(query, user_id)

# ---------------- CHAPTER BUTTONS ----------------
def chapter_keyboard(subject):
    chapters = ["chapter1", "chapter2", "chapter3"]  # placeholder

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(ch.title(), callback_data=f"chapter_{ch}")]
        for ch in chapters
    ])

# ---------------- SEND ONE MCQ ----------------
def send_mcq(query, user, chapter):

    # temporary sample MCQ
    question = "Electric field inside conductor is?"
    options = ["Zero", "Infinite", "Constant", "Increases"]
    correct = "Zero"

    buttons = [
        [InlineKeyboardButton(opt, callback_data=f"ans_{correct}_{opt}_{chapter}")]
        for opt in options
    ]

    query.edit_message_text(
        f"📘 Chapter: {chapter}\n\n❓ {question}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# ---------------- ANSWER HANDLER ----------------
def handle_answer(query, user, correct, chosen, chapter):
    if chosen == correct:
        text = "✅ Correct!"
    else:
        text = f"❌ Wrong! Correct: {correct}"

        # add to weak topics
        weak = userdb[user]["weak"]
        weak[chapter] = weak.get(chapter, 0) + 1
        save_data(userdb)

    query.edit_message_text(text)

# ---------------- SHOW WEAK TOPICS ----------------
def show_weak_topics(query, user):
    weak = userdb[user]["weak"]

    if not weak:
        query.edit_message_text("🎉 No weak topics! You're doing great!")
        return

    msg = "📊 Your Weak Topics:\n\n"
    for chapter, count in weak.items():
        msg += f"• {chapter} → mistakes: {count}\n"

    query.edit_message_text(msg)

# ---------------- MAIN ----------------
def main():
    bot = Updater("8396930272:AAF2MeHAB3q1xPz5OOQfxsVSqu_yfZpQON4", use_context=True)
    dp = bot.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button))

    bot.start_polling()
    bot.idle()

if __name__ == "__main__":
    main()
