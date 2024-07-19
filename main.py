from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import (CallbackQuery, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message, PhotoSize)

from config import Config, load_config

config: Config = load_config()
BOT_TOKEN: str = config.tg_bot.token

# Create bot and dispatcher objects
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# Create a "database" of users
user_dict: dict[int, dict[str, str | int | bool]] = {}


# Create a class inherited from StatesGroup for the group of states in our FSM
class FSMFillForm(StatesGroup):
    # Create instances of the State class, sequentially
    # listing the possible states the bot will be in
    # at different moments of interaction with the user
    fill_name = State()  # State waiting for name input
    fill_age = State()  # State waiting for age input
    fill_gender = State()  # State waiting for gender selection
    upload_photo = State()  # State waiting for photo upload
    fill_education = State()  # State waiting for education selection
    fill_wish_news = State()  # State waiting for selection to receive news
    # or not


# This handler will trigger on the /start command outside of states
# and offer to start filling out the form by sending the /fillform command
@dp.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    await message.answer(
        text='This bot demonstrates FSM functionality\n\n'
             'To start filling out the form - '
             'send the /fillform command'
    )


# This handler will trigger on the "/cancel" command in the default state
# and inform that this command works inside the state machine
@dp.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    await message.answer(
        text='There is nothing to cancel. You are outside the state machine\n\n'
             'To start filling out the form - '
             'send the /fillform command'
    )


# This handler will trigger on the "/cancel" command in any state
# except the default state, and disable the state machine
@dp.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    await message.answer(
        text='You have exited the state machine\n\n'
             'To start filling out the form again - '
             'send the /fillform command'
    )
    # Reset state and clear data received within states
    await state.clear()


# This handler will trigger on the /fillform command
# and put the bot in the state waiting for name input
@dp.message(Command(commands='fillform'), StateFilter(default_state))
async def process_fillform_command(message: Message, state: FSMContext):
    await message.answer(text='Please enter your name')
    # Set the state waiting for name input
    await state.set_state(FSMFillForm.fill_name)


# This handler will trigger if a correct name is entered
# and put the bot in the state waiting for age input
@dp.message(StateFilter(FSMFillForm.fill_name), F.text.isalpha())
async def process_name_sent(message: Message, state: FSMContext):
    # Save the entered name in storage under the key "name"
    await state.update_data(name=message.text)
    await message.answer(text='Thank you!\n\nNow enter your age')
    # Set the state waiting for age input
    await state.set_state(FSMFillForm.fill_age)


# This handler will trigger if something incorrect is entered
# during name input
@dp.message(StateFilter(FSMFillForm.fill_name))
async def warning_not_name(message: Message):
    await message.answer(
        text='What you sent does not look like a name\n\n'
             'Please enter your name\n\n'
             'If you want to cancel filling out the form - '
             'send the /cancel command'
    )


# This handler will trigger if a correct age is entered
# and put the bot in the state of selecting gender
@dp.message(StateFilter(FSMFillForm.fill_age),
            lambda x: x.text.isdigit() and 4 <= int(x.text) <= 120)
async def process_age_sent(message: Message, state: FSMContext):
    # Save the age in storage under the key "age"
    await state.update_data(age=message.text)
    # Create inline button objects
    male_button = InlineKeyboardButton(
        text='Male ♂',
        callback_data='male'
    )
    female_button = InlineKeyboardButton(
        text='Female ♀',
        callback_data='female'
    )
    undefined_button = InlineKeyboardButton(
        text='🤷 Not sure yet',
        callback_data='undefined_gender'
    )
    # Add buttons to the keyboard (two in one row and one in another)
    keyboard: list[list[InlineKeyboardButton]] = [
        [male_button, female_button],
        [undefined_button]
    ]
    # Create an inline keyboard object
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    # Send a message with the keyboard to the user
    await message.answer(
        text='Thank you!\n\nPlease specify your gender',
        reply_markup=markup
    )
    # Set the state waiting for gender selection
    await state.set_state(FSMFillForm.fill_gender)


# This handler will trigger if something incorrect is entered
# during age input
@dp.message(StateFilter(FSMFillForm.fill_age))
async def warning_not_age(message: Message):
    await message.answer(
        text='Age must be an integer between 4 and 120\n\n'
             'Try again\n\nIf you want to cancel '
             'filling out the form - send the /cancel command'
    )


# This handler will trigger on button press during
# gender selection and put the bot in the state of photo upload
@dp.callback_query(StateFilter(FSMFillForm.fill_gender),
                   F.data.in_(['male', 'female', 'undefined_gender']))
async def process_gender_press(callback: CallbackQuery, state: FSMContext):
    # Save the gender (callback.data of the pressed button) in storage
    # under the key "gender"
    await state.update_data(gender=callback.data)
    # Delete the message with buttons, as the next step is photo upload
    # so the user won't be tempted to click the buttons
    await callback.message.delete()
    await callback.message.answer(
        text='Thank you! Now please upload your photo'
    )
    # Set the state waiting for photo upload
    await state.set_state(FSMFillForm.upload_photo)


# This handler will trigger if something incorrect is entered/sent
# during gender selection
@dp.message(StateFilter(FSMFillForm.fill_gender))
async def warning_not_gender(message: Message):
    await message.answer(
        text='Please use the buttons when selecting gender\n\n'
             'If you want to cancel filling out the form - '
             'send the /cancel command'
    )


# This handler will trigger if a photo is sent
# and put the bot in the state of selecting education
@dp.message(StateFilter(FSMFillForm.upload_photo),
            F.photo[-1].as_('largest_photo'))
async def process_photo_sent(message: Message,
                             state: FSMContext,
                             largest_photo: PhotoSize):
    # Save the photo data (file_unique_id and file_id) in storage
    # under the keys "photo_unique_id" and "photo_id"
    await state.update_data(
        photo_unique_id=largest_photo.file_unique_id,
        photo_id=largest_photo.file_id
    )
    # Create inline button objects
    secondary_button = InlineKeyboardButton(
        text='Secondary',
        callback_data='secondary'
    )
    higher_button = InlineKeyboardButton(
        text='Higher',
        callback_data='higher'
    )
    no_edu_button = InlineKeyboardButton(
        text='🤷 None',
        callback_data='no_edu'
    )
    # Add buttons to the keyboard (two in one row and one in another)
    keyboard: list[list[InlineKeyboardButton]] = [
        [secondary_button, higher_button],
        [no_edu_button]
    ]
    # Create an inline keyboard object
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    # Send a message with the keyboard to the user
    await message.answer(
        text='Thank you!\n\nPlease specify your education',
        reply_markup=markup
    )
    # Set the state waiting for education selection
    await state.set_state(FSMFillForm.fill_education)


# This handler will trigger if something incorrect is entered/sent
# during photo upload
@dp.message(StateFilter(FSMFillForm.upload_photo))
async def warning_not_photo(message: Message):
    await message.answer(
        text='Please send your photo at this step\n\n'
             'If you want to cancel filling out the form - '
             'send the /cancel command'
    )


# This handler will trigger if education is selected
# and put the bot in the state of agreeing to receive news or not
@dp.callback_query(StateFilter(FSMFillForm.fill_education),
                   F.data.in_(['secondary', 'higher', 'no_edu']))
async def process_education_press(callback: CallbackQuery, state: FSMContext):
    # Save the education data under the key "education"
    await state.update_data(education=callback.data)
    # Create inline button objects
    yes_news_button = InlineKeyboardButton(
        text='Yes',
        callback_data='yes_news'
    )
    no_news_button = InlineKeyboardButton(
        text='No, thanks',
        callback_data='no_news'
    )
    # Add buttons to the keyboard (in one row)
    keyboard: list[list[InlineKeyboardButton]] = [
        [yes_news_button, no_news_button]
    ]
    # Create an inline keyboard object
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    # Send a message with the keyboard to the user
    await callback.message.edit_text(
        text='Thank you!\n\nWould you like to receive news?',
        reply_markup=markup
    )
    # Set the state waiting for the user's decision
    await state.set_state(FSMFillForm.fill_wish_news)


# This handler will trigger if something incorrect is entered/sent
# during education selection
@dp.message(StateFilter(FSMFillForm.fill_education))
async def warning_not_education(message: Message):
    await message.answer(
        text='Please use the buttons when selecting education\n\n'
             'If you want to cancel filling out the form - '
             'send the /cancel command'
    )


# This handler will trigger if the user has made a decision
# and the bot will exit the state machine
@dp.callback_query(StateFilter(FSMFillForm.fill_wish_news),
                   F.data.in_(['yes_news', 'no_news']))
async def process_wish_news_press(callback: CallbackQuery, state: FSMContext):
    # Save the user's decision in storage under the key "wish_news"
    await state.update_data(wish_news=callback.data == 'yes_news')
    user_dict[callback.from_user.id] = await state.get_data()
    # Exit the state machine
    await state.clear()
    # Send a message to the chat about exiting the state machine
    await callback.message.edit_text(
        text='Thank you! Your data has been saved!\n\n'
             'You have exited the state machine'
    )
    # Send a message to the chat with a suggestion to view their questionnaire
    await callback.message.answer(
        text='To view the data of your '
             'questionnaire - send the command /showdata'
    )


# This handler will trigger if something incorrect is entered/sent
# during decision making
@dp.message(StateFilter(FSMFillForm.fill_wish_news))
async def warning_not_wish_news(message: Message):
    await message.answer(
        text='Please use the buttons when deciding to receive news\n\n'
             'If you want to cancel filling out the form - '
             'send the /cancel command'
    )


# This handler will trigger on the /showdata command
# and send the chat the questionnaire data or a message about the absence of
# data
@dp.message(Command(commands='showdata'), StateFilter(default_state))
async def process_showdata_command(message: Message):
    # Send the user the questionnaire if it is in the "database"
    if message.from_user.id in user_dict:
        await message.answer_photo(
            photo=user_dict[message.from_user.id]['photo_id'],
            caption=f'Name: {user_dict[message.from_user.id]["name"]}\n'
                    f'Age: {user_dict[message.from_user.id]["age"]}\n'
                    f'Gender: {user_dict[message.from_user.id]["gender"]}\n'
                    f'Education: '
                    f'{user_dict[message.from_user.id]["education"]}\n'
                    f'Receive news: '
                    f'{user_dict[message.from_user.id]["wish_news"]}'
        )
    else:
        # If the user's questionnaire is not in the database - suggest
        # filling it out
        await message.answer(
            text='You have not filled out the questionnaire yet. '
                 'To start, send the '
                 'command /fillform'
        )


# This handler will trigger on any messages, except for those
# for which there are separate handlers, outside of states
@dp.message(StateFilter(default_state))
async def send_echo(message: Message):
    await message.reply(text='Sorry, I don’t understand you')


# Start polling
dp.run_polling(bot)
