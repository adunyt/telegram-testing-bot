from aiogram.fsm.state import StatesGroup, State

class GeneralStates(StatesGroup):
    validating = State()
    idle = State()
    
class RegisterStates(StatesGroup):
    getting_tg_user_info = State()
    getting_users_fullname = State()
    selecting_university = State()
    selecting_group = State()
    sending_user_data = State()
    
    
class TestingStates(StatesGroup):
    information_before_test = State()
    testing_user = State()
    test_statistic = State()