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


# class DosageState(template.Node):
# 
#     def __init__(self, dblock, ml_nvp, times_day, weeks):
#         self.dblock = dblock
#         self.ml_nvp = ml_nvp
#         self.times_day = times_day
#         self.weeks = weeks
# 
#     def render(self, context):
#         b = context[self.dblock]
#         u = context['request'].user
#         context[self.dosage_response.ml_nvp] = b.dosage_response.ml_nvp(u)
#         context[self.dosage_response.times_day] = b.dosage_response.times_day(u)
#         context[self.dosage_response.weeks] = b.dosage_response.weeks(u)
#         return
# 
# 
# @register.tag('getdosageresponse')
# def get_dosage_response(parser, token):
#     dblock = token.split_contents()[1:][0]
#     ml_nvp = token.split_contents()[1:][1]
#     times_day = token.split_contents()[1:][2]
#     weeks = token.split_contents()[1:][2]
#     return DosageState(dblock, ml_nvp, times_day, weeks)


