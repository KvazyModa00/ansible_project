from django.db import models

class FIO(models.Model):
    myname = models.CharField(max_length=100)

    class Meta:
        db_table = 'FIO'
        

class Job(models.Model):
    job = models.CharField(max_length=200)
    fio = models.ForeignKey(FIO, on_delete=models.CASCADE)

    class Meta:
        db_table = 'job'
        