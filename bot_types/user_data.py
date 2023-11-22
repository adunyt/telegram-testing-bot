class UserData:
    telegram_id: int
    username: str | None
    first_name: str
    second_name: str
    third_name: str
    university_id: int
    group_id: int
    
    def __init__(self, telegram_id: int, username: str | None, first_name: str, second_name: str, third_name: str, university_id: int, group_id: int) -> None:
        self.telegram_id = telegram_id
        self.username = username
        self.first_name = first_name
        self.second_name = second_name
        self.third_name = third_name
        self.university_id = university_id
        self.group_id = group_id
    
    def add_full_name(self, first_name: str, second_name: str, third_name: str):
        self.first_name = first_name
        self.second_name = second_name
        self.third_name = third_name
        
    def add_telegram_info(self, telegram_id: int, username: int):
        self.telegram_id = telegram_id
        self.username = username
        
    def add_university_info(self, university_id: int, group_id: int):
        self.university_id = university_id
        self.group_id = group_id
        
        
    def __str__(self) -> str:
        return f"User: {self.second_name} {self.first_name}, \
            with username {self.username} and with tg id {self.telegram_id}, \
            study in univerity that id is {self.university_id} and in group with id {self.group_id}"
        