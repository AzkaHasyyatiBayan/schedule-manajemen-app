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
    if nama in CUTI_KHUSUS:
        hari = tanggal_obj.weekday()
        if hari in CUTI_KHUSUS[nama]:
            return True
    return False


def is_dokter_available_for_kegiatan(nama, kegiatan, tanggal_obj):
    """Cek apakah dokter boleh masuk kegiatan tertentu di hari ini"""
    hari = tanggal_obj.weekday()
    if nama in RULES_DOKTER_KEGIATAN:
        rules = RULES_DOKTER_KEGIATAN[nama]
        if kegiatan in rules:
            return hari in rules[kegiatan]
        # Jika kegiatan TIDAK ada di rules, berarti tidak ada aturan khusus → boleh
        return True
    return True


def cek_piket_malam_sebelumnya(tanggal_obj):
    """Cek apakah ada yang piket malam H-1"""
    tgl_sebelum = tanggal_obj - timedelta(days=1)
    tgl_str = tgl_sebelum.strftime('%Y-%m-%d')
    
    piket_malam = Kegiatan.objects.filter(
        tanggal=tgl_str,
        kegiatan__icontains='PIKET PERSALINAN MALAM'
    ).first()
    
    if piket_malam:
        return [n.strip() for n in piket_malam.penyerta.split(';') if n.strip()]
    return []


def cek_hari_libur(tanggal_obj):
    """Cek apakah tanggal tersebut hari libur"""
    return HariLibur.objects.filter(tanggal=tanggal_obj).exists()


def rpf(pool, count, used_today, used_month, tanggal_obj, kegiatan=None):
    """Random pick from pool dengan pertimbangan"""
    available = [n for n in pool if n not in used_today]
    available = [n for n in available if not is_orang_libur(n, tanggal_obj)]
    
    # Cek aturan dokter untuk kegiatan tertentu
    if kegiatan:
        available = [n for n in available if is_dokter_available_for_kegiatan(n, kegiatan, tanggal_obj)]
    
    # Prioritas yang belum dipakai bulan ini
    belum_bulan = [n for n in available if n not in used_month]
    
    if belum_bulan and len(belum_bulan) >= count:
        available = belum_bulan
    
    if not available or len(available) < count:
        return []
    
    picked = random.sample(available, min(count, len(available)))
    return picked


def get_work_days_in_month(bulan, tahun):
    """Dapatkan semua hari kerja (Senin-Sabtu) dalam bulan, exclude libur & minggu"""
    work_days = []
    num_days = calendar.monthrange(tahun, bulan)[1]
    
    for day in range(1, num_days + 1):
        tgl_obj = datetime(tahun, bulan, day)
        # Skip Minggu (6)
        if tgl_obj.weekday() == 6:
            continue
        if cek_hari_libur(tgl_obj):
            continue
        work_days.append(tgl_obj)
    
    return work_days


def generate_jadwal_dalam_gedung(bulan, tahun, loka_karya=False):
    """
    Generate jadwal dalam gedung untuk 1 bulan penuh
    Returns: (jadwal_list, skipped_list)
    """
    jadwal_baru = []
    skipped = []
    
    work_days = get_work_days_in_month(bulan, tahun)
    if not work_days:
        return [], ["Tidak ada hari kerja di bulan ini"]
    
    used_month = {n: 0 for n in POOL_ILP + POOL_DOKTER + POOL_BIDAN}
    
    for tgl_obj in work_days:
        tgl_str = tgl_obj.strftime('%Y-%m-%d')
        hari_name = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'][tgl_obj.weekday()]
        
        libur_malam = cek_piket_malam_sebelumnya(tgl_obj)
        used_today = set(libur_malam)
        
        # a. PENDAFTARAN (tetap)
        jadwal_baru.append({
            'tanggal': tgl_str,
            'lokasi': 'Dalam Gedung',
            'kegiatan': 'PENDAFTARAN',
            'penyerta': '; '.join(PENDAFTARAN_TETAP),
            'kategori': 'dalam_gedung',
            'is_auto_generated': True,
        })
        used_today.update(PENDAFTARAN_TETAP)
        
        # b. SKRINING ILP 1
        p = rpf(POOL_ILP, 1, used_today, used_month, tgl_obj)
        if p:
            used_today.add(p[0])
            used_month[p[0]] = used_month.get(p[0], 0) + 1
            jadwal_baru.append({
                'tanggal': tgl_str,
                'lokasi': 'Dalam Gedung',
                'kegiatan': 'SKRINING ILP 1',
                'penyerta': p[0],
                'kategori': 'dalam_gedung',
                'is_auto_generated': True,
            })
        
        # c. SKRINING ILP 2
        p = rpf(POOL_ILP, 1, used_today, used_month, tgl_obj)
        if p:
            used_today.add(p[0])
            used_month[p[0]] = used_month.get(p[0], 0) + 1
            jadwal_baru.append({
                'tanggal': tgl_str,
                'lokasi': 'Dalam Gedung',
                'kegiatan': 'SKRINING ILP 2',
                'penyerta': p[0],
                'kategori': 'dalam_gedung',
                'is_auto_generated': True,
            })
        
        # d. POLI PROLANIS (3 orang)
        p = rpf(POOL_ILP, 3, used_today, used_month, tgl_obj)
        if len(p) >= 3:
            used_today.update(p)
            for n in p:
                used_month[n] = used_month.get(n, 0) + 1
            jadwal_baru.append({
                'tanggal': tgl_str,
                'lokasi': 'Dalam Gedung',
                'kegiatan': 'POLI PROLANIS',
                'penyerta': '; '.join(p),
                'kategori': 'dalam_gedung',
                'is_auto_generated': True,
            })
        
        # e. KLASTER DEWASA-LANSIA 1
        dok = rpf(POOL_DOKTER, 1, used_today, used_month, tgl_obj, kegiatan='KLASTER DEWASA-LANSIA 1')
        if dok:
            used_today.add(dok[0])
            used_month[dok[0]] = used_month.get(dok[0], 0) + 1
            jadwal_baru.append({
                'tanggal': tgl_str,
                'lokasi': 'Dalam Gedung',
                'kegiatan': 'KLASTER DEWASA-LANSIA 1',
                'penyerta': dok[0],
                'kategori': 'dalam_gedung',
                'is_auto_generated': True,
            })
        
        # f. KLASTER DEWASA-LANSIA 2
        dok = rpf(POOL_DOKTER, 1, used_today, used_month, tgl_obj, kegiatan='KLASTER DEWASA-LANSIA 2')
        if dok:
            used_today.add(dok[0])
            used_month[dok[0]] = used_month.get(dok[0], 0) + 1
            jadwal_baru.append({
                'tanggal': tgl_str,
                'lokasi': 'Dalam Gedung',
                'kegiatan': 'KLASTER DEWASA-LANSIA 2',
                'penyerta': dok[0],
                'kategori': 'dalam_gedung',
                'is_auto_generated': True,
            })
        
        # g. KLASTER IBU KIA & USG (1 dokter + 2 bidan)
        dok = rpf(POOL_DOKTER_KIA, 1, used_today, used_month, tgl_obj, kegiatan='KLASTER IBU KIA & USG')
        bidan = rpf(POOL_BIDAN, 2, used_today, used_month, tgl_obj)
        if dok and len(bidan) >= 2:
            used_today.add(dok[0])
            used_month[dok[0]] = used_month.get(dok[0], 0) + 1
            used_today.update(bidan)
            for n in bidan:
                used_month[n] = used_month.get(n, 0) + 1
            jadwal_baru.append({
                'tanggal': tgl_str,
                'lokasi': 'Dalam Gedung',
                'kegiatan': 'KLASTER IBU KIA & USG',
                'penyerta': f"{dok[0]}; {'; '.join(bidan)}",
                'kategori': 'dalam_gedung',
                'is_auto_generated': True,
            })
        
        # h. KLASTER ANAK (1 dokter + 2 bidan)
        # Semua dokter KIA boleh masuk, tapi tetap cek CUTI_KHUSUS
        dok = rpf(POOL_DOKTER_KIA, 1, used_today, used_month, tgl_obj, kegiatan='KLASTER ANAK')
        bidan = rpf(POOL_BIDAN, 2, used_today, used_month, tgl_obj)
        if dok and len(bidan) >= 2:
            used_today.add(dok[0])
            used_month[dok[0]] = used_month.get(dok[0], 0) + 1
            used_today.update(bidan)
            for n in bidan:
                used_month[n] = used_month.get(n, 0) + 1
            jadwal_baru.append({
                'tanggal': tgl_str,
                'lokasi': 'Dalam Gedung',
                'kegiatan': 'KLASTER ANAK',
                'penyerta': f"{dok[0]}; {'; '.join(bidan)}",
                'kategori': 'dalam_gedung',
                'is_auto_generated': True,
            })
        
        # i. R. IMUNISASI (hanya Kamis, 2 bidan)
        if hari_name == "Kamis":
            bidan = rpf(POOL_BIDAN, 2, used_today, used_month, tgl_obj)
            if len(bidan) >= 2:
                used_today.update(bidan)
                for n in bidan:
                    used_month[n] = used_month.get(n, 0) + 1
                jadwal_baru.append({
                    'tanggal': tgl_str,
                    'lokasi': 'Dalam Gedung',
                    'kegiatan': 'R. IMUNISASI',
                    'penyerta': '; '.join(bidan),
                    'kategori': 'dalam_gedung',
                    'is_auto_generated': True,
                })
        
        # j. R. TINDAKAN
        p = rpf(POOL_TINDAKAN, 1, used_today, used_month, tgl_obj)
        if p:
            used_today.add(p[0])
            used_month[p[0]] = used_month.get(p[0], 0) + 1
            jadwal_baru.append({
                'tanggal': tgl_str,
                'lokasi': 'Dalam Gedung',
                'kegiatan': 'R. TINDAKAN',
                'penyerta': p[0],
                'kategori': 'dalam_gedung',
                'is_auto_generated': True,
            })
        
        # k. BP GIGI (tetap)
        jadwal_baru.append({
            'tanggal': tgl_str,
            'lokasi': 'Dalam Gedung',
            'kegiatan': 'BP GIGI',
            'penyerta': '; '.join(BP_GIGI_TETAP),
            'kategori': 'dalam_gedung',
            'is_auto_generated': True,
        })
        used_today.update(BP_GIGI_TETAP)
        
        # l. APOTEK (tetap)
        jadwal_baru.append({
            'tanggal': tgl_str,
            'lokasi': 'Dalam Gedung',
            'kegiatan': 'APOTEK',
            'penyerta': '; '.join(APOTEK_TETAP),
            'kategori': 'dalam_gedung',
            'is_auto_generated': True,
        })
        used_today.update(APOTEK_TETAP)
        
        # m. LAB (tetap)
        jadwal_baru.append({
            'tanggal': tgl_str,
            'lokasi': 'Dalam Gedung',
            'kegiatan': 'LAB',
            'penyerta': '; '.join(LAB_TETAP),
            'kategori': 'dalam_gedung',
            'is_auto_generated': True,
        })
        used_today.update(LAB_TETAP)
        
        # n. R. TB (hanya Selasa)
        if hari_name == "Selasa":
            jadwal_baru.append({
                'tanggal': tgl_str,
                'lokasi': 'Dalam Gedung',
                'kegiatan': 'R. TB',
                'penyerta': 'Mutia Wulansari.,S.Kep.,Ners',
                'kategori': 'dalam_gedung',
                'is_auto_generated': True,
            })
            used_today.add('Mutia Wulansari.,S.Kep.,Ners')
            used_month['Mutia Wulansari.,S.Kep.,Ners'] = used_month.get('Mutia Wulansari.,S.Kep.,Ners', 0) + 1
        
        # o. ADMINISTRASI (2 tetap + 1 extra)
        extra = rpf(ADMINISTRASI_EXTRA, 1, used_today, used_month, tgl_obj)
        adm_total = ADMINISTRASI_TETAP + extra
        jadwal_baru.append({
            'tanggal': tgl_str,
            'lokasi': 'Dalam Gedung',
            'kegiatan': 'ADMINISTRASI',
            'penyerta': '; '.join(adm_total),
            'kategori': 'dalam_gedung',
            'is_auto_generated': True,
        })
        used_today.update(adm_total)
        for n in adm_total:
            used_month[n] = used_month.get(n, 0) + 1
        
        # p. PUSTU CIANGIR (tetap)
        jadwal_baru.append({
            'tanggal': tgl_str,
            'lokasi': 'Pustu Ciangir',
            'kegiatan': 'PELAYANAN PUSTU',
            'penyerta': PUSTU_CIANGIR,
            'kategori': 'dalam_gedung',
            'is_auto_generated': True,
        })
        used_today.add(PUSTU_CIANGIR)
        used_month[PUSTU_CIANGIR] = used_month.get(PUSTU_CIANGIR, 0) + 1
        
        # q. PUSTU SUMELAP (tetap)
        jadwal_baru.append({
            'tanggal': tgl_str,
            'lokasi': 'Pustu Sumelap',
            'kegiatan': 'PELAYANAN PUSTU',
            'penyerta': PUSTU_SUMELAP,
            'kategori': 'dalam_gedung',
            'is_auto_generated': True,
        })
        used_today.add(PUSTU_SUMELAP)
        used_month[PUSTU_SUMELAP] = used_month.get(PUSTU_SUMELAP, 0) + 1
        
        # Loka Karya Mini (jika dipilih, hanya Senin)
        if loka_karya and hari_name == "Senin":
            jadwal_baru.append({
                'tanggal': tgl_str,
                'lokasi': 'Dalam Gedung',
                'kegiatan': 'LOKA KARYA MINI BULANAN',
                'penyerta': '; '.join(LOKA_KARYA_MINI),
                'kategori': 'dalam_gedung',
                'is_auto_generated': True,
            })
            used_today.update(LOKA_KARYA_MINI)
            for n in LOKA_KARYA_MINI:
                used_month[n] = used_month.get(n, 0) + 1
    
    return jadwal_baru, skipped


def generate_jadwal_luar_gedung(bulan, tahun, jadwal_dalam_gedung=None):
    """
    Generate jadwal luar gedung untuk 1 bulan penuh
    Returns: (jadwal_list, skipped_list)
    """
    jadwal_baru = []
    skipped = []
    
    work_days = get_work_days_in_month(bulan, tahun)
    if not work_days:
        return [], ["Tidak ada hari kerja di bulan ini"]
    
    # Track siapa yang sudah dipakai di luar gedung per hari
    used_luar_per_day = {d.strftime('%Y-%m-%d'): set() for d in work_days}
    
    # Track siapa yang dipakai di dalam gedung per hari
    used_dalam_per_day = {}
    if jadwal_dalam_gedung:
        for j in jadwal_dalam_gedung:
            tgl = j['tanggal']
            if tgl not in used_dalam_per_day:
                used_dalam_per_day[tgl] = set()
            names = [n.strip() for n in j.get('penyerta', '').split(';') if n.strip()]
            used_dalam_per_day[tgl].update(names)
    
    # Track lokasi per bulan untuk distribusi merata
    lokasi_count = {lok: 0 for lok in LOKASI_LUAR_GEDUNG}
    
    work_days_shuffled = work_days.copy()
    random.shuffle(work_days_shuffled)
    
    # Process setiap kegiatan luar gedung
    for kegiatan_name, config in KEGIATAN_LUAR_GEDUNG.items():
        freq = config['freq']
        petugas_pool = config['petugas']
        penyerta_pool = config['penyerta']
        allow_double_dalam = config.get('allow_double_dalam', False)
        allow_double_luar = config.get('allow_double_luar', False)
        lokasi_fixed = config.get('lokasi_fixed', None)
        tanggal_fixed = config.get('tanggal_fixed', None)
        count_penyerta = config.get('count_penyerta', 1)
        
        placed = 0
        attempts = 0
        max_attempts = freq * 20 
        
        while placed < freq and attempts < max_attempts:
            attempts += 1
            
            # Pilih hari random
            if tanggal_fixed:
                try:
                    tgl_obj = datetime(tahun, bulan, tanggal_fixed)
                    if tgl_obj not in work_days:
                        skipped.append(f"{kegiatan_name}: Tanggal {tanggal_fixed} bukan hari kerja")
                        break
                except:
                    break
            else:
                tgl_obj = random.choice(work_days_shuffled)
            
            tgl_str = tgl_obj.strftime('%Y-%m-%d')
            
            # Pilih petugas
            petugas = rpf_simple(petugas_pool, 1, used_luar_per_day[tgl_str], tgl_obj)
            if not petugas:
                continue
            
            # Pilih penyerta
            penyerta = []
            if penyerta_pool and count_penyerta > 0:
                exclude = set(petugas)
                if not allow_double_luar:
                    exclude.update(used_luar_per_day[tgl_str])
                if not allow_double_dalam and tgl_str in used_dalam_per_day:
                    exclude.update(used_dalam_per_day[tgl_str])
                
                available_penyerta = [n for n in penyerta_pool if n not in exclude and not is_orang_libur(n, tgl_obj)]
                if len(available_penyerta) >= count_penyerta:
                    penyerta = random.sample(available_penyerta, count_penyerta)
                else:
                    continue
            
            # Pilih lokasi
            if lokasi_fixed:
                lokasi = lokasi_fixed
            else:
                min_lokasi = min(lokasi_count, key=lokasi_count.get)
                lokasi = min_lokasi
            
            # Build penyerta string
            all_names = petugas + penyerta
            penyerta_str = '; '.join(all_names)
            
            jadwal_baru.append({
                'tanggal': tgl_str,
                'lokasi': lokasi,
                'kegiatan': kegiatan_name,
                'penyerta': penyerta_str,
                'kategori': 'luar_gedung',
                'is_auto_generated': True,
            })
            
            # Update tracking
            used_luar_per_day[tgl_str].update(all_names)
            lokasi_count[lokasi] += 1
            placed += 1
        
        if placed < freq:
            skipped.append(f"{kegiatan_name}: Hanya {placed}/{freq} yang berhasil dijadwalkan")
    
    return jadwal_baru, skipped


def rpf_simple(pool, count, used_today, tanggal_obj):
    """Simple random pick tanpa used_month tracking"""
    available = [n for n in pool if n not in used_today]
    available = [n for n in available if not is_orang_libur(n, tanggal_obj)]
    
    if not available or len(available) < count:
        return []
    
    return random.sample(available, min(count, len(available)))