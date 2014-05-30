from django import template
register = template.Library()


class DosageState(template.Node):

    def __init__(self, cblock, dosage_response):
        self.cblock = cblock
        self.dosage_response = dosage_response

    def render(self, context):
        b = context[self.cblock]
        u = context['request'].user
        context[self.dosage_response] = b.dosage_response(u)
        return


@register.tag('getdosageresponse')
def get_response(parser, token):
    cblock = token.split_contents()[1:][0]
    dosage_response = token.split_contents()[1:][2]
    return DosageState(cblock, dosage_response)
