from abc import ABC, abstractmethod

from bot_types.user_data import UserData
from bot_types.test import TestData

class BackendAdapterBase(ABC): 
    # TestProvider
    @abstractmethod
    def get_test(self, id: int) -> TestData:
        pass
    @abstractmethod
    def submit_test(self, test_data: TestData) -> bool:
        pass
    
    # UserController
    @abstractmethod
    def find_preregistered_user(self, username: str) -> UserData:
        pass
    @abstractmethod
    def find_user(self, telegram_id: int) -> UserData:
        pass
    @abstractmethod
    def registrate_user(self, user_data: UserData) -> bool:
        pass
    
    # DataSearcher
    @abstractmethod
    def find_universities(self, name: str) -> dict[int, str]:
        pass
    @abstractmethod
    def find_groups(self, university_id: int, name: str) -> dict[int, str]:
        pass