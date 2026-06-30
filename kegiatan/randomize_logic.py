import random
import calendar
import logging
from datetime import datetime, timedelta, date
from .models import Kegiatan, HariLibur
from .constants import *

logger = logging.getLogger(__name__)


def fn_local(nama_list):
    return [n for n in nama_list if n not in NAMA_DIECUALIKAN]


def is_orang_libur(nama, tanggal_obj):
    if nama in CUTI_KHUSUS:
        hari = tanggal_obj.weekday()
        if hari in CUTI_KHUSUS[nama]:
            return True
    return False


def is_dokter_available_for_kegiatan(nama, kegiatan, tanggal_obj):
    """Cek apakah dokter BOLEH di kegiatan ini pada hari ini (batasan)"""
    hari = tanggal_obj.weekday()
    if nama in RULES_DOKTER_KEGIATAN:
        rules = RULES_DOKTER_KEGIATAN[nama]
        if kegiatan in rules:
            # Dokter ini HANYA boleh di hari yang tertera
            return hari in rules[kegiatan]
        # Jika kegiatan tidak ada di rules, tidak ada batasan
        return True
    return True


def cek_piket_malam_sebelumnya(tanggal_obj):
    tgl_sebelum = tanggal_obj - timedelta(days=1)
    tgl_str = tgl_sebelum.strftime('%Y-%m-%d')
    piket_malam = Kegiatan.objects.filter(
        tanggal=tgl_str, kegiatan__icontains='PIKET PERSALINAN MALAM'
    ).first()
    if piket_malam:
        return [n.strip() for n in piket_malam.penyerta.split(';') if n.strip()]
    return []


def cek_hari_libur(tanggal_obj):
    """Cek apakah tanggal tersebut hari libur (support date dan datetime)"""
    if hasattr(tanggal_obj, 'date') and callable(tanggal_obj.date):
        check_date = tanggal_obj.date()
    elif isinstance(tanggal_obj, date) and not isinstance(tanggal_obj, datetime):
        check_date = tanggal_obj
    else:
        try:
            check_date = datetime.strptime(str(tanggal_obj), '%Y-%m-%d').date()
        except:
            check_date = tanggal_obj
    
    is_libur = HariLibur.objects.filter(tanggal=check_date).exists()
    if is_libur:
        logger.info(f"🔴 Tanggal {check_date} adalah hari libur")
    return is_libur


def get_hari_libur_bulan(bulan, tahun):
    """Dapatkan semua hari libur di bulan tertentu (untuk debug)"""
    start_date = date(tahun, bulan, 1)
    end_date = date(tahun, bulan, calendar.monthrange(tahun, bulan)[1])
    libur_list = HariLibur.objects.filter(tanggal__range=[start_date, end_date])
    return [str(l.tanggal) for l in libur_list]


def rpf(pool, count, used_today, used_month, tanggal_obj, kegiatan=None, wajib=None):
    """Random pick from pool dengan pertimbangan dokter wajib"""
    # Jika ada dokter wajib untuk hari ini, langsung return
    if wajib and len(wajib) >= count:
        # Cek apakah dokter wajib tersedia (tidak libur, tidak dipakai)
        available_wajib = [n for n in wajib if n not in used_today and not is_orang_libur(n, tanggal_obj)]
        if len(available_wajib) >= count:
            return available_wajib[:count]
    
    available = [n for n in pool if n not in used_today]
    available = [n for n in available if not is_orang_libur(n, tanggal_obj)]
    
    if kegiatan:
        available = [n for n in available if is_dokter_available_for_kegiatan(n, kegiatan, tanggal_obj)]
    
    belum_bulan = [n for n in available if n not in used_month]
    if belum_bulan and len(belum_bulan) >= count:
        available = belum_bulan
    
    if not available or len(available) < count:
        return []
    
    return random.sample(available, min(count, len(available)))


def get_work_days_in_month(bulan, tahun):
    """Dapatkan semua hari kerja (Senin-Sabtu) dalam bulan, exclude libur & minggu"""
    work_days = []
    num_days = calendar.monthrange(tahun, bulan)[1]
    
    hari_libur_list = get_hari_libur_bulan(bulan, tahun)
    logger.info(f"📅 Hari libur di bulan {bulan}/{tahun}: {hari_libur_list}")
    
    for day in range(1, num_days + 1):
        tgl_obj = datetime(tahun, bulan, day)
        if tgl_obj.weekday() == 6:  # Skip Minggu
            continue
        if cek_hari_libur(tgl_obj):  # Skip hari libur
            continue
        work_days.append(tgl_obj)
    
    logger.info(f"✅ Total hari kerja: {len(work_days)}")
    return work_days


def get_nth_weekday_date(year, month, weekday, n):
    """Mendapatkan tanggal untuk hari ke-n di bulan tertentu (0=Senin)"""
    first_day = datetime(year, month, 1)
    first_weekday = first_day.weekday()
    diff = (weekday - first_weekday) % 7
    first_occurrence = first_day + timedelta(days=diff)
    target_date = first_occurrence + timedelta(weeks=n-1)
    if target_date.month != month:
        return None
    return target_date


def rpf_simple(pool, count, used_today, tanggal_obj):
    available = [n for n in pool if n not in used_today]
    available = [n for n in available if not is_orang_libur(n, tanggal_obj)]
    if not available or len(available) < count:
        return []
    return random.sample(available, min(count, len(available)))


def get_dokter_wajib(kegiatan, hari_idx):
    """Cek apakah ada dokter WAJIB untuk kegiatan ini di hari ini"""
    if kegiatan in DOKTER_WAJIB_KEGIATAN:
        wajib_dict = DOKTER_WAJIB_KEGIATAN[kegiatan]
        if hari_idx in wajib_dict:
            return wajib_dict[hari_idx]
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# GENERATE DALAM GEDUNG (FIXED: Ujang & Haeriah hanya di Pustu, Dokter WAJIB)
# ═══════════════════════════════════════════════════════════════════════════════
def generate_jadwal_dalam_gedung(bulan, tahun, loka_karya=False):
    jadwal_baru = []
    skipped = []
    work_days = get_work_days_in_month(bulan, tahun)
    if not work_days:
        return [], ["Tidak ada hari kerja di bulan ini"]
    
    used_month = {n: 0 for n in POOL_ILP + POOL_DOKTER + POOL_BIDAN}
    
    for tgl_obj in work_days:
        tgl_str = tgl_obj.strftime('%Y-%m-%d')
        hari_idx = tgl_obj.weekday()
        hari_name = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu'][hari_idx]
        libur_malam = cek_piket_malam_sebelumnya(tgl_obj)
        used_today = set(libur_malam)
        
        # a. PENDAFTARAN
        jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'PENDAFTARAN', 'penyerta': '; '.join(PENDAFTARAN_TETAP), 'kategori': 'dalam_gedung', 'is_auto_generated': True})
        used_today.update(PENDAFTARAN_TETAP)
        
        # b & c. SKRINING ILP 1 & 2 - GUNAKAN POOL FILTERED
        for keg in ['SKRINING ILP 1', 'SKRINING ILP 2']:
            p = rpf(POOL_ILP_F, 1, used_today, used_month, tgl_obj)
            if p:
                used_today.add(p[0]); used_month[p[0]] = used_month.get(p[0], 0) + 1
                jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': keg, 'penyerta': p[0], 'kategori': 'dalam_gedung', 'is_auto_generated': True})
        
        # d. POLI PROLANIS - GUNAKAN POOL FILTERED
        p = rpf(POOL_ILP_F, 3, used_today, used_month, tgl_obj)
        if len(p) >= 3:
            used_today.update(p)
            for n in p: used_month[n] = used_month.get(n, 0) + 1
            jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'POLI PROLANIS', 'penyerta': '; '.join(p), 'kategori': 'dalam_gedung', 'is_auto_generated': True})
        
        # e. KLASTER DEWASA-LANSIA 1 - FIXED: Cek dokter WAJIB
        dok_wajib = get_dokter_wajib('KLASTER DEWASA-LANSIA 1', hari_idx)
        if dok_wajib and dok_wajib not in used_today and not is_orang_libur(dok_wajib, tgl_obj):
            dok = [dok_wajib]
            logger.info(f"✅ {tgl_str} ({hari_name}): {dok_wajib} WAJIB di KLASTER DEWASA-LANSIA 1")
        else:
            dok = rpf(POOL_DOKTER_F, 1, used_today, used_month, tgl_obj, kegiatan='KLASTER DEWASA-LANSIA 1')
        
        if dok:
            used_today.add(dok[0]); used_month[dok[0]] = used_month.get(dok[0], 0) + 1
            jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'KLASTER DEWASA-LANSIA 1', 'penyerta': dok[0], 'kategori': 'dalam_gedung', 'is_auto_generated': True})
        
        # f. KLASTER DEWASA-LANSIA 2 - FIXED: Cek dokter WAJIB
        dok_wajib = get_dokter_wajib('KLASTER DEWASA-LANSIA 2', hari_idx)
        if dok_wajib and dok_wajib not in used_today and not is_orang_libur(dok_wajib, tgl_obj):
            dok = [dok_wajib]
            logger.info(f"✅ {tgl_str} ({hari_name}): {dok_wajib} WAJIB di KLASTER DEWASA-LANSIA 2")
        else:
            dok = rpf(POOL_DOKTER_F, 1, used_today, used_month, tgl_obj, kegiatan='KLASTER DEWASA-LANSIA 2')
        
        if dok:
            used_today.add(dok[0]); used_month[dok[0]] = used_month.get(dok[0], 0) + 1
            jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'KLASTER DEWASA-LANSIA 2', 'penyerta': dok[0], 'kategori': 'dalam_gedung', 'is_auto_generated': True})
        
        # g. KLASTER IBU KIA & USG - FIXED: Cek dokter WAJIB
        dok_wajib = get_dokter_wajib('KLASTER IBU KIA & USG', hari_idx)
        if dok_wajib and dok_wajib not in used_today and not is_orang_libur(dok_wajib, tgl_obj):
            dok = [dok_wajib]
            logger.info(f"✅ {tgl_str} ({hari_name}): {dok_wajib} WAJIB di KLASTER IBU KIA & USG")
        else:
            dok = rpf(POOL_DOKTER_KIA, 1, used_today, used_month, tgl_obj, kegiatan='KLASTER IBU KIA & USG')
        
        bidan = rpf(POOL_BIDAN, 2, used_today, used_month, tgl_obj)
        if dok and len(bidan) >= 2:
            used_today.add(dok[0]); used_month[dok[0]] = used_month.get(dok[0], 0) + 1
            used_today.update(bidan)
            for n in bidan: used_month[n] = used_month.get(n, 0) + 1
            jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'KLASTER IBU KIA & USG', 'penyerta': f"{dok[0]}; {'; '.join(bidan)}", 'kategori': 'dalam_gedung', 'is_auto_generated': True})
        
        # h. KLASTER ANAK
        dok = rpf(POOL_DOKTER_KIA, 1, used_today, used_month, tgl_obj, kegiatan='KLASTER ANAK')
        bidan = rpf(POOL_BIDAN, 2, used_today, used_month, tgl_obj)
        if dok and len(bidan) >= 2:
            used_today.add(dok[0]); used_month[dok[0]] = used_month.get(dok[0], 0) + 1
            used_today.update(bidan)
            for n in bidan: used_month[n] = used_month.get(n, 0) + 1
            jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'KLASTER ANAK', 'penyerta': f"{dok[0]}; {'; '.join(bidan)}", 'kategori': 'dalam_gedung', 'is_auto_generated': True})
        
        # i. R. IMUNISASI (Kamis)
        if hari_name == "Kamis":
            bidan = rpf(POOL_BIDAN, 2, used_today, used_month, tgl_obj)
            if len(bidan) >= 2:
                used_today.update(bidan)
                for n in bidan: used_month[n] = used_month.get(n, 0) + 1
                jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'R. IMUNISASI', 'penyerta': '; '.join(bidan), 'kategori': 'dalam_gedung', 'is_auto_generated': True})
        
        # j. R. TINDAKAN - GUNAKAN POOL FILTERED
        p = rpf(POOL_TINDAKAN_F, 1, used_today, used_month, tgl_obj)
        if p:
            used_today.add(p[0]); used_month[p[0]] = used_month.get(p[0], 0) + 1
            jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'R. TINDAKAN', 'penyerta': p[0], 'kategori': 'dalam_gedung', 'is_auto_generated': True})
        
        # k, l, m. BP GIGI, APOTEK, LAB
        for keg, staff in [('BP GIGI', BP_GIGI_TETAP), ('APOTEK', APOTEK_TETAP), ('LAB', LAB_TETAP)]:
            jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': keg, 'penyerta': '; '.join(staff), 'kategori': 'dalam_gedung', 'is_auto_generated': True})
            used_today.update(staff)
        
        # n. R. TB (Selasa)
        if hari_name == "Selasa":
            jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'R. TB', 'penyerta': 'Mutia Wulansari.,S.Kep.,Ners', 'kategori': 'dalam_gedung', 'is_auto_generated': True})
            used_today.add('Mutia Wulansari.,S.Kep.,Ners')
            used_month['Mutia Wulansari.,S.Kep.,Ners'] = used_month.get('Mutia Wulansari.,S.Kep.,Ners', 0) + 1
        
        # o. ADMINISTRASI - GUNAKAN POOL FILTERED
        extra = rpf(ADMINISTRASI_EXTRA, 1, used_today, used_month, tgl_obj)
        adm_total = ADMINISTRASI_TETAP + extra
        jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'ADMINISTRASI', 'penyerta': '; '.join(adm_total), 'kategori': 'dalam_gedung', 'is_auto_generated': True})
        used_today.update(adm_total)
        for n in adm_total: used_month[n] = used_month.get(n, 0) + 1
        
        # p & q. PUSTU (Ujang & Haeriah HANYA di sini)
        for lok, staff in [('Pustu Ciangir', PUSTU_CIANGIR), ('Pustu Sumelap', PUSTU_SUMELAP)]:
            jadwal_baru.append({'tanggal': tgl_str, 'lokasi': lok, 'kegiatan': 'PELAYANAN PUSTU', 'penyerta': staff, 'kategori': 'dalam_gedung', 'is_auto_generated': True})
            used_today.add(staff); used_month[staff] = used_month.get(staff, 0) + 1
        
        # Loka Karya Mini - GUNAKAN POOL FILTERED
        if loka_karya and hari_name == "Senin":
            jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'LOKA KARYA MINI BULANAN', 'penyerta': '; '.join(LOKA_KARYA_MINI_F), 'kategori': 'dalam_gedung', 'is_auto_generated': True})
            used_today.update(LOKA_KARYA_MINI_F)
            for n in LOKA_KARYA_MINI_F: used_month[n] = used_month.get(n, 0) + 1
    
    return jadwal_baru, skipped


# ═══════════════════════════════════════════════════════════════════════════════
# GENERATE BOK (31 kegiatan + Sekolah/Pesantren) - FIXED ERROR HANDLING
# ═══════════════════════════════════════════════════════════════════════════════
def generate_jadwal_luar_gedung_bok(bulan, tahun, jadwal_dalam_gedung=None):
    try:
        jadwal_baru = []
        skipped = []
        work_days = get_work_days_in_month(bulan, tahun)
        if not work_days:
            return [], ["Tidak ada hari kerja di bulan ini"]
        
        used_luar_per_day = {d.strftime('%Y-%m-%d'): set() for d in work_days}
        used_dalam_per_day = {}
        if jadwal_dalam_gedung:
            for j in jadwal_dalam_gedung:
                tgl = j['tanggal']
                if tgl not in used_dalam_per_day: 
                    used_dalam_per_day[tgl] = set()
                names = [n.strip() for n in j.get('penyerta', '').split(';') if n.strip()]
                used_dalam_per_day[tgl].update(names)
        
        lokasi_count = {lok: 0 for lok in LOKASI_LUAR_GEDUNG}
        work_days_shuffled = work_days.copy()
        random.shuffle(work_days_shuffled)
        
        sekolah_terpakai = []
        paket_sekolah_dates = {}  # Track tanggal untuk paket sekolah
        
        for kegiatan_name, config in KEGIATAN_BOK.items():
            try:
                freq = config.get('freq', 1)
                petugas_pool = config.get('petugas', [])
                penyerta_pool = config.get('penyerta', [])
                allow_double_dalam = config.get('allow_double_dalam', False)
                allow_double_luar = config.get('allow_double_luar', False)
                lokasi_fixed = config.get('lokasi_fixed', None)
                tanggal_fixed = config.get('tanggal_fixed', None)
                count_penyerta = config.get('count_penyerta', 1)
                is_sekolah = config.get('is_sekolah', False)
                wajib = config.get('wajib', None)
                paket_dengan = config.get('paket_dengan', None)
                
                placed = 0
                attempts = 0
                max_attempts = freq * 20
                
                while placed < freq and attempts < max_attempts:
                    attempts += 1
                    
                    # Untuk paket sekolah, gunakan tanggal yang sama dengan kegiatan paket
                    if paket_dengan and paket_dengan in paket_sekolah_dates and paket_sekolah_dates[paket_dengan]:
                        tgl_str = paket_sekolah_dates[paket_dengan].pop(0)
                        tgl_obj = datetime.strptime(tgl_str, '%Y-%m-%d')
                    elif tanggal_fixed:
                        try:
                            tgl_obj = datetime(tahun, bulan, tanggal_fixed)
                            if tgl_obj not in work_days:
                                skipped.append(f"{kegiatan_name}: Tanggal {tanggal_fixed} bukan hari kerja")
                                break
                        except Exception as e:
                            skipped.append(f"{kegiatan_name}: Error tanggal fixed - {str(e)}")
                            break
                    else:
                        if not work_days_shuffled:
                            skipped.append(f"{kegiatan_name}: Tidak ada hari kerja tersedia")
                            break
                        tgl_obj = random.choice(work_days_shuffled)
                    
                    tgl_str = tgl_obj.strftime('%Y-%m-%d')
                    
                    # Simpan tanggal untuk paket
                    if is_sekolah and not paket_dengan:
                        if kegiatan_name not in paket_sekolah_dates:
                            paket_sekolah_dates[kegiatan_name] = []
                        paket_sekolah_dates[kegiatan_name].append(tgl_str)
                    
                    if not petugas_pool:
                        skipped.append(f"{kegiatan_name}: Pool petugas kosong")
                        break
                    
                    # Untuk sekolah, petugas sudah ditentukan (WAJIB_SEKOLAH)
                    if is_sekolah and wajib:
                        petugas = [n for n in wajib if n not in used_luar_per_day.get(tgl_str, set()) and not is_orang_libur(n, tgl_obj)]
                        if len(petugas) < 1:
                            continue
                        petugas = petugas[:1]  # Ambil 1 petugas dari wajib
                    else:
                        petugas = rpf_simple(petugas_pool, 1, used_luar_per_day.get(tgl_str, set()), tgl_obj)
                        if not petugas:
                            continue
                    
                    penyerta = []
                    if penyerta_pool and count_penyerta > 0:
                        exclude = set(petugas)
                        exclude.update(NAMA_TIDAK_BOLEH_BOK)
                        if not allow_double_luar:
                            exclude.update(used_luar_per_day.get(tgl_str, set()))
                        if not allow_double_dalam and tgl_str in used_dalam_per_day:
                            exclude.update(used_dalam_per_day[tgl_str])
                        
                        # Untuk sekolah, exclude yang sudah jadi petugas
                        if is_sekolah and wajib:
                            exclude.update([n for n in wajib if n not in petugas])
                        
                        available_penyerta = [n for n in penyerta_pool if n not in exclude and not is_orang_libur(n, tgl_obj)]
                        if len(available_penyerta) >= count_penyerta:
                            penyerta = random.sample(available_penyerta, count_penyerta)
                        else:
                            continue
                    
                    if lokasi_fixed:
                        lokasi = lokasi_fixed
                    elif is_sekolah:
                        sekolah_tersedia = [s for s in DAFTAR_SEKOLAH_PESANTREN if s not in sekolah_terpakai]
                        if sekolah_tersedia:
                            sekolah_terpilih = random.choice(sekolah_tersedia)
                            sekolah_terpakai.append(sekolah_terpilih)
                            lokasi = f'Sekolah/Pesantren {sekolah_terpilih}'
                        else:
                            sekolah_terpakai = []
                            sekolah_terpilih = random.choice(DAFTAR_SEKOLAH_PESANTREN)
                            sekolah_terpakai.append(sekolah_terpilih)
                            lokasi = f'Sekolah/Pesantren {sekolah_terpilih}'
                    else:
                        if not lokasi_count:
                            lokasi = 'Luar Gedung'
                        else:
                            lokasi = min(lokasi_count, key=lokasi_count.get)
                    
                    all_names = petugas + penyerta
                    jadwal_baru.append({
                        'tanggal': tgl_str, 'lokasi': lokasi, 'kegiatan': kegiatan_name,
                        'penyerta': '; '.join(all_names), 'kategori': 'luar_gedung',
                        'sub_kategori': 'bok', 'is_auto_generated': True
                    })
                    
                    if tgl_str not in used_luar_per_day:
                        used_luar_per_day[tgl_str] = set()
                    used_luar_per_day[tgl_str].update(all_names)
                    
                    if lokasi in lokasi_count:
                        lokasi_count[lokasi] += 1
                    
                    placed += 1
                
                if placed < freq:
                    skipped.append(f"{kegiatan_name}: Hanya {placed}/{freq} yang berhasil dijadwalkan")
            
            except Exception as e:
                skipped.append(f"{kegiatan_name}: Error - {str(e)}")
                continue
        
        return jadwal_baru, skipped
    
    except Exception as e:
        return [], [f"Error fatal di generate_jadwal_luar_gedung_bok: {str(e)}"]


# ═══════════════════════════════════════════════════════════════════════════════
# GENERATE PELAYANAN LUAR GEDUNG (Posyandu, Posbindu, UKK, Pos Remaja) - FIXED
# ═══════════════════════════════════════════════════════════════════════════════
def generate_jadwal_luar_gedung_lainnya(bulan, tahun, jadwal_bok=None, jadwal_dalam_gedung=None):
    try:
        jadwal_baru = []
        skipped = []
        
        used_per_day = {}
        if jadwal_bok:
            for j in jadwal_bok:
                tgl = j['tanggal']
                if tgl not in used_per_day: 
                    used_per_day[tgl] = set()
                names = [n.strip() for n in j.get('penyerta', '').split(';') if n.strip()]
                used_per_day[tgl].update(names)
        if jadwal_dalam_gedung:
            for j in jadwal_dalam_gedung:
                tgl = j['tanggal']
                if tgl not in used_per_day: 
                    used_per_day[tgl] = set()
                names = [n.strip() for n in j.get('penyerta', '').split(';') if n.strip()]
                used_per_day[tgl].update(names)
        
        def get_date(hari, minggu_ke):
            return get_nth_weekday_date(tahun, bulan, hari, minggu_ke)
        
        # ─── 1. POSYANDU (tanggal fixed sesuai jadwal buka) ───────────────────
        posyandu_slots = []
        for nama_pos, data in JADWAL_POSYANDU_FIXED.items():
            tgl_obj = get_date(data['hari'], data['minggu_ke'])
            if tgl_obj and not cek_hari_libur(tgl_obj):
                tgl_str = tgl_obj.strftime('%Y-%m-%d')
                posyandu_slots.append({
                    'tanggal': tgl_str, 'lokasi': nama_pos,
                    'kelurahan': data['kelurahan'],
                    'petugas_default': data.get('petugas', []),
                    'penyerta_default': data.get('penyerta', [])
                })
        
        for keg_name, freq in KEGIATAN_POSYANDU_LIST:
            try:
                placed = 0
                attempts = 0
                
                if not posyandu_slots:
                    skipped.append(f"{keg_name}: Tidak ada slot posyandu tersedia")
                    continue
                
                slots_copy = posyandu_slots.copy()
                random.shuffle(slots_copy)
                
                while placed < freq and attempts < len(slots_copy) * 2:
                    attempts += 1
                    
                    if not slots_copy:
                        break
                    
                    slot_index = attempts % len(slots_copy) if len(slots_copy) > 0 else 0
                    slot = slots_copy[slot_index]
                    tgl_str = slot['tanggal']
                    
                    if tgl_str not in used_per_day: 
                        used_per_day[tgl_str] = set()
                    
                    petugas = slot['petugas_default']
                    penyerta = slot['penyerta_default']
                    
                    if not petugas:
                        p = rpf_simple(POOL_PETUGAS_BIDAN_PERAWAT, 1, used_per_day[tgl_str], datetime.strptime(tgl_str, '%Y-%m-%d'))
                        if p: 
                            petugas = p
                    
                    if not penyerta:
                        exclude = set(petugas) if petugas else set()
                        exclude.update(used_per_day[tgl_str])
                        available = [n for n in POOL_PETUGAS_BIDAN_PERAWAT if n not in exclude and not is_orang_libur(n, datetime.strptime(tgl_str, '%Y-%m-%d'))]
                        if available: 
                            penyerta = random.sample(available, 1)
                    
                    if petugas and penyerta:
                        all_names = petugas + penyerta
                        jadwal_baru.append({
                            'tanggal': tgl_str, 'lokasi': slot['lokasi'], 'kegiatan': keg_name,
                            'penyerta': '; '.join(all_names), 'kategori': 'luar_gedung',
                            'sub_kategori': 'posyandu', 'is_auto_generated': True
                        })
                        used_per_day[tgl_str].update(all_names)
                        placed += 1
                
                if placed < freq:
                    skipped.append(f"{keg_name}: Hanya {placed}/{freq} yang berhasil dijadwalkan")
            
            except Exception as e:
                skipped.append(f"{keg_name}: Error - {str(e)}")
                continue
        
        # ─── 2. POSBINDU (tanggal fixed) ──────────────────────────────────────
        for nama_pos, data in JADWAL_POSBINDU_FIXED.items():
            try:
                tgl_obj = get_date(data['hari'], data['minggu_ke'])
                if tgl_obj and not cek_hari_libur(tgl_obj):
                    tgl_str = tgl_obj.strftime('%Y-%m-%d')
                    if tgl_str not in used_per_day: 
                        used_per_day[tgl_str] = set()
                    petugas = data.get('petugas', [])
                    if petugas:
                        jadwal_baru.append({
                            'tanggal': tgl_str, 'lokasi': nama_pos, 'kegiatan': 'Pelaksanaan Posbindu',
                            'penyerta': '; '.join(petugas), 'kategori': 'luar_gedung',
                            'sub_kategori': 'posbindu', 'is_auto_generated': True
                        })
                        used_per_day[tgl_str].update(petugas)
            except Exception as e:
                skipped.append(f"Posbindu {nama_pos}: Error - {str(e)}")
                continue
        
        # ─── 3. POS REMAJA (tanggal fixed) ────────────────────────────────────
        for nama_pos, data in JADWAL_POS_REMAJA_FIXED.items():
            try:
                tgl_obj = get_date(data['hari'], data['minggu_ke'])
                if tgl_obj and not cek_hari_libur(tgl_obj):
                    tgl_str = tgl_obj.strftime('%Y-%m-%d')
                    if tgl_str not in used_per_day: 
                        used_per_day[tgl_str] = set()
                    petugas = data.get('petugas', [])
                    if petugas:
                        jadwal_baru.append({
                            'tanggal': tgl_str, 'lokasi': nama_pos, 'kegiatan': 'Pembinaan Kesehatan di Komunitas',
                            'penyerta': '; '.join(petugas), 'kategori': 'luar_gedung',
                            'sub_kategori': 'pos_remaja', 'is_auto_generated': True
                        })
                        used_per_day[tgl_str].update(petugas)
            except Exception as e:
                skipped.append(f"Pos Remaja {nama_pos}: Error - {str(e)}")
                continue
        
        # ─── 4. UKK (random work day) ─────────────────────────────────────────
        work_days = get_work_days_in_month(bulan, tahun)
        for ukk in DAFTAR_UKK:
            try:
                if not work_days: 
                    continue
                tgl_obj = random.choice(work_days)
                tgl_str = tgl_obj.strftime('%Y-%m-%d')
                if tgl_str not in used_per_day: 
                    used_per_day[tgl_str] = set()
                petugas = ukk.get('petugas', [])
                if petugas:
                    jadwal_baru.append({
                        'tanggal': tgl_str, 'lokasi': ukk['nama'], 'kegiatan': 'Pelayanan UKK',
                        'penyerta': '; '.join(petugas), 'kategori': 'luar_gedung',
                        'sub_kategori': 'ukk', 'is_auto_generated': True
                    })
                    used_per_day[tgl_str].update(petugas)
            except Exception as e:
                skipped.append(f"UKK {ukk.get('nama', 'Unknown')}: Error - {str(e)}")
                continue
        
        return jadwal_baru, skipped
    
    except Exception as e:
        return [], [f"Error fatal di generate_jadwal_luar_gedung_lainnya: {str(e)}"]