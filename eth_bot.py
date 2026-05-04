import requests
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "8682133039:AAGFkIMNNFU3C437ManhiG0dtEkI8KXgZFQ"
CHANNEL_ID = "@ethprice_live"

last_price = None


def get_eth_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "ethereum",
        "vs_currencies": "usd"
    }

    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    return float(data["ethereum"]["usd"])


async def start(update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ETH live tracker started. Updates will be posted to the channel."
    )

    context.job_queue.run_repeating(
        send_eth_update,
        interval=10,
        first=1
    )


async def price(update, context: ContextTypes.DEFAULT_TYPE):
    price = get_eth_price()
    await update.message.reply_text(f"ETH price: ${price:,.2f}")


async def send_eth_update(context: ContextTypes.DEFAULT_TYPE):
    global last_price

    try:
        current_price = get_eth_price()

        if last_price is None:
            last_price = current_price
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=f"ETH live price: ${current_price:,.2f}"
            )
            return

        if current_price != last_price:
            direction = "UP" if current_price > last_price else "DOWN"
            change = current_price - last_price

            text = (
                f"ETH price update\n\n"
                f"Current price: ${current_price:,.2f}\n"
                f"Move: {direction} ${abs(change):.2f}"
            )

            last_price = current_price

            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=text
            )

    except Exception as e:
        print("Error:", e)


app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("price", price))

print("ETH bot started...")
app.run_polling()