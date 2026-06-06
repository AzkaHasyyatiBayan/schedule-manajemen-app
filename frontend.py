import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from collections import defaultdict

# ---------- Konfigurasi Halaman ----------
st.set_page_config(
    page_title="Puskesmas Sangkali",
    page_icon="🏥",
    layout="wide"
)

# ---------- CSS + Font Awesome ----------
st.html("""
<link rel="stylesheet"
  href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>
<style>
  .main-header {
    background: linear-gradient(135deg, #14532d 0%, #166534 100%);
    padding: 2rem;
    border-radius: 20px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
  }
  .main-header h1 { margin: 0; }
  .data-card {
    background: white;
    padding: 1.5rem;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
    margin-bottom: 1rem;
  }
  .result-box {
    background: #f8fafc;
    padding: 1rem;
    border-radius: 12px;
    border-left: 5px solid #14532d;
    margin: 0.5rem 0;
  }
  .icon-text i { margin-right: 8px; color: #14532d; }
  .logo-container { display: flex; justify-content: center; margin-bottom: 1rem; }
  .badge-online {
    display: inline-block; background: #dcfce7; color: #15803d;
    font-size: 0.75rem; font-weight: 600; padding: 2px 10px;
    border-radius: 999px;
  }
  .badge-offline {
    display: inline-block; background: #fee2e2; color: #dc2626;
    font-size: 0.75rem; font-weight: 600; padding: 2px 10px;
    border-radius: 999px;
  }
  .svg-icon {
    display: inline-block;
    vertical-align: middle;
    margin-right: 6px;
  }
</style>
""")

# ---------- Konstanta ----------
API_BASE = "http://localhost:8000/api"

DAFTAR_NAMA = [
    "Ahmad Fauzi", "Anisa Rahma", "Budi Santoso", "Citra Dewi", "Dedi Kurniawan",
    "Eka Fitriani", "Fajar Pratama", "Gita Puspita", "Hendra Gunawan", "Indah Lestari",
    "Joko Susilo", "Kartika Sari", "Lukman Hakim", "Maya Sari", "Nanda Putra",
    "Oktavia Dewi", "Prabowo Subroto", "Qonita Zahra", "Rizki Amelia", "Siti Nurjanah",
    "Teguh Prasetyo", "Umi Kalsum", "Vina Oktaviani", "Wahyu Setiawan", "Xena Aulia",
    "Yusuf Maulana", "Zahra Firdaus", "Agus Salim", "Dewi Sartika", "Eko Prasetyo",
    "Fatimah Azzahra", "Gilang Ramadhan", "Hani Nurfadillah", "Ikhsan Pratama", "Jihan Nabila",
    "Khairul Anwar", "Laila Nuraini", "Miftahul Jannah", "Nadya Puspita", "Oscar Fernando"
]

# ---------- Session State ----------
for key, default in [
    ('logged_in', False),
    ('token', None),
    ('username', ''),
    ('page', 'user'),
    ('edit_data', None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ---------- Cek token dari URL (persist session) ----------
params = st.query_params
if not st.session_state.logged_in and 'token' in params:
    token = params['token']
    try:
        resp = requests.get(
            f"{API_BASE}/verify-token/",
            headers={"Authorization": f"Token {token}"},
            timeout=5
        )
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

def get_nama_dari_data():
    try:
        r = requests.get(f"{API_BASE}/search-user/", timeout=5)
        semua = r.json() if r.status_code == 200 else []
    except:
        semua = []
    nama_set = set()
    for d in semua:
        for n in str(d.get('penyerta','')).split(','):
            n = n.strip()
            if n: nama_set.add(n)
    return sorted(nama_set)

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
    st.markdown("""
    <div class="icon-text" style="margin-bottom:0.5rem">
      <svg class="svg-icon" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#14532d" stroke-width="2"
           stroke-linecap="round" stroke-linejoin="round">
        <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
      </svg>
      <span style="font-size:1.5rem; font-weight:600;">Cari Jadwal Kegiatan</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        nama_dari_data = get_nama_dari_data()
        nama_gabungan = nama_dari_data + [n for n in DAFTAR_NAMA if n not in set(nama_dari_data)]
        if not nama_gabungan: nama_gabungan = DAFTAR_NAMA

        with st.form("user_form"):
            nama    = st.selectbox("Nama Lengkap", nama_gabungan)
            tanggal = st.date_input("Tanggal Kegiatan", datetime.now().date())
            if st.form_submit_button("Cari Jadwal"):
                try:
                    resp = api_get("search-user/", params={"nama": nama, "tanggal": str(tanggal)})
                    if resp.status_code == 200:
                        hasil = resp.json()
                        if hasil:
                            st.success(f"Halo {nama}")
                            for h in hasil:
                                st.markdown(f"""
                                <div class="result-box">
                                    <b>Lokasi:</b> {h['lokasi']}<br>
                                    <b>Kegiatan:</b> {h['kegiatan']}<br>
                                    <b>Penyerta:</b> {h['penyerta']}
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
              <svg class="svg-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#14532d" stroke-width="2"
                   stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"/><path d="M12 16v-4M12 8h.01"/>
              </svg>
              <span style="font-weight:600;">Informasi</span>
            </div>
            <ul><li>Datang 15 menit lebih awal</li><li>Bawa KMS/BPJS</li><li>Gunakan masker</li></ul>
        </div>
        """, unsafe_allow_html=True)

        # SVG kalender dekoratif
        st.html("""
        <div style="text-align:center;margin-top:1rem">
        <svg viewBox="0 0 100 95" width="110" xmlns="http://www.w3.org/2000/svg">
          <rect x="5" y="15" width="90" height="75" rx="8" fill="#f8fafc" stroke="#14532d" stroke-width="2"/>
          <rect x="5" y="15" width="90" height="24" rx="8" fill="#14532d"/>
          <rect x="5" y="28" width="90" height="11" fill="#14532d"/>
          <text x="50" y="31" text-anchor="middle" fill="white" font-size="9"
                font-weight="bold" font-family="sans-serif">JUNI 2026</text>
          <rect x="28" y="9" width="6" height="16" rx="3" fill="#166534"/>
          <rect x="66" y="9" width="6" height="16" rx="3" fill="#166534"/>
          <text x="13"  y="52" fill="#9ca3af" font-size="6.5" font-family="sans-serif">Min</text>
          <text x="27"  y="52" fill="#9ca3af" font-size="6.5" font-family="sans-serif">Sen</text>
          <text x="41"  y="52" fill="#9ca3af" font-size="6.5" font-family="sans-serif">Sel</text>
          <text x="55"  y="52" fill="#9ca3af" font-size="6.5" font-family="sans-serif">Rab</text>
          <text x="67"  y="52" fill="#9ca3af" font-size="6.5" font-family="sans-serif">Kam</text>
          <text x="81"  y="52" fill="#9ca3af" font-size="6.5" font-family="sans-serif">Jum</text>
          <text x="41"  y="65" fill="#374151" font-size="8" font-family="sans-serif">3</text>
          <text x="55"  y="65" fill="#374151" font-size="8" font-family="sans-serif">4</text>
          <text x="69"  y="65" fill="#374151" font-size="8" font-family="sans-serif">5</text>
          <circle cx="88" cy="62" r="7" fill="#14532d"/>
          <text x="88" y="65" text-anchor="middle" fill="white"
                font-size="8" font-weight="bold" font-family="sans-serif">6</text>
          <text x="13"  y="80" fill="#374151" font-size="8" font-family="sans-serif">8</text>
          <text x="27"  y="80" fill="#374151" font-size="8" font-family="sans-serif">9</text>
          <text x="39"  y="80" fill="#374151" font-size="8" font-family="sans-serif">10</text>
          <text x="53"  y="80" fill="#374151" font-size="8" font-family="sans-serif">11</text>
          <text x="67"  y="80" fill="#374151" font-size="8" font-family="sans-serif">12</text>
          <text x="81"  y="80" fill="#374151" font-size="8" font-family="sans-serif">13</text>
        </svg>
        </div>
        """)

    # Jadwal terdekat
    st.markdown("""
    <div class="icon-text" style="margin-top:1.5rem; margin-bottom:0.5rem">
      <svg class="svg-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#14532d" stroke-width="2"
           stroke-linecap="round" stroke-linejoin="round">
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
      <svg class="svg-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#14532d" stroke-width="2"
           stroke-linecap="round" stroke-linejoin="round">
        <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
        <rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>
      </svg>
      <span style="font-size:1.5rem; font-weight:600;">Dashboard Admin</span>
    </div>
    """, unsafe_allow_html=True)
    st.success(f"Selamat datang, {st.session_state.username}")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Input Manual", "Google Sheet", "Pencarian", "Kelola Data", "Randomize (Dalam Gedung)"
    ])

    # ── Tab 1: Input Manual ──
    with tab1:
        with st.form("input_form"):
            col1, col2 = st.columns(2)
            with col1:
                tgl    = st.date_input("Tanggal")
                lokasi = st.text_input("Lokasi")
            with col2:
                kegiatan = st.text_input("Nama Kegiatan")
                penyerta = st.text_area("Penyerta", height=100)
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
                            st.success("Data berhasil disimpan!")
                            st.rerun()
                        else:
                            st.error(f"Gagal menyimpan: {resp.text}")
                    except Exception as e:
                        st.error(f"Error: {e}")

    # ── Tab 2: Google Sheet ──
    with tab2:
        st.markdown('<h4><i class="fa-solid fa-cloud-arrow-up"></i> Sync dari Google Spreadsheet</h4>',
                    unsafe_allow_html=True)
        st.caption("File > Share > Publish to web > CSV > Copy link")
        st.info("Kolom yang diperlukan: `tanggal`, `lokasi`, `kegiatan`, `penyerta`")
        csv_url = st.text_input("Link CSV terpublikasi", key="csv_url")
        if st.button("Ambil & Simpan Data"):
            if not csv_url.strip():
                st.warning("Masukkan URL terlebih dahulu")
            else:
                with st.spinner("Mengambil data..."):
                    try:
                        resp = api_post("sync-sheets/", {"csv_url": csv_url}, auth=True)
                        if resp.status_code == 200:
                            result = resp.json()
                            st.success(result.get('message', 'Data berhasil diimpor.'))
                            st.rerun()
                        else:
                            st.error(resp.json().get('error', resp.text))
                    except Exception as e:
                        st.error(f"Error: {e}")

    # ── Tab 3: Pencarian (dengan dropdown + input manual untuk Lokasi) ──
    with tab3:
        try:
            resp_data = api_get("kegiatan/", auth=True)
            semua_data = resp_data.json() if resp_data.status_code == 200 else []
        except:
            semua_data = []

        # Ambil daftar unik lokasi, kegiatan, penyerta
        lokasi_list = sorted(set(d['lokasi'] for d in semua_data if d.get('lokasi')))
        kegiatan_list = sorted(set(d['kegiatan'] for d in semua_data if d.get('kegiatan')))
        penyerta_set = set()
        for d in semua_data:
            for n in str(d.get('penyerta','')).split(','):
                n = n.strip()
                if n: penyerta_set.add(n)
        penyerta_list = sorted(penyerta_set)

        st.markdown('<h4><i class="fa-solid fa-filter"></i> Filter Pencarian</h4>', unsafe_allow_html=True)
        with st.form("search_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                tgl_src = st.date_input("Tanggal", value=None, key="src_tgl")
            with col2:
                # LOKASI: dropdown + input manual
                lok_options = ["Semua"] + lokasi_list + ["Cari manual..."]
                lok_dd = st.selectbox("Lokasi", lok_options, key="lok_dd")
                lok_src = ""
                if lok_dd == "Cari manual...":
                    lok_src = st.text_input("Ketik lokasi", key="lok_manual")
                elif lok_dd != "Semua":
                    lok_src = lok_dd
            with col3:
                # KEGIATAN: dropdown + input manual
                keg_options = ["Semua"] + kegiatan_list + ["Cari manual..."]
                keg_dd = st.selectbox("Nama Kegiatan", keg_options, key="keg_dd")
                keg_src = ""
                if keg_dd == "Cari manual...":
                    keg_src = st.text_input("Ketik nama kegiatan", key="keg_manual")
                elif keg_dd != "Semua":
                    keg_src = keg_dd

            # PENYERTA: dropdown + input manual
            peny_options = ["Semua"] + penyerta_list + ["Cari manual..."]
            peny_dd = st.selectbox("Penyerta", peny_options, key="peny_dd")
            peny_src = ""
            if peny_dd == "Cari manual...":
                peny_src = st.text_input("Ketik nama penyerta", key="peny_manual")
            elif peny_dd != "Semua":
                peny_src = peny_dd

            if st.form_submit_button("Cari"):
                params = {}
                if tgl_src: params["tanggal"]  = str(tgl_src)
                if lok_src: params["lokasi"]   = lok_src
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
                                # === GROUPING: gabung penyerta per (tanggal, lokasi, kegiatan) ===
                                groups = defaultdict(list)
                                for item in hasil:
                                    key = (item['tanggal'], item['lokasi'], item['kegiatan'])
                                    groups[key].append(item['penyerta'])
                                st.success(f"Ditemukan {len(groups)} grup data")
                                for (tanggal, lokasi, kegiatan), list_penyerta in groups.items():
                                    # Gabung penyerta dengan <br> agar tampil ke bawah
                                    penyerta_gabung = '<br>'.join(p for p in list_penyerta if p)
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

    # ── Tab 4: Kelola Data ──
    with tab4:
        st.subheader("Daftar Semua Kegiatan")
        try:
            resp = api_get("kegiatan/", auth=True)
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    df_raw = pd.DataFrame(data)
                    # Gabung penyerta dengan koma + newline untuk tampilan di dataframe
                    df_grouped = (
                        df_raw.groupby(['tanggal', 'lokasi', 'kegiatan'], sort=False)
                        .agg(
                            id=('id', 'first'),
                            penyerta=('penyerta', lambda x: ',\n'.join(x.tolist()))
                        )
                        .reset_index()
                    )[['id', 'tanggal', 'lokasi', 'kegiatan', 'penyerta']]
                    df_grouped.columns = ['ID', 'Tanggal', 'Lokasi', 'Kegiatan', 'Penyerta']
                    st.dataframe(
                        df_grouped,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Penyerta": st.column_config.TextColumn(width="large")
                        }
                    )

                    # Edit
                    st.markdown("---")
                    st.markdown('<h4><i class="fa-solid fa-pen-to-square"></i> Edit Data</h4>',
                                unsafe_allow_html=True)
                    edit_id = st.number_input("ID data yang akan diedit", min_value=1, step=1)
                    if st.button("Ambil Data"):
                        try:
                            resp_det = api_get(f"kegiatan/{edit_id}/", auth=True)
                            if resp_det.status_code == 200:
                                st.session_state.edit_data = resp_det.json()
                            else:
                                st.error("ID tidak ditemukan")
                                st.session_state.edit_data = None
                        except Exception as e:
                            st.error(f"Error: {e}")
                    if st.session_state.edit_data:
                        with st.form("edit_form"):
                            tgl_ed  = st.date_input("Tanggal",
                                                    value=pd.to_datetime(st.session_state.edit_data['tanggal']))
                            lok_ed  = st.text_input("Lokasi",        value=st.session_state.edit_data['lokasi'])
                            keg_ed  = st.text_input("Nama Kegiatan", value=st.session_state.edit_data['kegiatan'])
                            peny_ed = st.text_area("Penyerta",       value=st.session_state.edit_data['penyerta'])
                            if st.form_submit_button("Update"):
                                try:
                                    resp_upd = api_put(
                                        f"kegiatan/{edit_id}/",
                                        {"tanggal": str(tgl_ed), "lokasi": lok_ed,
                                         "kegiatan": keg_ed, "penyerta": peny_ed}
                                    )
                                    if resp_upd.status_code == 200:
                                        st.success("Data diperbarui.")
                                        st.session_state.edit_data = None
                                        st.rerun()
                                    else:
                                        st.error(f"Gagal update: {resp_upd.text}")
                                except Exception as e:
                                    st.error(f"Error: {e}")

                    # Hapus
                    st.markdown('<h4><i class="fa-solid fa-trash-can"></i> Hapus Data</h4>',
                                unsafe_allow_html=True)
                    del_id = st.number_input("ID data yang akan dihapus", min_value=1, step=1, key="del_id")
                    if st.button("Hapus"):
                        try:
                            resp_del = api_delete(f"kegiatan/{del_id}/")
                            if resp_del.status_code == 204:
                                st.success("Data dihapus.")
                                st.rerun()
                            else:
                                st.error(f"Gagal menghapus: {resp_del.text}")
                        except Exception as e:
                            st.error(f"Error: {e}")
                else:
                    st.info("Belum ada data")
            else:
                st.error("Gagal memuat data.")
        except Exception as e:
            st.error(f"Error: {e}")

    # ── Tab 5: Randomize ──
    with tab5:
        st.subheader("Randomize Kegiatan Dalam Gedung")
        st.info("Fitur ini akan datang.")
        with st.form("randomize_form"):
            st.text_input("Kriteria (nanti diisi)")
            st.form_submit_button("Acak (segera)")

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("<div style='text-align:center'>Puskesmas Sangkali &copy; 2026</div>", unsafe_allow_html=True)