# Daftar nama per ruangan untuk randomize dalam gedung

# ─── NAMA YANG DIKECUALIKAN ─────────────────────────────────────────────────
NAMA_DIECUALIKAN = ["Isep Deni Herdian, S.Kep.,MMRS", "Isep Suhendar,SKM"]

# ─── CUTI KHUSUS ────────────────────────────────────────────────────────────
# Format: {nama: [hari_cuti]} (0=Senin, 1=Selasa, ..., 6=Minggu)
CUTI_KHUSUS = {
    "dr.Muhammad Azhary Romdhon": [1, 3],  # Selasa & Kamis
    "dr.Iwan Setiawan": [5],  # Sabtu
}

# ─── RULES DOKTER SPESIFIK ──────────────────────────────────────────────────
# Format: {nama: [hari_bisa_masuk]}
RULES_DOKTER = {
    "dr. Volti Diana Suryawadi": [0, 5],  # Senin & Sabtu
    "dr. Siti Hana Fukui": [1, 3],  # Selasa & Kamis
    "dr.Muhammad Azhary Romdhon": [0, 2],  # Senin & Rabu (untuk KIA)
    "dr.Ferry Nalapraya": [1, 3],  # Selasa & Kamis (untuk KIA)
}

# ─── KELOMPOK TETAP (WAJIB) ─────────────────────────────────────────────────
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
    "Yogi Aris Diyanto, S.E",
    "Rangga Ismardana Gasbela,S.T"
]

ADMINISTRASI_EXTRA = [
    "Liska Permatasari, S.Kep.,Ners",
    "Andina Dea Priatna, SKM",
    "Alitsa Nuur Fithri, S.ST"
]

PUSTU_CIANGIR = "Haeriah, A.Md.Kep"
PUSTU_SUMELAP = "Ujang Effendi, S.Kep.,Ners"

# ─── POOL RANDOMIZE ─────────────────────────────────────────────────────────
POOL_ILP = [
    "Mutia Wulansari.,S.Kep.,Ners",
    "Liska Permatasari, S.Kep.,Ners",
    "Dede Khaerul Kamal Muchtar, AMK",
    "Iman Nurul Haq, A.Md.Kep",
    "Wida Idul Adha, S.Kep.,Ners",
    "Oriany Kemala Dewi, Amd.Kep",
    "Dede Aan Septiantini, A.Md.Kep",
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
    "Rudi Sutikno, SKM",
    "Eko Wahyu Saputro, S.K.M",
    "Nurul Hasanah, A.Md.KL",
    "Ameilia Putri Isyari, S.Gz",
    "Annisa Fauziah, A.Md.Gz"
]

POOL_DOKTER = [
    "dr.Ferry Nalapraya",
    "dr.Muhammad Azhary Romdhon",
    "dr.Iwan Setiawan",
    "dr. Siti Hana Fukui",
    "dr. Volti Diana Suryawadi"
]

POOL_DOKTER_KIA = [
    "dr.Ferry Nalapraya",
    "dr.Muhammad Azhary Romdhon",
    "dr.Iwan Setiawan"
]

POOL_BIDAN = [
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
    "Annisa Nafaulloh,S.Tr.Keb.,Bdn"
]

POOL_TINDAKAN = [
    "Mutia Wulansari.,S.Kep.,Ners",
    "Liska Permatasari, S.Kep.,Ners",
    "Dede Khaerul Kamal Muchtar, AMK",
    "Iman Nurul Haq, A.Md.Kep",
    "Wida Idul Adha, S.Kep.,Ners",
    "Oriany Kemala Dewi, Amd.Kep",
    "Dede Aan Septiantini, A.Md.Kep"
]

LOKA_KARYA_MINI = [
    "Dewi Sri Mulyani, Am.Keb",
    "Pipit Puspitasari, Am.Keb",
    "Mira Jatnikawati, Am.Keb",
    "Reni Mustikasari, Am.Keb",
    "Asri Awulan, S.Tr.Keb",
    "Ujang Effendi, S.Kep.,Ners",
    "Haeriah, A.Md.Kep"
]