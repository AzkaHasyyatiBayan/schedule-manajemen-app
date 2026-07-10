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
from django.utils import timezone
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


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER: AUTO SYNC HARI LIBUR (BARU)
# ═══════════════════════════════════════════════════════════════════════════════
def auto_sync_hari_libur_if_needed(tahun):
    """
    Cek apakah hari libur untuk tahun tertentu sudah ada di database.
    Jika belum, otomatis sync dari API Nager.Date.
    Returns: (success: bool, message: str)
    """
    # Cek apakah sudah ada data hari libur untuk tahun ini
    existing_count = HariLibur.objects.filter(tanggal__year=tahun).count()
    
    if existing_count > 0:
        return True, f"Hari libur tahun {tahun} sudah ada ({existing_count} data)"
    
    try:
        # Fetch dari API Nager.Date
        url = f"https://date.nager.at/api/v3/PublicHolidays/{tahun}/ID"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        holidays = response.json()
        created_count = 0
        
        for holiday in holidays:
            tanggal = holiday['date']
            nama_libur = holiday.get('localName', holiday.get('name', 'Hari Libur'))
            
            # Skip jika sudah ada
            if HariLibur.objects.filter(tanggal=tanggal).exists():
                continue
            
            # Tentukan jenis libur
            jenis = 'nasional'
            if 'Cuti Bersama' in nama_libur or 'Joint Holiday' in nama_libur:
                jenis = 'cuti_bersama'
            
            HariLibur.objects.create(
                tanggal=tanggal,
                keterangan=nama_libur,
                jenis=jenis
            )
            created_count += 1
        
        return True, f"Auto-sync berhasil: {created_count} hari libur tahun {tahun} ditambahkan"
    
    except Exception as e:
        return False, f"Auto-sync gagal: {str(e)}"


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
            source='manual'
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
    text = re.sub(r'^(Senin|Selasa|Rabu|Kamis|Jumat|Sabtu|Minggu),?\s*', '', text, flags=re.IGNORECASE)
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
    
    if ';' in text:
        return [n.strip() for n in text.split(';') if n.strip()]
    
    if '\n' in text:
        return [n.strip() for n in text.split('\n') if n.strip()]
    
    text = re.sub(r'\s+', ' ', text).strip()
    
    pattern = r'((?:dr\.?|drg\.?)?\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s*,\s*)?(?:S\.Tr\.Keb|S\.Kep\.?\s*,?\s*Ners|AMK|SKM|A\.Md\.Keb|A\.Md\.KL|S\.Gz|A\.Md\.Gz|S\.Farm\.?\s*,?\s*Apt|S\.E|S\.T|AMd\.?\s*RMIK|S\.ST|S\.Tr\.Kes|A\.Md\.AK|A\.Md\.Farm|A\.Md\.Kep|Amd\.?\s*Kep|Am\.?\s*Keb|dr\.?|drg\.?)?)'
    matches = re.findall(pattern, text)
    if len(matches) > 1:
        return [m.strip() for m in matches if m.strip()]
    
    return [text] if text else []


# ─── Sync Google Sheets ──────────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_google_sheets(request):
    url = request.data.get('csv_url', '').strip()
    mode = request.data.get('mode', 'append')

    if not url:
        return Response({'error': 'Parameter csv_url diperlukan'}, status=400)

    try:
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

        df_check = pd.read_csv(StringIO(resp.text))
        df_check.columns = [c.lower().strip() for c in df_check.columns]
        
        is_flat_format = all(col in df_check.columns for col in ['tanggal', 'lokasi', 'kegiatan', 'penyerta'])
        
        if is_flat_format:
            return _process_flat_format(df_check, mode)
        else:
            df_pivot = pd.read_csv(StringIO(resp.text), header=None)
            return _process_pivot_format(df_pivot, mode)

    except requests.exceptions.Timeout:
        return Response({'error': 'Timeout saat mengambil data dari Google Sheets'}, status=504)
    except requests.exceptions.HTTPError as e:
        return Response({'error': f'Gagal mengambil spreadsheet: {e}'}, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


def _process_flat_format(df, mode):
    """Proses format flat dengan perbaikan tanggal DD/MM/YYYY"""
    df = df.dropna(subset=['tanggal', 'lokasi'])

    if mode == 'replace':
        Kegiatan.objects.filter(source='google_sheet').delete()
    
    created = 0
    skipped = 0
    errors = []
    
    for i, row in df.iterrows():
        try:
            tanggal_raw = str(row['tanggal']).strip()
            
            # PERBAIKAN UTAMA: Paksa format Indonesia DD/MM/YYYY
            if re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}', tanggal_raw):
                tgl = pd.to_datetime(tanggal_raw, dayfirst=True, errors='coerce').date()
            else:
                tgl = pd.to_datetime(tanggal_raw, errors='coerce').date()

            if pd.isna(tgl):
                errors.append(f'Baris {i+2}: Format tanggal tidak dikenali ({tanggal_raw})')
                continue

            lok = str(row['lokasi']).strip()
            keg = capitalisasi_judul(str(row['kegiatan']).strip())
            peny = str(row.get('penyerta', '')).strip()

            kat = str(row.get('kategori', 'luar_gedung')).strip().lower()
            if kat not in ['dalam_gedung', 'luar_gedung']:
                kat = 'luar_gedung'

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
                source='google_sheet'
            )
            created += 1
        except Exception as e:
            errors.append(f'Baris {i+2}: {str(e)}')

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
    """Proses format pivot"""
    if df.empty:
        return Response({'error': 'File CSV kosong'}, status=400)

    if mode == 'replace':
        deleted_count, _ = Kegiatan.objects.filter(source='google_sheet').delete()

    created = 0
    skipped = 0
    errors = []
    
    current_kategori = 'dalam_gedung'
    current_lokasi = 'Dalam Gedung'
    
    header_row_idx = -1
    date_columns = {}
    
    for idx, row in df.iterrows():
        val_a = str(row[0]).strip().upper()
        if 'RUANG PELAYANAN' in val_a or 'DALAM GEDUNG' in val_a:
            current_kategori = 'dalam_gedung'
            current_lokasi = 'Dalam Gedung'
            continue
        elif 'LUAR GEDUNG' in val_a:
            current_kategori = 'luar_gedung'
            current_lokasi = 'Luar Gedung'
            continue
            
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

    schedule_data = {}
    current_activity = ""

    for idx in range(header_row_idx + 1, len(df)):
        row = df.iloc[idx]
        activity_name = str(row[0]).strip()
        
        if (activity_name == '' or activity_name.lower() == 'nan') and \
           all(str(row[i]).strip().lower() in ['nan', 'none', ''] for i in date_columns.keys()):
            continue

        if activity_name == '' or activity_name.lower() == 'nan':
            activity_name = current_activity
        else:
            current_activity = activity_name
            if activity_name not in schedule_data:
                schedule_data[activity_name] = {'kategori': current_kategori, 'dates': {}}

        for col_idx, date_str in date_columns.items():
            if col_idx < len(row):
                cell_value = str(row[col_idx]).strip()
                if cell_value and cell_value.lower() not in ['nan', 'none', '']:
                    names = split_names(cell_value)
                    
                    if date_str not in schedule_data[activity_name]['dates']:
                        schedule_data[activity_name]['dates'][date_str] = []
                    
                    schedule_data[activity_name]['dates'][date_str].extend(names)

    for activity, data in schedule_data.items():
        kategori = data['kategori']
        for date_str, names in data['dates'].items():
            try:
                final_penyerta = "; ".join(names)
                
                if kategori == 'dalam_gedung':
                    final_lokasi = 'Dalam Gedung'
                    sub_kat = ''
                else:
                    final_lokasi = activity
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
                    source='google_sheet'
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


# ─── Pencarian User Umum ─────────────────────────────────────────────────────
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


# ─── Jadwal Terdekat ─────────────────────────────────────────────────────────
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


# ─── Randomize Jadwal Dalam Gedung ───────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def randomize_dalam_gedung(request):
    try:
        from .randomize_logic import generate_jadwal_dalam_gedung
    except ImportError as e:
        return Response({
            'error': f'Import error: {str(e)}',
            'traceback': traceback.format_exc()
        }, status=500)
    
    bulan = request.data.get('bulan')
    tahun = request.data.get('tahun')
    loka_karya = request.data.get('loka_karya', False)
    
    if not all([bulan, tahun]):
        return Response({'error': 'bulan dan tahun diperlukan'}, status=400)

    try:
        bulan = int(bulan)
        tahun = int(tahun)
    except ValueError:
        return Response({'error': 'bulan dan tahun harus angka'}, status=400)

    # ═══════════════════════════════════════════════════════════════════════════
    # AUTO SYNC HARI LIBUR (BARU)
    # ═══════════════════════════════════════════════════════════════════════════
    sync_success, sync_message = auto_sync_hari_libur_if_needed(tahun)
    if not sync_success:
        return Response({
            'warning': sync_message,
            'details': 'Hari libur mungkin tidak lengkap, jadwal bisa tidak akurat'
        }, status=200)  # Return 200 dengan warning, bukan error

    try:
        jadwal_list, skipped = generate_jadwal_dalam_gedung(bulan, tahun, loka_karya)

        if not jadwal_list:
            return Response({
                'error': 'Gagal generate jadwal',
                'skipped': skipped
            }, status=400)

        preview = request.data.get('preview', True)

        if preview:
            return Response({
                'message': f'Berhasil generate {len(jadwal_list)} jadwal',
                'jadwal': jadwal_list,
                'skipped': skipped,
                'sync_info': sync_message  # Info sync hari libur
            })
        else:
            # Save dengan bulk_create
            try:
                with transaction.atomic():
                    existing_keys = set(
                        Kegiatan.objects.filter(
                            tanggal__in=[j['tanggal'] for j in jadwal_list]
                        ).values_list('tanggal', 'lokasi', 'kegiatan')
                    )
                    
                    new_jadwal = [
                        j for j in jadwal_list
                        if (j['tanggal'], j['lokasi'], j['kegiatan']) not in existing_keys
                    ]
                    
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
                    'saved': len(new_jadwal),
                    'sync_info': sync_message
                })
            
            except Exception as db_error:
                return Response({
                    'error': f'Gagal menyimpan: {str(db_error)}',
                    'traceback': traceback.format_exc()
                }, status=500)
    
    except Exception as e:
        return Response({
            'error': f'Gagal generate: {str(e)}',
            'traceback': traceback.format_exc()
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def randomize_luar_gedung_bok(request):
    """Generate jadwal luar gedung kategori BOK saja"""
    try:
        from .randomize_logic import generate_jadwal_luar_gedung_bok
    except ImportError as e:
        return Response({
            'error': f'Import error: {str(e)}',
            'traceback': traceback.format_exc()
        }, status=500)
    
    bulan = request.data.get('bulan')
    tahun = request.data.get('tahun')
    
    if not all([bulan, tahun]):
        return Response({'error': 'bulan dan tahun diperlukan'}, status=400)

    try:
        bulan = int(bulan)
        tahun = int(tahun)
    except ValueError:
        return Response({'error': 'bulan dan tahun harus angka'}, status=400)

    # ═══════════════════════════════════════════════════════════════════════════
    # AUTO SYNC HARI LIBUR (BARU)
    # ═══════════════════════════════════════════════════════════════════════════
    sync_success, sync_message = auto_sync_hari_libur_if_needed(tahun)
    if not sync_success:
        return Response({
            'warning': sync_message,
            'details': 'Hari libur mungkin tidak lengkap, jadwal bisa tidak akurat'
        }, status=200)

    try:
        # Generate dengan error handling
        jadwal_list, skipped = generate_jadwal_luar_gedung_bok(bulan, tahun)
        
        # Cek apakah ada error di skipped
        if skipped and any('Error' in s for s in skipped):
            return Response({
                'error': 'Gagal generate jadwal BOK',
                'details': skipped[0] if skipped else 'Unknown error'
            }, status=500)

        if not jadwal_list:
            return Response({
                'error': 'Gagal generate jadwal BOK',
                'skipped': skipped
            }, status=400)

        preview = request.data.get('preview', True)

        if preview:
            return Response({
                'message': f'Berhasil generate {len(jadwal_list)} jadwal BOK',
                'jadwal': jadwal_list,
                'skipped': skipped,
                'sync_info': sync_message
            })
        else:
            try:
                with transaction.atomic():
                    existing_keys = set(
                        Kegiatan.objects.filter(
                            tanggal__in=[j['tanggal'] for j in jadwal_list]
                        ).values_list('tanggal', 'lokasi', 'kegiatan')
                    )
                    
                    new_jadwal = [
                        j for j in jadwal_list
                        if (j['tanggal'], j['lokasi'], j['kegiatan']) not in existing_keys
                    ]
                    
                    objects_to_create = [
                        Kegiatan(
                            tanggal=j['tanggal'],
                            lokasi=j['lokasi'],
                            kegiatan=j['kegiatan'],
                            penyerta=j['penyerta'],
                            kategori='luar_gedung',
                            sub_kategori='bok',
                            is_auto_generated=True,
                            source='randomize'
                        )
                        for j in new_jadwal
                    ]
                    
                    Kegiatan.objects.bulk_create(objects_to_create, batch_size=100)
                
                return Response({
                    'message': f'Berhasil menyimpan {len(new_jadwal)} jadwal BOK',
                    'saved': len(new_jadwal),
                    'sync_info': sync_message
                })
            
            except Exception as db_error:
                return Response({
                    'error': f'Gagal menyimpan: {str(db_error)}',
                    'traceback': traceback.format_exc()
                }, status=500)
    
    except Exception as e:
        return Response({
            'error': f'Gagal generate: {str(e)}',
            'traceback': traceback.format_exc()
        }, status=500)


# ─── Randomize Jadwal Luar Gedung - Lainnya ──────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def randomize_luar_gedung_lainnya(request):
    """Generate jadwal luar gedung kategori lainnya (Posyandu, Posbindu, UKK, dll)"""
    try:
        from .randomize_logic import generate_jadwal_luar_gedung_lainnya
    except ImportError as e:
        return Response({
            'error': f'Import error: {str(e)}',
            'traceback': traceback.format_exc()
        }, status=500)
    
    bulan = request.data.get('bulan')
    tahun = request.data.get('tahun')
    
    if not all([bulan, tahun]):
        return Response({'error': 'bulan dan tahun diperlukan'}, status=400)

    try:
        bulan = int(bulan)
        tahun = int(tahun)
    except ValueError:
        return Response({'error': 'bulan dan tahun harus angka'}, status=400)

    # ═══════════════════════════════════════════════════════════════════════════
    # AUTO SYNC HARI LIBUR (BARU)
    # ═══════════════════════════════════════════════════════════════════════════
    sync_success, sync_message = auto_sync_hari_libur_if_needed(tahun)
    if not sync_success:
        return Response({
            'warning': sync_message,
            'details': 'Hari libur mungkin tidak lengkap, jadwal bisa tidak akurat'
        }, status=200)

    try:
        jadwal_list, skipped = generate_jadwal_luar_gedung_lainnya(bulan, tahun)

        if not jadwal_list:
            return Response({
                'error': 'Gagal generate jadwal',
                'skipped': skipped
            }, status=400)

        preview = request.data.get('preview', True)

        if preview:
            return Response({
                'message': f'Berhasil generate {len(jadwal_list)} jadwal',
                'jadwal': jadwal_list,
                'skipped': skipped,
                'sync_info': sync_message
            })
        else:
            try:
                with transaction.atomic():
                    existing_keys = set(
                        Kegiatan.objects.filter(
                            tanggal__in=[j['tanggal'] for j in jadwal_list]
                        ).values_list('tanggal', 'lokasi', 'kegiatan')
                    )
                    
                    new_jadwal = [
                        j for j in jadwal_list
                        if (j['tanggal'], j['lokasi'], j['kegiatan']) not in existing_keys
                    ]
                    
                    objects_to_create = [
                        Kegiatan(
                            tanggal=j['tanggal'],
                            lokasi=j['lokasi'],
                            kegiatan=j['kegiatan'],
                            penyerta=j['penyerta'],
                            kategori='luar_gedung',
                            sub_kategori=j.get('sub_kategori', 'lainnya'),
                            is_auto_generated=True,
                            source='randomize'
                        )
                        for j in new_jadwal
                    ]
                    
                    Kegiatan.objects.bulk_create(objects_to_create, batch_size=100)
                
                return Response({
                    'message': f'Berhasil menyimpan {len(new_jadwal)} jadwal',
                    'saved': len(new_jadwal),
                    'sync_info': sync_message
                })
            
            except Exception as db_error:
                return Response({
                    'error': f'Gagal menyimpan: {str(db_error)}',
                    'traceback': traceback.format_exc()
                }, status=500)
    
    except Exception as e:
        return Response({
            'error': f'Gagal generate: {str(e)}',
            'traceback': traceback.format_exc()
        }, status=500)


# ─── Simpan Jadwal dengan Edit ───────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def simpan_jadwal_with_edit(request):
    """Simpan jadwal yang sudah diedit dari preview"""
    jadwal_list = request.data.get('jadwal', [])
    
    if not jadwal_list:
        return Response({'error': 'Tidak ada jadwal untuk disimpan'}, status=400)
    
    try:
        with transaction.atomic():
            saved_count = 0
            for item in jadwal_list:
                Kegiatan.objects.create(
                    tanggal=item.get('tanggal'),
                    lokasi=item.get('lokasi'),
                    kegiatan=item.get('kegiatan'),
                    penyerta=item.get('penyerta'),
                    kategori=item.get('kategori', 'luar_gedung'),
                    sub_kategori=item.get('sub_kategori', 'lainnya'),
                    is_auto_generated=True,
                    source='randomize'
                )
                saved_count += 1
        
        return Response({
            'message': f'Berhasil menyimpan {saved_count} jadwal',
            'saved': saved_count
        })
    
    except Exception as e:
        return Response({
            'error': f'Gagal menyimpan: {str(e)}',
            'traceback': traceback.format_exc()
        }, status=500)


# ─── Hari Libur CRUD ─────────────────────────────────────────────────────────
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


# ─── Sync Hari Libur dari API Eksternal ──────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_hari_libur_api(request):
    """
    Sync hari libur nasional Indonesia dari Nager.Date API
    Endpoint: POST /api/sync-hari-libur-api/
    Body: {"tahun": 2026}
    """
    tahun = request.data.get('tahun')
    
    if not tahun:
        return Response({'error': 'tahun diperlukan'}, status=400)
    
    try:
        tahun = int(tahun)
    except ValueError:
        return Response({'error': 'tahun harus angka'}, status=400)
    
    try:
        # Fetch dari Nager.Date API (gratis, no API key)
        url = f"https://date.nager.at/api/v3/PublicHolidays/{tahun}/ID"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        holidays = response.json()
        created_count = 0
        skipped_count = 0
        
        for holiday in holidays:
            tanggal = holiday['date']  # Format: '2026-01-01'
            nama_libur = holiday.get('localName', holiday.get('name', 'Hari Libur'))
            
            # Cek apakah sudah ada di database
            if HariLibur.objects.filter(tanggal=tanggal).exists():
                skipped_count += 1
                continue
            
            # Tentukan jenis libur
            jenis = 'nasional'
            if 'Cuti Bersama' in nama_libur or 'Joint Holiday' in nama_libur:
                jenis = 'cuti_bersama'
            
            HariLibur.objects.create(
                tanggal=tanggal,
                keterangan=nama_libur,
                jenis=jenis
            )
            created_count += 1
        
        return Response({
            'message': f'Sinkronisasi hari libur tahun {tahun} berhasil',
            'created': created_count,
            'skipped': skipped_count,
            'total': len(holidays)
        })
    
    except requests.exceptions.Timeout:
        return Response({'error': 'Timeout saat mengakses API'}, status=504)
    except requests.exceptions.HTTPError as e:
        return Response({'error': f'API error: {str(e)}'}, status=502)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


# ─── List Hari Libur per Tahun ───────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_hari_libur_tahun(request, tahun):
    """
    List semua hari libur di tahun tertentu
    Endpoint: GET /api/hari-libur-tahun/2026/
    """
    try:
        tahun = int(tahun)
        libur_list = HariLibur.objects.filter(tanggal__year=tahun).order_by('tanggal')
        
        data = [{
            'tanggal': str(l.tanggal),
            'keterangan': l.keterangan,
            'jenis': l.jenis
        } for l in libur_list]
        
        return Response({
            'tahun': tahun,
            'total': len(data),
            'hari_libur': data
        })
    
    except ValueError:
        return Response({'error': 'tahun harus angka'}, status=400)


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT BARU: AUTO SYNC HARI LIBUR TAHUN DEPAN (BARU)
# ═══════════════════════════════════════════════════════════════════════════════
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def auto_sync_hari_libur_tahun_depan(request):
    """
    Sync hari libur untuk tahun depan secara otomatis.
    Dipanggil di akhir tahun untuk persiapan tahun depan.
    Endpoint: POST /api/auto-sync-hari-libur-tahun-depan/
    """
    current_year = timezone.now().year
    next_year = current_year + 1
    
    success, message = auto_sync_hari_libur_if_needed(next_year)
    
    if success:
        return Response({
            'message': message,
            'tahun': next_year
        })
    else:
        return Response({
            'error': message,
            'tahun': next_year
        }, status=500)


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINT BARU: SYNC HARI LIBUR MULTI-TAHUN (BARU)
# ═══════════════════════════════════════════════════════════════════════════════
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_hari_libur_range(request):
    """
    Sync hari libur untuk beberapa tahun sekaligus.
    Endpoint: POST /api/sync-hari-libur-range/
    Body: {"tahun_mulai": 2024, "tahun_akhir": 2026}
    """
    tahun_mulai = request.data.get('tahun_mulai')
    tahun_akhir = request.data.get('tahun_akhir')
    
    if not tahun_mulai or not tahun_akhir:
        return Response({'error': 'tahun_mulai dan tahun_akhir diperlukan'}, status=400)
    
    try:
        tahun_mulai = int(tahun_mulai)
        tahun_akhir = int(tahun_akhir)
        
        if tahun_mulai > tahun_akhir:
            return Response({'error': 'tahun_mulai harus lebih kecil dari tahun_akhir'}, status=400)
        
        results = []
        for tahun in range(tahun_mulai, tahun_akhir + 1):
            success, message = auto_sync_hari_libur_if_needed(tahun)
            results.append({
                'tahun': tahun,
                'success': success,
                'message': message
            })
        
        return Response({
            'message': f'Sync selesai untuk {len(results)} tahun',
            'results': results
        })
    
    except ValueError:
        return Response({'error': 'tahun harus angka'}, status=400)