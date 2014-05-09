from django import template
from nepi.activities.models import ConversationResponse, ConversationScenario
register = template.Library()


class ConversationState(template.Node):
    def __init__(self, user, scenario):
        self.user = template.Variable(user)
        self.scenario = template.Variable(scenario)

    def render(self, context):
        u = self.user.resolve(context)
        s = self.scenario.resolve(context)
        try:
            response = ConversationResponse.objects.get(conv_scen=scenario, user=u)
            if response.third_click:
                return response.third_click.id
            if response.first_click:
                return response.first_click.id
        except ConversationResponseDoesNotExist:
            return '0'

@register.tag('get_response')
def get_response(parser, token):
    user = token.split_contents()[1:][0]
    senario = token.split_contents()[1:][1]
    try:
        response = token.split_contents()[1:][2]
    except IndexError:
        response = '0'
        #is it okay to return different varaibles?
        #can you return something other than a ConversationState object?
    return ConversationState(user, senario)


# @register.tag('get_user_session_state')
# def get_user_session_state(parser, token):
#     user = token.split_contents()[1:][0]
#     session_id = token.split_contents()[1:][1]
#     return GetUserSessionState(user, session_id)