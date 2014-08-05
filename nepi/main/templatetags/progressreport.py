from django import template
from django.contrib.contenttypes.models import ContentType
from pagetree.models import PageBlock
from quizblock.models import Answer, Quiz

register = template.Library()


def get_quizzes_by_css_class(hierarchy, cls):
    ctype = ContentType.objects.get_for_model(Quiz)
    blocks = PageBlock.objects.filter(content_type__pk=ctype.pk,
                                      css_extra__contains=cls,
                                      section__hierarchy=hierarchy)
    ids = blocks.values_list('object_id', flat=True)
    return Quiz.objects.filter(id__in=ids)


def get_quizzes_by_parent(parent, exclude_cls):
    section_ids = [section.id for section in parent.get_descendants()]

    ctype = ContentType.objects.get_for_model(Quiz)
    blocks = PageBlock.objects.filter(
        content_type__pk=ctype.pk, section__id=section_ids).exclude(
        css_extra__contains=exclude_cls)
    ids = blocks.values_list('object_id', flat=True)
    return Quiz.objects.filter(id__in=ids)


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


@register.filter
def pretest_score(user_profile, hierarchy):
    quizzes = get_quizzes_by_css_class(hierarchy, 'pretest')
    return aggregate_score(quizzes, user_profile.user)


@register.filter
def posttest_score(user_profile, hierarchy):
    quizzes = get_quizzes_by_css_class(hierarchy, 'posttest')
    return aggregate_score(quizzes, user_profile.user)


@register.filter
def session_score(user_profile, session):
    if user_profile.percent_complete(session) == 100:
        quizzes = get_quizzes_by_parent(session, ['pretest', 'posttest'])
        return aggregate_score(quizzes, user_profile.user)
    else:
        return 'Incomplete'


@register.filter
def percent_complete(user_profile, hierarchy):
    return user_profile.percent_complete(hierarchy.get_root())


@register.filter
def percent_complete_group(user_profile, group):
    return user_profile.percent_complete(group.module.get_root())


@register.filter
def sessions_completed(user_profile, hierarchy):
    return user_profile.sessions_completed(hierarchy)


@register.filter
def last_location_url(user_profile, hierarchy):
    return user_profile.last_location(hierarchy).get_absolute_url()


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
