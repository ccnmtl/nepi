from django.db import models

class LearningModule(models.Model):
	content = models.CharField(max_length=200)
