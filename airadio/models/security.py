from django.db import models


class AuthorizedRetailUser(models.Model):
    domain = models.CharField(max_length=255)
    ipaddress = models.CharField(max_length=255)

    class Meta:
        app_label = 'airadio'
        db_table = 'authorizedretailuser'
        verbose_name = 'Authorized Retail User'
        verbose_name_plural = 'Authorized Retail Users'

    def __str__(self):
        return str(self.domain)
