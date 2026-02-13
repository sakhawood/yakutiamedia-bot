import datetime
from telegram.ext import MessageHandler
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, filters,
    ConversationHandler, ContextTypes
)
import gspread

# ==== ВСТАВЬТЕ СВОЙ ТОКЕН ====
BOT_TOKEN = "8545721090:AAExxvO71qjg7kqkyD5h_LhYy_vZl7X1KKg"
GROUP_CHAT_ID = -1003824519107 # позже вставим

# ==== Google Sheets ====
gc = gspread.service_account("credentials.json")
sheet = gc.open("Order_Yakutia.media").sheet1

NAME, EMAIL, PHONE, COMMENT = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите имя:")
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("Введите email:")
    return EMAIL


async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["email"] = update.message.text
    await update.message.reply_text("Введите телефон:")
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("Введите комментарий:")
    return COMMENT


async def get_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["comment"] = update.message.text

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    sheet.append_row([
        now,
        context.user_data["name"],
        context.user_data["email"],
        context.user_data["phone"],
        context.user_data["comment"]
    ])

    # СОЗДАЁМ message
    message = (
        f"<b>📥 Новая заявка</b>\n\n"
        f"<b>Дата:</b> {now}\n"
        f"<b>Имя:</b> {context.user_data['name']}\n"
        f"<b>Email:</b> {context.user_data['email']}\n"
        f"<b>Телефон:</b> {context.user_data['phone']}\n"
        f"<b>Комментарий:</b> {context.user_data['comment']}"
    )

    # ОТПРАВЛЯЕМ В ГРУППУ
    await context.bot.send_message(
        chat_id=GROUP_CHAT_ID,
        text=message,
        parse_mode="HTML"
    )

    await update.message.reply_text("Заявка сохранена.")

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отменено.")
    return ConversationHandler.END
    
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT, get_name)],
            EMAIL: [MessageHandler(filters.TEXT, get_email)],
            PHONE: [MessageHandler(filters.TEXT, get_phone)],
            COMMENT: [MessageHandler(filters.TEXT, get_comment)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv)
    app.run_polling()


if __name__ == "__main__":
    main()