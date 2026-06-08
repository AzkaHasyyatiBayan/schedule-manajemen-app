import streamlit as st
import pandas as pd
import requests
import re
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
    """Pisahkan nama penyerta. Prioritas: titik koma, lalu koma+spasi+kapital."""
    if not teks:
        return []
    if ';' in teks:
        return [p.strip() for p in teks.split(';') if p.strip()]
    # Fallback: koma diikuti spasi dan huruf besar
    parts = re.split(r', (?=[A-Z])', teks)
    return [p.strip() for p in parts if p.strip()]

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
    # --- Notifikasi Kegiatan Hari ini & Besok ---
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
            nama    = st.selectbox("Nama Lengkap", DAFTAR_NAMA)
            tanggal = st.date_input("Tanggal Kegiatan", datetime.now().date())
            if st.form_submit_button("Cari Jadwal"):
                try:
                    resp = api_get("search-user/", params={"nama": nama, "tanggal": str(tanggal)})
                    if resp.status_code == 200:
                        hasil = resp.json()
                        if hasil:
                            st.success(f"Halo {nama}")
                            for h in hasil:
                                # parsing penyerta yang lebih baik
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

    # Jadwal terdekat
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

    # ── Tab 1: Input Manual (dengan multiselect penyerta) ──
    with tab1:
        with st.form("input_form"):
            col1, col2 = st.columns(2)
            with col1:
                tgl    = st.date_input("Tanggal")
                lokasi = st.text_input("Lokasi")
            with col2:
                kegiatan = st.text_input("Nama Kegiatan")
                # Multiselect untuk memilih penyerta
                penyerta_terpilih = st.multiselect(
                    "Pilih Penyerta (bisa lebih dari satu)",
                    options=DAFTAR_NAMA,
                    placeholder="Ketik nama atau pilih dari daftar"
                )
                # Jika tidak dipilih, beri opsi input manual
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
                        resp = api_post(
                            "kegiatan/",
                            {"tanggal": str(tgl), "lokasi": lokasi,
                             "kegiatan": kegiatan, "penyerta": penyerta},
                            auth=True
                        )
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
                sync_mode = st.radio("Mode", ['append', 'replace'], horizontal=True,
                                     format_func=lambda x: "Tambahkan saja" if x=='append' else "Ganti semua")
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
            sync_mode = st.radio("Mode", ['append', 'replace'], horizontal=True,
                                 format_func=lambda x: "Tambahkan saja" if x=='append' else "Ganti semua")
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

    # ── Tab 4: Kelola Data (hapus berdasarkan grup kegiatan) ──
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
                            # simpan daftar ID asli untuk keperluan hapus
                            ids=('id', list)
                        )
                        .reset_index()
                    )
                    df_grouped.columns = ['Tanggal', 'Lokasi', 'Kegiatan', 'Penyerta', 'IDs']

                    # Proses pending delete
                    if st.session_state.pending_delete_ids:
                        # IDs ini adalah list of lists (karena tiap grup bisa punya beberapa id)
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

                    # Edit via dropdown
                    st.markdown("---")
                    st.markdown('<h4><i class="fa-solid fa-pen-to-square"></i> Edit Data</h4>', unsafe_allow_html=True)
                    opsi_edit = ["—"] + [
                        f"{row['Tanggal']} | {row['Lokasi']} | {row['Kegiatan']}"
                        for _, row in df_grouped.iterrows()
                    ]
                    pilihan = st.selectbox("Pilih kegiatan", opsi_edit)
                    if pilihan != "—":
                        tgl_pilih, lok_pilih, keg_pilih = pilihan.split(" | ")
                        # Ambil salah satu ID dari grup untuk edit
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
                                resp_upd = api_put(f"kegiatan/{edit_id}/", {"tanggal": str(tgl_ed), "lokasi": lok_ed, "kegiatan": keg_ed, "penyerta": peny_ed, "kategori": st.session_state.edit_data.get('kategori','Luar Gedung')})
                                if resp_upd.status_code == 200:
                                    st.session_state.notif = "Data diperbarui!"
                                    st.session_state.edit_data = None
                                    st.rerun()
                                else:
                                    st.error(resp_upd.text)

                    # Hapus per bulan/tahun
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
        st.subheader("History Kegiatan")
        try:
            resp = api_get("kegiatan/", auth=True)
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    today = date.today()
                    df = pd.DataFrame(data)
                    df['tanggal_date'] = pd.to_datetime(df['tanggal']).dt.date
                    df = df.sort_values('tanggal_date')
                    for _, row in df.iterrows():
                        tgl_date = row['tanggal_date']
                        if tgl_date < today:
                            cls = "past"
                        elif tgl_date == today:
                            cls = "today"
                        elif tgl_date == today + timedelta(days=1):
                            cls = "tomorrow"
                        else:
                            cls = "future"
                        hari = tgl_date.strftime('%A, %d %B %Y')
                        st.markdown(f"""
                        <div class="result-box {cls}">
                            <b>{hari}</b><br>
                            {row['lokasi']} - {row['kegiatan']} ({row.get('kategori','luar_gedung')})<br>
                            <small>{row['penyerta']}</small>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Belum ada data")
        except Exception as e:
            st.error(f"Error: {e}")

    # ── Tab 6: Randomize ──
    with tab6:
        st.subheader("Randomize Kegiatan Dalam Gedung")
        st.info("Fitur akan datang.")

# ─── Footer ───
st.markdown("---")
st.markdown("<div style='text-align:center'>Puskesmas Sangkali &copy; 2026</div>", unsafe_allow_html=True)