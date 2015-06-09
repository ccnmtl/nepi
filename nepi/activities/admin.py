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
admin.site.register(RetentionRateCard)
admin.site.register(RetentionResponse)
admin.site.register(RetentionClick)


class DayInline(admin.TabularInline):
    model = Day
    extra = 0


class MonthAdmin(admin.ModelAdmin):

    def section(self, obj):
        chart = obj.calendarchart_set.first()
        return chart.pageblock().section.label if chart else None

    def hierarchy(self, obj):
        chart = obj.calendarchart_set.first()
        return chart.pageblock().section.hierarchy.name if chart else None

    list_display = ['display_name', 'hierarchy', 'section']
    readonly_fields = ('hierarchy', 'section')
    inlines = [
        DayInline,
    ]

admin.site.register(Month, MonthAdmin)
