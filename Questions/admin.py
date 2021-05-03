from django.contrib import admin
from .models import *


class QuestionAdmin(admin.ModelAdmin):
    fields = ('question_title', 'tag', 'created_by', 'views')
    list_display = ('question_title', 'tag', 'created_by', 'combine_question_title_and_tag')
    list_display_links = ('tag', 'created_by')
    list_editable = ('question_title',)
    list_filter = ('created_by', 'tag')
    search_fields = ('tag', 'created_by')

    def combine_question_title_and_tag(self, obj):
        return "{} - {}".format(obj.question_title, obj.tag)


class InlineQuestion(admin.TabularInline):
    model = Question
    extra = 1


class TagAdmin(admin.ModelAdmin):
    inlines = [InlineQuestion]


admin.site.register(Question, QuestionAdmin)
admin.site.register(Tag, TagAdmin)

admin.site.site_header = 'Shareef Admin Panel'
admin.site.site_title = 'Shareef Admin'
