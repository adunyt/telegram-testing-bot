from aiogram import Router, F
from aiogram.types import Message, InlineQuery, InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton, InlineKeyboardMarkup, ChosenInlineResult
from aiogram.fsm.context import FSMContext
import re

from states import RegisterStates
from bot_types.user_data import UserData
from backend_adapter import FakeBackendAdapter
from routers import testing

registrationRouter = Router()
backend_adapter = FakeBackendAdapter()

@registrationRouter.message(
    RegisterStates.getting_users_fullname,
    F.text.regexp(re.compile(r'^\w+\ \w+\ \w+$'))
    )
async def university_select_message(message: Message, state: FSMContext):
    await message.answer(f"Ваше ФИО: {message.text}")
    fullname_splited = message.text.split(" ")
    fullname_dict = {"first_name": fullname_splited[1],
                     "second_name": fullname_splited[0],
                     "third_name": fullname_splited[2]}
    await state.update_data(fullname_dict)
    
    kb = [[InlineKeyboardButton(
        text="Выбрать вуз",
        switch_inline_query_current_chat="ВУЗ"
    )]]
    await message.answer(
        "Нажмите кнопку внизу или введите в текстовое поле '@quiz_hackathon_bot'\
        и начните вводить название вашего колледжа, после чего выберите ваш ВУЗ",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
        )
    await state.set_state(RegisterStates.selecting_university)
    
@registrationRouter.message(
    RegisterStates.getting_users_fullname)
async def get_user_fullname(message: Message):
    await message.answer(f"Введите ФИО в формате: Иванов Иван Иванович. \nВы ввели {message.text}")


@registrationRouter.inline_query(RegisterStates.selecting_university, F.query.startswith("ВУЗ"))
async def search_university(inline_query: InlineQuery):
    user_input = inline_query.query.split(" ")
    user_input.pop(0)
    universities_dict = backend_adapter.find_universities(" ".join(user_input))
    results = []
    for id, name in universities_dict.items():
        # В итоговый массив запихиваем каждую запись
        results.append(InlineQueryResultArticle(
            id=str(id),  # ссылки у нас уникальные, потому проблем не будет
            title=name,
            input_message_content=InputTextMessageContent(
                message_text=name
            )
        ))
    await inline_query.answer(results, is_personal=True)

@registrationRouter.chosen_inline_result(RegisterStates.selecting_university)
async def save_university_id(chosen_result: ChosenInlineResult, state: FSMContext):
    await state.update_data(university_id=chosen_result.result_id)

@registrationRouter.message(RegisterStates.selecting_university)
async def group_select_message(message: Message, state: FSMContext):
    await message.answer(f"Вы выбрали: {message.text}")
    kb = [[InlineKeyboardButton(
        text="Выбрать группу",
        switch_inline_query_current_chat="группа"
    )]]
    await message.answer(
        "Аналогично выбору ВУЗа нажмите на кнопку или введите '@quiz_hackathon_bot' и начните вводить группу",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=kb)
        )
    await state.set_state(RegisterStates.selecting_group)


@registrationRouter.chosen_inline_result(RegisterStates.selecting_group)
async def save_group_id(chosen_result: ChosenInlineResult, state: FSMContext):
    await state.update_data(group_id=chosen_result.result_id)
    
@registrationRouter.inline_query(RegisterStates.selecting_group, F.query.startswith("группа"))
async def search_group(inline_query: InlineQuery, state: FSMContext):
    user_input = inline_query.query.split(" ")
    user_input.pop(0)
    user_state_data = await state.get_data()
    user_university = int(user_state_data["university_id"])
    groups_dict = backend_adapter.find_groups(int(user_university), " ".join(user_input))
    results = []
    for id, name in groups_dict.items():
        # В итоговый массив запихиваем каждую запись
        results.append(InlineQueryResultArticle(
            id=str(id),
            title=name,
            input_message_content=InputTextMessageContent(
                message_text=name
            )
        ))
    await inline_query.answer(results, is_personal=True)

@registrationRouter.message(RegisterStates.selecting_group, F.via_bot.username )
async def finalize_user_registration(message: Message, state: FSMContext):
    await message.answer(f"Вы выбрали: {message.text}")
    
    user_state_data = await state.get_data()
    
    user_data = UserData(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=user_state_data["first_name"],
        second_name=user_state_data["second_name"],
        third_name=user_state_data["third_name"],
        university_id=int(user_state_data["university_id"]),
        group_id=int(user_state_data["group_id"])
    )
    
    backend_adapter.registrate_user(user_data)
    
    await message.answer("Спасибо, регистрация прошла успешно")
    await testing.show_info_about_test(state=state, bot=message.bot, chat_id=message.chat.id)