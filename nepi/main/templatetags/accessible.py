from django import template
from nepi.main.views import accessible as section_accessible

register = template.Library()


class AccessibleNode(template.Node):
    def __init__(self, section, nodelist_true, nodelist_false=None):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false
        self.section = section

    def render(self, context):
        s = context[self.section]

        if 'request' in context:
            r = context['request']
            u = r.user
            if section_accessible(s, u):
                return self.nodelist_true.render(context)

        return self.nodelist_false.render(context)


@register.tag('ifaccessible')
def accessible(parser, token):
    section = token.split_contents()[1:][0]
    nodelist_true = parser.parse(('else', 'endifaccessible'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endifaccessible',))
        parser.delete_first_token()
    else:
        nodelist_false = None
    return AccessibleNode(section, nodelist_true, nodelist_false)
