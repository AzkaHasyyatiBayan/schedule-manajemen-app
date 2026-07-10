# ─── DAFTAR SELURUH NAMA PEGAWAI ──────────────────────────────────────────────
DAFTAR_NAMA = [
    "Isep Deni Herdian,S.Kep.,MMRS", "Isep Suhendar,SKM",
    "Bdn. Yeni Yulyani Setianingsih,S.ST", "Bdn. Nina Ainun,S.Tr.Keb",
    "Rita Sahara,S.Tr.Keb", "Dewi Sri Mulyani,Am.Keb",
    "Pipit Puspitasari,Am.Keb", "Mira Jatnikawati,Am.Keb",
    "Reni Mustikasari,Am.Keb", "Alitsa Nuur Fithri,S.ST",
    "Yesi Apriyani,Am.Keb", "Asri Awulan,S.Tr.Keb",
    "Pia Nur Podiana,A.Md.Keb", "Intang Sri Purnama,AM.Keb",
    "Ucu Lestari,AM.Keb", "Annisa Nafaulloh,S.Tr.Keb.,Bdn",
    "Mutia Wulansari.,S.Kep.,Ners", "Ujang Effendi,S.Kep.,Ners",
    "Liska Permatasari,S.Kep.,Ners", "Dede Khaerul Kamal Muchtar,AMK",
    "Iman Nurul Haq,A.Md.Kep", "Wida Idul Adha,S.Kep.,Ners",
    "Oriany Kemala Dewi,Amd.Kep", "Haeriah,A.Md.Kep",
    "Dede Aan Septiantini,A.Md.Kep", "dr.Ferry Nalapraya",
    "dr.Muhammad Azhary Romdhon", "dr.Iwan Setiawan",
    "dr. Siti Hana Fukui", "dr. Volti Diana Suryawadi",
    "drg.Rifan Hanggoro.M.M.R.S", "Endah Setiawati,S.Tr.Kes",
    "Khilman Husna Pratama,S.Farm.,Apt", "Vita Tyana Virista,A.Md.AK",
    "Gina Giovany,A.Md.AK", "Eko Wahyu Saputro,S.K.M",
    "Nurul Hasanah,A.Md.KL", "Nova Silpiany Perdany,A.Md.Farm",
    "Ameilia Putri Isyari S.Gz", "Annisa Fauziah,A.Md.Gz",
    "Rudi Sutikno,SKM", "Yogi Aris Diyanto,S.E",
    "Rangga Ismardana Gasbela,S.T", "Winda Siti Sarah,AMd.RMIK",
    "Pupung Juliana", "Salsa Sabila", "Andina Dea Priatna,SKM", "Iip Supyan"
]

NAMA_DIECUALIKAN = ["Isep Deni Herdian,S.Kep.,MMRS", "Isep Suhendar,SKM"]

# ─── NAMA YANG TIDAK BOLEH DI KEGIATAN BOK ────────────────────────────────
NAMA_TIDAK_BOLEH_BOK = [
    "Intang Sri Purnama,AM.Keb", "Ameilia Putri Isyari,S.Gz",
    "Ucu Lestari,AM.Keb", "Annisa Nafaulloh,S.Tr.Keb.,Bdn",
    "Dede Aan Septiantini,A.Md.Kep", "Yogi Aris Diyanto,S.E",
    "Rangga Ismardana Gasbela,S.T", "Pupung Juliana",
    "Salsa Sabila", "Andina Dea Priatna,SKM", "Iip Supyan"
]

# ─── NAMA YANG HANYA BOLEH DI PUSTU ──────────────────────────────────────────
NAMA_HANYA_PUSTU = [
    "Ujang Effendi,S.Kep.,Ners",
    "Haeriah,A.Md.Kep",
]

# ─── KELOMPOK TETAP ──────────────────────────────────────────────────────────
PENDAFTARAN_TETAP = ["Winda Siti Sarah,AMd.RMIK", "Pupung Juliana", "Salsa Sabila"]
BP_GIGI_TETAP = ["drg.Rifan Hanggoro.M.M.R.S", "Endah Setiawati,S.Tr.Kes"]
APOTEK_TETAP = ["Khilman Husna Pratama,S.Farm.,Apt", "Nova Silpiany Perdany,A.Md.Farm"]
LAB_TETAP = ["Vita Tyana Virista,A.Md.AK", "Gina Giovany,A.Md.AK"]
ADMINISTRASI_TETAP = ["Rangga Ismardana Gasbela,S.T", "Yogi Aris Diyanto,S.E"]
ADMINISTRASI_EXTRA = ["Liska Permatasari,S.Kep.,Ners", "Andina Dea Priatna,SKM", "Alitsa Nuur Fithri,S.ST"]
PUSTU_CIANGIR = "Haeriah,A.Md.Kep"
PUSTU_SUMELAP = "Ujang Effendi,S.Kep.,Ners"

# ─── CUTI KHUSUS ─────────────────────────────────────────────────────────────
CUTI_KHUSUS = {
    'dr.Muhammad Azhary Romdhon': [1, 3],
    'dr.Iwan Setiawan': [5],
}

# ─── DOKTER WAJIB ─────────────────────────────────────────────────────────────
DOKTER_WAJIB_KEGIATAN = {
    'KLASTER DEWASA-LANSIA 1': {0: 'dr. Volti Diana Suryawadi', 1: 'dr. Siti Hana Fukui'},
    'KLASTER DEWASA-LANSIA 2': {5: 'dr. Volti Diana Suryawadi', 3: 'dr. Siti Hana Fukui'},
    'KLASTER IBU KIA & USG': {0: 'dr.Muhammad Azhary Romdhon', 2: 'dr.Muhammad Azhary Romdhon', 1: 'dr.Ferry Nalapraya', 3: 'dr.Ferry Nalapraya'},
}

# ─── RULES DOKTER ─────────────────────────────────────────────────────────────
RULES_DOKTER_KEGIATAN = {
    'dr. Volti Diana Suryawadi': {'KLASTER DEWASA-LANSIA 1': [0], 'KLASTER DEWASA-LANSIA 2': [5]},
    'dr. Siti Hana Fukui': {'KLASTER DEWASA-LANSIA 1': [1], 'KLASTER DEWASA-LANSIA 2': [3]},
    'dr.Muhammad Azhary Romdhon': {'KLASTER IBU KIA & USG': [0, 2]},
    'dr.Ferry Nalapraya': {'KLASTER IBU KIA & USG': [1, 3]},
}

# ─── POOL DALAM GEDUNG ──────────────────────────────────────────────────────
POOL_DOKTER = ['dr.Ferry Nalapraya', 'dr.Muhammad Azhary Romdhon', 'dr.Iwan Setiawan', 'dr. Siti Hana Fukui', 'dr. Volti Diana Suryawadi', 'Mutia Wulansari.,S.Kep.,Ners', 'Ujang Effendi,S.Kep.,Ners', 'Liska Permatasari,S.Kep.,Ners', 'Wida Idul Adha,S.Kep.,Ners']
POOL_DOKTER_KIA = ['dr.Ferry Nalapraya', 'dr.Muhammad Azhary Romdhon', 'dr.Iwan Setiawan']
POOL_BIDAN = ['Bdn. Yeni Yulyani Setianingsih,S.ST', 'Bdn. Nina Ainun,S.Tr.Keb', 'Rita Sahara,S.Tr.Keb', 'Dewi Sri Mulyani,Am.Keb', 'Pipit Puspitasari,Am.Keb', 'Mira Jatnikawati,Am.Keb', 'Reni Mustikasari,Am.Keb', 'Alitsa Nuur Fithri,S.ST', 'Yesi Apriyani,Am.Keb', 'Asri Awulan,S.Tr.Keb', 'Pia Nur Podiana,A.Md.Keb', 'Intang Sri Purnama,AM.Keb', 'Ucu Lestari,AM.Keb', 'Annisa Nafaulloh,S.Tr.Keb.,Bdn']
POOL_ILP = ['Mutia Wulansari.,S.Kep.,Ners', 'Liska Permatasari,S.Kep.,Ners', 'Dede Khaerul Kamal Muchtar,AMK', 'Iman Nurul Haq,A.Md.Kep', 'Wida Idul Adha,S.Kep.,Ners', 'Oriany Kemala Dewi,Amd.Kep', 'Dede Aan Septiantini,A.Md.Kep', 'Bdn. Yeni Yulyani Setianingsih,S.ST', 'Bdn. Nina Ainun,S.Tr.Keb', 'Rita Sahara,S.Tr.Keb', 'Dewi Sri Mulyani,Am.Keb', 'Pipit Puspitasari,Am.Keb', 'Mira Jatnikawati,Am.Keb', 'Reni Mustikasari,Am.Keb', 'Alitsa Nuur Fithri,S.ST', 'Yesi Apriyani,Am.Keb', 'Asri Awulan,S.Tr.Keb', 'Pia Nur Podiana,A.Md.Keb', 'Intang Sri Purnama,AM.Keb', 'Ucu Lestari,AM.Keb', 'Annisa Nafaulloh,S.Tr.Keb.,Bdn', 'Rudi Sutikno,SKM', 'Eko Wahyu Saputro,S.K.M', 'Nurul Hasanah,A.Md.KL', 'Ameilia Putri Isyari,S.Gz', 'Annisa Fauziah,A.Md.Gz']
POOL_TINDAKAN = ['Mutia Wulansari.,S.Kep.,Ners', 'Liska Permatasari,S.Kep.,Ners', 'Dede Khaerul Kamal Muchtar,AMK', 'Iman Nurul Haq,A.Md.Kep', 'Wida Idul Adha,S.Kep.,Ners', 'Oriany Kemala Dewi,Amd.Kep', 'Dede Aan Septiantini,A.Md.Kep']
LOKA_KARYA_MINI = ['Dewi Sri Mulyani,Am.Keb', 'Pipit Puspitasari,Am.Keb', 'Mira Jatnikawati,Am.Keb', 'Reni Mustikasari,Am.Keb', 'Asri Awulan,S.Tr.Keb', 'Ujang Effendi,S.Kep.,Ners', 'Haeriah,A.Md.Kep']

POOL_DOKTER_F = [n for n in POOL_DOKTER if n not in NAMA_HANYA_PUSTU]
POOL_ILP_F = [n for n in POOL_ILP if n not in NAMA_HANYA_PUSTU]
POOL_TINDAKAN_F = [n for n in POOL_TINDAKAN if n not in NAMA_HANYA_PUSTU]
LOKA_KARYA_MINI_F = [n for n in LOKA_KARYA_MINI if n not in NAMA_HANYA_PUSTU]

# ─── POOL LUAR GEDUNG ────────────────────────────────────────────────────────
POOL_PETUGAS_DOKTER_GIGI = ['dr.Ferry Nalapraya', 'drg.Rifan Hanggoro.M.M.R.S']

POOL_PETUGAS_BIDAN_PERAWAT = [
    'Bdn. Yeni Yulyani Setianingsih,S.ST', 'Bdn. Nina Ainun,S.Tr.Keb', 'Rita Sahara,S.Tr.Keb',
    'Dewi Sri Mulyani,Am.Keb', 'Pipit Puspitasari,Am.Keb', 'Mira Jatnikawati,Am.Keb',
    'Reni Mustikasari,Am.Keb', 'Alitsa Nuur Fithri,S.ST', 'Yesi Apriyani,Am.Keb',
    'Asri Awulan,S.Tr.Keb', 'Pia Nur Podiana,A.Md.Keb', 'Mutia Wulansari.,S.Kep.,Ners',
    'Ujang Effendi,S.Kep.,Ners', 'Liska Permatasari,S.Kep.,Ners', 'Dede Khaerul Kamal Muchtar,AMK',
    'Iman Nurul Haq,A.Md.Kep', 'Wida Idul Adha,S.Kep.,Ners', 'Oriany Kemala Dewi,Amd.Kep',
    'Haeriah,A.Md.Kep', 'Annisa Fauziah,A.Md.Gz'
]

POOL_PETUGAS_SANITARIAN = ['Isep Suhendar,SKM', 'Eko Wahyu Saputro,S.K.M', 'Rudi Sutikno,SKM']
POOL_PETUGAS_STBM = ['Eko Wahyu Saputro,S.K.M', 'Nurul Hasanah,A.Md.KL', 'Rudi Sutikno,SKM']

LOKASI_LUAR_GEDUNG = ['Tamanjaya', 'Tamansari', 'Sumelap', 'Mugarsari']

# ─── LOKASI STBM ─────────────────────────────────────────────────────────────
LOKASI_STBM = ['Tamanjaya', 'Tamansari', 'Sumelap', 'Mugarsari', 'Cieurih', 'Liunggunung', 'Kadupandak', 
               'Babakan Jati', 'Sukaasih', 'Cigintung', 'Kubangsari', 'Malingping', 'Sindangreret', 
               'Karisma', 'Cibeureum', 'Nagarasari', 'Situdukun', 'Gegernoong', 'Taman', 'Harapan Bunda', 
               'Kasih Bunda', 'Cidahu', 'Nusa Indah', 'Bantarsari', 'Selaawi', 'Sidamulih', 'Cipasung', 
               'Nangela', 'Jatiwangi', 'Kubang', 'Nyantong', 'Sinargalih', 'Ciatal', 'Bandung', 'Cipajaran', 
               'Situhiang', 'Ciledug', 'Selakaso', 'Cipamutih', 'Sangkali', 'Ciangir', 'Cipangebak']

# ─── JADWAL FIXED POSYANDU ──────────────────────────────────────────────────
JADWAL_POSYANDU_FIXED = {
    'Posyandu Cieurih': {'hari': 0, 'minggu_ke': 1, 'kelurahan': 'Sumelap', 'petugas': ['Asri Awulan,S.Tr.Keb'], 'penyerta': ['Wida Idul Adha,S.Kep.,Ners']},
    'Posyandu Liunggunung': {'hari': 1, 'minggu_ke': 1, 'kelurahan': 'Sumelap', 'petugas': ['Asri Awulan,S.Tr.Keb'], 'penyerta': ['Dede Khaerul Kamal Muchtar,AMK']},
    'Posyandu Kadupandak': {'hari': 2, 'minggu_ke': 1, 'kelurahan': 'Sumelap', 'petugas': ['Asri Awulan,S.Tr.Keb'], 'penyerta': ['Oriany Kemala Dewi,Amd.Kep']},
    'Posyandu Perum Puri Sumelap': {'hari': 0, 'minggu_ke': 2, 'kelurahan': 'Sumelap', 'petugas': ['Asri Awulan,S.Tr.Keb'], 'penyerta': []},
    'Posyandu Babakan Jati': {'hari': 1, 'minggu_ke': 2, 'kelurahan': 'Sumelap', 'petugas': ['Asri Awulan,S.Tr.Keb'], 'penyerta': ['Yesi Apriyani,Am.Keb']},
    'Posyandu Sumelap': {'hari': 2, 'minggu_ke': 2, 'kelurahan': 'Sumelap', 'petugas': ['Asri Awulan,S.Tr.Keb'], 'penyerta': []},
    'Posyandu Sukaasih': {'hari': 0, 'minggu_ke': 3, 'kelurahan': 'Sumelap', 'petugas': ['Asri Awulan,S.Tr.Keb'], 'penyerta': ['Ucu Lestari,AM.Keb']},
    'Posyandu Perum Sukawening': {'hari': 1, 'minggu_ke': 3, 'kelurahan': 'Sumelap', 'petugas': ['Asri Awulan,S.Tr.Keb'], 'penyerta': ['Ucu Lestari,AM.Keb']},
    'Posyandu Cigintung': {'hari': 2, 'minggu_ke': 3, 'kelurahan': 'Sumelap', 'petugas': ['Asri Awulan,S.Tr.Keb'], 'penyerta': ['Annisa Nafaulloh,S.Tr.Keb.,Bdn']},
    'Posyandu Ciharashas': {'hari': 0, 'minggu_ke': 1, 'kelurahan': 'Sumelap', 'petugas': ['Asri Awulan,S.Tr.Keb'], 'penyerta': []},
    'Posyandu Kubangsari': {'hari': 0, 'minggu_ke': 1, 'kelurahan': 'Tamanjaya', 'petugas': ['Pipit Puspitasari,Am.Keb'], 'penyerta': ['Dede Aan Septiantini,A.Md.Kep']},
    'Posyandu Malingping': {'hari': 1, 'minggu_ke': 1, 'kelurahan': 'Tamanjaya', 'petugas': ['Pipit Puspitasari,Am.Keb'], 'penyerta': ['Iman Nurul Haq,A.Md.Kep']},
    'Posyandu Sindangreret': {'hari': 2, 'minggu_ke': 1, 'kelurahan': 'Tamanjaya', 'petugas': ['Pipit Puspitasari,Am.Keb'], 'penyerta': ['Alitsa Nuur Fithri,S.ST']},
    'Posyandu Karisma': {'hari': 3, 'minggu_ke': 1, 'kelurahan': 'Tamanjaya', 'petugas': ['Pipit Puspitasari,Am.Keb'], 'penyerta': ['Alitsa Nuur Fithri,S.ST']},
    'Posyandu Cibeureum': {'hari': 0, 'minggu_ke': 2, 'kelurahan': 'Tamanjaya', 'petugas': ['Pipit Puspitasari,Am.Keb'], 'penyerta': ['Dede Aan Septiantini,A.Md.Kep']},
    'Posyandu Nagarasari': {'hari': 1, 'minggu_ke': 2, 'kelurahan': 'Tamanjaya', 'petugas': ['Pipit Puspitasari,Am.Keb'], 'penyerta': ['Liska Permatasari,S.Kep.,Ners']},
    'Posyandu Situdukun': {'hari': 2, 'minggu_ke': 2, 'kelurahan': 'Tamanjaya', 'petugas': ['Pipit Puspitasari,Am.Keb'], 'penyerta': []},
    'Posyandu Gegernoong': {'hari': 3, 'minggu_ke': 2, 'kelurahan': 'Tamanjaya', 'petugas': ['Pipit Puspitasari,Am.Keb'], 'penyerta': []},
    'Posyandu Taman': {'hari': 4, 'minggu_ke': 2, 'kelurahan': 'Tamanjaya', 'petugas': ['Pipit Puspitasari,Am.Keb'], 'penyerta': ['Pia Nur Podiana,A.Md.Keb']},
    'Posyandu Harapan Bunda': {'hari': 5, 'minggu_ke': 2, 'kelurahan': 'Tamanjaya', 'petugas': ['Pipit Puspitasari,Am.Keb'], 'penyerta': ['Annisa Nafaulloh,S.Tr.Keb.,Bdn']},
    'Posyandu Kasih Bunda': {'hari': 0, 'minggu_ke': 3, 'kelurahan': 'Tamanjaya', 'petugas': ['Pipit Puspitasari,Am.Keb'], 'penyerta': ['Pia Nur Podiana,A.Md.Keb']},
    'Posyandu Cidahu': {'hari': 1, 'minggu_ke': 3, 'kelurahan': 'Tamanjaya', 'petugas': ['Pipit Puspitasari,Am.Keb'], 'penyerta': ['Oriany Kemala Dewi,Amd.Kep']},
    'Posyandu Perum Nusa Indah': {'hari': 2, 'minggu_ke': 3, 'kelurahan': 'Tamanjaya', 'petugas': ['Pipit Puspitasari,Am.Keb'], 'penyerta': ['Liska Permatasari,S.Kep.,Ners']},
    'Posyandu Bantarsari': {'hari': 3, 'minggu_ke': 3, 'kelurahan': 'Tamanjaya', 'petugas': ['Pipit Puspitasari,Am.Keb'], 'penyerta': ['Iman Nurul Haq,A.Md.Kep']},
    'Posyandu Selaawi': {'hari': 1, 'minggu_ke': 1, 'kelurahan': 'Mugarsari', 'petugas': ['Dewi Sri Mulyani,Am.Keb'], 'penyerta': ['Wida Idul Adha,S.Kep.,Ners']},
    'Posyandu Sidamulih': {'hari': 3, 'minggu_ke': 1, 'kelurahan': 'Mugarsari', 'petugas': ['Dewi Sri Mulyani,Am.Keb'], 'penyerta': ['Bdn. Nina Ainun,S.Tr.Keb']},
    'Posyandu Bbk.Cipasung': {'hari': 1, 'minggu_ke': 2, 'kelurahan': 'Mugarsari', 'petugas': ['Dewi Sri Mulyani,Am.Keb'], 'penyerta': ['Wida Idul Adha,S.Kep.,Ners']},
    'Posyandu Nangela': {'hari': 2, 'minggu_ke': 2, 'kelurahan': 'Mugarsari', 'petugas': ['Dewi Sri Mulyani,Am.Keb'], 'penyerta': ['Bdn. Nina Ainun,S.Tr.Keb']},
    'Posyandu Jatiwangi': {'hari': 3, 'minggu_ke': 2, 'kelurahan': 'Mugarsari', 'petugas': ['Dewi Sri Mulyani,Am.Keb'], 'penyerta': []},
    'Posyandu Cipasung': {'hari': 1, 'minggu_ke': 3, 'kelurahan': 'Mugarsari', 'petugas': ['Dewi Sri Mulyani,Am.Keb'], 'penyerta': ['Ujang Effendi,S.Kep.,Ners']},
    'Posyandu Kubang': {'hari': 2, 'minggu_ke': 3, 'kelurahan': 'Mugarsari', 'petugas': ['Dewi Sri Mulyani,Am.Keb'], 'penyerta': ['Ujang Effendi,S.Kep.,Ners']},
    'Posyandu Nyantong': {'hari': 3, 'minggu_ke': 3, 'kelurahan': 'Mugarsari', 'petugas': ['Dewi Sri Mulyani,Am.Keb'], 'penyerta': []},
    'Posyandu Sinargalih': {'hari': 0, 'minggu_ke': 1, 'kelurahan': 'Tamansari', 'petugas': ['Mira Jatnikawati,Am.Keb'], 'penyerta': ['Iman Nurul Haq,A.Md.Kep', 'Reni Mustikasari,Am.Keb']},
    'Posyandu Ciatal': {'hari': 2, 'minggu_ke': 1, 'kelurahan': 'Tamansari', 'petugas': ['Mira Jatnikawati,Am.Keb'], 'penyerta': ['Reni Mustikasari,Am.Keb']},
    'Posyandu Bandung': {'hari': 3, 'minggu_ke': 1, 'kelurahan': 'Tamansari', 'petugas': ['Mira Jatnikawati,Am.Keb'], 'penyerta': ['Dede Khaerul Kamal Muchtar,AMK', 'Reni Mustikasari,Am.Keb']},
    'Posyandu Cipajaran': {'hari': 4, 'minggu_ke': 1, 'kelurahan': 'Tamansari', 'petugas': ['Mira Jatnikawati,Am.Keb'], 'penyerta': ['Bdn. Yeni Yulyani Setianingsih,S.ST', 'Reni Mustikasari,Am.Keb']},
    'Posyandu Situhiang': {'hari': 0, 'minggu_ke': 2, 'kelurahan': 'Tamansari', 'petugas': ['Mira Jatnikawati,Am.Keb'], 'penyerta': ['Reni Mustikasari,Am.Keb']},
    'Posyandu Ciledug': {'hari': 1, 'minggu_ke': 2, 'kelurahan': 'Tamansari', 'petugas': ['Mira Jatnikawati,Am.Keb'], 'penyerta': ['Reni Mustikasari,Am.Keb']},
    'Posyandu Selakaso': {'hari': 2, 'minggu_ke': 2, 'kelurahan': 'Tamansari', 'petugas': ['Mira Jatnikawati,Am.Keb'], 'penyerta': ['Iman Nurul Haq,A.Md.Kep', 'Reni Mustikasari,Am.Keb']},
    'Posyandu Cipamutih': {'hari': 3, 'minggu_ke': 2, 'kelurahan': 'Tamansari', 'petugas': ['Mira Jatnikawati,Am.Keb'], 'penyerta': ['Yesi Apriyani,Am.Keb', 'Reni Mustikasari,Am.Keb']},
    'Posyandu Sangkali': {'hari': 4, 'minggu_ke': 2, 'kelurahan': 'Tamansari', 'petugas': ['Mira Jatnikawati,Am.Keb'], 'penyerta': ['Bdn. Yeni Yulyani Setianingsih,S.ST', 'Reni Mustikasari,Am.Keb']},
    'Posyandu Ciangir': {'hari': 0, 'minggu_ke': 3, 'kelurahan': 'Tamansari', 'petugas': ['Mira Jatnikawati,Am.Keb'], 'penyerta': ['Haeriah,A.Md.Kep', 'Reni Mustikasari,Am.Keb']},
    'Posyandu Cipangebak': {'hari': 3, 'minggu_ke': 3, 'kelurahan': 'Tamansari', 'petugas': ['Mira Jatnikawati,Am.Keb'], 'penyerta': ['Haeriah,A.Md.Kep', 'Reni Mustikasari,Am.Keb']},
}

# ─── JADWAL FIXED POSBINDU ──────────────────────────────────────────────────
JADWAL_POSBINDU_FIXED = {
    'Posbindu Cigintung': {'hari': 2, 'minggu_ke': 3, 'kelurahan': 'Sumelap', 'petugas': ['Annisa Nafaulloh,S.Tr.Keb.,Bdn']},
    'Posbindu Sindangreret': {'hari': 3, 'minggu_ke': 1, 'kelurahan': 'Tamanjaya', 'petugas': ['Dede Aan Septiantini,A.Md.Kep']},
    'Posbindu Sidamulih': {'hari': 3, 'minggu_ke': 1, 'kelurahan': 'Mugarsari', 'petugas': ['Bdn. Nina Ainun,S.Tr.Keb']},
    'Posbindu Sumelap': {'hari': 1, 'minggu_ke': 2, 'kelurahan': 'Sumelap', 'petugas': ['Asri Awulan,S.Tr.Keb']},
    'Posbindu Taman': {'hari': 4, 'minggu_ke': 2, 'kelurahan': 'Tamanjaya', 'petugas': ['Pia Nur Podiana,A.Md.Keb']},
    'Posbindu Jatiwangi': {'hari': 3, 'minggu_ke': 2, 'kelurahan': 'Mugarsari', 'petugas': ['Dewi Sri Mulyani,Am.Keb']},
    'Posbindu Cipamutih': {'hari': 3, 'minggu_ke': 2, 'kelurahan': 'Tamansari', 'petugas': ['Yesi Apriyani,Am.Keb']},
    'Posbindu Nagarasari': {'hari': 4, 'minggu_ke': 2, 'kelurahan': 'Tamanjaya', 'petugas': ['Liska Permatasari,S.Kep.,Ners']},
    'Posbindu Sukaasih': {'hari': 0, 'minggu_ke': 3, 'kelurahan': 'Sumelap', 'petugas': ['Ucu Lestari,AM.Keb']},
    'Posbindu Cidahu': {'hari': 1, 'minggu_ke': 3, 'kelurahan': 'Tamanjaya', 'petugas': ['Oriany Kemala Dewi,Amd.Kep']},
    'Posbindu Perum Tamanjaya': {'hari': 3, 'minggu_ke': 3, 'kelurahan': 'Tamanjaya', 'petugas': ['Liska Permatasari,S.Kep.,Ners']},
    'Posbindu Sindangreret RW 05': {'hari': 0, 'minggu_ke': 2, 'kelurahan': 'Tamanjaya', 'petugas': ['Alitsa Nuur Fithri,S.ST']},
}

# ─── JADWAL FIXED POS REMAJA ─────────────────────────────────────────────────
JADWAL_POS_REMAJA_FIXED = {
    'Pos Yandu Remaja Kereta': {'hari': 3, 'minggu_ke': 4, 'kelurahan': 'Tamanjaya', 'petugas': ['Endah Setiawati,S.Tr.Kes']},
    'Pos Yandu Remaja Sakura': {'hari': 4, 'minggu_ke': 4, 'kelurahan': 'Tamanjaya', 'petugas': ['Annisa Nafaulloh,S.Tr.Keb.,Bdn']},
}

# ─── DAFTAR UKK ──────────────────────────────────────────────────────────────
DAFTAR_UKK = [
    {'nama': 'CV. Katumbiri', 'kelurahan': 'Sumelap', 'petugas': ['Mira Jatnikawati,Am.Keb']},
    {'nama': 'Pasar Geger Noong', 'kelurahan': 'Tamanjaya', 'petugas': ['Mira Jatnikawati,Am.Keb']},
]

# ─── DAFTAR SEKOLAH ──────────────────────────────────────────────────────────
DAFTAR_SEKOLAH_PESANTREN = [
    'Al-Ma\'muniyah', 'Al-Istiqomah', 'Al-Barokah', 'Raudlatutta\'allum',
    'Al-Ikhsan', 'Bustanul Ulum', 'Al-Furqon', 'Baetul Rohman',
    'Al-Muflih', 'Nurul Ihsan', 'Al-Falah', 'Babul Hikmah', 'Al-Huda',
    'Miftahul Ulum', 'Al-Musyri', 'Darul Ulum', 'Miftahul Anwar', 'Raudatul Ulum',
    'Al-Ihsan', 'Attaofiq', 'Al-Misbah', 'Miftahul Ulum Tamansari', 'Al-Mubarok',
    'Miftahussalam', 'Al-Muhtar', 'Al-Mubtadiin', 'Baitul Amanah', 'Sinargalih',
    'Al-Hikmah', 'Al-Ihsan Cipamutih', 'Miftahul Huda VII', 'Assarongki',
    'Miftahul Khoer Al-Musri II', 'Miftahul Ihsan', 'Al-Abror', 'Cilampahan'
]

# ─── WAJIB SEKOLAH ───────────────────────────────────────────────────────────
WAJIB_SEKOLAH = ['drg.Rifan Hanggoro.M.M.R.S', 'Endah Setiawati,S.Tr.Kes', 'Annisa Fauziah,A.Md.Gz']

# ─── POOL PENYERTA UNTUK BOK ─────────────────────────────────────────────────
POOL_PENYERTA_BOK = [
    'Bdn. Yeni Yulyani Setianingsih,S.ST', 'Bdn. Nina Ainun,S.Tr.Keb', 'Rita Sahara,S.Tr.Keb',
    'Dewi Sri Mulyani,Am.Keb', 'Pipit Puspitasari,Am.Keb', 'Mira Jatnikawati,Am.Keb',
    'Reni Mustikasari,Am.Keb', 'Alitsa Nuur Fithri,S.ST', 'Yesi Apriyani,Am.Keb',
    'Asri Awulan,S.Tr.Keb', 'Pia Nur Podiana,A.Md.Keb', 'Mutia Wulansari.,S.Kep.,Ners',
    'Ujang Effendi,S.Kep.,Ners', 'Liska Permatasari,S.Kep.,Ners', 'Dede Khaerul Kamal Muchtar,AMK',
    'Iman Nurul Haq,A.Md.Kep', 'Wida Idul Adha,S.Kep.,Ners', 'Oriany Kemala Dewi,Amd.Kep',
    'Haeriah,A.Md.Kep', 'Annisa Fauziah,A.Md.Gz'
]

# ─── DEFINISI KEGIATAN BOK ──────────────────────────────────────────────────
KEGIATAN_BOK = {
    # 1. ODGJ Berat
    'Pelacakan dan pengawasan minum obat untuk ODGJ Berat': {
        'freq': 25,
        'petugas': ['dr.Ferry Nalapraya', 'drg.Rifan Hanggoro.M.M.R.S'],
        'penyerta': POOL_PENYERTA_BOK[:12],
        'count_penyerta': 1,
        'allow_double_dalam': True,
        'allow_double_luar': True,
        'allow_penyerta_jadi_petugas': True,
    },

    # 2. Otopsi verbal
    'Pelacakan dan pelaporan kematian dan pelaksanaan otopsi verbal kematian Bayi/balita': {
        'freq': 1,
        'petugas': ['dr.Ferry Nalapraya', 'drg.Rifan Hanggoro.M.M.R.S'],
        'penyerta': POOL_PENYERTA_BOK[:12],
        'count_penyerta': 1,
        'allow_double_dalam': False,
        'allow_double_luar': False,
        'allow_penyerta_jadi_petugas': True,
    },

    # 3. Pendampingan stunting
    'Pendampingan rujukan balita stunting/gizi buruk': {
        'freq': 2,
        'petugas': ['Annisa Fauziah,A.Md.Gz'],
        'penyerta': POOL_PENYERTA_BOK,
        'count_penyerta': 1,
        'allow_double_dalam': False,
        'allow_double_luar': False,
        'allow_penyerta_jadi_petugas': True,
    },

    # 4. Sosialisasi Imunisasi
    'Sosialisasi Penyelenggaraan Imunisasi': {
        'freq': 1,
        'petugas': ['Pipit Puspitasari,Am.Keb'],
        'penyerta': POOL_PENYERTA_BOK,
        'count_penyerta': 1,
        'allow_double_dalam': False,
        'allow_double_luar': False,
        'lokasi_fixed': 'Tamansari',
        'tanggal_fixed': 27,
        'allow_penyerta_jadi_petugas': True,
    },

    # 5. Deteksi dini
    'Deteksi dini dan cek kesehatan gratis di masyarakat': {
        'freq': 14,
        'petugas': POOL_PENYERTA_BOK,
        'penyerta': POOL_PENYERTA_BOK,
        'count_penyerta': 3,
        'allow_double_dalam': False,
        'allow_double_luar': True,
        'allow_penyerta_jadi_petugas': True,
    },

    # 6. Pemantauan PTM
    'Pemantauan dan tindak lanjut penyakit tidak menular': {
        'freq': 20,
        'petugas': POOL_PENYERTA_BOK[:18],
        'penyerta': POOL_PENYERTA_BOK,
        'count_penyerta': 1,
        'allow_double_dalam': False,
        'allow_double_luar': True,
        'allow_penyerta_jadi_petugas': True,
    },

    # 7. IKL fasilitas umum
    'Inspeksi Kesehatan Lingkungan (IKL) di sarana fasilitas umum': {
        'freq': 10,
        'petugas': POOL_PETUGAS_SANITARIAN + POOL_PENYERTA_BOK,
        'penyerta': POOL_PETUGAS_SANITARIAN + POOL_PENYERTA_BOK,
        'count_penyerta': 1,
        'allow_double_dalam': True,
        'allow_double_luar': True,
        'allow_penyerta_jadi_petugas': True,
    },

    # 8. IKL TPP
    'Inspeksi Kesehatan Lingkungan di Sarana Tempat Pengolahan Pangan (TPP)': {
        'freq': 10,
        'petugas': POOL_PETUGAS_SANITARIAN + POOL_PENYERTA_BOK,
        'penyerta': POOL_PETUGAS_SANITARIAN + POOL_PENYERTA_BOK,
        'count_penyerta': 1,
        'allow_double_dalam': True,
        'allow_double_luar': True,
        'allow_penyerta_jadi_petugas': True,
    },

    # 9. IKL Air Minum
    'Inspeksi Kesehatan Lingkungan di Sarana Air Minum': {
        'freq': 10,
        'petugas': POOL_PETUGAS_SANITARIAN + POOL_PENYERTA_BOK,
        'penyerta': POOL_PETUGAS_SANITARIAN + POOL_PENYERTA_BOK,
        'count_penyerta': 1,
        'allow_double_dalam': True,
        'allow_double_luar': True,
        'allow_penyerta_jadi_petugas': True,
    },

    # 10. Pemberdayaan STBM
    'Pemberdayaan kader masyarakat melalui pemicuan untuk implementasi pilar 2-5 STBM': {
        'freq': 10,
        'petugas': POOL_PETUGAS_STBM,
        'penyerta': POOL_PENYERTA_BOK,
        'count_penyerta': 1,
        'allow_double_dalam': True,
        'allow_double_luar': True,
        'lokasi_pool': LOKASI_STBM,
        'allow_penyerta_jadi_petugas': True,
    },

    # 11. Monitoring STBM
    'Monitoring Pemberdayaan kader masyarakat melalui pemicuan untuk implementasi pilar 2-5 STBM': {
        'freq': 10,
        'petugas': POOL_PETUGAS_STBM,
        'penyerta': POOL_PENYERTA_BOK,
        'count_penyerta': 1,
        'allow_double_dalam': True,
        'allow_double_luar': True,
        'lokasi_pool': LOKASI_STBM,
        'allow_penyerta_jadi_petugas': True,
    },

    # 12. Verifikasi STBM
    'Verifikasi Pemberdayaan kader masyarakat melalui pemicuan untuk implementasi pilar 2-5 STBM': {
        'freq': 14,
        'petugas': POOL_PETUGAS_STBM,
        'penyerta': POOL_PENYERTA_BOK,
        'count_penyerta': 1,
        'allow_double_dalam': True,
        'allow_double_luar': True,
        'lokasi_pool': LOKASI_STBM,
        'allow_penyerta_jadi_petugas': True,
    },

    # 13. Pemantauan TBC
    'Pemantauan minum obat dan terapi pencegahan TBC': {
        'freq': 4,
        'petugas': ['Mutia Wulansari.,S.Kep.,Ners'],
        'penyerta': POOL_PENYERTA_BOK,
        'count_penyerta': 1,
        'allow_double_dalam': False,
        'allow_double_luar': False,
        'allow_penyerta_jadi_petugas': True,
    },

    # 14. Penemuan Kasus TB
    'Penemuan Kasus Aktif TB': {
        'freq': 4,
        'petugas': ['Mutia Wulansari.,S.Kep.,Ners'],
        'penyerta': POOL_PENYERTA_BOK,
        'count_penyerta': 1,
        'allow_double_dalam': False,
        'allow_double_luar': False,
        'allow_penyerta_jadi_petugas': True,
    },

    # 15. Pelacakan Kasus Mangkir
    'Pelacakan Kasus Mangkir': {
        'freq': 4,
        'petugas': ['Mutia Wulansari.,S.Kep.,Ners'],
        'penyerta': POOL_PENYERTA_BOK,
        'count_penyerta': 1,
        'allow_double_dalam': False,
        'allow_double_luar': False,
        'allow_penyerta_jadi_petugas': True,
    },

    # 16. Investigasi TB
    'Investigasi Kasus TB': {
        'freq': 4,
        'petugas': ['Mutia Wulansari.,S.Kep.,Ners'],
        'penyerta': POOL_PENYERTA_BOK,
        'count_penyerta': 1,
        'allow_double_dalam': False,
        'allow_double_luar': False,
        'allow_penyerta_jadi_petugas': True,
    },

    # 17. Pneumonia
    'Penemuan kasus dan deteksi dini pneumonia': {
        'freq': 4,
        'petugas': ['Pia Nur Podiana,A.Md.Keb'],
        'penyerta': POOL_PENYERTA_BOK,
        'count_penyerta': 1,
        'allow_double_dalam': False,
        'allow_double_luar': False,
        'allow_penyerta_jadi_petugas': True,
    },

    # 18. AFP - tanpa penyerta
    'Kunjungan ulang 60 hari AFP': {
        'freq': 1,
        'petugas': ['Iman Nurul Haq,A.Md.Kep'],
        'penyerta': [],
        'count_penyerta': 0,
        'allow_double_dalam': False,
        'allow_double_luar': False,
        'allow_penyerta_jadi_petugas': False,
    },

    # 19. Penyakit tropis
    'Penemuan dan tindak lanjut penyakit tropis terabaikan': {
        'freq': 4,
        'petugas': ['Mutia Wulansari.,S.Kep.,Ners'],
        'penyerta': POOL_PENYERTA_BOK,
        'count_penyerta': 1,
        'allow_double_dalam': False,
        'allow_double_luar': False,
        'allow_penyerta_jadi_petugas': True,
    },

    # 20. Hepatitis B
    'Pemantauan bayi usia 9-12 bulan yang lahir dari ibu Hepatitis B': {
        'freq': 1,
        'petugas': ['Oriany Kemala Dewi,Amd.Kep'],
        'penyerta': POOL_PENYERTA_BOK,
        'count_penyerta': 1,
        'allow_double_dalam': False,
        'allow_double_luar': False,
        'allow_penyerta_jadi_petugas': True,
    },

    # 21. HIV/Sifilis
    'Pemantauan status bayi dari ibu positif HIV/sifilis': {
        'freq': 2,
        'petugas': POOL_PENYERTA_BOK,
        'penyerta': POOL_PENYERTA_BOK,
        'count_penyerta': 1,
        'allow_double_dalam': False,
        'allow_double_luar': False,
        'allow_penyerta_jadi_petugas': True,
    },

    # 22. Jentik Nyamuk
    'Pemeriksaan Jentik Nyamuk (survei Vektor DBD)': {
        'freq': 4,
        'petugas': ['Nurul Hasanah,A.Md.KL'],
        'penyerta': POOL_PENYERTA_BOK,
        'count_penyerta': 1,
        'allow_double_dalam': True,
        'allow_double_luar': False,
        'allow_penyerta_jadi_petugas': True,
    },

    # 23. PSN
    'PSN oleh kader G1R1J': {
        'freq': 4,
        'petugas': ['Nurul Hasanah,A.Md.KL'],
        'penyerta': POOL_PENYERTA_BOK,
        'count_penyerta': 1,
        'allow_double_dalam': True,
        'allow_double_luar': False,
        'allow_penyerta_jadi_petugas': True,
    },

    # 24. Larvasidasi
    'Larvasidasi DBD': {
        'freq': 4,
        'petugas': ['Nurul Hasanah,A.Md.KL'],
        'penyerta': POOL_PENYERTA_BOK,
        'count_penyerta': 1,
        'allow_double_dalam': True,
        'allow_double_luar': False,
        'allow_penyerta_jadi_petugas': True,
    },

    # 25. Fogging
    'Pengasapan Atau Fogging Nyamuk': {
        'freq': 2,
        'petugas': ['Nurul Hasanah,A.Md.KL'],
        'penyerta': POOL_PENYERTA_BOK,
        'count_penyerta': 2,
        'allow_double_dalam': True,
        'allow_double_luar': False,
        'allow_penyerta_jadi_petugas': True,
    },

    # 26. KAMRT
    'Surveilans Kualitas Air Minum Rumah Tangga (KAMRT)': {
        'freq': 30,
        'petugas': ['Eko Wahyu Saputro,S.K.M', 'Nurul Hasanah,A.Md.KL'],
        'penyerta': POOL_PENYERTA_BOK,
        'count_penyerta': 1,
        'allow_double_dalam': True,
        'allow_double_luar': True,
        'allow_penyerta_jadi_petugas': True,
    },

    # 27. Epidemiologi
    'Penyelidikan Kasus Epidemiologi Penyakit Kasus Penyakit menular': {
        'freq': 4,
        'petugas': ['Iman Nurul Haq,A.Md.Kep'],
        'penyerta': POOL_PENYERTA_BOK,
        'count_penyerta': 1,
        'allow_double_dalam': True,
        'allow_double_luar': False,
        'allow_penyerta_jadi_petugas': True,
    },

    # 28. Verifikasi KLB
    'Verifikasi Sinyal penyakit potensial wabah/KLB': {
        'freq': 2,
        'petugas': ['Iman Nurul Haq,A.Md.Kep', 'Nurul Hasanah,A.Md.KL'],
        'penyerta': POOL_PENYERTA_BOK,
        'count_penyerta': 1,
        'allow_double_dalam': True,
        'allow_double_luar': False,
        'allow_penyerta_jadi_petugas': True,
    },

    # 29. Arbovirosis
    'Penyelidikan Epidimiologi Penyakit Arbovirosis': {
        'freq': 4,
        'petugas': ['Iman Nurul Haq,A.Md.Kep'],
        'penyerta': POOL_PENYERTA_BOK,
        'count_penyerta': 1,
        'allow_double_dalam': True,
        'allow_double_luar': False,
        'allow_penyerta_jadi_petugas': True,
    },

    # 30. Zoonosis
    'Penyelidikan Epidimiologi Penyakit Zoonosis': {
        'freq': 2,
        'petugas': ['Iman Nurul Haq,A.Md.Kep'],
        'penyerta': POOL_PENYERTA_BOK,
        'count_penyerta': 1,
        'allow_double_dalam': True,
        'allow_double_luar': False,
        'allow_penyerta_jadi_petugas': True,
    },

    # 31. ILP
    'Pendampingan pelaksanaan ILP di pustu dan Unit Pelayanan Kesehatan Desa/Kelurahan (UPKD/K)': {
        'freq': 1,
        'petugas': ['Rudi Sutikno,SKM'],
        'penyerta': POOL_PENYERTA_BOK,
        'count_penyerta': 1,
        'allow_double_dalam': False,
        'allow_double_luar': False,
        'allow_penyerta_jadi_petugas': True,
    },

    # ─── SEKOLAH ──────────────────────────────────────────────────────────────
    'Skrining Kesehatan di Sekolah': {
        'freq': 4,
        'petugas': WAJIB_SEKOLAH,
        'penyerta': POOL_BIDAN,
        'count_penyerta': 1,
        'allow_double_dalam': False,
        'allow_double_luar': False,
        'is_sekolah': True,
        'wajib': WAJIB_SEKOLAH,
        'allow_penyerta_jadi_petugas': True,
    },

    'Pembinaan Kesehatan di Sekolah': {
        'freq': 4,
        'petugas': ['Rudi Sutikno,SKM'],
        'penyerta': POOL_PENYERTA_BOK,
        'count_penyerta': 1,
        'allow_double_dalam': False,
        'allow_double_luar': False,
        'is_sekolah': True,
        'paket_dengan': 'Skrining Kesehatan di Sekolah',
        'allow_penyerta_jadi_petugas': True,
    },
}

# ─── KEGIATAN POSYANDU ──────────────────────────────────────────────────────
KEGIATAN_POSYANDU_LIST = [
    ('Pelaksanaan Imunisasi Bayi dan baduta di posyandu', 8),
    ('Pelayanan Imunisasi Kejar', 8),
    ('Pelaksanaan Kelas Ibu Hamil', 4),
    ('Pelaksanaan Kelas Ibu Balita', 4),
    ('Pelaksanaan skrining dan intervensi hasil skrining masalah Kesehatan jiwa di UKBM/Lembaga', 20),
    ('Kunjungan Lapangan Bumil Masalah Gizi', 4),
    ('Kunjungan Lapangan Bayi Balita Masalah Gizi', 4),
]

# ─── KEGIATAN POS REMAJA ────────────────────────────────────────────────────
KEGIATAN_POS_REMAJA_LIST = [('Pembinaan Kesehatan di Komunitas', 2)]