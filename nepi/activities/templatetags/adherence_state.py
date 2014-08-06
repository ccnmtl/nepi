from django.contrib.contenttypes.models import ContentType
from pagetree.models import PageBlock
from quizblock.models import Quiz, Submission, Response
from django import template
register = template.Library()


class GetUserResponse(template.Node):

    def __init__(self, quiz_identifier, var_name):
        '''This works...'''
        self.quiz_identifier = quiz_identifier
        self.var_name = var_name

    def render(self, context):
        ctype = ContentType.objects.get_for_model(Quiz)
        try:
            blocks = PageBlock.objects.filter(content_type__pk=ctype.pk,
                                              css_extra__contains=
                                              self.quiz_identifier)
            ids = blocks.values_list('object_id', flat=True)
            quizzes = Quiz.objects.filter(id__in=ids)
            quiz = quizzes[0]
            user = context['request'].user
            user_submission = Submission.objects.get(user=user, quiz=quiz)
            response = Response.objects.get(submission=user_submission)
            return response.value
        except Submission.DoesNotExist:
            return ''
        except IndexError:
            return ''
        return ''


@register.tag('get_response_for')
def get_user_response(parser, token):
    quiz_identifier = token.split_contents()[1:][0]
    var_name = token.split_contents()[1:][2]
    return GetUserResponse(quiz_identifier, var_name)
