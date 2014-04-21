from models import NurseConversation, PatientConversation
from models import ConversationScenario#ConversationDialog, ConversationScenario
from models import Conversation, ConversationResponse
from django.contrib import admin

admin.site.register(NurseConversation)
admin.site.register(PatientConversation)
#admin.site.register(ConversationDialog)
admin.site.register(ConversationScenario)
admin.site.register(Conversation)
admin.site.register(ConversationResponse)
