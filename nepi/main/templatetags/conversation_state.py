from django import template
from nepi.activities.models import ConversationResponse
register = template.Library()


class ConversationState(template.Node):
    def __init__(self, user, scenario):
        self.user = template.Variable(user)
        self.scenario = template.Variable(scenario)

    def render(self, context):
        u = self.user.resolve(context)
        try:
            response = ConversationResponse.objects.get(
                conv_scen=self.scenario, user=u)
            if response.third_click:
                return response.third_click.id
            if response.first_click:
                return response.first_click.id
        except ConversationResponse.DoesNotExist:
            return 0


@register.tag('get_response')
def get_response(parser, token):
    user = token.split_contents()[1:][0]
    senario = token.split_contents()[1:][1]
    #response = token.split_contents()[1:][2]
    return ConversationState(user, senario)  #, response)
