from aiogram import Router, F
from aiogram.types import CallbackQuery, PollAnswer, Poll, Message
from aiogram import types
from aiogram.fsm.context import FSMContext
import time
import asyncio
import logging
from aiogram.utils.keyboard import InlineKeyboardBuilder


from states import TestingStates
from bot_types.test import TestData, TestStatistic
from backend_adapter import FakeBackendAdapter
from aiogram import Bot

testingRouter = Router()
backend_adapter = FakeBackendAdapter()


async def show_info_about_test(state: FSMContext, bot: Bot, chat_id: int):
    user_state_data = await state.get_data()
    test_data: TestData = user_state_data["test_data"]
    builder = InlineKeyboardBuilder()
    builder.add(types.InlineKeyboardButton(text="Начать тест", callback_data=str(test_data.id)))
    await bot.send_message(
        chat_id=chat_id,
        text=f"Номер теста: {test_data.id}\nНазвание теста: {test_data.name}\nОписание теста: {test_data.description}",
        reply_markup=builder.as_markup()
        )
    await state.set_state(TestingStates.information_before_test)
    

@testingRouter.callback_query(TestingStates.information_before_test)
async def start_test(callback: CallbackQuery, state: FSMContext):
    # Answer to callback
    await callback.message.answer("Начинаем!")
    await callback.answer()
    # Set state for testing cycle 
    await state.set_state(TestingStates.testing_user)
    # Init question index
    await state.update_data(current_question_index=-1)
    await next_question(state=state, bot=callback.bot, user_id=callback.from_user.id)

async def save_question_result(option_ids: list[int], state: FSMContext):
    user_state_data = await state.get_data()
    # Getting data from state
    test_data: TestData = user_state_data["test_data"]
    question_num = int(user_state_data["current_question_index"])
    answered_question = test_data.questions[question_num]
    answers = answered_question.answers_dict
    # Add user answers to question class
    answer_dict_keys = [*answers] # All ids from dict
    answer_dict_values = [*answers.values()] # All text answers from dict
    user_answers = {}
    for answer_id in option_ids:
        user_answers[answer_dict_keys[answer_id]] = answer_dict_values[answer_id]
    close_time = time.time() - float(user_state_data["question_start_time"]) # Calculate time for question
    answered_question.submit_question(close_time=close_time, user_answer=user_answers)
    # Update information about test
    await state.update_data(test_data=test_data)
       
@testingRouter.poll_answer(TestingStates.testing_user)
async def testing_cycle(poll_answer: PollAnswer, state: FSMContext):
    # Save answer
    await save_question_result(poll_answer.option_ids, state)
    # Cancel countdown timer to detect skipped question 
    user_state_data = await state.get_data()
    autoclose_checker = user_state_data["autoclose_checker_task"]
    autoclose_checker.cancel()
    # Close poll
    poll_message_id = user_state_data["current_poll_message_id"]
    await poll_answer.bot.stop_poll(chat_id=poll_answer.user.id, message_id=poll_message_id)
    # Send next question
    await next_question(state=state, bot=poll_answer.bot, user_id=poll_answer.user.id)
    
async def next_question(state: FSMContext, bot: Bot, user_id: int):
    # Getting test data
    user_state_data = await state.get_data()
    test_data: TestData = user_state_data["test_data"]
    question_num = int(user_state_data["current_question_index"])
    # Increase question number
    question_num += 1
    # Update question data
    await state.update_data(current_question_index=question_num)
    await state.update_data(question_start_time=time.time())
    # Check end of the test
    if question_num == len(test_data.questions): 
        await end_test(state=state, bot=bot, user_id=user_id)
        return
    
    # Get question
    new_question = test_data.questions[question_num] 
    # Send poll
    sended_message = await bot.send_poll(chat_id=user_id,
                        question=new_question.text,
                        allows_multiple_answers=new_question.is_multiple_answer,
                        options=[text for text in new_question.answers_dict.values()],
                        open_period=new_question.openTime,
                        is_anonymous=False,
                        protect_content=True)
    # Save message id with poll
    await state.update_data(current_poll_message_id=sended_message.message_id)
    # Start countdown
    autoclose_checker = asyncio.create_task(autoclosed_poll_checker(sended_message.poll, user_id, state))
    await state.update_data(autoclose_checker_task=autoclose_checker)
    try:
        await autoclose_checker
    except asyncio.CancelledError:
        logging.info("User answered, task cancelled")
    
async def end_test(state: FSMContext, bot: Bot, user_id):
    # Getting test data
    user_state_data = await state.get_data()
    test_data: TestData = user_state_data["test_data"]
    backend_adapter.submit_test(test_data=test_data)
    statistic = test_data.calculate_statistic()
    test_ending_txt = f"Ура, вы прошли тест!\nСтатистика:\
        \n🕒 Общее время: {statistic.total_test_time:.2f} секунд\
        \n⌛ Среднее время на ответ: {statistic.average_time_for_answer:.1f} секунд\
        \n\
        \n✅ Правильных ответов: {statistic.right_answers_count}/{statistic.total_question_count}\
        \n❌ Неправильных ответов: {statistic.wrong_answers_count}/{statistic.total_question_count}\
        \n⭕ Пропущенных ответов: {statistic.skipped_answers_count}/{statistic.total_question_count}"
    await bot.send_message(chat_id=user_id, text=test_ending_txt)
    await state.set_state(None)
    
    

async def autoclosed_poll_checker(poll: Poll, user_id: int, state: FSMContext):
    user_state_data = await state.get_data()
    question_num = user_state_data["current_question_index"]
    await asyncio.sleep(poll.open_period)
    new_user_state_data = await state.get_data()
    new_question_num = new_user_state_data["current_question_index"]
    if (question_num == new_question_num):
        await save_question_result([], state)
        await next_question(state=state, bot=poll.bot, user_id=user_id)