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
            return 0

@register.tag('get_response')
def get_response(parser, token):
    user = token.split_contents()[1:][0]
    senario = token.split_contents()[1:][1]
    response = token.split_contents()[1:][2]
    return ConversationState(user, senario, response)

# @register.tag('ifaccessible')
# def accessible(parser, token):
#     section = token.split_contents()[1:][0]
#     nodelist_true = parser.parse(('else', 'endifaccessible'))
#     token = parser.next_token()
#     if token.contents == 'else':
#         nodelist_false = parser.parse(('endifaccessible',))
#         parser.delete_first_token()
#     else:
#         nodelist_false = None
#     return AccessibleNode(section, nodelist_true, nodelist_false)
# @register.tag('get_user_session_state')
# def get_user_session_state(parser, token):
#     user = token.split_contents()[1:][0]
#     session_id = token.split_contents()[1:][1]
#     return GetUserSessionState(user, session_id)
# 
# 
# class CoversationNode(template.Node):
#     def __init__(self, section, nodelist_true, nodelist_false=None):
#         self.nodelist_true = nodelist_true
#         self.nodelist_false = nodelist_false
#         self.section = section
# 
# 
#     def render(self, context):
#         s = context[self.section]
#         
#         if 'request' in context:
#             r = context['request']
#             u = r.user
#     
#             visited, last_section = s.gate_check(u)
# 
#             if s.get_previous().submitted(u):# and visited:
#                 return self.nodelist_true.render(context)
# 
#         return self.nodelist_false.render(context)
# 
# 
