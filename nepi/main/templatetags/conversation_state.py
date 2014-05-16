from django import template
register = template.Library()


class ConversationState(template.Node):
    # if there is not response yet can we do this?
    # do I need to stick this in the template?
    def __init__(self, cblock, scenario_response):
        self.cblock = cblock
        self.scenario_response = scenario_response

    def render(self, context):
        b = context[self.cblock]
        #print b
        u = context['request'].user
        #print b.last_response(u).conversation.scenario_type
        context[self.scenario_response] = b.last_response(u)
        return ''


@register.tag('get_response')
def get_response(parser, token):
    cblock = token.split_contents()[1:][0]
    scenario_response = token.split_contents()[1:][1]
    return ConversationState(cblock, scenario_response)
