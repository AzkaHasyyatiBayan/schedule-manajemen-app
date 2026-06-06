from django.db import models

class Kegiatan(models.Model):
    tanggal = models.DateField()
    lokasi = models.CharField(max_length=200)
    kegiatan = models.CharField(max_length=200)
    penyerta = models.CharField(max_length=500)
    
    def __str__(self):
        return f"{self.tanggal} - {self.kegiatan}"


