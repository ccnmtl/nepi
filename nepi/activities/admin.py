from nepi.activities.models import (ConversationScenario,
                                    Conversation,
                                    ConversationResponse,
                                    ImageMapItem,
                                    ImageMapChart,
                                    CalendarChart)
from django.contrib import admin


admin.site.register(ConversationScenario)
admin.site.register(Conversation)
admin.site.register(ConversationResponse)
admin.site.register(ImageMapItem)
admin.site.register(ImageMapChart)
admin.site.register(CalendarChart)
