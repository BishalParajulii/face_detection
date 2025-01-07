from rest_framework import serializers
from .models import ProcessedVideo

class ProcessedVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessedVideo
        fields = ('video_file', 'location_longitude', 'location_latitude')
