from nepi.activities.models import (ConversationScenario,
                                    Conversation,
                                    ConversationResponse,
                                    ImageInteractive,
                                    CalendarChart)
from django.contrib import admin


admin.site.register(ConversationScenario)
admin.site.register(Conversation)
admin.site.register(ConversationResponse)
admin.site.register(ImageInteractive)
admin.site.register(CalendarChart)
