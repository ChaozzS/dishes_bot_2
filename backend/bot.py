import os
import json
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Telegram environment variables
TOKEN = os.environ['TELEGRAM_TOKEN']
ADMIN_CHAT_ID = int(os.environ['ADMIN_CHAT_ID'])  # your Telegram user ID
WEB_APP_URL = os.environ['WEB_APP_URL']  # e.g. https://<your-railway-project>.railway.app/menu

# Ingredient mapping
INGREDIENTS = {
    'Маргарита': ['Томатный соус', 'Сыр Моцарелла', 'Базилик']
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    web_button = InlineKeyboardButton(
        text='🌐 Открыть меню',
        web_app=WebAppInfo(url=WEB_APP_URL)
    )
    await update.message.reply_text(
        'Привет! Нажмите, чтобы открыть меню:',
        reply_markup=InlineKeyboardMarkup([[web_button]])
    )

async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = json.loads(update.effective_message.web_app_data.data)
    item = data.get('item')
    ingredients = INGREDIENTS.get(item, [])
    text = f"🍽 *{item}*\nИнгредиенты: {', '.join(ingredients)}"
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=text, parse_mode='Markdown')
    await update.effective_message.reply_text('✅ Ваш заказ принят!')
    # Offer to order again
    web_button = InlineKeyboardButton('🌐 Ещё заказ', web_app=WebAppInfo(url=WEB_APP_URL))
    await context.bot.send_message(chat_id=update.effective_message.chat_id,
                                   text='Хотите ещё?',
                                   reply_markup=InlineKeyboardMarkup([[web_button]]))

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Отмена. Чтобы снова открыть меню, /start.')

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('cancel', cancel))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))
    if os.environ.get('RAILWAY'):
        port = int(os.environ.get('PORT', '8443'))
        app.run_webhook(listen='0.0.0.0', port=port, webhook_url=f"{WEB_APP_URL}/bot{TOKEN}")
    else:
        app.run_polling(drop_pending_updates=True)