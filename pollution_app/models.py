from django.db import models

class River(models.Model):
    name = models.CharField(max_length=100)
    lat = models.FloatField()
    lon = models.FloatField()
    description = models.TextField()

    def __str__(self):
        return self.name


class Prediction(models.Model):
    river = models.ForeignKey(River, on_delete=models.CASCADE)
    date = models.DateField()
    temperature = models.FloatField()
    ph = models.FloatField()
    nitrogen = models.FloatField()
    flow_speed = models.FloatField()
    result = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Прогноз для {self.river.name} на {self.date}"
