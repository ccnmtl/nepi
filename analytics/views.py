from annoying.decorators import render_to
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from pagetree.models import Section
import csv
#from wacep.certificates.models import CertificateCourse, CourseAccess
#from wacep.main.views import get_submodule


def responses_for(user):
    result = {}
    for s in user.submission_set.order_by('submitted'):
        for r in s.response_set.all():
            result[r.question.id] = r.value
    return result


def get_row(user, all_questions):
    responses = user_responses(user)
    user_questions = []
    question_ids = responses.keys()
    for q in all_questions:
        if q.id in question_ids:
            user_questions.append(responses[q.id])
        else:
            user_questions.append(None)
    return {
        'user': user,
        'user_questions': user_questions
    }


@login_required
@staff_member_required
@render_to('analytics/the_table.html')
def course_table(request, section_id):
    questions = []
    section = Section.objects.get(pk=section_id)
    if section.get_descendants().count() > 0:
        course = section.get_descendants()
        questions = find_questions(course)
    else:
        questions = find_questions(section)

    all_users = []
    find_certificate_course = CertificateCourse.objects.get(section=section)
    find_course_access = CourseAccess.objects.filter(
        course=find_certificate_course)
    for each in find_course_access:
        all_users.append(each.user)

    the_table = []
    heading = generate_heading(questions)

    for the_user in all_users:
        the_table.append(generate_row(the_user, section,
                                      questions))

    return {'heading': heading, 'the_table': the_table,
            'section_id': section_id}


def find_questions(sections):
    questions = []
    try:
        for the_section in sections:
            for the_pageblock in the_section.pageblock_set.all():
                if the_pageblock.block().__class__.display_name == 'Quiz':
                    questions.extend(the_pageblock.block().question_set.all())

    except:
        the_section = sections
        for the_pageblock in the_section.pageblock_set.all():
            if the_pageblock.block().__class__.display_name == 'Quiz':
                questions.extend(the_pageblock.block().question_set.all())

    return questions


def new_get_module(section):
    if section.is_root():
        return None
    if section.depth == 2:
        return section
    return section.get_ancestors()[1]


def generate_heading(all_questions):
    modules = ["", "", "", ""]
    questions = ['First Name', 'Last Name', 'username', 'Email']
    for question in all_questions:
        module_number = get_submodule(
            question.quiz.pageblocks.all()[0].section)
        question_number = question.display_number()
        store = str(module_number) + " " + str(question_number)
        modules.append(store)
        try:
            text = (question.text).encode('ascii', 'ignore')
        except:
            text = ""
        row = ["%s" % (text)]
        questions.extend(row)
    return {'modules': modules, 'questions': questions}


def generate_row(the_user, all_sections, all_questions):
    responses = responses_for(the_user)
    user_questions = []
    question_ids = responses.keys()

    for the_question in all_questions:
        if the_question.id in question_ids:
            user_questions.append(responses[the_question.id])
        else:
            user_questions.append(None)

    return {
        'the_user': the_user,
        'user_questions': user_questions,
    }


def generate_csv_row(the_user, all_sections, all_questions):
    responses = responses_for(the_user)
    user_questions = []
    question_ids = responses.keys()
    user_row = []

    for the_question in all_questions:
        if the_question.id in question_ids:
            user_questions.append(responses[the_question.id])
        else:
            user_questions.append(None)

    user_row = [the_user.first_name, the_user.last_name,
                the_user.username, the_user.email]

    for each in user_questions:
        try:
            qrow = each.encode('ascii', 'ignore')
            user_row.append(qrow)
        except:
            qrow = each
            user_row.append(qrow)

    return user_row


@login_required
@staff_member_required
def export_csv(request, section_id):
    questions = []
    section = Section.objects.get(pk=section_id)
    if section.get_descendants().count() > 0:
        course = section.get_descendants()
        questions = find_questions(course)
    else:
        questions = find_questions(section)
    all_users = User.objects.filter(is_staff=False)

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename=wacep_responses.csv')
    writer = csv.writer(response)

    headers = generate_heading(questions)
    writer.writerow(headers['modules'])
    writer.writerow(headers['questions'])

    for the_user in all_users:
        writer.writerow(generate_csv_row(the_user, section,
                                         questions))
    return response
