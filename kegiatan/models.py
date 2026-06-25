from django.db import models

class Kegiatan(models.Model):
    KATEGORI_CHOICES = [
        ('luar_gedung', 'Luar Gedung'),
        ('dalam_gedung', 'Dalam Gedung'),
    ]
    
    SUB_KATEGORI_CHOICES = [
        ('posyandu', 'Posyandu'),
        ('bok', 'BOK'),
        ('sekolah', 'Sekolah'),
        ('kunjungan_lapangan', 'Kunjungan Lapangan'),
        ('inspeksi', 'Inspeksi Kesehatan'),
        ('rapat', 'Rapat'),
        ('lainnya', 'Lainnya'),
    ]
    
    tanggal = models.DateField()
    lokasi = models.CharField(max_length=200)
    kegiatan = models.CharField(max_length=200)
    penyerta = models.TextField()
    kategori = models.CharField(max_length=15, choices=KATEGORI_CHOICES, default='luar_gedung')
    sub_kategori = models.CharField(max_length=20, choices=SUB_KATEGORI_CHOICES, default='lainnya', blank=True)
    
    # Field untuk track randomize
    is_auto_generated = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.tanggal} - {self.kegiatan}"


class HariLibur(models.Model):
    JENIS_CHOICES = [
        ('nasional', 'Hari Libur Nasional'),
        ('cuti_bersama', 'Cuti Bersama'),
        ('custom', 'Custom'),
    ]
    
    tanggal = models.DateField(unique=True)
    keterangan = models.CharField(max_length=200)
    jenis = models.CharField(max_length=15, choices=JENIS_CHOICES, default='nasional')

    def __str__(self):
        return f"{self.tanggal} - {self.keterangan}"