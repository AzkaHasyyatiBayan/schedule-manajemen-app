from rest_framework import serializers
from .models import Kegiatan

class KegiatanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kegiatan
        fields = ['id', 'tanggal', 'lokasi', 'kegiatan', 'penyerta']