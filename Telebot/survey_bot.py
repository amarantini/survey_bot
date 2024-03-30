from telegram import ForceReply, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, CallbackContext, CommandHandler, MessageHandler, CallbackQueryHandler, filters
import os
import argparse
import pandas as pd
import time

parser = argparse.ArgumentParser()
parser.add_argument('question_input', type=str,
                    help='path to question input .csv file')

# token that we get from the BotFather
TOKEN = os.environ["SURVEY_BOT_TOKEN"]

class survay_bot:
    def __init__(self, texts, buttons, output_path="./outputs/") -> None:
        self.output_path = output_path
        if not os.path.exists(output_path):
            os.mkdir(self.output_path) 
        self.IDX = 0
        self.TEXT = texts
        self.BUTTONS = buttons
        self.START = "Start"
        self.result = []
        self.is_end = False

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

    async def message_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        data = update.message.text
        if data == self.START:
            self.IDX = 0
            self.is_end = False
            self.result = []
        elif self.is_end:
            await self.unknown(update, context)
            return
        else:
            self.IDX += 1
            self.result.append(data)

        text = str(self.IDX+1) + ". " + self.TEXT[self.IDX]

        if self.IDX < len(self.TEXT):
            if len(self.BUTTONS[self.IDX]) > 0:
                # multiple choice question
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton(button, callback_data=button)
                        for button in self.BUTTONS[self.IDX]
                    ]])
                )
            else:
                # open ended question
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=ForceReply(selective=True)
                )
        else:
            # At the end of the survey
            self.is_end = True
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Thank you for completing the survey!",
                parse_mode=ParseMode.HTML
            )
            # save survey result
            df = pd.DataFrame(self.result, columns=["Answers"])
            # saving the dataframe
            df.to_csv(self.output_path + time.strftime("%Y%m%d-%H%M%S")+".csv", index=False)

    async def button_callback(self, update: Update, context: CallbackContext) -> None:
        data = update.callback_query.data
       
        if data == self.START:
            self.IDX = 0
            self.is_end = False
            self.result = []
        else:
            self.IDX += 1
            self.result.append(data)
        
        text = str(self.IDX+1) + ". " + self.TEXT[self.IDX]
        
        if self.IDX < len(self.TEXT):
            if len(self.BUTTONS[self.IDX]) > 0:
                # multiple choice question
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton(button, callback_data=button)
                        for button in self.BUTTONS[self.IDX]
                    ]])
                )
            else:
                # open ended question
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=ForceReply(selective=True)
                )
        else:
            # At the end of the survey
            self.is_end = True
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Thank you for completing the survey!",
                parse_mode=ParseMode.HTML
            )
            # save survey result
            df = pd.DataFrame(self.result, columns=["Answers"])
            # saving the dataframe
            df.to_csv(self.output_path + time.strftime("%Y%m%d-%H%M%S")+".csv", index=False)

# Reading the respomnse from the user and responding to it accordingly
def main() -> None:
    args = parser.parse_args()

    # load questions
    questions = pd.read_csv(args.question_input,sep='\t')
    texts = questions["Questions"].tolist()
    buttons = questions["Buttons"].tolist()
    
    # preprocess button
    buttons = [string.split(",") if not pd.isna(string) else []  for string in buttons]
    for button_list in buttons:
        for i in range(len(button_list)):
            button_list[i] = button_list[i].strip()

    bot = survay_bot(texts, buttons)
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Menu handler
    application.add_handler(CommandHandler("menu", bot.menu))

    # Button callback handler
    application.add_handler(CallbackQueryHandler(bot.button_callback))

    # Open end question reply handler
    application.add_handler(MessageHandler(filters.TEXT, bot.message_callback))

    # Unknown handlers
    unknown_handler = MessageHandler(filters.COMMAND, bot.unknown)
    application.add_handler(unknown_handler)

    application.run_polling()


if __name__ == '__main__':
    main()