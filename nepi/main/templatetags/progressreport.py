from django import template
from pagetree.models import PageBlock
from quizblock.models import Answer

register = template.Library()


def get_scorable_blocks(session,
                        css_extra_contains=None,
                        css_extra_exclude=None):

    scorable = []
    for page in session.get_descendants():
        for pb in page.pageblock_set.all():
            if (hasattr(pb.block(), 'score')):
                scorable.append(pb.id)

    blocks = PageBlock.objects.filter(id__in=scorable)

    if css_extra_contains:
        blocks = blocks.filter(css_extra__contains=css_extra_contains)

    if css_extra_exclude:
        for css in css_extra_exclude:
            blocks = blocks.exclude(css_extra__contains=css)

    return blocks


def aggregate_scorable_blocks(users, blocks):
    # only users who are complete are included in the session score
    total_completed = 0
    total_score = 0.0

    if blocks.count() == 0:
        return None  # nothing to see here

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
        return 0
    else:
        return total_score / total_completed


def average_session_score(users, hierarchy):
    sessions = hierarchy.get_root().get_children()

    ctx = {'sessions': []}
    exclude = ['pretest', 'posttest']
    session_count = len(sessions)
    completed = 0
    total_score = 0.0

    for session in sessions:
        blocks = get_scorable_blocks(session, css_extra_exclude=exclude)
        session_score = aggregate_scorable_blocks(users, blocks)

        if session_score is None:  # nothing to score here
            ctx['sessions'].append(None)
            session_count -= 1
        elif session_score == 0:  # incomplete
            ctx['sessions'].append(session_score)
        else:
            ctx['sessions'].append(int(round(session_score * 100)))
            total_score += session_score
            completed += 1

    if completed == session_count and completed > 0:
        ctx['average_score'] = round(total_score / completed * 100)

    return ctx


def average_quiz_score(users, hierarchy, css_extra_contains):
    blocks = get_scorable_blocks(hierarchy.get_root(),
                                 css_extra_contains=css_extra_contains)
    session_score = aggregate_scorable_blocks(users, blocks)

    if session_score is None:  # nothing to score here
        return 'n/a'
    elif session_score == 0:  # incomplete
        return 'Incomplete'
    else:
        return str(int(round(session_score * 100))) + "%"


def get_progress_report(users, hierarchy):
    ctx = {'total_users': len(users)}

    ctx.update(average_session_score(users, hierarchy))
    ctx['pretest'] = average_quiz_score(users, hierarchy, 'pretest')
    ctx['posttest'] = average_quiz_score(users, hierarchy, 'posttest')
    return ctx


def aggregate_group_report(groups):
    data = {'total': 0, 'completed': 0, 'incomplete': 0, 'inprogress': 0}

    for group in groups:
        module_root = group.module.get_root()
        active = group.is_active()
        for profile in group.students():
            data['total'] += 1
            pct = profile.percent_complete(module_root)
            if pct == 100:
                data['completed'] += 1
            elif pct > 0:
                if active:
                    data['inprogress'] += 1
                else:
                    data['incomplete'] += 1
    return data


@register.simple_tag
def display_average_quiz_score(user, hierarchy, css_extra_contains):
    return average_quiz_score([user], hierarchy, css_extra_contains)


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
