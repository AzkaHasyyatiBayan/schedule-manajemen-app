from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, throttle_classes, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.throttling import AnonRateThrottle
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
from .models import Kegiatan, HariLibur
from .serializers import KegiatanSerializer, HariLiburSerializer
from .utils import capitalisasi_judul
import pandas as pd
import requests
import re
import traceback
from io import StringIO
from datetime import datetime


# ─── Throttle khusus untuk login ─────────────────────────────────────────────
class LoginRateThrottle(AnonRateThrottle):
    scope = 'login'


# ─── ViewSet CRUD (hanya admin dengan token) ─────────────────────────────────
@method_decorator(csrf_exempt, name='dispatch')
class KegiatanViewSet(viewsets.ModelViewSet):
    queryset = Kegiatan.objects.all().order_by('-tanggal')
    serializer_class = KegiatanSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        nama = serializer.validated_data.get('kegiatan', '')
        serializer.save(
            kegiatan=capitalisasi_judul(nama),
            source='manual'  # Set source untuk input manual
        )

    def perform_update(self, serializer):
        nama = serializer.validated_data.get('kegiatan', '')
        serializer.save(kegiatan=capitalisasi_judul(nama))

    @action(detail=False, methods=['post'], url_path='bulk-delete')
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': 'ids diperlukan'}, status=400)
        deleted, _ = Kegiatan.objects.filter(id__in=ids).delete()
        return Response({'message': f'{deleted} data dihapus.'})


# ─── Login ───────────────────────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([LoginRateThrottle])
def login_view(request):
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '')

    if not username or not password:
        return Response(
            {'error': 'Username dan password wajib diisi'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(request, username=username, password=password)
    if user is not None:
        if not user.is_active:
            return Response(
                {'error': 'Akun tidak aktif'},
                status=status.HTTP_403_FORBIDDEN
            )
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'message': 'Login berhasil',
            'token': token.key,
            'username': user.username,
        })
    return Response(
        {'error': 'Username atau password salah'},
        status=status.HTTP_401_UNAUTHORIZED
    )


# ─── Logout ──────────────────────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        request.user.auth_token.delete()
    except Exception:
        pass
    return Response({'message': 'Logout berhasil'})


# ─── Helper Functions untuk Pivot Table Parser ──────────────────────────────
BULAN_MAP = {
    'Januari': 1, 'Februari': 2, 'Maret': 3, 'April': 4,
    'Mei': 5, 'Juni': 6, 'Juli': 7, 'Agustus': 8,
    'September': 9, 'Oktober': 10, 'November': 11, 'Desember': 12
}

def parse_tanggal_indo(text):
    """Parse tanggal format Indonesia: 'Selasa, 02 Juni 2026' -> '2026-06-02'"""
    text = str(text).strip()
    # Hapus nama hari
    text = re.sub(r'^(Senin|Selasa|Rabu|Kamis|Jumat|Sabtu|Minggu),?\s*', '', text, flags=re.IGNORECASE)
    # Parse tanggal
    match = re.match(r'(\d{1,2})\s+(\w+)\s+(\d{4})', text)
    if match:
        day = int(match.group(1))
        month_name = match.group(2)
        year = int(match.group(3))
        month = BULAN_MAP.get(month_name)
        if month:
            try:
                return datetime(year, month, day).strftime('%Y-%m-%d')
            except:
                pass
    return None

def split_names(text):
    """Split multiple nama dalam satu sel menjadi list"""
    if not text or str(text).strip().lower() in ['nan', 'none', '']:
        return []
    
    text = str(text).strip()
    
    # Split dengan semicolon
    if ';' in text:
        return [n.strip() for n in text.split(';') if n.strip()]
    
    # Split dengan newline
    if '\n' in text:
        return [n.strip() for n in text.split('\n') if n.strip()]
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Split berdasarkan pola gelar
    pattern = r'((?:dr\.?|drg\.?)?\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s*,\s*)?(?:S\.Tr\.Keb|S\.Kep\.?\s*,?\s*Ners|AMK|SKM|A\.Md\.Keb|A\.Md\.KL|S\.Gz|A\.Md\.Gz|S\.Farm\.?\s*,?\s*Apt|S\.E|S\.T|AMd\.?\s*RMIK|S\.ST|S\.Tr\.Kes|A\.Md\.AK|A\.Md\.Farm|A\.Md\.Kep|Amd\.?\s*Kep|Am\.?\s*Keb|dr\.?|drg\.?)?)'
    matches = re.findall(pattern, text)
    if len(matches) > 1:
        return [m.strip() for m in matches if m.strip()]
    
    # Fallback: return as is
    return [text] if text else []


# ─── Sync Google Sheets (UPDATED - support pivot & flat format + smart replace) ──
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_google_sheets(request):
    url = request.data.get('csv_url', '').strip()
    mode = request.data.get('mode', 'append')

    if not url:
        return Response({'error': 'Parameter csv_url diperlukan'}, status=400)

    try:
        # 1. Download CSV
        if '/spreadsheets/d/e/' in url:
            csv_url = url.split('?')[0] + '?output=csv'
        elif '/spreadsheets/d/' in url:
            sheet_id = url.split('/d/')[1].split('/')[0]
            csv_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv'
        else:
            csv_url = url

        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(csv_url, headers=headers, timeout=15)
        resp.raise_for_status()

        # 2. Deteksi format: Flat atau Pivot
        df_check = pd.read_csv(StringIO(resp.text))
        df_check.columns = [c.lower().strip() for c in df_check.columns]
        
        # Cek apakah format flat (ada kolom tanggal, lokasi, kegiatan, penyerta)
        is_flat_format = all(col in df_check.columns for col in ['tanggal', 'lokasi', 'kegiatan', 'penyerta'])
        
        if is_flat_format:
            # ─── FORMAT FLAT ──────────────────────────────────────────────
            return _process_flat_format(df_check, mode)
        else:
            # ─── FORMAT PIVOT ─────────────────────────────────────────────
            df_pivot = pd.read_csv(StringIO(resp.text), header=None)
            return _process_pivot_format(df_pivot, mode)

    except requests.exceptions.Timeout:
        return Response({'error': 'Timeout saat mengambil data dari Google Sheets'}, status=504)
    except requests.exceptions.HTTPError as e:
        return Response({'error': f'Gagal mengambil spreadsheet: {e}'}, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


def _process_flat_format(df, mode):
    """Proses format flat (tabel biasa dengan kolom tanggal, lokasi, kegiatan, penyerta)"""
    df = df.dropna(subset=['tanggal', 'lokasi'])

    # Smart Replace: hanya hapus data dengan source='google_sheet'
    if mode == 'replace':
        deleted_count, _ = Kegiatan.objects.filter(source='google_sheet').delete()
    
    created = 0
    skipped = 0
    errors = []
    
    for i, row in df.iterrows():
        try:
            tgl = pd.to_datetime(row['tanggal']).date()
            lok = str(row['lokasi']).strip()
            keg = capitalisasi_judul(str(row['kegiatan']).strip())
            peny = str(row['penyerta']).strip()

            # Support kategori (opsional)
            kat = str(row.get('kategori', 'luar_gedung')).strip().lower()
            if kat not in ['dalam_gedung', 'luar_gedung']:
                kat = 'luar_gedung'

            # Support sub_kategori (opsional)
            sub_kat = str(row.get('sub_kategori', 'lainnya')).strip().lower()
            if sub_kat not in ['posyandu', 'bok', 'sekolah', 'kunjungan_lapangan', 'inspeksi', 'rapat', 'lainnya']:
                sub_kat = 'lainnya'

            if mode == 'append':
                if Kegiatan.objects.filter(tanggal=tgl, lokasi=lok, kegiatan=keg).exists():
                    skipped += 1
                    continue

            Kegiatan.objects.create(
                tanggal=tgl,
                lokasi=lok,
                kegiatan=keg,
                penyerta=peny,
                kategori=kat,
                sub_kategori=sub_kat,
                source='google_sheet'  # Set source
            )
            created += 1
        except Exception as e:
            errors.append(f'Baris {i+2}: {e}')

    msg = f'{created} data baru diimpor.'
    if mode == 'replace':
        msg = f'Data dari Google Sheet lama dihapus. {msg}'
    elif skipped > 0:
        msg += f' {skipped} data sudah ada dan dilewati.'
    
    result = {'message': msg, 'format': 'flat'}
    if errors:
        result['peringatan'] = errors[:10]
    return Response(result)


def _process_pivot_format(df, mode):
    """Proses format pivot (tabel mingguan dengan header tanggal)"""
    if df.empty:
        return Response({'error': 'File CSV kosong'}, status=400)

    # Smart Replace: hanya hapus data dengan source='google_sheet'
    if mode == 'replace':
        deleted_count, _ = Kegiatan.objects.filter(source='google_sheet').delete()

    created = 0
    skipped = 0
    errors = []
    
    current_kategori = 'dalam_gedung'
    current_lokasi = 'Dalam Gedung'
    
    # Cari baris header tanggal
    header_row_idx = -1
    date_columns = {}
    
    for idx, row in df.iterrows():
        # Deteksi Section Header
        val_a = str(row[0]).strip().upper()
        if 'RUANG PELAYANAN' in val_a or 'DALAM GEDUNG' in val_a:
            current_kategori = 'dalam_gedung'
            current_lokasi = 'Dalam Gedung'
            continue
        elif 'LUAR GEDUNG' in val_a:
            current_kategori = 'luar_gedung'
            current_lokasi = 'Luar Gedung'
            continue
            
        # Deteksi Baris Tanggal (Header)
        is_header = False
        for col_idx, cell in enumerate(row):
            cell_str = str(cell).strip()
            parsed_date = parse_tanggal_indo(cell_str)
            if parsed_date:
                is_header = True
                date_columns[col_idx] = parsed_date
        
        if is_header:
            header_row_idx = idx
            break

    if header_row_idx == -1:
        return Response({
            'error': 'Format tidak dikenali. Pastikan ada baris header berisi tanggal (contoh: Senin, 01 Juni 2026)'
        }, status=400)

    # Proses Data Baris per Baris
    schedule_data = {}
    current_activity = ""

    for idx in range(header_row_idx + 1, len(df)):
        row = df.iloc[idx]
        activity_name = str(row[0]).strip()
        
        # Skip baris kosong total
        if (activity_name == '' or activity_name.lower() == 'nan') and \
           all(str(row[i]).strip().lower() in ['nan', 'none', ''] for i in date_columns.keys()):
            continue

        # Handle Merged Cell simulation
        if activity_name == '' or activity_name.lower() == 'nan':
            activity_name = current_activity
        else:
            current_activity = activity_name
            if activity_name not in schedule_data:
                schedule_data[activity_name] = {'kategori': current_kategori, 'dates': {}}

        # Ambil nama-nama dari setiap kolom tanggal
        for col_idx, date_str in date_columns.items():
            if col_idx < len(row):
                cell_value = str(row[col_idx]).strip()
                if cell_value and cell_value.lower() not in ['nan', 'none', '']:
                    names = split_names(cell_value)
                    
                    if date_str not in schedule_data[activity_name]['dates']:
                        schedule_data[activity_name]['dates'][date_str] = []
                    
                    schedule_data[activity_name]['dates'][date_str].extend(names)

    # Simpan ke Database
    for activity, data in schedule_data.items():
        kategori = data['kategori']
        for date_str, names in data['dates'].items():
            try:
                final_penyerta = "; ".join(names)
                
                # Tentukan Lokasi
                if kategori == 'dalam_gedung':
                    final_lokasi = 'Dalam Gedung'
                    sub_kat = ''
                else:
                    final_lokasi = activity
                    # Deteksi sub_kategori dari nama kegiatan
                    activity_lower = activity.lower()
                    if 'posyandu' in activity_lower:
                        sub_kat = 'posyandu'
                    elif 'inspeksi' in activity_lower or 'lingkungan' in activity_lower:
                        sub_kat = 'inspeksi'
                    elif 'rapat' in activity_lower:
                        sub_kat = 'rapat'
                    elif 'sekolah' in activity_lower or 'mi ' in activity_lower or 'mts' in activity_lower or 'smp' in activity_lower:
                        sub_kat = 'sekolah'
                    elif 'kunjungan' in activity_lower or 'lapangan' in activity_lower:
                        sub_kat = 'kunjungan_lapangan'
                    else:
                        sub_kat = 'lainnya'

                # Cek duplikat
                if mode == 'append' and Kegiatan.objects.filter(
                    tanggal=date_str, 
                    kegiatan=capitalisasi_judul(activity), 
                    lokasi=final_lokasi
                ).exists():
                    skipped += 1
                    continue

                Kegiatan.objects.create(
                    tanggal=date_str,
                    lokasi=final_lokasi,
                    kegiatan=capitalisasi_judul(activity),
                    penyerta=final_penyerta,
                    kategori=kategori,
                    sub_kategori=sub_kat,
                    source='google_sheet'  # Set source
                )
                created += 1

            except Exception as e:
                errors.append(f'{activity} ({date_str}): {str(e)}')

    msg = f'{created} data berhasil diproses.'
    if mode == 'replace':
        msg = f'Data dari Google Sheet lama dihapus. {msg}'
    if skipped > 0:
        msg += f' {skipped} data sudah ada dan dilewati.'
    
    result = {'message': msg, 'format': 'pivot'}
    if errors:
        result['peringatan'] = errors[:10]
    return Response(result)


# ─── Pencarian Admin ─────────────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_admin(request):
    qs = Kegiatan.objects.all().order_by('-tanggal')
    tgl = request.query_params.get('tanggal')
    lok = request.query_params.get('lokasi')
    keg = request.query_params.get('kegiatan')
    peny = request.query_params.get('penyerta')

    if tgl:
        qs = qs.filter(tanggal=tgl)
    if lok:
        qs = qs.filter(lokasi__icontains=lok)
    if keg:
        qs = qs.filter(kegiatan__icontains=keg)
    if peny:
        qs = qs.filter(penyerta__icontains=peny)

    serializer = KegiatanSerializer(qs, many=True)
    return Response(serializer.data)


# ─── Pencarian User Umum (UPDATED - include kategori & source) ──────────────
@api_view(['GET'])
@permission_classes([AllowAny])
def search_user(request):
    qs = Kegiatan.objects.all()
    tgl = request.query_params.get('tanggal')
    nama = request.query_params.get('nama')

    if tgl:
        qs = qs.filter(tanggal=tgl)
    if nama:
        qs = qs.filter(penyerta__icontains=nama)

    data = [{
        'tanggal': str(k.tanggal),
        'lokasi': k.lokasi,
        'kegiatan': k.kegiatan,
        'penyerta': k.penyerta,
        'kategori': k.kategori,
        'sub_kategori': k.sub_kategori,
        'source': k.source,
    } for k in qs]
    return Response(data)


# ─── Jadwal Terdekat (UPDATED - include kategori & source) ──────────────────
@api_view(['GET'])
@permission_classes([AllowAny])
def jadwal_terdekat(request):
    from django.utils import timezone
    today = timezone.now().date()
    qs = Kegiatan.objects.filter(tanggal__gte=today).order_by('tanggal')[:10]
    data = [{
        'tanggal': str(k.tanggal),
        'lokasi': k.lokasi,
        'kegiatan': k.kegiatan,
        'penyerta': k.penyerta,
        'kategori': k.kategori,
        'sub_kategori': k.sub_kategori,
        'source': k.source,
    } for k in qs]
    return Response(data)


# ─── Verifikasi Token ────────────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_token(request):
    return Response({'username': request.user.username})


# ─── Hapus per Bulan/Tahun ──────────────────────────────────────────────────
@api_view(['DELETE', 'POST'])
@permission_classes([IsAuthenticated])
def delete_kegiatan_by_date(request):
    month = request.data.get('month') or request.query_params.get('month')
    year = request.data.get('year') or request.query_params.get('year')
    if not month or not year:
        return Response({'error': 'month dan year diperlukan'}, status=400)
    try:
        month = int(month)
        year = int(year)
    except ValueError:
        return Response({'error': 'month dan year harus angka'}, status=400)

    deleted, _ = Kegiatan.objects.filter(tanggal__month=month, tanggal__year=year).delete()
    return Response({'message': f'{deleted} data dihapus untuk {month}/{year}.'})


# ─── Randomize Jadwal (FIXED - bulk_create untuk performa) ─────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def randomize_dalam_gedung(request):
    # Step 1: Import dengan error handling
    try:
        from .randomize_logic import generate_jadwal_dalam_gedung, generate_jadwal_luar_gedung
    except ImportError as e:
        return Response({
            'error': f'Import error: {str(e)}',
            'details': 'Pastikan randomize_logic.py dan constants.py sudah benar',
            'traceback': traceback.format_exc()
        }, status=500)
    
    # Step 2: Validasi input
    bulan = request.data.get('bulan')
    tahun = request.data.get('tahun')
    loka_karya = request.data.get('loka_karya', False)
    jenis = request.data.get('jenis', 'dalam_gedung')

    if not all([bulan, tahun]):
        return Response({'error': 'bulan dan tahun diperlukan'}, status=400)

    try:
        bulan = int(bulan)
        tahun = int(tahun)
    except ValueError:
        return Response({'error': 'bulan dan tahun harus angka'}, status=400)

    # Step 3: Generate jadwal dengan error handling
    try:
        if jenis == 'luar_gedung':
            jadwal_dalam, skipped_dalam = generate_jadwal_dalam_gedung(bulan, tahun, loka_karya)
            jadwal_list, skipped = generate_jadwal_luar_gedung(bulan, tahun, jadwal_dalam)
        else:
            jadwal_list, skipped = generate_jadwal_dalam_gedung(bulan, tahun, loka_karya)

        if not jadwal_list:
            return Response({
                'error': 'Gagal generate jadwal',
                'skipped': skipped,
                'details': 'Tidak ada jadwal yang berhasil di-generate. Cek apakah ada hari libur atau tidak ada hari kerja di bulan tersebut.'
            }, status=400)

        preview = request.data.get('preview', True)

        if preview:
            return Response({
                'message': f'Berhasil generate {len(jadwal_list)} jadwal',
                'jadwal': jadwal_list,
                'skipped': skipped
            })
        else:
            # Step 4: FILTER duplikat dulu SEBELUM bulk_create
            # Ambil semua kombinasi (tanggal, lokasi, kegiatan) yang sudah ada
            existing_keys = set(
                Kegiatan.objects.filter(
                    tanggal__in=[j['tanggal'] for j in jadwal_list]
                ).values_list('tanggal', 'lokasi', 'kegiatan')
            )
            
            # Filter hanya yang belum ada
            new_jadwal = [
                j for j in jadwal_list
                if (j['tanggal'], j['lokasi'], j['kegiatan']) not in existing_keys
            ]
            
            if not new_jadwal:
                return Response({
                    'message': 'Tidak ada jadwal baru untuk disimpan (semua sudah ada)',
                    'skipped': skipped,
                    'saved': 0
                })
            
            # Step 5: BULK CREATE dalam transaction (1 query untuk semua data)
            try:
                with transaction.atomic():
                    objects_to_create = [
                        Kegiatan(
                            tanggal=j['tanggal'],
                            lokasi=j['lokasi'],
                            kegiatan=j['kegiatan'],
                            penyerta=j['penyerta'],
                            kategori=j['kategori'],
                            is_auto_generated=j.get('is_auto_generated', True),
                            source='randomize'
                        )
                        for j in new_jadwal
                    ]
                    
                    Kegiatan.objects.bulk_create(objects_to_create, batch_size=100)
                
                return Response({
                    'message': f'Berhasil menyimpan {len(new_jadwal)} jadwal',
                    'skipped': skipped,
                    'saved': len(new_jadwal),
                    'dilewati_karena_duplikat': len(jadwal_list) - len(new_jadwal)
                })
            
            except Exception as db_error:
                return Response({
                    'error': f'Gagal menyimpan ke database: {str(db_error)}',
                    'details': 'Kemungkinan ada data yang tidak valid',
                    'traceback': traceback.format_exc()
                }, status=500)
    
    except Exception as e:
        # Catch semua error dan return dengan detail
        return Response({
            'error': f'Gagal generate jadwal: {str(e)}',
            'details': 'Periksa log untuk detail error',
            'traceback': traceback.format_exc(),
            'skipped': []
        }, status=500)


# ─── Hari Libur CRUD (NEW) ──────────────────────────────────────────────────
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def hari_libur_list(request):
    if request.method == 'GET':
        libur = HariLibur.objects.all().order_by('tanggal')
        serializer = HariLiburSerializer(libur, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = HariLiburSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def hari_libur_detail(request, pk):
    try:
        libur = HariLibur.objects.get(pk=pk)
    except HariLibur.DoesNotExist:
        return Response(status=404)

    if request.method == 'GET':
        serializer = HariLiburSerializer(libur)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = HariLiburSerializer(libur, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    elif request.method == 'DELETE':
        libur.delete()
        return Response(status=204)