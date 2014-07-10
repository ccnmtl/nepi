from django import template
register = template.Library()


class ConversationState(template.Node):

    def __init__(self, cblock, scenario_response):
        self.cblock = cblock
        self.scenario_response = scenario_response

    def render(self, context):
        b = context[self.cblock]
        u = context['request'].user
        context[self.scenario_response] = b.last_response(u)
        return


@register.tag('getresponse')
def get_response(parser, token):
    cblock = token.split_contents()[1:][0]
    scenario_response = token.split_contents()[1:][2]
    return ConversationState(cblock, scenario_response)
