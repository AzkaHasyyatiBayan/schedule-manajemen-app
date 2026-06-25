import random
import calendar
from datetime import datetime, timedelta
from .models import Kegiatan, HariLibur
from .constants import *

def fn_local(nama_list):
    """Filter nama yang diecualikan"""
    return [n for n in nama_list if n not in NAMA_DIECUALIKAN]

def is_orang_libur(nama, tanggal_obj):
    """Cek apakah orang tersebut libur/cuti pada tanggal tertentu"""
    # Cek cuti khusus
    if nama in CUTI_KHUSUS:
        hari = tanggal_obj.weekday()
        if hari in CUTI_KHUSUS[nama]:
            return True
    
    # Cek rules dokter
    if nama in RULES_DOKTER:
        hari = tanggal_obj.weekday()
        if hari not in RULES_DOKTER[nama]:
            return True
    
    return False

def cek_piket_malam_sebelumnya(tanggal_obj):
    """Cek apakah ada yang piket malam H-1"""
    tgl_sebelum = tanggal_obj - timedelta(days=1)
    tgl_str = tgl_sebelum.strftime('%Y-%m-%d')
    
    piket_malam = Kegiatan.objects.filter(
        tanggal=tgl_str,
        kegiatan__icontains='PIKET PERSALINAN MALAM'
    ).first()
    
    if piket_malam:
        # Parse penyerta
        nama_list = [n.strip() for n in piket_malam.penyerta.split(';')]
        return nama_list
    return []

def cek_hari_libur(tanggal_obj):
    """Cek apakah tanggal tersebut hari libur"""
    return HariLibur.objects.filter(tanggal=tanggal_obj).exists()

def rpf(pool, count, used_today, used_week, tanggal_obj):
    """Random pick from pool dengan pertimbangan"""
    # Filter yang sudah dipakai hari ini
    available = [n for n in pool if n not in used_today]
    
    # Filter yang libur/cuti
    available = [n for n in available if not is_orang_libur(n, tanggal_obj)]
    
    # Filter yang sudah dipakai minggu ini (prioritas yang belum pernah)
    belum_minggu = [n for n in available if n not in used_week]
    
    if belum_minggu and len(belum_minggu) >= count:
        available = belum_minggu
    
    if not available or len(available) < count:
        return []
    
    # Random pick
    picked = random.sample(available, min(count, len(available)))
    return picked

def generate_jadwal_dalam_gedung(bulan, tahun, minggu_ke, loka_karya=False):
    """
    Generate jadwal dalam gedung untuk minggu tertentu
    Returns: list of dict {tanggal, lokasi, kegiatan, penyerta, kategori}
    """
    jadwal_baru = []
    skipped = []
    
    # Hitung hari kerja di minggu tersebut
    cal_month = calendar.monthcalendar(tahun, bulan)
    if minggu_ke > len(cal_month):
        return [], [f"Bulan ini hanya {len(cal_month)} minggu"]
    
    week = cal_month[minggu_ke - 1]
    work_days = [d for idx, d in enumerate(week) if d != 0 and idx < 6]  # Senin-Sabtu
    
    if not work_days:
        return [], ["Tidak ada hari kerja di minggu ini"]
    
    hari_names = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
    used_week = set()
    use_count = {n: 0 for n in POOL_ILP + POOL_DOKTER}
    
    for tgl in work_days:
        tgl_str = f"{tahun}-{bulan:02d}-{tgl:02d}"
        tgl_obj = datetime(tahun, bulan, tgl)
        hari_idx = tgl_obj.weekday()
        hari_name = hari_names[hari_idx]
        
        # Skip hari libur
        if cek_hari_libur(tgl_obj):
            skipped.append(f"{tgl_str} (Hari Libur)")
            continue
        
        # Cek yang libur karena piket malam H-1
        libur_malam = cek_piket_malam_sebelumnya(tgl_obj)
        
        used_today = set(libur_malam)
        
        # a. PENDAFTARAN (tetap)
        jadwal_baru.append({
            'tanggal': tgl_str,
            'lokasi': 'Dalam Gedung',
            'kegiatan': 'PENDAFTARAN',
            'penyerta': '; '.join(PENDAFTARAN_TETAP),
            'kategori': 'dalam_gedung'
        })
        used_today.update(PENDAFTARAN_TETAP)
        
        # b. SKRINING ILP 1
        p = rpf(POOL_ILP, 1, used_today, used_week, tgl_obj)
        if p:
            used_today.add(p[0])
            used_week.add(p[0])
            use_count[p[0]] = use_count.get(p[0], 0) + 1
            jadwal_baru.append({
                'tanggal': tgl_str,
                'lokasi': 'Dalam Gedung',
                'kegiatan': 'SKRINING ILP 1',
                'penyerta': p[0],
                'kategori': 'dalam_gedung'
            })
        
        # c. SKRINING ILP 2
        p = rpf(POOL_ILP, 1, used_today, used_week, tgl_obj)
        if p:
            used_today.add(p[0])
            used_week.add(p[0])
            use_count[p[0]] = use_count.get(p[0], 0) + 1
            jadwal_baru.append({
                'tanggal': tgl_str,
                'lokasi': 'Dalam Gedung',
                'kegiatan': 'SKRINING ILP 2',
                'penyerta': p[0],
                'kategori': 'dalam_gedung'
            })
        
        # d. POLI PROLANIS (3 orang)
        p = rpf(POOL_ILP, 3, used_today, used_week, tgl_obj)
        if len(p) >= 3:
            used_today.update(p)
            used_week.update(p)
            for n in p:
                use_count[n] = use_count.get(n, 0) + 1
            jadwal_baru.append({
                'tanggal': tgl_str,
                'lokasi': 'Dalam Gedung',
                'kegiatan': 'POLI PROLANIS',
                'penyerta': '; '.join(p),
                'kategori': 'dalam_gedung'
            })
        
        # e. KLASTER DEWASA-LANSIA 1
        dok = rpf(POOL_DOKTER, 1, used_today, used_week, tgl_obj)
        if dok:
            used_today.add(dok[0])
            used_week.add(dok[0])
            use_count[dok[0]] = use_count.get(dok[0], 0) + 1
            jadwal_baru.append({
                'tanggal': tgl_str,
                'lokasi': 'Dalam Gedung',
                'kegiatan': 'KLASTER DEWASA-LANSIA 1',
                'penyerta': dok[0],
                'kategori': 'dalam_gedung'
            })
        
        # f. KLASTER DEWASA-LANSIA 2
        dok = rpf(POOL_DOKTER, 1, used_today, used_week, tgl_obj)
        if dok:
            used_today.add(dok[0])
            used_week.add(dok[0])
            use_count[dok[0]] = use_count.get(dok[0], 0) + 1
            jadwal_baru.append({
                'tanggal': tgl_str,
                'lokasi': 'Dalam Gedung',
                'kegiatan': 'KLASTER DEWASA-LANSIA 2',
                'penyerta': dok[0],
                'kategori': 'dalam_gedung'
            })
        
        # g. KLASTER IBU KIA & USG (1 dokter + 2 bidan)
        dok = rpf(POOL_DOKTER_KIA, 1, used_today, used_week, tgl_obj)
        bidan = rpf(POOL_BIDAN, 2, used_today, used_week, tgl_obj)
        if dok and len(bidan) >= 2:
            used_today.add(dok[0])
            used_week.add(dok[0])
            use_count[dok[0]] = use_count.get(dok[0], 0) + 1
            used_today.update(bidan)
            used_week.update(bidan)
            for n in bidan:
                use_count[n] = use_count.get(n, 0) + 1
            jadwal_baru.append({
                'tanggal': tgl_str,
                'lokasi': 'Dalam Gedung',
                'kegiatan': 'KLASTER IBU KIA & USG',
                'penyerta': f"{dok[0]}; {'; '.join(bidan)}",
                'kategori': 'dalam_gedung'
            })
        
        # h. KLASTER ANAK (1 dokter + 2 bidan)
        dok = rpf(POOL_DOKTER_KIA, 1, used_today, used_week, tgl_obj)
        bidan = rpf(POOL_BIDAN, 2, used_today, used_week, tgl_obj)
        if dok and len(bidan) >= 2:
            used_today.add(dok[0])
            used_week.add(dok[0])
            use_count[dok[0]] = use_count.get(dok[0], 0) + 1
            used_today.update(bidan)
            used_week.update(bidan)
            for n in bidan:
                use_count[n] = use_count.get(n, 0) + 1
            jadwal_baru.append({
                'tanggal': tgl_str,
                'lokasi': 'Dalam Gedung',
                'kegiatan': 'KLASTER ANAK',
                'penyerta': f"{dok[0]}; {'; '.join(bidan)}",
                'kategori': 'dalam_gedung'
            })
        
        # i. R. IMUNISASI (hanya Kamis, 2 bidan)
        if hari_name == "Kamis":
            bidan = rpf(POOL_BIDAN, 2, used_today, used_week, tgl_obj)
            if len(bidan) >= 2:
                used_today.update(bidan)
                used_week.update(bidan)
                for n in bidan:
                    use_count[n] = use_count.get(n, 0) + 1
                jadwal_baru.append({
                    'tanggal': tgl_str,
                    'lokasi': 'Dalam Gedung',
                    'kegiatan': 'R. IMUNISASI',
                    'penyerta': '; '.join(bidan),
                    'kategori': 'dalam_gedung'
                })
        
        # j. R. TINDAKAN
        p = rpf(POOL_TINDAKAN, 1, used_today, used_week, tgl_obj)
        if p:
            used_today.add(p[0])
            used_week.add(p[0])
            use_count[p[0]] = use_count.get(p[0], 0) + 1
            jadwal_baru.append({
                'tanggal': tgl_str,
                'lokasi': 'Dalam Gedung',
                'kegiatan': 'R. TINDAKAN',
                'penyerta': p[0],
                'kategori': 'dalam_gedung'
            })
        
        # k. BP GIGI (tetap)
        jadwal_baru.append({
            'tanggal': tgl_str,
            'lokasi': 'Dalam Gedung',
            'kegiatan': 'BP GIGI',
            'penyerta': '; '.join(BP_GIGI_TETAP),
            'kategori': 'dalam_gedung'
        })
        used_today.update(BP_GIGI_TETAP)
        
        # l. APOTEK (tetap)
        jadwal_baru.append({
            'tanggal': tgl_str,
            'lokasi': 'Dalam Gedung',
            'kegiatan': 'APOTEK',
            'penyerta': '; '.join(APOTEK_TETAP),
            'kategori': 'dalam_gedung'
        })
        used_today.update(APOTEK_TETAP)
        
        # m. LAB (tetap)
        jadwal_baru.append({
            'tanggal': tgl_str,
            'lokasi': 'Dalam Gedung',
            'kegiatan': 'LAB',
            'penyerta': '; '.join(LAB_TETAP),
            'kategori': 'dalam_gedung'
        })
        used_today.update(LAB_TETAP)
        
        # n. R. TB (hanya Selasa)
        if hari_name == "Selasa":
            jadwal_baru.append({
                'tanggal': tgl_str,
                'lokasi': 'Dalam Gedung',
                'kegiatan': 'R. TB',
                'penyerta': 'Mutia Wulansari.,S.Kep.,Ners',
                'kategori': 'dalam_gedung'
            })
            used_today.add('Mutia Wulansari.,S.Kep.,Ners')
            used_week.add('Mutia Wulansari.,S.Kep.,Ners')
        
        # o. ADMINISTRASI (2 tetap + 1 extra)
        extra = rpf(ADMINISTRASI_EXTRA, 1, used_today, used_week, tgl_obj)
        adm_total = ADMINISTRASI_TETAP + extra
        jadwal_baru.append({
            'tanggal': tgl_str,
            'lokasi': 'Dalam Gedung',
            'kegiatan': 'ADMINISTRASI',
            'penyerta': '; '.join(adm_total),
            'kategori': 'dalam_gedung'
        })
        used_today.update(adm_total)
        used_week.update(adm_total)
        for n in adm_total:
            use_count[n] = use_count.get(n, 0) + 1
        
        # p. PUSTU CIANGIR (tetap)
        jadwal_baru.append({
            'tanggal': tgl_str,
            'lokasi': 'Pustu Ciangir',
            'kegiatan': 'PELAYANAN PUSTU',
            'penyerta': PUSTU_CIANGIR,
            'kategori': 'dalam_gedung'
        })
        used_today.add(PUSTU_CIANGIR)
        used_week.add(PUSTU_CIANGIR)
        
        # q. PUSTU SUMELAP (tetap)
        jadwal_baru.append({
            'tanggal': tgl_str,
            'lokasi': 'Pustu Sumelap',
            'kegiatan': 'PELAYANAN PUSTU',
            'penyerta': PUSTU_SUMELAP,
            'kategori': 'dalam_gedung'
        })
        used_today.add(PUSTU_SUMELAP)
        used_week.add(PUSTU_SUMELAP)
        
        # Loka Karya Mini (jika dipilih)
        if loka_karya and hari_name == "Senin":  # Contoh: hanya Senin
            jadwal_baru.append({
                'tanggal': tgl_str,
                'lokasi': 'Dalam Gedung',
                'kegiatan': 'LOKA KARYA MINI BULANAN',
                'penyerta': '; '.join(LOKA_KARYA_MINI),
                'kategori': 'dalam_gedung'
            })
            used_today.update(LOKA_KARYA_MINI)
            used_week.update(LOKA_KARYA_MINI)
    
    return jadwal_baru, skipped