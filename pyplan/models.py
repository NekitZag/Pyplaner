from django.db import models

class Session_Groups(models.Model):
    Name = models.CharField(max_length=200)
    Note = models.CharField(max_length=200)

class Topic(models.Model):
    text = models.CharField(max_length=200)
    #id1 = models.CharField(max_length=300)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text

class Entry(models.Model):
    """инф изученная пользователем по теме"""
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    text = models.TextField()
    date_added= models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'entries'

    def __str__(self):
        """Возрврат строковое представление модели"""
        return f"{self.text[:50]}..."

class Instructors(models.Model):
    SAP_TAB = models.CharField(max_length=200)
    LNAME = models.CharField(max_length=200)
    FNAME = models.CharField(max_length=200)
    MNAME = models.CharField(max_length=200)
    DOLGN = models.CharField(max_length=200)
    GROUP = models.CharField(max_length=200)
    TYPE_ARCRAFT = models.CharField(max_length=200, null=True)

class KRS_according_staff_schedule(models.Model):
    SAP_TAB = models.CharField(max_length=200)
    FULL_NAME = models.CharField(max_length=200)
    DOLGN = models.CharField(max_length=200)
    PODRAZ = models.CharField(max_length=200)

class KRS_LIS_air_squadrons_according_staffing_table(models.Model):
    SAP_TAB = models.CharField(max_length=200)
    FULL_NAME = models.CharField(max_length=200)
    DOLGN = models.CharField(max_length=200)
    PODRAZ = models.CharField(max_length=200)

class freelance_instructor_pilots_check(models.Model):
    SAP_TAB = models.CharField(max_length=200)
    FULL_NAME = models.CharField(max_length=200)
    DOLGN = models.CharField(max_length=200)
    PODRAZ = models.CharField(max_length=200)
    DAT_PROV = models.DateTimeField()
    DAT_TREN = models.DateTimeField()

class freelance_instructor_pilots(models.Model):
    SAP_TAB = models.CharField(max_length=200)
    FULL_NAME = models.CharField(max_length=200)
    DOLGN = models.CharField(max_length=200)
    PODRAZ = models.CharField(max_length=200)
    DAT_PROV = models.DateTimeField(null=True)
    DAT_TREN = models.DateTimeField()