# ============================================================
# FILE: randomize_logic.py (LANJUTAN)
# ============================================================

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
            return hari in rules[kegiatan]
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
    if wajib and len(wajib) >= count:
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
        if tgl_obj.weekday() == 6:
            continue
        if cek_hari_libur(tgl_obj):
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
# GENERATE DALAM GEDUNG (TANPA RANDOM - MENGGUNAKAN JADWAL TETAP)
# ═══════════════════════════════════════════════════════════════════════════════
def generate_jadwal_dalam_gedung(bulan, tahun, loka_karya=False):
    """
    Generate jadwal dalam gedung TANPA randomisasi.
    Semua kegiatan menggunakan jadwal tetap dengan petugas yang sudah ditentukan.
    """
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
        
        # a. PENDAFTARAN - TETAP
        jadwal_baru.append({
            'tanggal': tgl_str, 
            'lokasi': 'Dalam Gedung', 
            'kegiatan': 'PENDAFTARAN', 
            'penyerta': '; '.join(PENDAFTARAN_TETAP), 
            'kategori': 'dalam_gedung', 
            'is_auto_generated': True
        })
        used_today.update(PENDAFTARAN_TETAP)
        for n in PENDAFTARAN_TETAP:
            used_month[n] = used_month.get(n, 0) + 1
        
        # b & c. SKRINING ILP 1 & 2
        for keg in ['SKRINING ILP 1', 'SKRINING ILP 2']:
            available = [n for n in POOL_ILP_F if n not in used_today and not is_orang_libur(n, tgl_obj)]
            if available:
                petugas = [available[0]]
                used_today.add(petugas[0])
                used_month[petugas[0]] = used_month.get(petugas[0], 0) + 1
                jadwal_baru.append({
                    'tanggal': tgl_str, 
                    'lokasi': 'Dalam Gedung', 
                    'kegiatan': keg, 
                    'penyerta': petugas[0], 
                    'kategori': 'dalam_gedung', 
                    'is_auto_generated': True
                })
            else:
                skipped.append(f"{tgl_str}: Tidak ada petugas untuk {keg}")
        
        # d. POLI PROLANIS
        available = [n for n in POOL_ILP_F if n not in used_today and not is_orang_libur(n, tgl_obj)]
        if len(available) >= 3:
            petugas = available[:3]
            used_today.update(petugas)
            for n in petugas:
                used_month[n] = used_month.get(n, 0) + 1
            jadwal_baru.append({
                'tanggal': tgl_str, 
                'lokasi': 'Dalam Gedung', 
                'kegiatan': 'POLI PROLANIS', 
                'penyerta': '; '.join(petugas), 
                'kategori': 'dalam_gedung', 
                'is_auto_generated': True
            })
        else:
            skipped.append(f"{tgl_str}: Tidak cukup petugas untuk POLI PROLANIS (butuh 3, tersedia {len(available)})")
        
        # e. KLASTER DEWASA-LANSIA 1
        dok_wajib = get_dokter_wajib('KLASTER DEWASA-LANSIA 1', hari_idx)
        if dok_wajib and dok_wajib not in used_today and not is_orang_libur(dok_wajib, tgl_obj):
            dok = [dok_wajib]
            logger.info(f"✅ {tgl_str} ({hari_name}): {dok_wajib} WAJIB di KLASTER DEWASA-LANSIA 1")
        else:
            available = [n for n in POOL_DOKTER_F if n not in used_today and not is_orang_libur(n, tgl_obj) 
                        and is_dokter_available_for_kegiatan(n, 'KLASTER DEWASA-LANSIA 1', tgl_obj)]
            dok = available[:1] if available else []
        
        if dok:
            used_today.add(dok[0])
            used_month[dok[0]] = used_month.get(dok[0], 0) + 1
            jadwal_baru.append({
                'tanggal': tgl_str, 
                'lokasi': 'Dalam Gedung', 
                'kegiatan': 'KLASTER DEWASA-LANSIA 1', 
                'penyerta': dok[0], 
                'kategori': 'dalam_gedung', 
                'is_auto_generated': True
            })
        else:
            skipped.append(f"{tgl_str}: Tidak ada dokter untuk KLASTER DEWASA-LANSIA 1")
        
        # f. KLASTER DEWASA-LANSIA 2
        dok_wajib = get_dokter_wajib('KLASTER DEWASA-LANSIA 2', hari_idx)
        if dok_wajib and dok_wajib not in used_today and not is_orang_libur(dok_wajib, tgl_obj):
            dok = [dok_wajib]
            logger.info(f"✅ {tgl_str} ({hari_name}): {dok_wajib} WAJIB di KLASTER DEWASA-LANSIA 2")
        else:
            available = [n for n in POOL_DOKTER_F if n not in used_today and not is_orang_libur(n, tgl_obj)
                        and is_dokter_available_for_kegiatan(n, 'KLASTER DEWASA-LANSIA 2', tgl_obj)]
            dok = available[:1] if available else []
        
        if dok:
            used_today.add(dok[0])
            used_month[dok[0]] = used_month.get(dok[0], 0) + 1
            jadwal_baru.append({
                'tanggal': tgl_str, 
                'lokasi': 'Dalam Gedung', 
                'kegiatan': 'KLASTER DEWASA-LANSIA 2', 
                'penyerta': dok[0], 
                'kategori': 'dalam_gedung', 
                'is_auto_generated': True
            })
        else:
            skipped.append(f"{tgl_str}: Tidak ada dokter untuk KLASTER DEWASA-LANSIA 2")
        
        # g. KLASTER IBU KIA & USG
        dok_wajib = get_dokter_wajib('KLASTER IBU KIA & USG', hari_idx)
        if dok_wajib and dok_wajib not in used_today and not is_orang_libur(dok_wajib, tgl_obj):
            dok = [dok_wajib]
            logger.info(f"✅ {tgl_str} ({hari_name}): {dok_wajib} WAJIB di KLASTER IBU KIA & USG")
        else:
            available = [n for n in POOL_DOKTER_KIA if n not in used_today and not is_orang_libur(n, tgl_obj)
                        and is_dokter_available_for_kegiatan(n, 'KLASTER IBU KIA & USG', tgl_obj)]
            dok = available[:1] if available else []
        
        available_bidan = [n for n in POOL_BIDAN if n not in used_today and not is_orang_libur(n, tgl_obj)]
        bidan = available_bidan[:2] if len(available_bidan) >= 2 else []
        
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
                'is_auto_generated': True
            })
        else:
            if not dok:
                skipped.append(f"{tgl_str}: Tidak ada dokter untuk KLASTER IBU KIA & USG")
            elif len(bidan) < 2:
                skipped.append(f"{tgl_str}: Tidak cukup bidan untuk KLASTER IBU KIA & USG (butuh 2, tersedia {len(bidan)})")
        
        # h. KLASTER ANAK
        available_dokter = [n for n in POOL_DOKTER_KIA if n not in used_today and not is_orang_libur(n, tgl_obj)
                           and is_dokter_available_for_kegiatan(n, 'KLASTER ANAK', tgl_obj)]
        dok = available_dokter[:1] if available_dokter else []
        
        available_bidan = [n for n in POOL_BIDAN if n not in used_today and not is_orang_libur(n, tgl_obj)]
        bidan = available_bidan[:2] if len(available_bidan) >= 2 else []
        
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
                'is_auto_generated': True
            })
        else:
            if not dok:
                skipped.append(f"{tgl_str}: Tidak ada dokter untuk KLASTER ANAK")
            elif len(bidan) < 2:
                skipped.append(f"{tgl_str}: Tidak cukup bidan untuk KLASTER ANAK (butuh 2, tersedia {len(bidan)})")
        
        # i. R. IMUNISASI (Kamis)
        if hari_name == "Kamis":
            available_bidan = [n for n in POOL_BIDAN if n not in used_today and not is_orang_libur(n, tgl_obj)]
            if len(available_bidan) >= 2:
                bidan = available_bidan[:2]
                used_today.update(bidan)
                for n in bidan:
                    used_month[n] = used_month.get(n, 0) + 1
                jadwal_baru.append({
                    'tanggal': tgl_str, 
                    'lokasi': 'Dalam Gedung', 
                    'kegiatan': 'R. IMUNISASI', 
                    'penyerta': '; '.join(bidan), 
                    'kategori': 'dalam_gedung', 
                    'is_auto_generated': True
                })
            else:
                skipped.append(f"{tgl_str}: Tidak cukup bidan untuk R. IMUNISASI (butuh 2, tersedia {len(available_bidan)})")
        
        # j. R. TINDAKAN
        available = [n for n in POOL_TINDAKAN_F if n not in used_today and not is_orang_libur(n, tgl_obj)]
        if available:
            petugas = [available[0]]
            used_today.add(petugas[0])
            used_month[petugas[0]] = used_month.get(petugas[0], 0) + 1
            jadwal_baru.append({
                'tanggal': tgl_str, 
                'lokasi': 'Dalam Gedung', 
                'kegiatan': 'R. TINDAKAN', 
                'penyerta': petugas[0], 
                'kategori': 'dalam_gedung', 
                'is_auto_generated': True
            })
        else:
            skipped.append(f"{tgl_str}: Tidak ada petugas untuk R. TINDAKAN")
        
        # k, l, m. BP GIGI, APOTEK, LAB
        for keg, staff in [('BP GIGI', BP_GIGI_TETAP), ('APOTEK', APOTEK_TETAP), ('LAB', LAB_TETAP)]:
            jadwal_baru.append({
                'tanggal': tgl_str, 
                'lokasi': 'Dalam Gedung', 
                'kegiatan': keg, 
                'penyerta': '; '.join(staff), 
                'kategori': 'dalam_gedung', 
                'is_auto_generated': True
            })
            used_today.update(staff)
            for n in staff:
                used_month[n] = used_month.get(n, 0) + 1
        
        # n. R. TB (Selasa)
        if hari_name == "Selasa":
            jadwal_baru.append({
                'tanggal': tgl_str, 
                'lokasi': 'Dalam Gedung', 
                'kegiatan': 'R. TB', 
                'penyerta': 'Mutia Wulansari.,S.Kep.,Ners', 
                'kategori': 'dalam_gedung', 
                'is_auto_generated': True
            })
            used_today.add('Mutia Wulansari.,S.Kep.,Ners')
            used_month['Mutia Wulansari.,S.Kep.,Ners'] = used_month.get('Mutia Wulansari.,S.Kep.,Ners', 0) + 1
        
        # o. ADMINISTRASI
        available_extra = [n for n in ADMINISTRASI_EXTRA if n not in used_today and not is_orang_libur(n, tgl_obj)]
        extra = available_extra[:1] if available_extra else []
        adm_total = ADMINISTRASI_TETAP + extra
        jadwal_baru.append({
            'tanggal': tgl_str, 
            'lokasi': 'Dalam Gedung', 
            'kegiatan': 'ADMINISTRASI', 
            'penyerta': '; '.join(adm_total), 
            'kategori': 'dalam_gedung', 
            'is_auto_generated': True
        })
        used_today.update(adm_total)
        for n in adm_total:
            used_month[n] = used_month.get(n, 0) + 1
        
        # p & q. PUSTU
        for lok, staff in [('Pustu Ciangir', PUSTU_CIANGIR), ('Pustu Sumelap', PUSTU_SUMELAP)]:
            jadwal_baru.append({
                'tanggal': tgl_str, 
                'lokasi': lok, 
                'kegiatan': 'PELAYANAN PUSTU', 
                'penyerta': staff, 
                'kategori': 'dalam_gedung', 
                'is_auto_generated': True
            })
            used_today.add(staff)
            used_month[staff] = used_month.get(staff, 0) + 1
        
        # Loka Karya Mini (Senin)
        if loka_karya and hari_name == "Senin":
            jadwal_baru.append({
                'tanggal': tgl_str, 
                'lokasi': 'Dalam Gedung', 
                'kegiatan': 'LOKA KARYA MINI BULANAN', 
                'penyerta': '; '.join(LOKA_KARYA_MINI_F), 
                'kategori': 'dalam_gedung', 
                'is_auto_generated': True
            })
            used_today.update(LOKA_KARYA_MINI_F)
            for n in LOKA_KARYA_MINI_F:
                used_month[n] = used_month.get(n, 0) + 1
    
    return jadwal_baru, skipped


# ═══════════════════════════════════════════════════════════════════════════════
# GENERATE PELAYANAN LUAR GEDUNG (TANPA RANDOM - MENGGUNAKAN JADWAL TETAP)
# ═══════════════════════════════════════════════════════════════════════════════
def generate_jadwal_luar_gedung_lainnya(bulan, tahun, jadwal_bok=None, jadwal_dalam_gedung=None):
    """
    Generate jadwal pelayanan luar gedung (Posyandu, Posbindu, UKK, Pos Remaja)
    TANPA randomisasi - menggunakan jadwal tetap yang sudah ditentukan.
    """
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
        
        # ─── 1. POSYANDU ──────────────────────────────────────────────────────
        for nama_pos, data in JADWAL_POSYANDU_FIXED.items():
            try:
                tgl_obj = get_date(data['hari'], data['minggu_ke'])
                if not tgl_obj:
                    skipped.append(f"{nama_pos}: Tanggal tidak valid")
                    continue
                    
                if cek_hari_libur(tgl_obj):
                    skipped.append(f"{nama_pos}: Tanggal {tgl_obj.strftime('%Y-%m-%d')} adalah hari libur")
                    continue
                
                tgl_str = tgl_obj.strftime('%Y-%m-%d')
                if tgl_str not in used_per_day:
                    used_per_day[tgl_str] = set()
                
                petugas = data.get('petugas', [])
                penyerta = data.get('penyerta', [])
                
                petugas = [p for p in petugas if not is_orang_libur(p, tgl_obj)]
                penyerta = [p for p in penyerta if not is_orang_libur(p, tgl_obj)]
                
                if petugas:
                    all_names = petugas + penyerta
                    jadwal_baru.append({
                        'tanggal': tgl_str, 
                        'lokasi': nama_pos, 
                        'kegiatan': 'Pelaksanaan Posyandu',
                        'penyerta': '; '.join(all_names), 
                        'kategori': 'luar_gedung',
                        'sub_kategori': 'posyandu', 
                        'is_auto_generated': True
                    })
                    used_per_day[tgl_str].update(all_names)
                else:
                    skipped.append(f"{nama_pos}: Tidak ada petugas tersedia")
                    
            except Exception as e:
                skipped.append(f"Posyandu {nama_pos}: Error - {str(e)}")
                continue
        
        # ─── 2. POSBINDU ──────────────────────────────────────────────────────
        for nama_pos, data in JADWAL_POSBINDU_FIXED.items():
            try:
                tgl_obj = get_date(data['hari'], data['minggu_ke'])
                if not tgl_obj:
                    skipped.append(f"{nama_pos}: Tanggal tidak valid")
                    continue
                    
                if cek_hari_libur(tgl_obj):
                    skipped.append(f"{nama_pos}: Tanggal {tgl_obj.strftime('%Y-%m-%d')} adalah hari libur")
                    continue
                
                tgl_str = tgl_obj.strftime('%Y-%m-%d')
                if tgl_str not in used_per_day:
                    used_per_day[tgl_str] = set()
                
                petugas = data.get('petugas', [])
                petugas = [p for p in petugas if not is_orang_libur(p, tgl_obj)]
                
                if petugas:
                    jadwal_baru.append({
                        'tanggal': tgl_str, 
                        'lokasi': nama_pos, 
                        'kegiatan': 'Pelaksanaan Posbindu',
                        'penyerta': '; '.join(petugas), 
                        'kategori': 'luar_gedung',
                        'sub_kategori': 'posbindu', 
                        'is_auto_generated': True
                    })
                    used_per_day[tgl_str].update(petugas)
                else:
                    skipped.append(f"{nama_pos}: Tidak ada petugas tersedia")
                    
            except Exception as e:
                skipped.append(f"Posbindu {nama_pos}: Error - {str(e)}")
                continue
        
        # ─── 3. POS REMAJA ────────────────────────────────────────────────────
        for nama_pos, data in JADWAL_POS_REMAJA_FIXED.items():
            try:
                tgl_obj = get_date(data['hari'], data['minggu_ke'])
                if not tgl_obj:
                    skipped.append(f"{nama_pos}: Tanggal tidak valid")
                    continue
                    
                if cek_hari_libur(tgl_obj):
                    skipped.append(f"{nama_pos}: Tanggal {tgl_obj.strftime('%Y-%m-%d')} adalah hari libur")
                    continue
                
                tgl_str = tgl_obj.strftime('%Y-%m-%d')
                if tgl_str not in used_per_day:
                    used_per_day[tgl_str] = set()
                
                petugas = data.get('petugas', [])
                petugas = [p for p in petugas if not is_orang_libur(p, tgl_obj)]
                
                if petugas:
                    jadwal_baru.append({
                        'tanggal': tgl_str, 
                        'lokasi': nama_pos, 
                        'kegiatan': 'Pembinaan Kesehatan di Komunitas',
                        'penyerta': '; '.join(petugas), 
                        'kategori': 'luar_gedung',
                        'sub_kategori': 'pos_remaja', 
                        'is_auto_generated': True
                    })
                    used_per_day[tgl_str].update(petugas)
                else:
                    skipped.append(f"{nama_pos}: Tidak ada petugas tersedia")
                    
            except Exception as e:
                skipped.append(f"Pos Remaja {nama_pos}: Error - {str(e)}")
                continue
        
        # ─── 4. UKK ───────────────────────────────────────────────────────────
        for ukk in DAFTAR_UKK:
            try:
                work_days = get_work_days_in_month(bulan, tahun)
                if not work_days:
                    skipped.append(f"UKK {ukk.get('nama', 'Unknown')}: Tidak ada hari kerja")
                    continue
                
                available_days = []
                for tgl_obj in work_days:
                    tgl_str = tgl_obj.strftime('%Y-%m-%d')
                    if tgl_str not in used_per_day:
                        available_days.append(tgl_obj)
                
                if not available_days:
                    skipped.append(f"UKK {ukk.get('nama', 'Unknown')}: Tidak ada hari tersedia")
                    continue
                
                tgl_obj = available_days[0]
                tgl_str = tgl_obj.strftime('%Y-%m-%d')
                if tgl_str not in used_per_day:
                    used_per_day[tgl_str] = set()
                
                petugas = ukk.get('petugas', [])
                petugas = [p for p in petugas if not is_orang_libur(p, tgl_obj)]
                
                if petugas:
                    jadwal_baru.append({
                        'tanggal': tgl_str, 
                        'lokasi': ukk['nama'], 
                        'kegiatan': 'Pelayanan UKK',
                        'penyerta': '; '.join(petugas), 
                        'kategori': 'luar_gedung',
                        'sub_kategori': 'ukk', 
                        'is_auto_generated': True
                    })
                    used_per_day[tgl_str].update(petugas)
                else:
                    skipped.append(f"UKK {ukk.get('nama', 'Unknown')}: Tidak ada petugas tersedia")
                    
            except Exception as e:
                skipped.append(f"UKK {ukk.get('nama', 'Unknown')}: Error - {str(e)}")
                continue
        
        return jadwal_baru, skipped
    
    except Exception as e:
        return [], [f"Error fatal di generate_jadwal_luar_gedung_lainnya: {str(e)}"]


# ═══════════════════════════════════════════════════════════════════════════════
# GENERATE BOK (31 kegiatan + Sekolah/Pesantren) - HANYA INI YANG RANDOM
# ═══════════════════════════════════════════════════════════════════════════════
def generate_jadwal_luar_gedung_bok(bulan, tahun, jadwal_dalam_gedung=None):
    """
    Generate jadwal BOK dengan RANDOMISASI.
    Hanya fungsi ini yang menggunakan randomisasi.
    
    ATURAN:
    - 1 orang hanya boleh 1 kegiatan per hari (baik sebagai petugas maupun penyerta)
    - KAMRT diproses pertama (prioritas)
    - Untuk KAMRT: jika Eko & Nurul sudah terpakai, penyerta bisa naik jadi petugas
    """
    try:
        jadwal_baru = []
        skipped = []
        work_days = get_work_days_in_month(bulan, tahun)
        if not work_days:
            return [], ["Tidak ada hari kerja di bulan ini"]
        
        # Track semua orang yang sudah dipakai di hari tertentu (BOK + Dalam Gedung)
        # 1 orang hanya boleh 1 kegiatan per hari
        used_per_day = {}
        for d in work_days:
            used_per_day[d.strftime('%Y-%m-%d')] = set()
        
        # Track dari jadwal dalam gedung
        if jadwal_dalam_gedung:
            for j in jadwal_dalam_gedung:
                tgl = j['tanggal']
                if tgl not in used_per_day:
                    used_per_day[tgl] = set()
                names = [n.strip() for n in j.get('penyerta', '').split(';') if n.strip()]
                for n in names:
                    used_per_day[tgl].add(n)
        
        # Track lokasi per kegiatan per hari (untuk allow_double_luar=True)
        double_luar_tracker = {}
        for d in work_days:
            double_luar_tracker[d.strftime('%Y-%m-%d')] = {}
        
        # Track count lokasi untuk distribusi merata
        lokasi_count = {}
        for lok in LOKASI_LUAR_GEDUNG:
            lokasi_count[lok] = 0
        
        work_days_shuffled = work_days.copy()
        random.shuffle(work_days_shuffled)
        
        sekolah_terpakai = []
        paket_sekolah_dates = {}
        
        # KAMRT diproses pertama (prioritas)
        kegiatan_prioritas = ['Surveilans Kualitas Air Minum Rumah Tangga (KAMRT)']
        kegiatan_lain = [k for k in KEGIATAN_BOK.keys() if k not in kegiatan_prioritas]
        urutan_kegiatan = kegiatan_prioritas + kegiatan_lain
        
        for kegiatan_name in urutan_kegiatan:
            config = KEGIATAN_BOK[kegiatan_name]
            freq = config.get('freq', 1)
            petugas_pool = config.get('petugas', [])
            penyerta_pool = config.get('penyerta', [])
            allow_double_dalam = config.get('allow_double_dalam', False)
            allow_double_luar = config.get('allow_double_luar', False)
            lokasi_fixed = config.get('lokasi_fixed', None)
            tanggal_fixed = config.get('tanggal_fixed', None)
            count_penyerta = config.get('count_penyerta', 1)
            is_sekolah = config.get('is_sekolah', False)
            paket_dengan = config.get('paket_dengan', None)
            lokasi_pool = config.get('lokasi_pool', None)
            allow_penyerta_jadi_petugas = config.get('allow_penyerta_jadi_petugas', False)
            
            placed = 0
            attempts = 0
            max_attempts = freq * 200
            
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
                
                # Pastikan used_per_day untuk tanggal ini ada
                if tgl_str not in used_per_day:
                    used_per_day[tgl_str] = set()
                
                # ═══════════════════════════════════════════════════════════════
                # LOGIKA UNTUK allow_double_luar = True
                # ═══════════════════════════════════════════════════════════════
                if allow_double_luar:
                    # Untuk kegiatan yang boleh multiple di hari yang sama
                    
                    # CEK KHUSUS UNTUK KAMRT: izinkan penyerta menjadi petugas
                    is_kamrt = (kegiatan_name == 'Surveilans Kualitas Air Minum Rumah Tangga (KAMRT)')
                    
                    # 1. Pilih petugas
                    petugas = None
                    
                    if is_kamrt and allow_penyerta_jadi_petugas:
                        # KAMRT: Prioritas Eko & Nurul, jika sudah terpakai, ambil dari penyerta
                        # Cari petugas utama yang tersedia (belum dipakai hari ini)
                        available_petugas_utama = []
                        for n in petugas_pool:
                            if n not in used_per_day[tgl_str] and not is_orang_libur(n, tgl_obj):
                                available_petugas_utama.append(n)
                        
                        if available_petugas_utama:
                            petugas = [random.choice(available_petugas_utama)]
                        else:
                            # Semua petugas utama sudah dipakai hari ini
                            # Cari dari penyerta yang belum dipakai
                            available_penyerta_jadi_petugas = []
                            for n in penyerta_pool:
                                if n not in used_per_day[tgl_str] and not is_orang_libur(n, tgl_obj):
                                    available_penyerta_jadi_petugas.append(n)
                            
                            if not available_penyerta_jadi_petugas:
                                continue
                            
                            petugas = [random.choice(available_penyerta_jadi_petugas)]
                    else:
                        # Kegiatan lain: petugas tidak boleh sama di hari yang sama
                        available_petugas = []
                        for n in petugas_pool:
                            if n not in used_per_day[tgl_str] and not is_orang_libur(n, tgl_obj):
                                available_petugas.append(n)
                        if not available_petugas:
                            continue
                        petugas = [random.choice(available_petugas)]
                    
                    # 2. Pilih penyerta
                    penyerta = []
                    if penyerta_pool and count_penyerta > 0:
                        exclude = set()
                        for n in petugas:
                            exclude.add(n)
                        for n in used_per_day.get(tgl_str, set()):
                            exclude.add(n)
                        
                        available_penyerta = []
                        for n in penyerta_pool:
                            if n not in exclude and not is_orang_libur(n, tgl_obj):
                                available_penyerta.append(n)
                        
                        if len(available_penyerta) >= count_penyerta:
                            penyerta = random.sample(available_penyerta, count_penyerta)
                        else:
                            continue
                    
                    # 3. Pilih lokasi
                    if lokasi_fixed:
                        lokasi = lokasi_fixed
                    elif lokasi_pool:
                        # Cari lokasi yang belum dipakai untuk kegiatan ini di hari ini
                        key = (kegiatan_name, tgl_str)
                        used_lokasi = set()
                        if tgl_str in double_luar_tracker and key in double_luar_tracker[tgl_str]:
                            used_lokasi = double_luar_tracker[tgl_str][key]
                        
                        available_lokasi = []
                        for l in lokasi_pool:
                            if l not in used_lokasi:
                                available_lokasi.append(l)
                        
                        if not available_lokasi:
                            continue
                        lokasi = random.choice(available_lokasi)
                    else:
                        if not lokasi_count:
                            lokasi = 'Luar Gedung'
                        else:
                            min_count = min(lokasi_count.values())
                            for l, c in lokasi_count.items():
                                if c == min_count:
                                    lokasi = l
                                    break
                    
                    # 4. Track semua (1 orang hanya 1 kegiatan per hari)
                    all_names = petugas + penyerta
                    
                    # Tambahkan ke used_per_day
                    for n in all_names:
                        used_per_day[tgl_str].add(n)
                    
                    # Track lokasi per kegiatan per hari
                    key = (kegiatan_name, tgl_str)
                    if tgl_str not in double_luar_tracker:
                        double_luar_tracker[tgl_str] = {}
                    if key not in double_luar_tracker[tgl_str]:
                        double_luar_tracker[tgl_str][key] = set()
                    double_luar_tracker[tgl_str][key].add(lokasi)
                    
                    if lokasi in lokasi_count:
                        lokasi_count[lokasi] = lokasi_count.get(lokasi, 0) + 1
                    
                else:
                    # Untuk kegiatan yang TIDAK BOLEH double luar
                    # 1. Pilih petugas
                    available_petugas = []
                    for n in petugas_pool:
                        if n not in used_per_day.get(tgl_str, set()) and not is_orang_libur(n, tgl_obj):
                            available_petugas.append(n)
                    if not available_petugas:
                        continue
                    petugas = [random.choice(available_petugas)]
                    
                    # 2. Pilih penyerta
                    penyerta = []
                    if penyerta_pool and count_penyerta > 0:
                        exclude = set()
                        for n in petugas:
                            exclude.add(n)
                        for n in used_per_day.get(tgl_str, set()):
                            exclude.add(n)
                        
                        available_penyerta = []
                        for n in penyerta_pool:
                            if n not in exclude and not is_orang_libur(n, tgl_obj):
                                available_penyerta.append(n)
                        
                        if len(available_penyerta) >= count_penyerta:
                            penyerta = random.sample(available_penyerta, count_penyerta)
                        else:
                            continue
                    
                    # 3. Pilih lokasi
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
                            min_count = min(lokasi_count.values())
                            for l, c in lokasi_count.items():
                                if c == min_count:
                                    lokasi = l
                                    break
                    
                    # 4. Track semua (1 orang hanya 1 kegiatan per hari)
                    all_names = petugas + penyerta
                    
                    for n in all_names:
                        used_per_day[tgl_str].add(n)
                    
                    if lokasi in lokasi_count:
                        lokasi_count[lokasi] = lokasi_count.get(lokasi, 0) + 1
                
                jadwal_baru.append({
                    'tanggal': tgl_str,
                    'lokasi': lokasi,
                    'kegiatan': kegiatan_name,
                    'penyerta': '; '.join(all_names),
                    'kategori': 'luar_gedung',
                    'sub_kategori': 'bok',
                    'is_auto_generated': True
                })
                
                placed += 1
            
            if placed < freq:
                skipped.append(f"{kegiatan_name}: Hanya {placed}/{freq} yang berhasil dijadwalkan")
        
        return jadwal_baru, skipped
    
    except Exception as e:
        return [], [f"Error fatal di generate_jadwal_luar_gedung_bok: {str(e)}"]