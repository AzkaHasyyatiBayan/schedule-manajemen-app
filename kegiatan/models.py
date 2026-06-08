from django.db import models

class Kegiatan(models.Model):
    KATEGORI_CHOICES = [
        ('luar_gedung', 'Luar Gedung'),
        ('dalam_gedung', 'Dalam Gedung'),
    ]
    tanggal = models.DateField()
    lokasi = models.CharField(max_length=200)
    kegiatan = models.CharField(max_length=200)
    penyerta = models.TextField()
    kategori = models.CharField(max_length=15, choices=KATEGORI_CHOICES, default='luar_gedung')

    def __str__(self):
        return f"{self.tanggal} - {self.kegiatan}"