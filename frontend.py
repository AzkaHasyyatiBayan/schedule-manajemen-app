import streamlit as st
import pandas as pd
import requests
import re
import random
import calendar
from datetime import datetime, date, timedelta
from collections import defaultdict

# ---------- Konfigurasi Halaman ----------
st.set_page_config(page_title="Puskesmas Sangkali", page_icon="🏥", layout="wide")

# ---------- CSS + Font Awesome ----------
st.html("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>
<style>
  .main-header {
    background: linear-gradient(135deg, #14532d 0%, #166534 100%);
    padding: 2rem; border-radius: 20px; color: white;
    text-align: center; margin-bottom: 2rem;
  }
  .main-header h1 { margin: 0; }
  .data-card { background: white; padding: 1.5rem; border-radius: 16px;
               border: 1px solid #e5e7eb; margin-bottom: 1rem; }
  .result-box { background: #f8fafc; padding: 1rem; border-radius: 12px;
                border-left: 5px solid #14532d; margin: 0.5rem 0; }
  .icon-text i { margin-right: 8px; color: #14532d; }
  .logo-container { display: flex; justify-content: center; margin-bottom: 1rem; }
  .badge-online { display: inline-block; background: #dcfce7; color: #15803d;
                  font-size: 0.75rem; font-weight: 600; padding: 2px 10px; border-radius: 999px; }
  .badge-offline { display: inline-block; background: #fee2e2; color: #dc2626;
                   font-size: 0.75rem; font-weight: 600; padding: 2px 10px; border-radius: 999px; }
  .svg-icon { display: inline-block; vertical-align: middle; margin-right: 6px; }
  .past { color: #9ca3af; }
  .today { color: #15803d; font-weight: bold; }
  .tomorrow { color: #2563eb; }
  .future { color: #111827; }
  .reduced-link { color: #6b7280; font-style: italic; font-size: 0.9rem; }
  .notification-card { background: #dcfce7; border: 1px solid #bbf7d0;
                       padding: 1rem; border-radius: 12px; margin-bottom: 1rem; }
  .notification-card ul { margin-top: 0.5rem; padding-left: 1.5rem; }
  .notification-card li { margin-bottom: 0.25rem; }
  .center-red-btn { display: flex; justify-content: center; margin: 1rem 0; }
  .center-red-btn button { background-color: #dc2626 !important; color: white !important;
                           border: none !important; font-weight: 500;
                           padding: 0.4rem 1.5rem !important; border-radius: 8px; width: auto !important; }
  .center-red-btn button:hover { background-color: #b91c1c !important; }
  .randomize-card { background: #f0fdf4; border: 1px solid #bbf7d0; padding: 1rem; border-radius: 12px; margin-bottom: 1rem; }
</style>
""")

API_BASE = "http://localhost:8000/api"

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

# ==================== DATA KARYAWAN BERDASARKAN ROLE ====================
def get_karyawan_by_role(role_keywords):
    """Filter karyawan berdasarkan role dari DAFTAR_NAMA"""
    role_map = {
        'dokter': ['dr.', 'drg.'],
        'perawat_ners': ['Ners', 'S.Kep', 'Amd.Kep', 'A.Md.Kep'],
        'bidan': ['Bdn.', 'S.Tr.Keb', 'Am.Keb', 'A.Md.Keb'],
        'promkes': ['Promosi', 'SKM'],
        'sanitarian': ['Sanitarian', 'S.K.M', 'A.Md.KL'],
        'gizi': ['S.Gz', 'A.Md.Gz'],
        'apoteker': ['Apt', 'S.Farm'],
        'lab': ['A.Md.AK'],
        'gigi': ['drg.', 'S.Tr.Kes'],
        'administrasi': ['S.E', 'S.T', 'S.Kep', 'S.ST', 'SKM', 'AMd.RMIK']
    }
    keywords = role_map.get(role_keywords, [])
    hasil = []
    for nama in DAFTAR_NAMA:
        for kw in keywords:
            if kw.lower() in nama.lower():
                hasil.append(nama)
                break
    return list(set(hasil))

# Karyawan tetap
PENDAFTARAN_TETAP = ["Winda Siti Sarah, AMd.RMIK", "Pupung Juliana", "Salsa Sabila"]
BP_GIGI_TETAP = ["drg.Rifan Hanggoro.M.M.R.S", "Endah Setiawati,S.Tr.Kes"]
APOTEK_TETAP = ["Khilman Husna Pratama, S.Farm.,Apt", "Nova Silpiany Perdany, A.Md.Farm"]
LAB_TETAP = ["Vita Tyana Virista, A.Md.AK", "Gina Giovany, A.Md.AK"]
PUSTU_CIANGIR = "Haeriah, A.Md.Kep"
PUSTU_SUMELAP = "Ujang Effendi, S.Kep.,Ners"
ADMINISTRASI_TETAP = ["Rangga Ismardana Gasbela,S.T", "Yogi Aris Diyanto, S.E"]
ADMINISTRASI_EXTRA = ["Liska Permatasari, S.Kep.,Ners", "Alitsa Nuur Fithri, S.ST", "Andina Dea Priatna, SKM"]

# ---------- Session State ----------
for key, default in [
    ('logged_in', False),
    ('token', None),
    ('username', ''),
    ('page', 'user'),
    ('edit_data', None),
    ('last_csv_url', ''),
    ('notif', None),
    ('pending_delete_ids', []),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ---------- Cek token dari URL ----------
params = st.query_params
if not st.session_state.logged_in and 'token' in params:
    token = params['token']
    try:
        resp = requests.get(f"{API_BASE}/verify-token/", headers={"Authorization": f"Token {token}"}, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            st.session_state.logged_in = True
            st.session_state.token = token
            st.session_state.username = data.get('username', 'Admin')
            st.query_params.clear()
            st.rerun()
        else:
            st.query_params.clear()
    except Exception:
        pass

# ---------- Helper API ----------
def auth_headers():
    return {"Authorization": f"Token {st.session_state.token}"}

def api_get(path, params=None, auth=False):
    h = auth_headers() if auth else {}
    return requests.get(f"{API_BASE}/{path}", params=params, headers=h, timeout=10)

def api_post(path, data, auth=False):
    h = {"Content-Type": "application/json"}
    if auth: h.update(auth_headers())
    return requests.post(f"{API_BASE}/{path}", json=data, headers=h, timeout=10)

def api_put(path, data):
    return requests.put(f"{API_BASE}/{path}", json=data, headers=auth_headers(), timeout=10)

def api_delete(path):
    return requests.delete(f"{API_BASE}/{path}", headers=auth_headers(), timeout=10)

def parse_penyerta(teks):
    if not teks:
        return []
    if ';' in teks:
        return [p.strip() for p in teks.split(';') if p.strip()]
    parts = re.split(r', (?=[A-Z])', teks)
    return [p.strip() for p in parts if p.strip()]

# ==================== FUNGSI RANDOMIZE JADWAL ====================
def random_pick_from_list(lst, count=1, exclude=None):
    if exclude is None:
        exclude = []
    available = [x for x in lst if x not in exclude]
    if len(available) < count:
        return available
    return random.sample(available, count)

def generate_jadwal_bulanan(month, year):
    """Generate jadwal untuk satu bulan penuh (Senin-Sabtu)"""
    random.seed(f"{year}-{month}")
    
    cal = calendar.monthcalendar(year, month)
    work_days = []
    for week in cal:
        for day_idx, day in enumerate(week):
            if day != 0 and day_idx < 6:
                work_days.append(day)
    
    day_names = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
    
    semua_dokter = get_karyawan_by_role('dokter')
    semua_perawat_ners = get_karyawan_by_role('perawat_ners')
    semua_bidan = get_karyawan_by_role('bidan')
    semua_promkes = get_karyawan_by_role('promkes')
    semua_sanitarian = get_karyawan_by_role('sanitarian')
    semua_gizi = get_karyawan_by_role('gizi')
    
    pool_ilp_prolanis = list(set(semua_perawat_ners + semua_bidan + semua_promkes + semua_sanitarian + semua_gizi))
    
    jadwal_generated = []
    
    for tanggal in work_days:
        tgl_str = f"{year}-{month:02d}-{tanggal:02d}"
        tgl_obj = datetime(year, month, tanggal)
        hari_ke = tgl_obj.weekday()
        nama_hari = day_names[hari_ke]
        
        used_today = set()
        jadwal_hari = []
        
        # 1. PENDAFTARAN
        jadwal_hari.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'PENDAFTARAN', 'penyerta': '; '.join(PENDAFTARAN_TETAP)})
        used_today.update(PENDAFTARAN_TETAP)
        
        # 2. SKRINING ILP 1 & 2
        for i in range(1, 3):
            available = [p for p in pool_ilp_prolanis if p not in used_today]
            if available:
                petugas = random.choice(available)
                used_today.add(petugas)
                jadwal_hari.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': f'SKRINING ILP {i}', 'penyerta': petugas})
        
        # 3. POLI PROLANIS
        available_prolanis = [p for p in pool_ilp_prolanis if p not in used_today]
        if len(available_prolanis) >= 3:
            petugas_prolanis = random.sample(available_prolanis, 3)
            used_today.update(petugas_prolanis)
            jadwal_hari.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'POLI PROLANIS', 'penyerta': '; '.join(petugas_prolanis)})
        
        # 4. KLASTER DEWASA-LANSIA 1 & 2
        for i in range(1, 3):
            available_dokter = [d for d in semua_dokter if d not in used_today]
            if available_dokter:
                petugas = random.choice(available_dokter)
                used_today.add(petugas)
            else:
                available_ners = [n for n in semua_perawat_ners if n not in used_today]
                petugas = random.choice(available_ners) if available_ners else "Tidak tersedia"
                if petugas != "Tidak tersedia":
                    used_today.add(petugas)
            jadwal_hari.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': f'KLASTER DEWASA-LANSIA {i}', 'penyerta': petugas})
        
        # 5. KLASTER IBU KIA & USG
        available_bidan = [b for b in semua_bidan if b not in used_today]
        available_dokter = [d for d in semua_dokter if d not in used_today]
        petugas_bidan = random.sample(available_bidan, 2) if len(available_bidan) >= 2 else available_bidan
        used_today.update(petugas_bidan)
        petugas_dokter = random.choice(available_dokter) if available_dokter else "Tidak tersedia"
        if petugas_dokter != "Tidak tersedia":
            used_today.add(petugas_dokter)
        jadwal_hari.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'KLASTER IBU KIA & USG', 'penyerta': f"{'; '.join(petugas_bidan)}; {petugas_dokter}"})
        
        # 6. KLASTER ANAK
        available_bidan = [b for b in semua_bidan if b not in used_today]
        available_dokter = [d for d in semua_dokter if d not in used_today]
        petugas_bidan = random.sample(available_bidan, 2) if len(available_bidan) >= 2 else available_bidan
        used_today.update(petugas_bidan)
        petugas_dokter = random.choice(available_dokter) if available_dokter else "Tidak tersedia"
        if petugas_dokter != "Tidak tersedia":
            used_today.add(petugas_dokter)
        jadwal_hari.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'KLASTER ANAK', 'penyerta': f"{'; '.join(petugas_bidan)}; {petugas_dokter}"})
        
        # 7. R. IMUNISASI (hanya Kamis)
        if nama_hari == "Kamis":
            available_bidan = [b for b in semua_bidan if b not in used_today]
            petugas_imunisasi = random.sample(available_bidan, 2) if len(available_bidan) >= 2 else available_bidan
            used_today.update(petugas_imunisasi)
            jadwal_hari.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'R. IMUNISASI', 'penyerta': '; '.join(petugas_imunisasi)})
        
        # 8. R. TINDAKAN
        available_perawat = [p for p in semua_perawat_ners if p not in used_today]
        petugas_tindakan = random.choice(available_perawat) if available_perawat else "Tidak tersedia"
        if petugas_tindakan != "Tidak tersedia":
            used_today.add(petugas_tindakan)
        jadwal_hari.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'R. TINDAKAN', 'penyerta': petugas_tindakan})
        
        # 9. BP GIGI
        jadwal_hari.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'BP GIGI', 'penyerta': '; '.join(BP_GIGI_TETAP)})
        used_today.update(BP_GIGI_TETAP)
        
        # 10. APOTEK
        jadwal_hari.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'APOTEK', 'penyerta': '; '.join(APOTEK_TETAP)})
        used_today.update(APOTEK_TETAP)
        
        # 11. LAB
        jadwal_hari.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'LAB', 'penyerta': '; '.join(LAB_TETAP)})
        used_today.update(LAB_TETAP)
        
        # 12. R. TB (hanya Selasa)
        if nama_hari == "Selasa":
            available_perawat = [p for p in semua_perawat_ners if p not in used_today]
            petugas_tb = random.choice(available_perawat) if available_perawat else "Tidak tersedia"
            if petugas_tb != "Tidak tersedia":
                used_today.add(petugas_tb)
            jadwal_hari.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'R. TB', 'penyerta': petugas_tb})
        
        # 13. ADMINISTRASI
        admin_extra = random_pick_from_list(ADMINISTRASI_EXTRA, count=2)
        semua_admin = ADMINISTRASI_TETAP + admin_extra
        jadwal_hari.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'ADMINISTRASI', 'penyerta': '; '.join(semua_admin)})
        used_today.update(semua_admin)
        
        # 14. PUSTU CIANGIR
        jadwal_hari.append({'tanggal': tgl_str, 'lokasi': 'Pustu Ciangir', 'kegiatan': 'PELAYANAN PUSTU', 'penyerta': PUSTU_CIANGIR})
        used_today.add(PUSTU_CIANGIR)
        
        # 15. PUSTU SUMELAP
        jadwal_hari.append({'tanggal': tgl_str, 'lokasi': 'Pustu Sumelap', 'kegiatan': 'PELAYANAN PUSTU', 'penyerta': PUSTU_SUMELAP})
        used_today.add(PUSTU_SUMELAP)
        
        # 16. PIKET PERSALINAN (bidan yang belum dipakai)
        all_bidan = set(semua_bidan)
        used_bidan = used_today.intersection(all_bidan)
        available_bidan_piket = list(all_bidan - used_bidan)
        if available_bidan_piket:
            petugas_piket = random.choice(available_bidan_piket)
            jadwal_hari.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'PIKET PERSALINAN', 'penyerta': petugas_piket})
        
        jadwal_generated.extend(jadwal_hari)
    
    return jadwal_generated

if st.session_state.notif:
    st.toast(st.session_state.notif, icon="✅")
    st.session_state.notif = None

# ---------- Header ----------
st.markdown("""
<div class="main-header">
    <h1>Puskesmas Sangkali</h1>
    <p>Pelayanan Kesehatan Masyarakat</p>
</div>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    try:
        st.image("assets/logo.png", width=100)
    except:
        st.warning("Logo tidak ditemukan (assets/logo.png)")
    st.markdown('</div>', unsafe_allow_html=True)
    st.title("Menu")
    if st.button("Jadwal Kegiatan", use_container_width=True):
        st.session_state.page = "user"
        st.rerun()
    if not st.session_state.logged_in:
        if st.button("Login Admin", use_container_width=True):
            st.session_state.page = "admin_login"
            st.rerun()
    else:
        st.markdown(f"Login sebagai **{st.session_state.username}**")
        if st.button("Dashboard Admin", use_container_width=True):
            st.session_state.page = "admin_dashboard"
            st.rerun()
        if st.button("Logout", use_container_width=True):
            try:
                api_post("logout/", {}, auth=True)
            except:
                pass
            st.session_state.logged_in = False
            st.session_state.token = None
            st.session_state.username = ''
            st.session_state.page = "user"
            st.query_params.clear()
            st.rerun()
    st.markdown("---")
    try:
        r = requests.get(f"{API_BASE}/jadwal-terdekat/", timeout=3)
        if r.status_code == 200:
            st.html('<span class="badge-online">&#9679; Server Online</span>')
        else:
            st.html('<span class="badge-offline">&#9679; Server Error</span>')
    except:
        st.html('<span class="badge-offline">&#9679; Server Offline</span>')

# ========================== HALAMAN USER ==========================
if st.session_state.page == "user":
    try:
        today = date.today()
        tomorrow = today + timedelta(days=1)
        resp_notif = requests.get(f"{API_BASE}/jadwal-terdekat/", timeout=3)
        if resp_notif.status_code == 200:
            jadwal = resp_notif.json()
            notif_hari_ini = [j for j in jadwal if j['tanggal'] == str(today)]
            notif_besok = [j for j in jadwal if j['tanggal'] == str(tomorrow)]
            if notif_hari_ini:
                items = ''.join(f"<li>{j['kegiatan']} di {j['lokasi']}</li>" for j in notif_hari_ini)
                st.markdown(f"<div class='notification-card'><i class='fa-solid fa-circle-exclamation'></i><b>Hari ini ada kegiatan:</b><ul>{items}</ul></div>", unsafe_allow_html=True)
            if notif_besok:
                items = ''.join(f"<li>{j['kegiatan']} di {j['lokasi']}</li>" for j in notif_besok)
                st.markdown(f"<div class='notification-card' style='background:#eff6ff; border-color:#bfdbfe;'><i class='fa-solid fa-calendar-check'></i><b>Besok (H-1):</b><ul>{items}</ul></div>", unsafe_allow_html=True)
    except:
        pass

    st.markdown("""
    <div class="icon-text" style="margin-bottom:0.5rem">
      <svg class="svg-icon" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#14532d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
      </svg>
      <span style="font-size:1.5rem; font-weight:600;">Cari Jadwal Kegiatan</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        with st.form("user_form"):
            nama = st.selectbox("Nama Lengkap", DAFTAR_NAMA)
            tanggal = st.date_input("Tanggal Kegiatan", datetime.now().date())
            if st.form_submit_button("Cari Jadwal"):
                try:
                    resp = api_get("search-user/", params={"nama": nama, "tanggal": str(tanggal)})
                    if resp.status_code == 200:
                        hasil = resp.json()
                        if hasil:
                            st.success(f"Halo {nama}")
                            for h in hasil:
                                peny_list = parse_penyerta(h['penyerta'])
                                peny_items = ''.join(f"<li>{p}</li>" for p in peny_list)
                                st.markdown(f"""
                                <div class="result-box">
                                    <b>Lokasi:</b> {h['lokasi']}<br>
                                    <b>Kegiatan:</b> {h['kegiatan']}<br>
                                    <b>Penyerta:</b><ul>{peny_items}</ul>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.warning(f"Tidak ada kegiatan untuk {nama} pada tanggal {tanggal}.")
                    else:
                        st.error("Gagal menghubungi server")
                except Exception as e:
                    st.error(f"Error: {e}")

    with col2:
        st.markdown("""
        <div class="data-card">
            <div class="icon-text">
              <svg class="svg-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#14532d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>
              </svg>
              <span style="font-weight:600;">Informasi</span>
            </div>
            <ul><li>Datang 15 menit lebih awal</li><li>Bawa KMS/BPJS</li><li>Gunakan masker</li></ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="icon-text" style="margin-top:1.5rem; margin-bottom:0.5rem">
      <svg class="svg-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#14532d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/>
        <line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
      </svg>
      <span style="font-size:1.3rem; font-weight:600;">Jadwal Terdekat</span>
    </div>
    """, unsafe_allow_html=True)

    try:
        resp_jadwal = api_get("jadwal-terdekat/")
        if resp_jadwal.status_code == 200:
            jadwal = resp_jadwal.json()
            if jadwal:
                df = pd.DataFrame(jadwal)
                df.columns = ['Tanggal', 'Lokasi', 'Kegiatan', 'Penyerta']
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Belum ada jadwal")
    except:
        st.warning("Tidak dapat memuat jadwal")

# ========================== LOGIN ADMIN ==========================
elif st.session_state.page == "admin_login":
    col_c, col_m, col_c2 = st.columns([1, 2, 1])
    with col_m:
        st.markdown("""
        <div style="text-align:center; margin-bottom:0.5rem;">
          <svg width="48" height="48" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
            <rect x="15" y="38" width="50" height="34" rx="8" fill="#14532d"/>
            <path d="M 28 38 Q 28 18 40 18 Q 52 18 52 38"
                  fill="none" stroke="#14532d" stroke-width="7" stroke-linecap="round"/>
            <circle cx="40" cy="53" r="7" fill="#dcfce7"/>
            <rect x="37" y="53" width="6" height="10" rx="3" fill="#dcfce7"/>
          </svg>
          <h2 style="margin-top:0.2rem; color:#14532d;">Login Admin</h2>
        </div>
        """, unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                if not username or not password:
                    st.error("Username dan password wajib diisi.")
                else:
                    try:
                        resp = api_post("login/", {"username": username, "password": password})
                        if resp.status_code == 200:
                            data = resp.json()
                            st.session_state.logged_in = True
                            st.session_state.token = data['token']
                            st.session_state.username = data.get('username', username)
                            st.session_state.page = "admin_dashboard"
                            st.query_params["token"] = data['token']
                            st.rerun()
                        elif resp.status_code == 429:
                            st.error("Terlalu banyak percobaan login.")
                        else:
                            st.error(resp.json().get('error', 'Login gagal'))
                    except Exception as e:
                        st.error(f"Koneksi error: {e}")
        st.caption("Kembali ke halaman utama: klik 'Jadwal Kegiatan' di sidebar.")

# ========================== DASHBOARD ADMIN ==========================
elif st.session_state.page == "admin_dashboard":
    if not st.session_state.logged_in or not st.session_state.token:
        st.warning("Anda harus login terlebih dahulu.")
        st.session_state.page = "admin_login"
        st.rerun()

    st.markdown("""
    <div class="icon-text" style="margin-bottom:0.5rem">
      <svg class="svg-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#14532d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
        <rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>
      </svg>
      <span style="font-size:1.5rem; font-weight:600;">Dashboard Admin</span>
    </div>
    """, unsafe_allow_html=True)
    st.success(f"Selamat datang, {st.session_state.username}")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Input Manual", "Google Sheet", "Pencarian", "Kelola Data",
        "History", "Randomize (Dalam Gedung)"
    ])

    # ── Tab 1: Input Manual ──
    with tab1:
        with st.form("input_form"):
            col1, col2 = st.columns(2)
            with col1:
                tgl = st.date_input("Tanggal")
                lokasi = st.text_input("Lokasi")
            with col2:
                kegiatan = st.text_input("Nama Kegiatan")
                penyerta_terpilih = st.multiselect(
                    "Pilih Penyerta (bisa lebih dari satu)",
                    options=DAFTAR_NAMA,
                    placeholder="Ketik nama atau pilih dari daftar"
                )
                if not penyerta_terpilih:
                    penyerta = st.text_area("Atau tulis manual (pisahkan dengan ;)", height=80)
                else:
                    penyerta = "; ".join(penyerta_terpilih)
                    st.caption(f"Penyerta: {penyerta}")
            if st.form_submit_button("Simpan"):
                if not lokasi or not kegiatan:
                    st.error("Lokasi dan Nama Kegiatan wajib diisi.")
                else:
                    try:
                        resp = api_post("kegiatan/", {"tanggal": str(tgl), "lokasi": lokasi, "kegiatan": kegiatan, "penyerta": penyerta}, auth=True)
                        if resp.status_code == 201:
                            st.session_state.notif = "Data berhasil disimpan!"
                            st.rerun()
                        else:
                            st.error(f"Gagal menyimpan: {resp.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")

    # ── Tab 2: Google Sheet ──
    with tab2:
        st.markdown('<h4><i class="fa-solid fa-cloud-arrow-up"></i> Sync dari Google Spreadsheet</h4>', unsafe_allow_html=True)
        st.caption("File > Share > Publish to web > CSV > Copy link")
        st.info("Kolom: `tanggal`, `lokasi`, `kegiatan`, `penyerta` (penyerta dipisah titik koma)")
        if st.session_state.last_csv_url:
            st.markdown(f"<p class='reduced-link'>Link tersimpan: {st.session_state.last_csv_url}</p>", unsafe_allow_html=True)
            col_upd, col_del = st.columns(2)
            with col_upd:
                if st.button("Update Link", use_container_width=True):
                    st.session_state.show_csv_input = True
            with col_del:
                if st.button("Hapus Link", use_container_width=True):
                    st.session_state.last_csv_url = ""
                    st.rerun()
            show_input = st.session_state.get('show_csv_input', False)
            if show_input:
                csv_url = st.text_input("Link CSV terpublikasi (baru)", key="csv_url_new")
                sync_mode = st.radio("Mode", ['append', 'replace'], horizontal=True, format_func=lambda x: "Tambahkan saja" if x=='append' else "Ganti semua")
                if st.button("Simpan & Sync"):
                    if csv_url:
                        with st.spinner("Sync..."):
                            resp = api_post("sync-sheets/", {"csv_url": csv_url, "mode": sync_mode}, auth=True)
                            if resp.status_code == 200:
                                st.session_state.last_csv_url = csv_url
                                st.session_state.show_csv_input = False
                                st.session_state.notif = "Data Google Sheet berhasil disinkronkan!"
                                st.rerun()
                            else:
                                st.error(resp.json().get('error'))
        else:
            csv_url = st.text_input("Link CSV terpublikasi", key="csv_url_blank")
            sync_mode = st.radio("Mode", ['append', 'replace'], horizontal=True, format_func=lambda x: "Tambahkan saja" if x=='append' else "Ganti semua")
            if st.button("Ambil & Simpan Data"):
                if csv_url:
                    with st.spinner("Sync..."):
                        resp = api_post("sync-sheets/", {"csv_url": csv_url, "mode": sync_mode}, auth=True)
                        if resp.status_code == 200:
                            st.session_state.last_csv_url = csv_url
                            st.session_state.notif = "Data Google Sheet berhasil disinkronkan!"
                            st.rerun()
                        else:
                            st.error(resp.json().get('error'))

          # ── Tab 3: Pencarian ──
    with tab3:
        try:
            resp_data = api_get("kegiatan/", auth=True)
            semua_data = resp_data.json() if resp_data.status_code == 200 else []
        except:
            semua_data = []
        lokasi_list = sorted(set(d['lokasi'] for d in semua_data if d.get('lokasi')))
        kegiatan_list = sorted(set(d['kegiatan'] for d in semua_data if d.get('kegiatan')))
        penyerta_set = set()
        for d in semua_data:
            for n in parse_penyerta(d.get('penyerta','')):
                if n: penyerta_set.add(n)
        penyerta_list = sorted(penyerta_set)

        st.markdown('<h4><i class="fa-solid fa-filter"></i> Filter Pencarian</h4>', unsafe_allow_html=True)
        with st.form("search_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                tgl_src = st.date_input("Tanggal", value=None, key="src_tgl")
            with col2:
                lok_options = ["Semua"] + lokasi_list + ["Cari manual..."]
                lok_dd = st.selectbox("Lokasi", lok_options)
                lok_src = ""
                if lok_dd == "Cari manual...":
                    lok_src = st.text_input("Ketik lokasi")
                elif lok_dd != "Semua":
                    lok_src = lok_dd
            with col3:
                keg_options = ["Semua"] + kegiatan_list + ["Cari manual..."]
                keg_dd = st.selectbox("Nama Kegiatan", keg_options)
                keg_src = ""
                if keg_dd == "Cari manual...":
                    keg_src = st.text_input("Ketik kegiatan")
                elif keg_dd != "Semua":
                    keg_src = keg_dd
            peny_options = ["Semua"] + penyerta_list + ["Cari manual..."]
            peny_dd = st.selectbox("Penyerta", peny_options)
            peny_src = ""
            if peny_dd == "Cari manual...":
                peny_src = st.text_input("Ketik penyerta")
            elif peny_dd != "Semua":
                peny_src = peny_dd

            if st.form_submit_button("Cari"):
                params = {}
                if tgl_src: params["tanggal"] = str(tgl_src)
                if lok_src: params["lokasi"] = lok_src
                if keg_src: params["kegiatan"] = keg_src
                if peny_src: params["penyerta"] = peny_src
                if not params:
                    st.warning("Isi minimal satu filter.")
                else:
                    try:
                        resp = api_get("search-admin/", params=params, auth=True)
                        if resp.status_code == 200:
                            hasil = resp.json()
                            if hasil:
                                groups = defaultdict(list)
                                for item in hasil:
                                    key = (item['tanggal'], item['lokasi'], item['kegiatan'])
                                    groups[key].append(item['penyerta'])
                                st.success(f"Ditemukan {len(groups)} grup data")
                                for (tanggal, lokasi, kegiatan), list_penyerta in groups.items():
                                    all_names = []
                                    for p_text in list_penyerta:
                                        all_names.extend(parse_penyerta(p_text))
                                    penyerta_gabung = '<br>'.join(all_names)
                                    st.markdown(f"""
                                    <div class="result-box">
                                        <b>{tanggal}</b> - {lokasi}<br>
                                        {kegiatan}<br>
                                        <small>{penyerta_gabung}</small>
                                    </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.info("Tidak ditemukan")
                        else:
                            st.error("Gagal mengambil data")
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        # ========== CEK KARYAWAN TIDAK TERJADWAL ==========
        st.markdown("---")
        st.markdown('<h4><i class="fa-solid fa-user-plus"></i> Cek Karyawan yang Tidak Terjadwal (Untuk Jadwal Luar Gedung)</h4>', unsafe_allow_html=True)
        st.caption("Lihat karyawan yang tidak memiliki jadwal dalam gedung pada tanggal tertentu, untuk dialokasikan ke jadwal luar gedung via SPS.")
        
        col_cek1, col_cek2, col_cek3 = st.columns([2, 2, 1])
        with col_cek1:
            tgl_cek = st.date_input("📅 Pilih Tanggal", datetime.now().date(), key="tgl_cek_karyawan")
        with col_cek2:
            # Filter role (opsional)
            role_filter = st.multiselect("Filter Role (opsional, kosongkan untuk semua)", 
                                         ["Dokter", "Perawat", "Bidan", "Promkes", "Sanitarian", "Gizi", "Apoteker", "Lab", "Gigi", "Administrasi"],
                                         default=[])
        with col_cek3:
            st.write("")
            if st.button("🔍 Cek Karyawan Tidak Terjadwal", use_container_width=True, type="primary"):
                tgl_str = str(tgl_cek)
                
                # Nama yang dikecualikan (tidak masuk jadwal manapun)
                NAMA_DIECUALIKAN = [
                    "Isep Deni Herdian, S.Kep.,MMRS",
                    "Isep Suhendar,SKM"
                ]
                
                # Fungsi get karyawan by role
                def get_karyawan_by_role_local(role_keywords):
                    role_map = {
                        'dokter': ['dr.', 'drg.'],
                        'perawat_ners': ['Ners', 'S.Kep', 'Amd.Kep', 'A.Md.Kep'],
                        'bidan': ['Bdn.', 'S.Tr.Keb', 'Am.Keb', 'A.Md.Keb'],
                        'promkes': ['Promosi', 'SKM'],
                        'sanitarian': ['Sanitarian', 'S.K.M', 'A.Md.KL'],
                        'gizi': ['S.Gz', 'A.Md.Gz'],
                        'apoteker': ['Apt', 'S.Farm'],
                        'lab': ['A.Md.AK'],
                        'gigi': ['drg.', 'S.Tr.Kes'],
                        'administrasi': ['S.E', 'S.T', 'S.Kep', 'S.ST', 'SKM', 'AMd.RMIK']
                    }
                    keywords = role_map.get(role_keywords, [])
                    hasil = []
                    for nama in DAFTAR_NAMA:
                        for kw in keywords:
                            if kw.lower() in nama.lower():
                                if nama not in NAMA_DIECUALIKAN:
                                    hasil.append(nama)
                                break
                    return list(set(hasil))
                
                # Ambil semua karyawan berdasarkan role yang difilter
                semua_karyawan = []
                if "Dokter" in role_filter or not role_filter:
                    semua_karyawan.extend(get_karyawan_by_role_local('dokter'))
                if "Perawat" in role_filter or not role_filter:
                    semua_karyawan.extend(get_karyawan_by_role_local('perawat_ners'))
                if "Bidan" in role_filter or not role_filter:
                    semua_karyawan.extend(get_karyawan_by_role_local('bidan'))
                if "Promkes" in role_filter or not role_filter:
                    semua_karyawan.extend(get_karyawan_by_role_local('promkes'))
                if "Sanitarian" in role_filter or not role_filter:
                    semua_karyawan.extend(get_karyawan_by_role_local('sanitarian'))
                if "Gizi" in role_filter or not role_filter:
                    semua_karyawan.extend(get_karyawan_by_role_local('gizi'))
                if "Apoteker" in role_filter or not role_filter:
                    semua_karyawan.extend(get_karyawan_by_role_local('apoteker'))
                if "Lab" in role_filter or not role_filter:
                    semua_karyawan.extend(get_karyawan_by_role_local('lab'))
                if "Gigi" in role_filter or not role_filter:
                    semua_karyawan.extend(get_karyawan_by_role_local('gigi'))
                if "Administrasi" in role_filter or not role_filter:
                    semua_karyawan.extend(get_karyawan_by_role_local('administrasi'))
                
                # Hapus duplikat
                semua_karyawan = list(set(semua_karyawan))
                
                if not semua_karyawan:
                    st.warning("Tidak ada karyawan dengan filter role yang dipilih")
                else:
                    # Ambil semua jadwal pada tanggal tersebut
                    try:
                        resp_jadwal = api_get("kegiatan/", auth=True)
                        if resp_jadwal.status_code == 200:
                            data_jadwal = resp_jadwal.json()
                            jadwal_tanggal = [j for j in data_jadwal if j['tanggal'] == tgl_str]
                            
                            # Ambil semua nama yang sudah terjadwal di tanggal itu
                            karyawan_terjadwal = set()
                            for j in jadwal_tanggal:
                                penyerta_list = parse_penyerta(j['penyerta'])
                                karyawan_terjadwal.update(penyerta_list)
                            
                            # Cari karyawan yang tidak terjadwal
                            karyawan_tidak_terjadwal = [k for k in semua_karyawan if k not in karyawan_terjadwal]
                            
                            # Tampilkan hasil
                            if karyawan_tidak_terjadwal:
                                st.warning(f"📊 **Total karyawan yang TIDAK terjadwal pada {tgl_str}: {len(karyawan_tidak_terjadwal)} orang**")
                                st.info("💡 Karyawan ini bisa dialokasikan ke **JADWAL LUAR GEDUNG** (input manual via SPS)")
                                
                                # Tampilkan dalam bentuk DATAFRAME (rapi!)
                                st.subheader("📋 Daftar Karyawan Tidak Terjadwal")
                                
                                # Urutkan nama
                                karyawan_sorted = sorted(karyawan_tidak_terjadwal)
                                
                                # Buat dataframe
                                df_tidak_terjadwal = pd.DataFrame({
                                    "No": range(1, len(karyawan_sorted) + 1),
                                    "Nama Karyawan": karyawan_sorted
                                })
                                st.dataframe(df_tidak_terjadwal, use_container_width=True, hide_index=True)
                                
                                # Tombol download CSV
                                csv_data = df_tidak_terjadwal.to_csv(index=False)
                                st.download_button(
                                    label="📥 Download Daftar (CSV)",
                                    data=csv_data,
                                    file_name=f"karyawan_tidak_terjadwal_{tgl_str}.csv",
                                    mime="text/csv"
                                )
                                
                                # Juga tampilkan dalam bentuk teks polos (untuk copy)
                                with st.expander("📄 Lihat sebagai teks (bisa dicopy)"):
                                    daftar_nama = '\n'.join([f"{i+1}. {nama}" for i, nama in enumerate(karyawan_sorted)])
                                    st.code(daftar_nama, language="text")
                                    
                            else:
                                st.success(f"✅ Semua karyawan ({len(semua_karyawan)} orang) sudah memiliki jadwal dalam gedung pada tanggal {tgl_str}!")
                        else:
                            st.error("Gagal mengambil data jadwal")
                    except Exception as e:
                        st.error(f"Error: {e}")

    # ── Tab 4: Kelola Data ──
    with tab4:
        st.subheader("Daftar Semua Kegiatan")
        try:
            resp = api_get("kegiatan/", auth=True)
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    df_raw = pd.DataFrame(data)
                    df_grouped = (
                        df_raw.groupby(['tanggal', 'lokasi', 'kegiatan'], sort=False)
                        .agg(
                            penyerta=('penyerta', lambda x: ';\n'.join(x.tolist())),
                            ids=('id', list)
                        )
                        .reset_index()
                    )
                    df_grouped.columns = ['Tanggal', 'Lokasi', 'Kegiatan', 'Penyerta', 'IDs']

                    if st.session_state.pending_delete_ids:
                        flat_ids = []
                        for id_list in st.session_state.pending_delete_ids:
                            flat_ids.extend(id_list)
                        if flat_ids:
                            with st.spinner("Menghapus..."):
                                resp_del = api_post("kegiatan/bulk-delete/", {"ids": flat_ids}, auth=True)
                                if resp_del.status_code == 200:
                                    st.session_state.notif = resp_del.json().get('message')
                                    st.session_state.pending_delete_ids = []
                                    st.rerun()
                                else:
                                    st.error("Gagal menghapus")
                                    st.session_state.pending_delete_ids = []

                    event = st.dataframe(
                        df_grouped[['Tanggal', 'Lokasi', 'Kegiatan', 'Penyerta']],
                        use_container_width=True,
                        hide_index=True,
                        on_select="rerun",
                        selection_mode="multi-row",
                        key="kelola_data"
                    )
                    selected_rows = event.selection.rows if event.selection else []
                    valid_rows = [i for i in selected_rows if 0 <= i < len(df_grouped)]
                    if valid_rows:
                        selected_ids = [df_grouped.iloc[i]['IDs'] for i in valid_rows]
                        st.markdown(f"**{len(selected_ids)} grup data terpilih**")
                        st.markdown('<div class="center-red-btn">', unsafe_allow_html=True)
                        if st.button("🗑️ Hapus Data Terpilih", use_container_width=False):
                            st.session_state.pending_delete_ids = selected_ids
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)

                    st.markdown("---")
                    st.markdown('<h4><i class="fa-solid fa-pen-to-square"></i> Edit Data</h4>', unsafe_allow_html=True)
                    opsi_edit = ["—"] + [f"{row['Tanggal']} | {row['Lokasi']} | {row['Kegiatan']}" for _, row in df_grouped.iterrows()]
                    pilihan = st.selectbox("Pilih kegiatan", opsi_edit)
                    if pilihan != "—":
                        tgl_pilih, lok_pilih, keg_pilih = pilihan.split(" | ")
                        matched = df_grouped[(df_grouped['Tanggal'] == tgl_pilih) & (df_grouped['Lokasi'] == lok_pilih) & (df_grouped['Kegiatan'] == keg_pilih)]
                        if not matched.empty:
                            edit_id = matched.iloc[0]['IDs'][0]
                            if st.button("Muat Data"):
                                resp_det = api_get(f"kegiatan/{edit_id}/", auth=True)
                                if resp_det.status_code == 200:
                                    st.session_state.edit_data = resp_det.json()
                                else:
                                    st.error("ID tidak ditemukan")
                    if st.session_state.edit_data:
                        with st.form("edit_form"):
                            tgl_ed = st.date_input("Tanggal", value=pd.to_datetime(st.session_state.edit_data['tanggal']))
                            lok_ed = st.text_input("Lokasi", value=st.session_state.edit_data['lokasi'])
                            keg_ed = st.text_input("Nama Kegiatan", value=st.session_state.edit_data['kegiatan'])
                            peny_ed = st.text_area("Penyerta", value=st.session_state.edit_data['penyerta'])
                            if st.form_submit_button("Update"):
                                resp_upd = api_put(f"kegiatan/{edit_id}/", {"tanggal": str(tgl_ed), "lokasi": lok_ed, "kegiatan": keg_ed, "penyerta": peny_ed})
                                if resp_upd.status_code == 200:
                                    st.session_state.notif = "Data diperbarui!"
                                    st.session_state.edit_data = None
                                    st.rerun()
                                else:
                                    st.error(resp_upd.text)

                    st.markdown("---")
                    st.markdown('<h4><i class="fa-solid fa-calendar-xmark"></i> Hapus per Bulan/Tahun</h4>', unsafe_allow_html=True)
                    col_m, col_y, col_btn = st.columns([2,2,1])
                    with col_m:
                        bulan = st.selectbox("Bulan", range(1,13), index=datetime.now().month-1)
                    with col_y:
                        tahun = st.number_input("Tahun", value=datetime.now().year)
                    with col_btn:
                        st.write("")
                        if st.button("Hapus"):
                            resp_del = api_post("delete-by-date/", {"month": bulan, "year": tahun}, auth=True)
                            if resp_del.status_code == 200:
                                st.session_state.notif = resp_del.json()['message']
                                st.rerun()
                            else:
                                st.error("Gagal")
                else:
                    st.info("Belum ada data")
            else:
                st.error("Gagal memuat data")
        except Exception as e:
            st.error(f"Error: {e}")

       # ── Tab 5: History ──
    with tab5:
        st.subheader("📜 History Kegiatan")
        st.caption("Lihat riwayat kegiatan yang sudah lewat dan yang akan datang")
        
        # Tombol filter
        col_filter1, col_filter2, col_filter3 = st.columns([2, 2, 1])
        with col_filter1:
            filter_status = st.selectbox("Filter Status", ["Semua", "Sudah Lewat", "Hari Ini", "Akan Datang"])
        with col_filter2:
            filter_bulan_history = st.selectbox("Filter Bulan", 
                                               ["Semua", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
                                                "Juli", "Agustus", "September", "Oktober", "November", "Desember"])
        with col_filter3:
            st.write("")
            if st.button("🔄 Refresh", use_container_width=True):
                st.rerun()
        
        try:
            resp = api_get("kegiatan/", auth=True)
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    today = date.today()
                    df = pd.DataFrame(data)
                    df['tanggal_date'] = pd.to_datetime(df['tanggal']).dt.date
                    df = df.sort_values('tanggal_date', ascending=False)
                    
                    # Terapkan filter
                    if filter_status == "Sudah Lewat":
                        df = df[df['tanggal_date'] < today]
                    elif filter_status == "Hari Ini":
                        df = df[df['tanggal_date'] == today]
                    elif filter_status == "Akan Datang":
                        df = df[df['tanggal_date'] > today]
                    
                    if filter_bulan_history != "Semua":
                        bulan_num = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
                                    "Juli", "Agustus", "September", "Oktober", "November", "Desember"].index(filter_bulan_history) + 1
                        df = df[pd.to_datetime(df['tanggal']).dt.month == bulan_num]
                    
                    if df.empty:
                        st.info("Tidak ada data sesuai filter")
                    else:
                        st.write(f"📊 **Total: {len(df)} kegiatan**")
                        
                        # Tampilkan data dalam bentuk tabel dengan checkbox untuk hapus
                        st.markdown("---")
                        
                        # Pilih multiple kegiatan untuk dihapus
                        kegiatan_options = []
                        for _, row in df.iterrows():
                            tgl_date = row['tanggal_date']
                            if tgl_date < today:
                                status_icon = "📅 (Sudah Lewat)"
                            elif tgl_date == today:
                                status_icon = "🔴 (HARI INI)"
                            else:
                                status_icon = "🟢 (Akan Datang)"
                            kegiatan_options.append(f"{row['tanggal']} | {row['lokasi']} | {row['kegiatan']} | {row['id']} | {status_icon}")
                        
                        selected_items = st.multiselect("Pilih kegiatan yang ingin dihapus", kegiatan_options)
                        
                        col_hapus1, col_hapus2, col_hapus3 = st.columns([1, 2, 1])
                        with col_hapus2:
                            if selected_items and st.button("🗑️ Hapus Terpilih", type="secondary", use_container_width=True):
                                ids_to_delete = []
                                for item in selected_items:
                                    # Extract ID dari string (format: ... | {id} | ...)
                                    parts = item.split(" | ")
                                    if len(parts) >= 4:
                                        try:
                                            id_kegiatan = int(parts[3])
                                            ids_to_delete.append(id_kegiatan)
                                        except:
                                            pass
                                
                                if ids_to_delete:
                                    with st.spinner(f"Menghapus {len(ids_to_delete)} kegiatan..."):
                                        resp_del = api_post("kegiatan/bulk-delete/", {"ids": ids_to_delete}, auth=True)
                                        if resp_del.status_code == 200:
                                            st.session_state.notif = f"✅ Berhasil menghapus {len(ids_to_delete)} kegiatan!"
                                            st.rerun()
                                        else:
                                            st.error("Gagal menghapus data")
                                else:
                                    st.warning("Tidak ada ID yang valid")
                        
                        # Tampilkan data dalam card
                        st.markdown("---")
                        st.subheader("📋 Daftar Kegiatan")
                        
                        for _, row in df.iterrows():
                            tgl_date = row['tanggal_date']
                            if tgl_date < today:
                                cls = "past"
                                status_text = "✅ Sudah Lewat"
                            elif tgl_date == today:
                                cls = "today"
                                status_text = "🔴 HARI INI"
                            elif tgl_date == today + timedelta(days=1):
                                cls = "tomorrow"
                                status_text = "⏰ Besok"
                            else:
                                cls = "future"
                                status_text = "📅 Akan Datang"
                            
                            hari = tgl_date.strftime('%A, %d %B %Y')
                            st.markdown(f"""
                            <div class="result-box {cls}" style="position: relative;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div>
                                        <b>{hari}</b> <span style="font-size: 0.8rem;">({status_text})</span><br>
                                        <b>Lokasi:</b> {row['lokasi']}<br>
                                        <b>Kegiatan:</b> {row['kegiatan']}<br>
                                        <small><b>Penyerta:</b> {row['penyerta']}</small>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("Belum ada data kegiatan")
            else:
                st.error("Gagal memuat data")
        except Exception as e:
            st.error(f"Error: {e}")
        
        # Tombol hapus semua history (khusus yang sudah lewat)
        st.markdown("---")
        st.subheader("🗑️ Hapus Massal")
        
        col_massal1, col_massal2, col_massal3 = st.columns([1, 2, 1])
        with col_massal2:
            if st.button("⚠️ Hapus Semua Kegiatan yang Sudah Lewat", type="secondary", use_container_width=True):
                st.warning("⚠️ Yakin ingin menghapus SEMUA kegiatan yang sudah lewat?")
                
                col_confirm1, col_confirm2, col_confirm3 = st.columns([1, 1, 1])
                with col_confirm1:
                    if st.button("✅ Ya, Hapus", use_container_width=True):
                        try:
                            resp = api_get("kegiatan/", auth=True)
                            if resp.status_code == 200:
                                data = resp.json()
                                today = date.today()
                                ids_to_delete = []
                                for item in data:
                                    tgl_kegiatan = datetime.strptime(item['tanggal'], '%Y-%m-%d').date()
                                    if tgl_kegiatan < today:
                                        ids_to_delete.append(item['id'])
                                
                                if ids_to_delete:
                                    resp_del = api_post("kegiatan/bulk-delete/", {"ids": ids_to_delete}, auth=True)
                                    if resp_del.status_code == 200:
                                        st.session_state.notif = f"✅ Berhasil menghapus {len(ids_to_delete)} kegiatan yang sudah lewat!"
                                        st.rerun()
                                    else:
                                        st.error("Gagal menghapus")
                                else:
                                    st.info("Tidak ada kegiatan yang sudah lewat")
                        except Exception as e:
                            st.error(f"Error: {e}")
                with col_confirm2:
                    if st.button("❌ Batal", use_container_width=True):
                        st.rerun()

        # ── Tab 6: Randomize (Dalam Gedung) ──
    with tab6:
        st.subheader("🎲 Randomize Jadwal Bulanan (Dalam Gedung)")
        st.caption("Generate jadwal otomatis untuk hari kerja Senin-Sabtu")
        st.warning("⚠️ Pastikan data PIKET PERSALINAN sudah diinput via SPS terlebih dahulu. Jika ada PIKET PERSALINAN MALAM pada suatu hari, maka esok harinya tidak akan digenerate jadwal dalam gedung.")
        
        # Nama yang TIDAK boleh dimasukkan ke jadwal manapun
        NAMA_DIECUALIKAN = [
            "Isep Deni Herdian, S.Kep.,MMRS",
            "Isep Suhendar,SKM"
        ]
        
        col_bulan, col_tahun, col_gen = st.columns([2, 2, 1])
        with col_bulan:
            bulan_pilih = st.selectbox("Bulan", range(1, 13), index=datetime.now().month-1,
                                       format_func=lambda x: ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
                                                              "Juli", "Agustus", "September", "Oktober", "November", "Desember"][x-1])
        with col_tahun:
            tahun_pilih = st.number_input("Tahun", value=datetime.now().year, min_value=2020, max_value=2030)
        with col_gen:
            st.write("")
            minggu_pilih = st.selectbox("Minggu ke-", [1, 2, 3, 4, 5], index=0)
            if st.button("🎲 Generate Jadwal", use_container_width=True, type="primary"):
                with st.spinner(f"Menggenerate jadwal untuk minggu ke-{minggu_pilih}..."):
                    import calendar
                    import random
                    from datetime import timedelta
                    
                    # Filter nama yang dikecualikan
                    def filter_nama(nama_list):
                        return [n for n in nama_list if n not in NAMA_DIECUALIKAN]
                    
                    def get_by_role(keywords):
                        semua = [n for n in DAFTAR_NAMA if any(kw.lower() in n.lower() for kw in keywords)]
                        return filter_nama(semua)
                    
                    # Fungsi untuk cek jadwal piket malam dari database
                    def cek_piket_malam(tanggal):
                        """Cek apakah ada jadwal PIKET PERSALINAN MALAM pada tanggal tersebut"""
                        try:
                            resp = api_get("kegiatan/", auth=True)
                            if resp.status_code == 200:
                                data = resp.json()
                                for item in data:
                                    if item['tanggal'] == tanggal and item['kegiatan'] == 'PIKET PERSALINAN MALAM':
                                        return True
                        except:
                            pass
                        return False
                    
                    # Semua karyawan berdasarkan role (2 nama sudah dikecualikan)
                    semua_dokter = get_by_role(['dr.', 'drg.'])
                    semua_perawat = get_by_role(['Ners', 'S.Kep', 'Amd.Kep', 'A.Md.Kep'])
                    semua_bidan = get_by_role(['Bdn.', 'S.Tr.Keb', 'Am.Keb', 'A.Md.Keb'])
                    semua_promkes = get_by_role(['Promosi', 'SKM'])
                    semua_sanitarian = get_by_role(['Sanitarian', 'S.K.M', 'A.Md.KL'])
                    semua_gizi = get_by_role(['S.Gz', 'A.Md.Gz'])
                    
                    # Pool untuk ILP dan Prolanis
                    pool_ilp = list(set(semua_perawat + semua_bidan + semua_promkes + semua_sanitarian + semua_gizi))
                    
                    # Karyawan tetap (sudah difilter)
                    tetap_pendaftaran = filter_nama(["Winda Siti Sarah, AMd.RMIK", "Pupung Juliana", "Salsa Sabila"])
                    tetap_bpgigi = filter_nama(["drg.Rifan Hanggoro.M.M.R.S", "Endah Setiawati,S.Tr.Kes"])
                    tetap_apotek = filter_nama(["Khilman Husna Pratama, S.Farm.,Apt", "Nova Silpiany Perdany, A.Md.Farm"])
                    tetap_lab = filter_nama(["Vita Tyana Virista, A.Md.AK", "Gina Giovany, A.Md.AK"])
                    tetap_ciangir = "Haeriah, A.Md.Kep"
                    tetap_sumelap = "Ujang Effendi, S.Kep.,Ners"
                    tetap_admin = filter_nama(["Rangga Ismardana Gasbela,S.T", "Yogi Aris Diyanto, S.E"])
                    extra_admin = filter_nama(["Liska Permatasari, S.Kep.,Ners", "Alitsa Nuur Fithri, S.ST", "Andina Dea Priatna, SKM"])
                    
                    # Tracking penggunaan karyawan per MINGGU
                    used_this_week = set()
                    usage_count = {nama: 0 for nama in pool_ilp + semua_dokter + semua_perawat + semua_bidan}
                    
                    def random_pick_with_fairness(lst, count=1, exclude=None):
                        """Pilih karyawan dengan prioritas yang jarang dipakai"""
                        exclude = exclude or set()
                        available = [x for x in lst if x not in exclude and x not in used_this_week]
                        if not available:
                            available = [x for x in lst if x not in exclude]
                        if not available or len(available) < count:
                            return []
                        available.sort(key=lambda x: usage_count.get(x, 0))
                        return random.sample(available[:min(count*3, len(available))], min(count, len(available)))
                    
                    # Dapatkan minggu tertentu dari bulan
                    cal = calendar.monthcalendar(tahun_pilih, bulan_pilih)
                    minggu_index = minggu_pilih - 1
                    if minggu_index >= len(cal):
                        st.error(f"Bulan ini hanya memiliki {len(cal)} minggu")
                        st.stop()
                    
                    week = cal[minggu_index]
                    work_days = []
                    for day_idx, day in enumerate(week):
                        if day != 0 and day_idx < 6:
                            work_days.append(day)
                    
                    if not work_days:
                        st.warning(f"Minggu ke-{minggu_pilih} tidak memiliki hari kerja")
                        st.stop()
                    
                    hari_names = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu"]
                    jadwal_baru = []
                    
                    # Reset penggunaan untuk minggu ini
                    used_this_week = set()
                    skipped_days = []
                    
                    for tgl in work_days:
                        tgl_str = f"{tahun_pilih}-{bulan_pilih:02d}-{tgl:02d}"
                        tgl_obj = datetime(tahun_pilih, bulan_pilih, tgl)
                        nama_hari = hari_names[tgl_obj.weekday()]
                        
                        # CEK BENTROK: Jika H-1 ada piket malam, SKIP hari ini
                        tgl_sebelum = (tgl_obj - timedelta(days=1)).strftime('%Y-%m-%d')
                        if cek_piket_malam(tgl_sebelum):
                            skipped_days.append(tgl_str)
                            continue
                        
                        used_today = set()
                        
                        # PENDAFTARAN
                        if tetap_pendaftaran:
                            jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'PENDAFTARAN', 'penyerta': '; '.join(tetap_pendaftaran)})
                            used_today.update(tetap_pendaftaran)
                        
                        # SKRINING ILP 1 & 2
                        for i in range(1, 3):
                            p = random_pick_with_fairness(pool_ilp, 1, used_today)
                            if p:
                                used_today.add(p[0])
                                used_this_week.add(p[0])
                                usage_count[p[0]] = usage_count.get(p[0], 0) + 1
                                jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': f'SKRINING ILP {i}', 'penyerta': p[0]})
                        
                        # POLI PROLANIS (3 orang)
                        p = random_pick_with_fairness(pool_ilp, 3, used_today)
                        if len(p) >= 3:
                            used_today.update(p)
                            used_this_week.update(p)
                            for nama in p:
                                usage_count[nama] = usage_count.get(nama, 0) + 1
                            jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'POLI PROLANIS', 'penyerta': '; '.join(p)})
                        
                        # KLASTER DEWASA-LANSIA 1 & 2
                        for i in range(1, 3):
                            dok = random_pick_with_fairness(semua_dokter, 1, used_today)
                            if dok:
                                used_today.add(dok[0])
                                used_this_week.add(dok[0])
                                usage_count[dok[0]] = usage_count.get(dok[0], 0) + 1
                                jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': f'KLASTER DEWASA-LANSIA {i}', 'penyerta': dok[0]})
                            else:
                                per = random_pick_with_fairness(semua_perawat, 1, used_today)
                                if per:
                                    used_today.add(per[0])
                                    used_this_week.add(per[0])
                                    usage_count[per[0]] = usage_count.get(per[0], 0) + 1
                                    jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': f'KLASTER DEWASA-LANSIA {i}', 'penyerta': per[0]})
                        
                        # KLASTER IBU KIA & USG (2 bidan + 1 dokter)
                        b = random_pick_with_fairness(semua_bidan, 2, used_today)
                        d = random_pick_with_fairness(semua_dokter, 1, used_today)
                        used_today.update(b)
                        used_this_week.update(b)
                        for nama in b:
                            usage_count[nama] = usage_count.get(nama, 0) + 1
                        if d:
                            used_today.add(d[0])
                            used_this_week.add(d[0])
                            usage_count[d[0]] = usage_count.get(d[0], 0) + 1
                        jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'KLASTER IBU KIA & USG', 'penyerta': f"{'; '.join(b)}; {d[0] if d else 'Tidak ada'}"})
                        
                        # KLASTER ANAK (2 bidan + 1 dokter)
                        b = random_pick_with_fairness(semua_bidan, 2, used_today)
                        d = random_pick_with_fairness(semua_dokter, 1, used_today)
                        used_today.update(b)
                        used_this_week.update(b)
                        for nama in b:
                            usage_count[nama] = usage_count.get(nama, 0) + 1
                        if d:
                            used_today.add(d[0])
                            used_this_week.add(d[0])
                            usage_count[d[0]] = usage_count.get(d[0], 0) + 1
                        jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'KLASTER ANAK', 'penyerta': f"{'; '.join(b)}; {d[0] if d else 'Tidak ada'}"})
                        
                        # R. IMUNISASI (Kamis, 2 bidan)
                        if nama_hari == "Kamis":
                            b = random_pick_with_fairness(semua_bidan, 2, used_today)
                            used_today.update(b)
                            used_this_week.update(b)
                            for nama in b:
                                usage_count[nama] = usage_count.get(nama, 0) + 1
                            jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'R. IMUNISASI', 'penyerta': '; '.join(b) if b else 'Tidak ada'})
                        
                        # R. TINDAKAN (1 perawat)
                        p = random_pick_with_fairness(semua_perawat, 1, used_today)
                        if p:
                            used_today.add(p[0])
                            used_this_week.add(p[0])
                            usage_count[p[0]] = usage_count.get(p[0], 0) + 1
                            jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'R. TINDAKAN', 'penyerta': p[0]})
                        
                        # BP GIGI, APOTEK, LAB
                        if tetap_bpgigi:
                            jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'BP GIGI', 'penyerta': '; '.join(tetap_bpgigi)})
                            used_today.update(tetap_bpgigi)
                        if tetap_apotek:
                            jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'APOTEK', 'penyerta': '; '.join(tetap_apotek)})
                            used_today.update(tetap_apotek)
                        if tetap_lab:
                            jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'LAB', 'penyerta': '; '.join(tetap_lab)})
                            used_today.update(tetap_lab)
                        
                        # R. TB (hanya Selasa, hanya Mutia Wulansari)
                        if nama_hari == "Selasa":
                            petugas_tb = "Mutia Wulansari.,S.Kep.,Ners"
                            if petugas_tb not in NAMA_DIECUALIKAN:
                                jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'R. TB', 'penyerta': petugas_tb})
                                used_today.add(petugas_tb)
                                used_this_week.add(petugas_tb)
                                usage_count[petugas_tb] = usage_count.get(petugas_tb, 0) + 1
                        
                        # ADMINISTRASI
                        extra = random_pick_with_fairness(extra_admin, 2)
                        semua_admin = tetap_admin + extra
                        if semua_admin:
                            jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'ADMINISTRASI', 'penyerta': '; '.join(semua_admin)})
                            used_today.update(semua_admin)
                            used_this_week.update(semua_admin)
                            for nama in semua_admin:
                                usage_count[nama] = usage_count.get(nama, 0) + 1
                        
                        # PUSTU
                        jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Pustu Ciangir', 'kegiatan': 'PELAYANAN PUSTU', 'penyerta': tetap_ciangir})
                        jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Pustu Sumelap', 'kegiatan': 'PELAYANAN PUSTU', 'penyerta': tetap_sumelap})
                        used_today.add(tetap_ciangir)
                        used_today.add(tetap_sumelap)
                    
                    # Tampilkan hari yang di-skip karena piket malam
                    if skipped_days:
                        st.info(f"⚠️ Hari berikut ini TIDAK digenerate karena H-1 ada PIKET PERSALINAN MALAM: {', '.join(skipped_days)}")
                    
                    # Simpan ke database
                    saved = 0
                    progress_text = st.empty()
                    progress_bar = st.progress(0)
                    
                    for i, j in enumerate(jadwal_baru):
                        progress_text.text(f"Menyimpan {i+1} dari {len(jadwal_baru)}: {j['kegiatan']}")
                        progress_bar.progress((i+1)/len(jadwal_baru))
                        try:
                            resp_cek = api_get("kegiatan/", auth=True)
                            exists = False
                            if resp_cek.status_code == 200:
                                existing = resp_cek.json()
                                exists = any(e['tanggal'] == j['tanggal'] and e['kegiatan'] == j['kegiatan'] for e in existing)
                            if not exists:
                                resp = api_post("kegiatan/", j, auth=True)
                                if resp.status_code == 201:
                                    saved += 1
                        except Exception as e:
                            pass
                    
                    progress_text.empty()
                    progress_bar.empty()
                    
                    if saved > 0:
                        st.success(f"✅ Berhasil generate {saved} jadwal untuk minggu ke-{minggu_pilih}!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Gagal menyimpan jadwal. Cek koneksi ke server Django.")
        
        st.markdown("---")
        st.subheader("📋 Hasil Generate Jadwal")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            bulan_filter = st.selectbox("Filter Bulan", range(1, 13), index=datetime.now().month-1,
                                       format_func=lambda x: ["Januari","Februari","Maret","April","Mei","Juni",
                                                              "Juli","Agustus","September","Oktober","November","Desember"][x-1],
                                       key="filter_bulan")
        with col_f2:
            tahun_filter = st.number_input("Filter Tahun", value=datetime.now().year, key="filter_tahun")
        
        try:
            resp = api_get("kegiatan/", auth=True)
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    df = pd.DataFrame(data)
                    df['tanggal'] = pd.to_datetime(df['tanggal'])
                    df_filter = df[(df['tanggal'].dt.month == bulan_filter) & (df['tanggal'].dt.year == tahun_filter)]
                    df_filter = df_filter.sort_values('tanggal')
                    if not df_filter.empty:
                        st.dataframe(df_filter[['tanggal', 'lokasi', 'kegiatan', 'penyerta']], use_container_width=True, hide_index=True)
                    else:
                        st.info(f"Belum ada jadwal untuk {bulan_filter}/{tahun_filter}")
                else:
                    st.info("Belum ada data")
        except:
            st.warning("Gagal mengambil data")
# ─── Footer ───
st.markdown("---")
st.markdown("<div style='text-align:center'>Puskesmas Sangkali &copy; 2026</div>", unsafe_allow_html=True)