from django.db import models

# Create your models here.
class Credentials(models.Model):
    username  = models.TextField()
    password  = models.TextField()
    
class ExcelSheetData(models.Model):
    data  = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

