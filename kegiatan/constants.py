# ─── DAFTAR SELURUH NAMA PEGAWAI ──────────────────────────────────────────────
DAFTAR_NAMA = [
    "Isep Deni Herdian, S.Kep.,MMRS",
    "Isep Suhendar,SKM",
    "Bdn. Yeni Yulyani Setianingsih, S.ST",
    "Bdn. Nina Ainun, S.Tr.Keb",
    "Rita Sahara, S.Tr.Keb",
    "Dewi Sri Mulyani, Am.Keb",
    "Pipit Puspitasari, Am.Keb",
    "Mira Jatnikawati, Am.Keb",
    "Reni Mustikasari, Am.Keb",
    "Alitsa Nuur Fithri, S.ST",
    "Yesi Apriyani, Am.Keb",
    "Asri Awulan, S.Tr.Keb",
    "Pia Nur Podiana, A.Md.Keb",
    "Intang Sri Purnama, AM.Keb",
    "Ucu Lestari, AM.Keb",
    "Annisa Nafaulloh,S.Tr.Keb.,Bdn",
    "Mutia Wulansari.,S.Kep.,Ners",
    "Ujang Effendi, S.Kep.,Ners",
    "Liska Permatasari, S.Kep.,Ners",
    "Dede Khaerul Kamal Muchtar, AMK",
    "Iman Nurul Haq, A.Md.Kep",
    "Wida Idul Adha, S.Kep.,Ners",
    "Oriany Kemala Dewi, Amd.Kep",
    "Haeriah, A.Md.Kep",
    "Dede Aan Septiantini, A.Md.Kep",
    "dr.Ferry Nalapraya",
    "dr.Muhammad Azhary Romdhon",
    "dr.Iwan Setiawan",
    "dr. Siti Hana Fukui",
    "dr. Volti Diana Suryawadi",
    "drg.Rifan Hanggoro.M.M.R.S",
    "Endah Setiawati,S.Tr.Kes",
    "Khilman Husna Pratama, S.Farm.,Apt",
    "Vita Tyana Virista, A.Md.AK",
    "Gina Giovany, A.Md.AK",
    "Eko Wahyu Saputro, S.K.M",
    "Nurul Hasanah, A.Md.KL",
    "Nova Silpiany Perdany, A.Md.Farm",
    "Ameilia Putri Isyari, S.Gz",
    "Annisa Fauziah, A.Md.Gz",
    "Rudi Sutikno, SKM",
    "Yogi Aris Diyanto, S.E",
    "Rangga Ismardana Gasbela,S.T",
    "Winda Siti Sarah, AMd.RMIK",
    "Pupung Juliana",
    "Salsa Sabila",
    "Andina Dea Priatna, SKM",
    "Iip Supyan"
]

# ─── NAMA YANG DIKECUALIKAN DARI BEBERAPA FITUR ────────────────────────────
NAMA_DIECUALIKAN = [
    "Isep Deni Herdian, S.Kep.,MMRS",
    "Isep Suhendar,SKM"
]

# ─── NAMA YANG TIDAK BOLEH DI KEGIATAN BOK ─────────────────────────────────
NAMA_TIDAK_BOLEH_BOK = [
    "Intang Sri Purnama,AM.Keb",
    "Ameilia Putri Isyari,S.Gz",
    "Ucu Lestari,AM.Keb",
    "Annisa Nafaulloh,S.Tr.Keb.,Bdn",
    "Dede Aan Septiantini,A.Md.Kep",
    "Yogi Aris Diyanto,S.E",
    "Rangga Ismardana Gasbela,S.T",
    "Pupung Juliana",
    "Salsa Sabila",
    "Andina Dea Priatna,SKM",
    "Iip Supyan"
]

# ─── KELOMPOK TETAP ──────────────────────────────────────────────────────────
PENDAFTARAN_TETAP = [
    "Winda Siti Sarah, AMd.RMIK",
    "Pupung Juliana",
    "Salsa Sabila"
]

BP_GIGI_TETAP = [
    "drg.Rifan Hanggoro.M.M.R.S",
    "Endah Setiawati,S.Tr.Kes"
]

APOTEK_TETAP = [
    "Khilman Husna Pratama, S.Farm.,Apt",
    "Nova Silpiany Perdany, A.Md.Farm"
]

LAB_TETAP = [
    "Vita Tyana Virista, A.Md.AK",
    "Gina Giovany, A.Md.AK"
]

ADMINISTRASI_TETAP = [
    "Rangga Ismardana Gasbela,S.T",
    "Yogi Aris Diyanto, S.E"
]

ADMINISTRASI_EXTRA = [
    "Liska Permatasari, S.Kep.,Ners",
    "Alitsa Nuur Fithri, S.ST",
    "Andina Dea Priatna, SKM"
]

PUSTU_CIANGIR = "Haeriah, A.Md.Kep"
PUSTU_SUMELAP = "Ujang Effendi, S.Kep.,Ners"

# ─── ROLE MAPPING UNTUK FILTER DAN RANDOMIZE ────────────────────────────────
ROLE_MAP = {
    'dokter': ['dr.', 'drg.'],
    'perawat_ners': ['Ners', 'S.Kep', 'Amd.Kep', 'A.Md.Kep'],
    'bidan': ['Bdn.', 'S.Tr.Keb', 'Am.Keb', 'A.Md.Keb'],
    'promkes': ['Promosi', 'SKM'],
    'sanitarian': ['Sanitarian', 'S.K.M', 'A.Md.KL'],
    'gizi': ['S.Gz', 'A.Md.Gz'],
    'apoteker': ['Apt', 'S.Farm'],
    'lab': ['A.Md.AK'],
    'gigi': ['drg.', 'S.Tr.Kes'],
    'administrasi': ['S.E', 'S.T', 'S.Kep', 'S.ST', 'SKM', 'AMd.RMIK'],
}

# ─── BULAN (untuk opsi select) ──────────────────────────────────────────────
BULAN_OPTIONS = [
    'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
    'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
]

# ─── HARI KERJA (untuk randomize) ───────────────────────────────────────────
HARI_KERJA = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu']

# ─── CUTI KHUSUS (hari libur per minggu, 0=Senin, 6=Minggu) ─────────────────
CUTI_KHUSUS = {
    'dr.Muhammad Azhary Romdhon': [1, 3],  # Selasa & Kamis
    'dr.Iwan Setiawan': [5],  # Sabtu
}

# ─── RULES DOKTER (hari yang BOLEH masuk untuk kegiatan tertentu) ─────────────
RULES_DOKTER_KEGIATAN = {
    'dr. Volti Diana Suryawadi': {
        'KLASTER DEWASA-LANSIA 1': [0, 5],  # Senin & Sabtu
        'KLASTER DEWASA-LANSIA 2': [0, 5],
    },
    'dr. Siti Hana Fukui': {
        'KLASTER DEWASA-LANSIA 1': [1, 3],  # Selasa & Kamis
        'KLASTER DEWASA-LANSIA 2': [1, 3],
    },
    'dr.Muhammad Azhary Romdhon': {
        'KLASTER IBU KIA & USG': [0, 2],  # Senin & Rabu SAJA
    },
    'dr.Ferry Nalapraya': {
        'KLASTER IBU KIA & USG': [1, 3],  # Selasa & Kamis SAJA
    },
}

# ─── POOL DALAM GEDUNG ──────────────────────────────────────────────────────
POOL_DOKTER = [
    'dr.Ferry Nalapraya',
    'dr.Muhammad Azhary Romdhon',
    'dr.Iwan Setiawan',
    'dr. Siti Hana Fukui',
    'dr. Volti Diana Suryawadi',
    'Mutia Wulansari.,S.Kep.,Ners',
    'Ujang Effendi, S.Kep.,Ners',
    'Liska Permatasari, S.Kep.,Ners',
    'Wida Idul Adha, S.Kep.,Ners',
]

POOL_DOKTER_KIA = [
    'dr.Ferry Nalapraya',
    'dr.Muhammad Azhary Romdhon',
    'dr.Iwan Setiawan',
]

POOL_BIDAN = [
    'Bdn. Yeni Yulyani Setianingsih, S.ST',
    'Bdn. Nina Ainun, S.Tr.Keb',
    'Rita Sahara, S.Tr.Keb',
    'Dewi Sri Mulyani, Am.Keb',
    'Pipit Puspitasari, Am.Keb',
    'Mira Jatnikawati, Am.Keb',
    'Reni Mustikasari, Am.Keb',
    'Alitsa Nuur Fithri, S.ST',
    'Yesi Apriyani, Am.Keb',
    'Asri Awulan, S.Tr.Keb',
    'Pia Nur Podiana, A.Md.Keb',
    'Intang Sri Purnama, AM.Keb',
    'Ucu Lestari, AM.Keb',
    'Annisa Nafaulloh,S.Tr.Keb.,Bdn',
]

POOL_ILP = [
    'Mutia Wulansari.,S.Kep.,Ners',
    'Liska Permatasari, S.Kep.,Ners',
    'Dede Khaerul Kamal Muchtar, AMK',
    'Iman Nurul Haq, A.Md.Kep',
    'Wida Idul Adha, S.Kep.,Ners',
    'Oriany Kemala Dewi, Amd.Kep',
    'Dede Aan Septiantini, A.Md.Kep',
    'Bdn. Yeni Yulyani Setianingsih, S.ST',
    'Bdn. Nina Ainun, S.Tr.Keb',
    'Rita Sahara, S.Tr.Keb',
    'Dewi Sri Mulyani, Am.Keb',
    'Pipit Puspitasari, Am.Keb',
    'Mira Jatnikawati, Am.Keb',
    'Reni Mustikasari, Am.Keb',
    'Alitsa Nuur Fithri, S.ST',
    'Yesi Apriyani, Am.Keb',
    'Asri Awulan, S.Tr.Keb',
    'Pia Nur Podiana, A.Md.Keb',
    'Intang Sri Purnama, AM.Keb',
    'Ucu Lestari, AM.Keb',
    'Annisa Nafaulloh,S.Tr.Keb.,Bdn',
    'Rudi Sutikno, SKM',
    'Eko Wahyu Saputro, S.K.M',
    'Nurul Hasanah, A.Md.KL',
    'Ameilia Putri Isyari, S.Gz',
    'Annisa Fauziah, A.Md.Gz',
]

POOL_TINDAKAN = [
    'Mutia Wulansari.,S.Kep.,Ners',
    'Liska Permatasari, S.Kep.,Ners',
    'Dede Khaerul Kamal Muchtar, AMK',
    'Iman Nurul Haq, A.Md.Kep',
    'Wida Idul Adha, S.Kep.,Ners',
    'Oriany Kemala Dewi, Amd.Kep',
    'Dede Aan Septiantini, A.Md.Kep',
]

LOKA_KARYA_MINI = [
    'Dewi Sri Mulyani, Am.Keb',
    'Pipit Puspitasari, Am.Keb',
    'Mira Jatnikawati, Am.Keb',
    'Reni Mustikasari, Am.Keb',
    'Asri Awulan, S.Tr.Keb',
    'Ujang Effendi, S.Kep.,Ners',
    'Haeriah, A.Md.Kep',
]

# ─── POOL LUAR GEDUNG ────────────────────────────────────────────────────────
POOL_PETUGAS_DOKTER_GIGI = ['dr.Ferry Nalapraya', 'drg.Rifan Hanggoro.M.M.R.S']
POOL_PETUGAS_BIDAN_PERAWAT = [
    'Bdn. Yeni Yulyani Setianingsih, S.ST',
    'Bdn. Nina Ainun, S.Tr.Keb',
    'Rita Sahara, S.Tr.Keb',
    'Dewi Sri Mulyani, Am.Keb',
    'Pipit Puspitasari, Am.Keb',
    'Mira Jatnikawati, Am.Keb',
    'Reni Mustikasari, Am.Keb',
    'Alitsa Nuur Fithri, S.ST',
    'Yesi Apriyani, Am.Keb',
    'Asri Awulan, S.Tr.Keb',
    'Pia Nur Podiana, A.Md.Keb',
    'Mutia Wulansari.,S.Kep.,Ners',
    'Ujang Effendi, S.Kep.,Ners',
    'Liska Permatasari, S.Kep.,Ners',
    'Dede Khaerul Kamal Muchtar, AMK',
    'Iman Nurul Haq, A.Md.Kep',
    'Wida Idul Adha, S.Kep.,Ners',
    'Oriany Kemala Dewi, Amd.Kep',
    'Haeriah, A.Md.Kep',
    'Annisa Fauziah, A.Md.Gz',
]
POOL_PETUGAS_SANITARIAN = [
    'Isep Suhendar,SKM',
    'Eko Wahyu Saputro, S.K.M',
    'Rudi Sutikno, SKM',
]
POOL_PETUGAS_STBM = [
    'Eko Wahyu Saputro, S.K.M',
    'Nurul Hasanah, A.Md.KL',
    'Rudi Sutikno, SKM',
]

# ─── LOKASI LUAR GEDUNG (harus tersebar merata) ─────────────────────────────
LOKASI_LUAR_GEDUNG = ['Tamanjaya', 'Tamansari', 'Sumelap', 'Mugarsari']

# ─── DEFINISI KEGIATAN LUAR GEDUNG ──────────────────────────────────────────
KEGIATAN_LUAR_GEDUNG = {
    'Pelacakan dan pengawasan minum obat untuk ODGJ Berat': {
        'freq': 25,
        'petugas': POOL_PETUGAS_DOKTER_GIGI,
        'penyerta': POOL_PETUGAS_BIDAN_PERAWAT,
        'allow_double_dalam': True,
        'allow_double_luar': False,
        'lokasi_fixed': None,
    },
    'Pelacakan dan pelaporan kematian dan pelaksanaan otopsi verbal kematian Bayi/balita': {
        'freq': 1,
        'petugas': POOL_PETUGAS_DOKTER_GIGI,
        'penyerta': POOL_PETUGAS_BIDAN_PERAWAT,
        'allow_double_dalam': False,
        'allow_double_luar': False,
        'lokasi_fixed': None,
    },
    'Pendampingan rujukan balita stunting/gizi buruk': {
        'freq': 2,
        'petugas': ['Annisa Fauziah, A.Md.Gz'],
        'penyerta': POOL_PETUGAS_BIDAN_PERAWAT,
        'allow_double_dalam': False,
        'allow_double_luar': False,
        'lokasi_fixed': None,
    },
    'Sosialisasi Penyelenggaraan Imunisasi': {
        'freq': 1,
        'petugas': ['Pipit Puspitasari, Am.Keb'],
        'penyerta': POOL_PETUGAS_BIDAN_PERAWAT,
        'allow_double_dalam': False,
        'allow_double_luar': False,
        'lokasi_fixed': 'Tamansari',
        'tanggal_fixed': 27,
    },
    'Deteksi dini dan cek kesehatan gratis di masyarakat': {
        'freq': 14,
        'petugas': POOL_PETUGAS_BIDAN_PERAWAT,
        'penyerta': POOL_PETUGAS_BIDAN_PERAWAT,
        'allow_double_dalam': False,
        'allow_double_luar': False,
        'lokasi_fixed': None,
    },
    'Pemantauan dan tindak lanjut penyakit tidak menular': {
        'freq': 20,
        'petugas': POOL_PETUGAS_BIDAN_PERAWAT[:17],
        'penyerta': POOL_PETUGAS_BIDAN_PERAWAT,
        'allow_double_dalam': False,
        'allow_double_luar': False,
        'lokasi_fixed': None,
    },
    'Inspeksi Kesehatan Lingkungan (IKL) di sarana fasilitas umum': {
        'freq': 10,
        'petugas': POOL_PETUGAS_SANITARIAN + POOL_PETUGAS_BIDAN_PERAWAT,
        'penyerta': POOL_PETUGAS_SANITARIAN + POOL_PETUGAS_BIDAN_PERAWAT,
        'allow_double_dalam': True,
        'allow_double_luar': False,
        'lokasi_fixed': None,
    },
    'Inspeksi Kesehatan Lingkungan di Sarana Tempat Pengolahan Pangan (TPP)': {
        'freq': 10,
        'petugas': POOL_PETUGAS_SANITARIAN + POOL_PETUGAS_BIDAN_PERAWAT,
        'penyerta': POOL_PETUGAS_SANITARIAN + POOL_PETUGAS_BIDAN_PERAWAT,
        'allow_double_dalam': True,
        'allow_double_luar': False,
        'lokasi_fixed': None,
    },
    'Inspeksi Kesehatan Lingkungan di Sarana Air Minum': {
        'freq': 10,
        'petugas': POOL_PETUGAS_SANITARIAN + POOL_PETUGAS_BIDAN_PERAWAT,
        'penyerta': POOL_PETUGAS_SANITARIAN + POOL_PETUGAS_BIDAN_PERAWAT,
        'allow_double_dalam': True,
        'allow_double_luar': False,
        'lokasi_fixed': None,
    },
    'Pemberdayaan kader masyarakat melalui pemicuan untuk implementasi pilar 2-5 STBM': {
        'freq': 10,
        'petugas': POOL_PETUGAS_STBM,
        'penyerta': POOL_PETUGAS_STBM,
        'allow_double_dalam': True,
        'allow_double_luar': False,
        'lokasi_fixed': None,
    },
    'Monitoring Pemberdayaan kader masyarakat melalui pemicuan untuk implementasi pilar 2-5 STBM': {
        'freq': 10,
        'petugas': POOL_PETUGAS_STBM,
        'penyerta': POOL_PETUGAS_STBM,
        'allow_double_dalam': True,
        'allow_double_luar': False,
        'lokasi_fixed': None,
    },
    'Verifikasi Pemberdayaan kader masyarakat melalui pemicuan untuk implementasi pilar 2-5 STBM': {
        'freq': 14,
        'petugas': POOL_PETUGAS_STBM,
        'penyerta': POOL_PETUGAS_STBM,
        'allow_double_dalam': True,
        'allow_double_luar': False,
        'lokasi_fixed': None,
    },
    'Pemantauan minum obat dan terapi pencegahan TBC': {
        'freq': 4,
        'petugas': ['Mutia Wulansari.,S.Kep.,Ners'],
        'penyerta': POOL_PETUGAS_BIDAN_PERAWAT,
        'allow_double_dalam': False,
        'allow_double_luar': False,
        'lokasi_fixed': None,
    },
    'Penemuan Kasus Aktif TB': {
        'freq': 4,
        'petugas': ['Mutia Wulansari.,S.Kep.,Ners'],
        'penyerta': POOL_PETUGAS_BIDAN_PERAWAT,
        'allow_double_dalam': False,
        'allow_double_luar': False,
        'lokasi_fixed': None,
    },
    'Pelacakan Kasus Mangkir': {
        'freq': 4,
        'petugas': ['Mutia Wulansari.,S.Kep.,Ners'],
        'penyerta': POOL_PETUGAS_BIDAN_PERAWAT,
        'allow_double_dalam': False,
        'allow_double_luar': False,
        'lokasi_fixed': None,
    },
    'Investigasi Kasus TB': {
        'freq': 4,
        'petugas': ['Mutia Wulansari.,S.Kep.,Ners'],
        'penyerta': POOL_PETUGAS_BIDAN_PERAWAT,
        'allow_double_dalam': False,
        'allow_double_luar': False,
        'lokasi_fixed': None,
    },
    'Penemuan kasus dan deteksi dini pneumonia': {
        'freq': 4,
        'petugas': ['Pia Nur Podiana, A.Md.Keb'],
        'penyerta': POOL_PETUGAS_BIDAN_PERAWAT,
        'allow_double_dalam': False,
        'allow_double_luar': False,
        'lokasi_fixed': None,
    },
    'Kunjungan ulang 60 hari AFP': {
        'freq': 1,
        'petugas': ['Iman Nurul Haq, A.Md.Kep'],
        'penyerta': [],
        'allow_double_dalam': False,
        'allow_double_luar': False,
        'lokasi_fixed': None,
    },
    'Penemuan dan tindak lanjut penyakit tropis terabaikan': {
        'freq': 4,
        'petugas': ['Mutia Wulansari.,S.Kep.,Ners'],
        'penyerta': POOL_PETUGAS_BIDAN_PERAWAT,
        'allow_double_dalam': False,
        'allow_double_luar': False,
        'lokasi_fixed': None,
    },
    'Pemantauan bayi usia 9-12 bulan yang lahir dari ibu Hepatitis B': {
        'freq': 1,
        'petugas': ['Oriany Kemala Dewi, Amd.Kep'],
        'penyerta': POOL_PETUGAS_BIDAN_PERAWAT,
        'allow_double_dalam': False,
        'allow_double_luar': False,
        'lokasi_fixed': None,
    },
    'Pemantauan status bayi dari ibu positif HIV/sifilis': {
        'freq': 2,
        'petugas': POOL_PETUGAS_BIDAN_PERAWAT[:17],
        'penyerta': POOL_PETUGAS_BIDAN_PERAWAT[:17],
        'allow_double_dalam': False,
        'allow_double_luar': False,
        'lokasi_fixed': None,
    },
    'Pemeriksaan Jentik Nyamuk (survei Vektor DBD)': {
        'freq': 4,
        'petugas': ['Nurul Hasanah, A.Md.KL'],
        'penyerta': POOL_PETUGAS_BIDAN_PERAWAT,
        'allow_double_dalam': True,
        'allow_double_luar': False,
        'lokasi_fixed': None,
    },
    'PSN oleh kader G1R1J': {
        'freq': 4,
        'petugas': ['Nurul Hasanah, A.Md.KL'],
        'penyerta': POOL_PETUGAS_BIDAN_PERAWAT,
        'allow_double_dalam': True,
        'allow_double_luar': False,
        'lokasi_fixed': None,
    },
    'Larvasidasi DBD': {
        'freq': 4,
        'petugas': ['Nurul Hasanah, A.Md.KL'],
        'penyerta': POOL_PETUGAS_BIDAN_PERAWAT,
        'allow_double_dalam': True,
        'allow_double_luar': False,
        'lokasi_fixed': None,
    },
    'Pengasapan Atau Fogging Nyamuk': {
        'freq': 2,
        'petugas': ['Nurul Hasanah, A.Md.KL'],
        'penyerta': POOL_PETUGAS_BIDAN_PERAWAT,
        'count_penyerta': 2,
        'allow_double_dalam': True,
        'allow_double_luar': False,
        'lokasi_fixed': None,
    },
    'Surveilans Kualitas Air Minum Rumah Tangga (KAMRT)': {
        'freq': 30,
        'petugas': ['Eko Wahyu Saputro, S.K.M', 'Nurul Hasanah, A.Md.KL'],
        'penyerta': POOL_PETUGAS_BIDAN_PERAWAT,
        'allow_double_dalam': True,
        'allow_double_luar': False,
        'lokasi_fixed': None,
    },
    'Penyelidikan Kasus Epidemiologi Penyakit Kasus Penyakit menular': {
        'freq': 4,
        'petugas': ['Iman Nurul Haq, A.Md.Kep'],
        'penyerta': POOL_PETUGAS_BIDAN_PERAWAT,
        'allow_double_dalam': True,
        'allow_double_luar': False,
        'lokasi_fixed': None,
    },
    'Verifikasi Sinyal penyakit potensial wabah/KLB': {
        'freq': 2,
        'petugas': ['Iman Nurul Haq, A.Md.Kep', 'Nurul Hasanah, A.Md.KL'],
        'penyerta': POOL_PETUGAS_BIDAN_PERAWAT,
        'allow_double_dalam': True,
        'allow_double_luar': False,
        'lokasi_fixed': None,
    },
    'Penyelidikan Epidimiologi Penyakit Arbovirosis': {
        'freq': 4,
        'petugas': ['Iman Nurul Haq, A.Md.Kep'],
        'penyerta': POOL_PETUGAS_BIDAN_PERAWAT,
        'allow_double_dalam': True,
        'allow_double_luar': False,
        'lokasi_fixed': None,
    },
    'Penyelidikan Epidimiologi Penyakit Zoonosis': {
        'freq': 2,
        'petugas': ['Iman Nurul Haq, A.Md.Kep'],
        'penyerta': POOL_PETUGAS_BIDAN_PERAWAT,
        'allow_double_dalam': True,
        'allow_double_luar': False,
        'lokasi_fixed': None,
    },
    'Pendampingan pelaksanaan ILP di pustu dan Unit Pelayanan Kesehatan Desa/Kelurahan (UPKD/K)': {
        'freq': 1,
        'petugas': ['Rudi Sutikno, SKM'],
        'penyerta': POOL_PETUGAS_BIDAN_PERAWAT,
        'allow_double_dalam': False,
        'allow_double_luar': False,
        'lokasi_fixed': None,
    },
}