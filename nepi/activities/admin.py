from nepi.activities.models import (Conversation,
                                    ConversationResponse,
                                    Month, Day,
                                    RetentionResponse,
                                    RetentionClick)
from django.contrib import admin


admin.site.register(Conversation)
admin.site.register(ConversationResponse)


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


class RetentionResponseAdmin(admin.ModelAdmin):
    search_fields = ['user__username']
    list_display = ['user', ]

admin.site.register(RetentionClick)
admin.site.register(RetentionResponse, RetentionResponseAdmin)
