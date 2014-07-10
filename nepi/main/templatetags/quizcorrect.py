from django import template

register = template.Library()


def is_question_complete(question, user):
    answers = question.correct_answer_values()
    if len(answers) == 0:
        # No "correct" values for this question
        return True

    responses = question.user_responses(user)
    return len(responses) > 0


def is_question_correct(question, user):
    answers = question.correct_answer_values()
    if len(answers) == 0:
        # No "correct" values for this question
        return True

    responses = question.user_responses(user)
    if len(answers) != len(responses):
        # The user hasn't completely answered the question yet
        return False

    correct = True
    for resp in responses:
        correct = correct and resp.value in answers
    return correct


def is_quiz_correct(quiz, user):
    correct = True
    for question in quiz.question_set.all():
        correct = correct and is_question_correct(question, user)
    return correct


def is_quiz_complete(quiz, user):
    correct = True
    for question in quiz.question_set.all():
        correct = correct and is_question_complete(question, user)
    return correct


class IfQuizCorrectNode(template.Node):
    def __init__(self, quiz, nodelist_true, nodelist_false=None):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.quiz = quiz

    def render(self, context):
        quiz = context[self.quiz]
        user = context['request'].user

        if is_quiz_correct(quiz, user):
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)


@register.tag('ifquizcorrect')
def IfQuizCorrect(parser, token):
    quiz = token.split_contents()[1:][0]
    nodelist_true = parser.parse(('else', 'endifquizcorrect'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endifquizcorrect',))
        parser.delete_first_token()
    else:
        nodelist_false = None
    return IfQuizCorrectNode(quiz, nodelist_true, nodelist_false)


class IfQuizCompleteNode(template.Node):
    def __init__(self, quiz, nodelist_true, nodelist_false=None):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.quiz = quiz

    def render(self, context):
        quiz = context[self.quiz]
        user = context['request'].user

        if is_quiz_complete(quiz, user):
            return self.nodelist_true.render(context)
        elif self.nodelist_false is not None:
            return self.nodelist_false.render(context)
        else:
            return ''


@register.tag('ifquizcomplete')
def IfQuizComplete(parser, token):
    quiz = token.split_contents()[1:][0]
    nodelist_true = parser.parse(('else', 'endifquizcomplete'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endifquizcomplete',))
        parser.delete_first_token()
    else:
        nodelist_false = None
    return IfQuizCompleteNode(quiz, nodelist_true, nodelist_false)
