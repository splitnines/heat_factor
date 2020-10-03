from django.db import models


class Uspsa(models.Model):
    uspsa_num = models.CharField(max_length=10)
    division = models.CharField(max_length=20)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True, editable=True)

    class Meta:
        unique_together = ('uspsa_num', 'division')
        db_table = u'uspsa'
        verbose_name = "USPSA"
        verbose_name_plural = "USPSA"

    def __str__(self):
        return self.uspsa_num
