from aiogram import Router, F
from aiogram.types import CallbackQuery, PollAnswer, Poll
from aiogram.fsm.context import FSMContext
import time
import asyncio

from states import TestingStates
from bot_types.test import TestData, TestStatistic
from backend_adapter import FakeBackendAdapter
from aiogram import Bot

testingRouter = Router()
backend_adapter = FakeBackendAdapter()

@testingRouter.callback_query(TestingStates.information_before_test)
async def first_question(callback: CallbackQuery, state: FSMContext):
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
    await bot.send_poll(chat_id=user_id,
                        question=new_question.text,
                        allows_multiple_answers=new_question.is_multiple_answer,
                        options=[text for text in new_question.answers_dict.values()],
                        open_period=new_question.openTime,
                        is_anonymous=False)
    
async def end_test(state: FSMContext, bot, user_id):
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
    