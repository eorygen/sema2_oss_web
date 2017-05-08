from django.db import models

class AnswerSetUniqueManager(models.Manager):

    def get_queryset(self):
        return super(AnswerSetUniqueManager, self).get_queryset().filter(is_duplicate=False)