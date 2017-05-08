from django.contrib import admin

from sema2.models import Program, ProgramVersion, ProgramParticipantState, Schedule, EventLog, Answer, AnswerSet, Question, QuestionSet, Survey, \
    ProgramInvite, ProgramParticipantBridge, QuestionOption, ConditionalQuestionSetPredicate

admin.site.register(Program)
admin.site.register(ProgramVersion)
admin.site.register(ProgramParticipantState)
admin.site.register(Schedule)

class EvenLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'log_type', 'user', 'description', 'data')

admin.site.register(EventLog, EvenLogAdmin)

admin.site.register(Survey)


class QuestionSetAdmin(admin.ModelAdmin):
    list_display = ('pk', 'display_name', 'uuid', 'status')

admin.site.register(QuestionSet, QuestionSetAdmin)

admin.site.register(Question)


class QuestionOptionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'label', 'value')

admin.site.register(QuestionOption, QuestionOptionAdmin)


class ProgramParticipantBridgeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'program', 'program_participant_status', 'cached_received_answer_set_count', 'cached_answered_answer_set_count', 'cached_compliance_fraction', 'cached_last_upload_timestamp', 'cached_last_sync_timestamp', 'timezone', 'device_push_token')
    search_fields = ('user__username',)

admin.site.register(ProgramParticipantBridge, ProgramParticipantBridgeAdmin)


class AnswerSetAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'survey', 'program_version', 'iteration', 'uploaded_timestamp', 'is_duplicate')


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('pk', 'answered_timestamp', 'displayed_timestamp', 'set', 'question', 'answer_value')

admin.site.register(AnswerSet, AnswerSetAdmin)

admin.site.register(Answer, AnswerAdmin)

admin.site.register(ConditionalQuestionSetPredicate)

admin.site.register(ProgramInvite)
