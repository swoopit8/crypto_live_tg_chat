from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pycoingecko import CoinGeckoAPI
import re
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

cg = CoinGeckoAPI()


async def command_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = ("Саламалейкум! Вот что я умею:\n"
                    "/current - показать цены на популярные криптовалюты.\n"
                    "Отправьте '/{название криптовалюты}_price' для получения текущей цены на криптовалюту.")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text)


async def current_prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    coins = ['bitcoin', 'ethereum', 'ripple', 'litecoin', 'cardano', 'solana',
             'binancecoin', 'avalanche-2', 'optimism', 'fantom', 'dogecoin']
    prices = cg.get_price(ids=','.join(coins), vs_currencies='usd')
    message_text = "Текущие цены:\n"
    for coin, data in prices.items():
        message_text += f"{coin.title()}: ${data['usd']}\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message_text)


async def handle_dynamic_price_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message.text.lower()
    match = re.match(r"/(\w+)_price$", message)
    if match:
        await price_query_handler(update, context, match.group(1))


async def price_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, coin_name):
    try:
        price_info = cg.get_price(ids=coin_name, vs_currencies='usd')
        if coin_name in price_info:
            price = price_info[coin_name]['usd']
            response_text = f"Цена {coin_name.upper()}: ${price}"
        else:
            response_text = "Информация о данной криптовалюте не найдена."
    except Exception as e:
        response_text = f"Ошибка при получении данных: {str(e)}"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response_text)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_message = "Старт? Иди бля, маму твою старт."  # Замените текст на более подходящий при необходимости
    await context.bot.send_message(chat_id=update.effective_chat.id, text=start_message)

def main():
    application = Application.builder().token("ENTER YOUR TELEGRAM TOKEN HERE").build()

    # Регистрация обработчиков
    application.add_handler(CommandHandler("command", command_list))
    application.add_handler(CommandHandler("current", current_prices))
    application.add_handler(MessageHandler(filters.Regex(r"^/\w+_price$"), handle_dynamic_price_query))
    application.add_handler(CommandHandler("start", start))  # Регистрируем обработчик команды /start

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()
