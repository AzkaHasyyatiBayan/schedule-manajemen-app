from rest_framework import serializers
from .models import Kegiatan, HariLibur

class KegiatanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kegiatan
        fields = ['id', 'tanggal', 'lokasi', 'kegiatan', 'penyerta', 'kategori', 'sub_kategori', 'is_auto_generated']

class HariLiburSerializer(serializers.ModelSerializer):
    class Meta:
        model = HariLibur
        fields = ['id', 'tanggal', 'keterangan', 'jenis']