from django.db import models


class Gridiron(models.Model):
    team_name = models.CharField(max_length=100, unique=True, editable=True)
    team_mem1 = models.CharField(max_length=20, unique=True, editable=True)
    team_mem2 = models.CharField(max_length=20, unique=True, editable=True)
    team_mem3 = models.CharField(max_length=20, unique=True, editable=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True, editable=True)

    class Meta:
        db_table = u'gridiron'
        verbose_name = "GRIDIRON"
        verbose_name_plural = "GRIDIRON"

    def __str__(self):
        return self.team_name
