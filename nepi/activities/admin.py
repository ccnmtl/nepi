from nepi.activities.models import (ConversationScenario,
                                    Conversation,
                                    ConversationResponse,
                                    ImageInteractive,
                                    CalendarChart,
                                    Month,
                                    Day,
                                    RetentionRateCard,
                                    RetentionResponse,
                                    RetentionClick)
from django.contrib import admin


admin.site.register(ConversationScenario)
admin.site.register(Conversation)
admin.site.register(ConversationResponse)
admin.site.register(ImageInteractive)
admin.site.register(CalendarChart)
admin.site.register(Month)
admin.site.register(Day)
admin.site.register(RetentionRateCard)
admin.site.register(RetentionResponse)
admin.site.register(RetentionClick)
