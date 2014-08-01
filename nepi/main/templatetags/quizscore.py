from django import template
from quizblock.models import Answer

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


class MapAnswerNode(template.Node):
    def __init__(self, response, var_name):
        self.response = response
        self.var_name = var_name

    def render(self, context):
        response = context[self.response]
        answer = Answer.objects.get(question=response.question,
                                    value=response.value)
        context[self.var_name] = answer
        return ''


@register.tag('map_response_to_answer')
def map_response_to_answer(parser, token):
    response = token.split_contents()[1:][0]
    var_name = token.split_contents()[1:][2]
    return MapAnswerNode(response, var_name)
