class Question:
    id: int
    text: str
    openTime: int
    closeTime: float
    is_multiple_answer: bool
    answers_dict: dict[int, str]
    correct_answers_id: list[int]
    user_answers: list[int]
    
    def __init__(self, id: int, text: str, openTime: int, answers_dict: dict[int, str], correct_answers_id: list[int], is_multiple_answer: bool = False) -> None:
        self.id = id
        self.text = text
        self.openTime = openTime
        self.answers_dict = answers_dict
        self.correct_answers_id = correct_answers_id
        self.is_multiple_answer = is_multiple_answer
        
    def submit_question(self, close_time: float, user_answer: dict[int, str]):
        self.closeTime = close_time
        self.user_answers = user_answer
        
class TestStatistic:
    average_time_for_answer: float = 0
    total_test_time: float = 0
    total_question_count: int = 0
    right_answers_count: int = 0
    skipped_answers_count: int = 0
    wrong_answers_count: int = 0
    
class TestData: 
    id: int
    name: str
    description: str
    questions: list[Question]
    
    def __init__(self, id: int, name: str, questions: list[Question], description: str = "") -> None:
        self.id = id
        self.name = name
        self.questions = questions
        self.description = description
        
    def calculate_statistic(self) -> TestStatistic:
        result = TestStatistic()
        result.total_question_count = len(self.questions)
        for question in self.questions:
            result.total_test_time += question.closeTime
            if not question.user_answers:
                result.skipped_answers_count += 1
                continue
            count_of_right_answers = len([answer for answer in question.user_answers if answer in question.correct_answers_id])
            
            # logic for counting correct answers
            if count_of_right_answers != len(question.correct_answers_id):
                result.wrong_answers_count += 1
                continue
            
            result.right_answers_count += 1
        
        result.average_time_for_answer = result.total_test_time / result.total_question_count
        
        return result