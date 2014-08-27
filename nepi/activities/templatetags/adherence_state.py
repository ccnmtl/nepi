from django.contrib.contenttypes.models import ContentType
from pagetree.models import PageBlock
from quizblock.models import Quiz, Submission, Response, Question
from django import template
register = template.Library()


class GetUserResponse(template.Node):

    def __init__(self, quiz_identifier, var_name):
        self.quiz_identifier = quiz_identifier
        self.var_name = var_name

    def render(self, context):
        try:
            ctype = ContentType.objects.get_for_model(Quiz)
            blocks = PageBlock.objects.filter(
                content_type__pk=ctype.pk,
                css_extra__contains=self.quiz_identifier)
            ids = blocks.values_list('object_id', flat=True)

            quizzes = Quiz.objects.filter(id__in=ids)
            quiz = quizzes[0]  # there should just be one
            user = context['request'].user
            user_submission = Submission.objects.get(user=user, quiz=quiz)
            response = Response.objects.get(submission=user_submission)
            question = Question.objects.get(id=response.question.id)
            answer = question.correct_answer_values()[0]
            context[self.var_name] = answer
            return ''
        except Submission.DoesNotExist:
            return ''
        except IndexError:
            return ''
        return ''


@register.tag('get_response_for')
def get_user_response(parser, token):
    quiz_identifier = token.split_contents()[1:][0].strip()
    var_name = token.split_contents()[1:][2]
    return GetUserResponse(quiz_identifier, var_name)
