from aiogram import Router, F
from aiogram.filters import Command, CommandStart, CommandObject, StateFilter
from aiogram.types import Message, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
import re

from states import RegisterStates, TestingStates
from backend_adapter import FakeBackendAdapter

commandRouter = Router()
backend_adapter = FakeBackendAdapter()

@commandRouter.message(
    StateFilter(None),
    Command("start"),
    CommandStart(deep_link=True, magic=F.args.regexp(re.compile(r'^\d+$')))
    )
async def cmd_start_test(message: Message, command: CommandObject, state: FSMContext):
    test_num = command.args
    await state.update_data(bot_status="member")
    
    test_result = backend_adapter.get_test(int(test_num)) # validate test id via backend
    if (test_result is None):
        await message.answer("Такого теста не существует! Проверьте ссылку.")
        return

    user_result = backend_adapter.find_user(message.from_user.id) # check if user registered 
    if (user_result is None):
        await message.answer("Кажется вы еще не зарегестрированны в системе...")
        await message.answer("Введите своё ФИО в формате: Иванов Иван Иванович")
        await state.set_state(RegisterStates.getting_users_fullname)
        return
    else:
        await message.answer(f"Найдена учетная запись {user_result.second_name} {user_result.first_name}")
    
    await state.update_data(test_data=test_result)
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Начать тест", callback_data=test_num))
    await message.answer(f"Номер теста: {test_result.id}\nНазвание теста: {test_result.name}\nОписание теста: {test_result.description}",
                         reply_markup=builder.as_markup())
    await state.set_state(TestingStates.information_before_test)


@commandRouter.message(
    StateFilter(None),
    Command("start"))
async def cmd_start_test(message: Message):
    await message.answer(f"Для использования данного бота необходимо использовать ссылку")