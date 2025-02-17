<<<<<<< HEAD
from rest_framework import serializers
from .models import Beat

class BeatSerializer(serializers.ModelSerializer):
    producer = serializers.ReadOnlyField(source='producer.username')
    class Meta:
        model = Beat
        fields = ('id', 'title', 'producer', 'audio_file', 'price', 'created_at', 'updated_at')



=======
from rest_framework import serializers
from .models import Beat

class BeatSerializer(serializers.ModelSerializer):
    producer = serializers.ReadOnlyField(source='producer.username')
    class Meta:
        model = Beat
        fields = ('id', 'title', 'producer', 'audio_file', 'price', 'created_at', 'updated_at')



>>>>>>> 43e6d2dca8d245f001e712240bfadecec0527f1e
