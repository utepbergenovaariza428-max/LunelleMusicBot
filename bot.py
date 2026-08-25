import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ChatJoinRequestHandler, ContextTypes

TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])
CHANNEL_ID = int(os.environ["CHANNEL_ID"])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎧 Получить доступ", callback_data="access")]
    ]

    await update.message.reply_text(
        "🌙 Добро пожаловать в Lunelle Music!\n\n"
        "🎧 Здесь ты можешь получить доступ к нашей музыкальной коллекции.\n\n"
        "Нажми кнопку ниже, чтобы отправить заявку.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def access(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    invite = await context.bot.create_chat_invite_link(
        chat_id=CHANNEL_ID,
        creates_join_request=True
    )

    keyboard = [
        [InlineKeyboardButton(
            "📩 Отправить заявку",
            url=invite.invite_link
        )]
    ]

    await query.message.reply_text(
        "🔐 Для доступа к Lunelle Music отправь заявку на вступление.\n\n"
        "После этого дождись одобрения администратора.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def join_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    request = update.chat_join_request
    user = request.from_user

    username = f"@{user.username}" if user.username else "нет"

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Одобрить",
                callback_data=f"approve:{user.id}"
            ),
            InlineKeyboardButton(
                "❌ Отклонить",
                callback_data=f"decline:{user.id}"
            )
        ]
    ]

    await context.bot.send_message(
        ADMIN_ID,
        f"📩 Новая заявка!\n\n"
        f"👤 Имя: {user.full_name}\n"
        f"🔗 Username: {username}\n"
        f"🆔 ID: {user.id}",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if query.from_user.id != ADMIN_ID:
        await query.answer("⛔ У тебя нет доступа.", show_alert=True)
        return

    action, user_id = query.data.split(":")
    user_id = int(user_id)

    if action == "approve":
        await context.bot.approve_chat_join_request(
            CHANNEL_ID,
            user_id
        )

        await query.answer("Заявка одобрена!")
        await query.edit_message_text(
            query.message.text + "\n\n✅ ОДОБРЕНО"
        )

    elif action == "decline":
        await context.bot.decline_chat_join_request(
            CHANNEL_ID,
            user_id
        )

        await query.answer("Заявка отклонена!")
        await query.edit_message_text(
            query.message.text + "\n\n❌ ОТКЛОНЕНО"
        )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        CallbackQueryHandler(access, pattern="^access$")
    )
    app.add_handler(
        CallbackQueryHandler(
            decision,
            pattern="^(approve|decline):"
        )
    )
    app.add_handler(
        ChatJoinRequestHandler(join_request)
    )

    print("Lunelle Music Bot запущен!")
    app.run_polling()


if __name__ == "__main__":
    main()
