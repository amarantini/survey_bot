from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CallbackContext, CommandHandler, MessageHandler, CallbackQueryHandler, filters


# token that we get from the BotFather
TOKEN = "6368731600:AAERA8QTjoqzWLA4TZZza-dP6j8a0-uIn4s"

class survay_bot:
    def __init__(self) -> None:
        self.IDX = 0
        self.TEXT = ["Do you like cat?"]
        self.BUTTONS = [["yes", "no"]]
        self.START = "Start"
        self.result = []
        # TODO: fetch survey questions
        

    async def menu(self, update: Update, context: CallbackContext) -> None:
        """
        This handler sends a menu with the inline buttons
        """

        await context.bot.send_message(
            update.effective_chat.id,
            "<b>Menu</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(self.START, callback_data=self.START)
            ]])

        )

    async def unknown(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


    async def button_callback(self, update: Update, context: CallbackContext) -> None:
        data = update.callback_query.data
       
        if data == self.START:
            self.IDX = 0
        else:
            self.IDX += 1
            self.result.append(data)
        
        if self.IDX < len(self.TEXT):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=self.TEXT[self.IDX],
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(button, callback_data=button)
                    for button in self.BUTTONS[self.IDX]
                ]])
            )
        else:
            # At the end of the survey
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Thank you for completing the survey!",
                parse_mode=ParseMode.HTML
            )
            # TODO: save survey result

# Reading the respomnse from the user and responding to it accordingly
def main() -> None:
    bot = survay_bot()
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Menu handler
    application.add_handler(CommandHandler("menu", bot.menu))

    # Button callback handler
    application.add_handler(CallbackQueryHandler(bot.button_callback))

    # Unknown handlers
    unknown_handler = MessageHandler(filters.COMMAND, bot.unknown)
    application.add_handler(unknown_handler)

    application.run_polling()


if __name__ == '__main__':
    main()