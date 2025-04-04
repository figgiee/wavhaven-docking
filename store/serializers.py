from rest_framework import serializers
from .models import Beat
from taggit.serializers import (TagListSerializerField,
                              TaggitSerializer)

class BeatSerializer(TaggitSerializer, serializers.ModelSerializer):
    producer = serializers.ReadOnlyField(source='producer.username')
    tags = TagListSerializerField()
    
    class Meta:
        model = Beat
        fields = ('id', 'title', 'producer', 'audio_file', 'price', 'tags', 'created_at', 'updated_at')


