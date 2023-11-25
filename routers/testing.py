from aiogram import Router, F
from aiogram.types import CallbackQuery, PollAnswer, Poll
from aiogram.fsm.context import FSMContext
import time

from states import TestingStates
from bot_types.test import TestData
from backend_adapter import FakeBackendAdapter
from aiogram import Bot

testingRouter = Router()
backend_adapter = FakeBackendAdapter()

@testingRouter.callback_query(TestingStates.information_before_test)
async def first_question(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Начинаем!")
    await callback.answer()
    await state.set_state(TestingStates.testing_user)
    user_state_data = await state.get_data()
    test_data: TestData = user_state_data["test_data"]
    question = test_data.questions[0]
    await state.update_data(current_question_index=0)
    await state.update_data(question_start_time=time.time())
    await callback.message.answer_poll(question=question.text,
                                       allows_multiple_answers=question.is_multiple_answer,
                                        options=[text for text in question.answers_dict.values()],
                                       open_period=question.openTime,
                                       is_anonymous=False)

async def save_test_result(option_ids: list[int], state: FSMContext):
    user_state_data = await state.get_data()
    test_data: TestData = user_state_data["test_data"]
    question_num = int(user_state_data["current_question_index"])
    answered_question = test_data.questions[question_num]
    answers = answered_question.answers_dict
    answer_dict_keys = [*answers]
    answer_dict_values = [*answers.values()]
    user_answers = {}
    for answer_id in option_ids:
        user_answers[answer_dict_keys[answer_id]] = answer_dict_values[answer_id]
    close_time = time.time() - float(user_state_data["question_start_time"])
    answered_question.submit_question(close_time=close_time, user_answer=user_answers)        
    await state.update_data(test_data=test_data)
    
    
async def end_test(test_data: TestData, state: FSMContext, bot: Bot, user_id: int):
    statistic = test_data.calculate_statistic()
    test_ending_txt = f"Ура, вы прошли тест!\nСтатистика:\
        \n🕒 Общее время: {statistic.total_test_time:.2f}\
        \n⌛ Среднее время на ответ: {statistic.average_time_for_answer:.2f}\
        \n\
        \n✅ Правильных ответов: {statistic.right_answers_count}/{statistic.total_question_count}\
        \n❌ Неправильных ответов: {statistic.wrong_answers_count}/{statistic.total_question_count}\
        \n⭕ Пропущенных ответов: {statistic.skipped_answers_count}/{statistic.total_question_count}"
    await bot.send_message(chat_id=user_id, text=test_ending_txt)
    await state.set_state(None)
    backend_adapter.submit_test(test_data=test_data)
    
    
@testingRouter.poll_answer(TestingStates.testing_user)
async def testing_cycle(poll_answer: PollAnswer, state: FSMContext):
    # Save answer
    await save_test_result(poll_answer.option_ids, state)
    
    user_state_data = await state.get_data()
    test_data: TestData = user_state_data["test_data"]
    question_num = int(user_state_data["current_question_index"])
    
    # Send to user new question
    question_num += 1
    if question_num == len(test_data.questions): # Check end of the test
        await end_test(test_data=test_data,
                       state=state,
                       bot=poll_answer.bot,
                       user_id=poll_answer.user.id)
        return
    
    # If new question exist, send new poll
    await state.update_data(current_question_index=question_num)
    new_question = test_data.questions[question_num]
    await poll_answer.bot.send_poll(chat_id=poll_answer.user.id,
                                    question=new_question.text,
                                    allows_multiple_answers=new_question.is_multiple_answer,
                                    options=[text for text in new_question.answers_dict.values()],
                                    open_period=new_question.openTime,
                                    is_anonymous=False)
