from adapters.backend_adapter_base import BackendAdapterBase
from bot_types.test import TestData, Question
from bot_types.user_data import UserData

class FakeBackendAdapter(BackendAdapterBase):
    tests = {
        1: TestData(
            id=1,
            name="First test",
            questions=[
                Question(
                    id=1,
                    text=" __________________ система — совокупность программных средств, обеспечивающая управление аппаратной частью компьютера и прикладными программами, а также их взаимодействием между собой и пользователем.",
                    openTime=75,
                    answers_dict={1: "Интекрактивная", 2: "Операционная", 3: "Функциональная"},
                    correct_answers_id=[2]
                ),
                Question(
                    id=2,
                    text="__________________ — система программ на машинном языке, управляющая передачей данных между аппаратными средствами вычислительной системы.",
                    openTime=50,
                    answers_dict={4: "MIOS", 5: "BIOS", 6: "SIOB"},
                    correct_answers_id=[5]
                ),
                Question(
                    id=3,
                    text="__________________ плата — основная плата системного блока ПК.",
                    openTime=50,
                    answers_dict={7: "Электронная", 8: "Отцовская", 9: "Материнская"},
                    correct_answers_id=[9]
                ),
                Question(
                    id=4,
                    text="__________________ — один или несколько специальным образом организованных файлов, хранящих систематизированную информацию.",
                    openTime=60,
                    answers_dict={10: "Экспертная база", 10: "База данных", 11: "База знаний"},
                    correct_answers_id=[10]
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
    }

    # Sample data for groups, organized by university ID
    groups = {
        397: {
            1: "Computer Science",
            2: "Physics",
            3: "Mathematics",
        },
        343: {
            4: "Engineering",
            5: "Biology",
            6: "Economics",
        },
        555: {
            7: "Law School",
            8: "Business School",
        },
        789: {
            9: "Electrical Engineering",
            10: "Medicine",
        },
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