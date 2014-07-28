from django import template

register = template.Library()


def is_user_correct(question, user):
    responses = question.user_responses(user)
    answers = question.correct_answer_values()

    if not question.answerable() or len(answers) == 0:
        # no correct answer. but user needs to have answered the question
        return len(responses) > 0

    if len(answers) != len(responses):
        # The user hasn't completely answered the question yet
        return False

    correct = True
    for resp in responses:
        correct = correct and str(resp.value) in answers
    return correct


@register.filter
def aggregate_score(quizzes, user):
    question_count = 0.0
    questions_correct = 0
    for quiz in quizzes:
        for question in quiz.question_set.all():
            question_count += 1
            if is_user_correct(question, user):
                questions_correct += 1

    if question_count == 0:
        return 0
    else:
        return int(questions_correct / question_count * 100)
