from django.db import models


class AdminHoneypotLoginattempt(models.Model):
    username = models.CharField(max_length=255, blank=True, null=True)
    session_key = models.CharField(max_length=50, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField()
    path = models.TextField(blank=True, null=True)
    ip_address = models.CharField(max_length=39, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'admin_honeypot_loginattempt'
        app_label = 'admin_honeypot'
