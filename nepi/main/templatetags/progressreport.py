from django import template
from django.contrib.contenttypes.models import ContentType
from django.db import models
from pagetree.models import PageBlock
from quizblock.models import Answer, Quiz


register = template.Library()


def get_quizzes_by_css_class(hierarchy, cls):
    ctype = ContentType.objects.get_for_model(Quiz)
    return PageBlock.objects.filter(content_type__pk=ctype.pk,
                                    css_extra__contains=cls,
                                    section__hierarchy=hierarchy)


def get_scorable_content_types():
    types = []
    hierarchy = models.get_model('pagetree', 'hierarchy')
    for block in hierarchy.available_pageblocks():
        if (hasattr(block, 'score')):
            types.append(ContentType.objects.get_for_model(block))

    return types


def get_scorable_blocks(session, types):
    scorable = []
    for page in session.get_descendants():
        for pb in page.pageblock_set.filter(content_type__in=types).exclude(
                css_extra__contains='pretest').exclude(
                css_extra__contains='posttest'):
            scorable.append(pb)

    return scorable


def aggregate_scorable_blocks(users, blocks):
    # only users who are complete are included in the session score
    total_completed = 0
    total_score = 0.0

    if len(blocks) == 0:
        return (None, 0)  # nothing to see here

    for u in users:
        completed = 0
        score = 0
        for pb in blocks:
            block_score = pb.block().score(u)
            if block_score is None:
                completed = 0
                score = 0
                break  # incomplete users are not counted
            else:
                score += block_score
                completed += 1

        total_completed += completed
        total_score += score

    if total_completed == 0:
        return (0, 0)
    else:
        return (total_score / total_completed, total_completed)


def average_session_score(users, hierarchy):
    sessions = hierarchy.get_root().get_children()

    ctx = {'sessions': []}
    session_count = len(sessions)
    total_completed = 0
    total_score = 0.0

    types = get_scorable_content_types()

    for session in sessions:
        blocks = get_scorable_blocks(session, types)
        (session_score, session_completed) = \
            aggregate_scorable_blocks(users, blocks)

        if session_score is None:  # nothing to score
            ctx['sessions'].append(None)
            session_count -= 1
        elif session_completed == 0:  # incomplete
            ctx['sessions'].append(-1)
        else:
            ctx['sessions'].append(int(round(session_score * 100)))
            total_score += session_score
            total_completed += 1

    if total_completed == session_count and total_completed > 0:
        ctx['average_score'] = round(total_score / total_completed * 100)

    return ctx


def average_quiz_score(users, hierarchy, cls):
    blocks = get_quizzes_by_css_class(hierarchy, cls)
    (score, completed) = aggregate_scorable_blocks(users, blocks)
    if score is None:
        return None
    elif completed == 0:
        return -1
    else:
        return int(round(score * 100))


@register.simple_tag
def display_average_quiz_score(user, hierarchy, css_extra_contains):
    score = average_quiz_score([user], hierarchy, css_extra_contains)
    if score is None:
        return "n/a"
    elif score < 0:
        return "Incomplete"
    else:
        return "%s%%" % score


def satisfaction_rating(users, hierarchy):
    '''
        Satisfaction Score: only use question 1,
        if 4 or 5 (agree or strongly agree) was selected, this is Y,
        if anything below 4 was selected this is no.
        Percent reporting satisfaction is percent Y out of total group.
    '''
    blocks = get_quizzes_by_css_class(hierarchy, 'satisfaction')

    if blocks.count() == 0:
        return None

    quiz = blocks[0].block()
    if quiz.question_set.count() == 0:
        return None

    total = 0.0
    completed = 0

    question = quiz.question_set.all()[0]
    for user in users:
        responses = question.user_responses(user)
        if len(responses) > 0:
            completed += 1
            if responses[0].value == "4" or responses[0].value == "5":
                total += 1

    if completed == 0:
        return None
    else:
        return int(round(total / completed * 100))


def get_progress_report(users, hierarchy):
    ctx = {'total_users': len(users)}

    ctx.update(average_session_score(users, hierarchy))

    ctx['pretest'] = average_quiz_score(users, hierarchy, 'pretest')
    ctx['posttest'] = average_quiz_score(users, hierarchy, 'posttest')

    if (ctx['pretest'] is not None and ctx['pretest'] >= 0
            and ctx['posttest'] is not None and ctx['posttest'] >= 0):
        ctx['prepostchange'] = ctx['posttest'] - ctx['pretest']

    ctx['satisfaction'] = satisfaction_rating(users, hierarchy)
    return ctx


@register.filter
def percent_complete(user_profile, hierarchy):
    pct = user_profile.percent_complete(hierarchy.get_root())
    return "{0:.2f}".format(round(pct, 2))


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
