import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver

# URL for the black product
BLACK_PRODUCT_URL = "https://www.wallhack.com/products/sp-004-black"

# Function to check product availability
def check_wallhack_product():
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    service = Service(r"C:\Users\edgedriver_win64\msedgedriver.exe")  # Replace with the actual path to EdgeDriver
    driver = webdriver.Edge(service=service, options=options)

    try:
        driver.get(BLACK_PRODUCT_URL)
        driver.implicitly_wait(10)  # Wait for the page to load

        # Locate the button with the class "add-to-cart-btn"
        button = driver.find_element(By.CLASS_NAME, "add-to-cart-btn")

        # Check if the button is disabled
        is_disabled = button.get_attribute("disabled") is not None

        # Check the text of the button
        button_text = button.text.strip().lower()

        if is_disabled or "sold out" in button_text:
            return "The SP-004 Black is sold out."
        elif "add to cart" in button_text:
            return "The SP-004 Black is available! You can add it to your cart."
        else:
            return "Couldn't determine the product's availability. Check the website."
    except Exception as e:
        return f"Error occurred: {e}"
    finally:
        driver.quit()

# Telegram bot handlers
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hello! I will check the availability of SP-004 Black for you. Use /status to check manually.")

async def status(update: Update, context: CallbackContext):
    await update.message.reply_text("Checking availability...")
    result = check_wallhack_product()
    await update.message.reply_text(result)

# Automated updates every 2 hours
async def send_updates(context: CallbackContext):
    chat_id = context.job.chat_id
    result = check_wallhack_product()
    await context.bot.send_message(chat_id=chat_id, text=f"Automated Update: {result}")

# Command to start automated updates
async def start_updates(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id

    # Ensure the JobQueue is available
    if context.job_queue:
        context.job_queue.run_repeating(send_updates, interval=2 * 60 * 60, first=0, chat_id=chat_id)
        await update.message.reply_text("You will now receive updates about SP-004 Black every 2 hours.")
    else:
        await update.message.reply_text("Job queue is not available. Please restart the bot.")

# Main function
def main():
    TOKEN = "YOUR_KEY"  # Replace with your bot token from BotFather
    application = Application.builder().token(TOKEN).build()

    # Initialize the JobQueue
    job_queue = application.job_queue

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("startupdates", start_updates))

    application.run_polling()


if __name__ == "__main__":
    main()
