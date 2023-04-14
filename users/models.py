from django.db import models

# Create your models here.
class SelfMadeGroup(models.Model):
    group = models.CharField(max_length=200)
    name = models.TextField()
    date_add = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name_plural = 'groups'
    def __str__(self):
        return f"{self.name[:100]}..."
