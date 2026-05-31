from django.db import models

class Job(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField(help_text="List required skills, one per line")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class Application(models.Model):

    class Status(models.TextChoices):
        PENDING    = 'PENDING',    'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        REVIEWED   = 'REVIEWED',   'Reviewed'
        FAILED     = 'FAILED',     'Failed'

    job             = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    candidate_name  = models.CharField(max_length=200)
    candidate_email = models.EmailField()
    resume          = models.FileField(upload_to='resumes/%Y/%m/')
    status          = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    ai_score        = models.IntegerField(null=True, blank=True)
    ai_feedback     = models.JSONField(null=True, blank=True)
    applied_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.candidate_name} → {self.job.title} ({self.status})"

    class Meta:
        ordering = ['-applied_at']