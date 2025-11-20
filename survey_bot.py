import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

BOT_TOKEN = "7980271951:AAGIFJ1X2GMR5u-TF91UZnxLaEsdx295jjs"
ADMIN_CHAT_ID = 402960599

QUESTIONS = [
    "Здравствуйте! Как вас зовут?",
    "Приятно познакомиться! Из какой вы страны (город)?",
    "Сколько вам лет?",
    "На сколько килограммов хотите похудеть?",
    "Откуда вы пришли: рекомендация (от кого) или соцсети (из какой)?",
    "Слышали о системе сбалансированного питания, по которой работаю, или рассказать подробно?",
    "Укажите свой номер телефона, по которому я смогу связаться с вами в Telegram или WhatsApp."
]

FINAL_MESSAGE = (
    "❤️ Здорово, что вы решили изменить свою жизнь. Вы не одни — я уже помогла сотням людей "
    "сбросить лишнее и не набрать снова. Я свяжусь с вами в ближайшее время.👋"
)

# Хранилище сессий пользователей (в памяти)
sessions = {}

logging.basicConfig(level=logging.INFO)


def start(update, context):
    user_id = update.message.from_user.id
    sessions[user_id] = {
        "index": 0,
        "answers": []
    }
    update.message.reply_text(QUESTIONS[0])


def handle_answer(update, context):
    user = update.message.from_user
    user_id = user.id
    text = update.message.text

    # Если нет сессии — начать заново
    if user_id not in sessions:
        sessions[user_id] = {"index": 0, "answers": []}
        update.message.reply_text(QUESTIONS[0])
        return

    session = sessions[user_id]
    q_index = session["index"]

    # Сохранить ответ
    if q_index < len(QUESTIONS):
        session["answers"].append(text)
        session["index"] += 1

    # Если есть ещё вопросы — задаём
    if session["index"] < len(QUESTIONS):
        next_q = QUESTIONS[session["index"]]
        update.message.reply_text(next_q)
        return

    # Анкета закончена — отправляем админу
    answers_text = ""
    for i, ans in enumerate(session["answers"]):
        answers_text += f"{i+1}) {QUESTIONS[i]}\n→ {ans}\n\n"

    summary = (
        "✅ Новая анкета\n\n"
        f"Пользователь: {user.first_name} @{user.username}\n"
        f"user_id: {user_id}\n\n"
        f"{answers_text}"
    )

    context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=summary)

    # Финальное сообщение пользователю
    update.message.reply_text(FINAL_MESSAGE)

    # Очистка сессии
    del sessions[user_id]


def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_answer))

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
