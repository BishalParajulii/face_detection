from django.db import models

# Create your models here.
class ProcessedVideo(models.Model):
    video_file = models.FileField(upload_to='uploads/videos/')
    location_longitude = models.FloatField()
    location_latitude = models.FloatField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_frames_path = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Video uploaded at {self.uploaded_at} (Location: {self.location_latitude}, {self.location_longitude})"