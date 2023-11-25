from abc import ABC, abstractmethod

from bot_types.user_data import UserData
from bot_types.test import TestData, Question

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
    def find_universities(self, name: str) -> list[str]:
        pass
    @abstractmethod
    def find_groups(self, university_name: str, name: str) -> list[str]:
        pass
    @abstractmethod
    def find_disciplines(self, discipline_name: str) -> list[str]:
        pass
    
    
class FakeBackendAdapter(BackendAdapterBase):
    tests = {
        1: TestData(
            id=1,
            name="First test",
            questions=[
                Question(
                    id=1,
                    text="Ты чурка?",
                    openTime=10,
                    answers_dict={1: "Да", 2: "Нет"},
                    correct_answers_id=[2]
                ),
                Question(
                    id=2,
                    text="Ты абоба?",
                    openTime=7,
                    answers_dict={3: "Возможно", 4: "Не знаю"},
                    correct_answers_id=[3]
                ),
                Question(
                    id=3,
                    text="Сегодня вторник?",
                    openTime=50,
                    answers_dict={5: "Пятница", 6: "Понедельник"},
                    correct_answers_id=[6]
                ),
                Question(
                    id=4,
                    text="Кто ты?",
                    openTime=9,
                    answers_dict={7: "Я", 8: "Не я"},
                    correct_answers_id=[8]
                ),
            ]
        ),
    }

    # Sample data for popular universities
    universities = {
        397: "University of Toronto",
        343: "University of Tokyo",
        555: "Harvard University",
        789: "Stanford University",
        # Add more as needed
    }

    # Sample data for groups, organized by university ID
    groups = {
        397: {
            1: "Computer Science",
            2: "Physics",
            3: "Mathematics",
            # Add more groups for University of Toronto
        },
        343: {
            4: "Engineering",
            5: "Biology",
            6: "Economics",
            # Add more groups for University of Tokyo
        },
        555: {
            7: "Law School",
            8: "Business School",
            # Add more groups for Harvard University
        },
        789: {
            9: "Electrical Engineering",
            10: "Medicine",
            # Add more groups for Stanford University
        },
        # Add more universities and groups as needed
    }

    def get_test(self, id: int) -> TestData | None:
        if id in self.tests.keys():
            return self.tests[id]
        else:
            return None

    def submit_test(self, test_data: TestData) -> bool:
        # Simulating a successful submission
        print("Test was sended!")
        return True
    
    def find_preregistered_user(self, username: str) -> UserData:
        # Simulating finding a user by username
        return UserData(1, username, "John", "Doe", "", 397, 1)

    def find_user(self, telegram_id: int) -> UserData:
        # Simulating finding a user by Telegram ID
        return UserData(telegram_id, None, "John", "Doe", "", 343, 3)

    def registrate_user(self, user_data: UserData) -> bool:
        # Simulating a successful user registration
        print(f"Registrated user " + str(user_data))
        return True
    
    def find_universities(self, name: str) -> dict[int, str]:
        # Simulating finding universities by name for input suggestions
        name = name.lower()
        suggestions = {}

        for university_id, university_name in self.universities.items():
            if name in university_name.lower():
                suggestions[university_id] = university_name

        return suggestions

    def find_groups(self, university_id: int, name: str) -> dict[int, str]:
        # Simulating finding groups by university ID and name for input suggestions
        name = name.lower()
        suggestions = {}

        if university_id in self.groups:
            for group_id, group_name in self.groups[university_id].items():
                if name in group_name.lower():
                    suggestions[group_id] = group_name

        return suggestions