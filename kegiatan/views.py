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
from .models import Kegiatan, HariLibur
from .serializers import KegiatanSerializer, HariLiburSerializer
from .utils import capitalisasi_judul
import pandas as pd
import requests
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
        serializer.save(kegiatan=capitalisasi_judul(nama))

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


# ─── Sync Google Sheets (UPDATED - support kategori) ────────────────────────
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

        df = pd.read_csv(StringIO(resp.text))
        df.columns = [c.lower().strip() for c in df.columns]

        required = ['tanggal', 'lokasi', 'kegiatan', 'penyerta']
        missing = [col for col in required if col not in df.columns]
        if missing:
            return Response(
                {'error': f'Kolom tidak ditemukan: {missing}. Kolom yang ada: {list(df.columns)}'},
                status=400
            )

        df = df.dropna(subset=['tanggal', 'lokasi'])

        if mode == 'replace':
            Kegiatan.objects.all().delete()

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
                    sub_kategori=sub_kat
                )
                created += 1
            except Exception as e:
                errors.append(f'Baris {i+2}: {e}')

        msg = f'{created} data baru diimpor.'
        if mode == 'replace':
            msg = 'Data lama dihapus. ' + msg
        elif skipped > 0:
            msg += f' {skipped} data sudah ada dan dilewati.'
        result = {'message': msg}
        if errors:
            result['peringatan'] = errors
        return Response(result)

    except requests.exceptions.Timeout:
        return Response({'error': 'Timeout saat mengambil data dari Google Sheets'}, status=504)
    except requests.exceptions.HTTPError as e:
        return Response({'error': f'Gagal mengambil spreadsheet: {e}'}, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=500)


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


# ─── Pencarian User Umum (UPDATED - include kategori) ───────────────────────
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
    } for k in qs]
    return Response(data)


# ─── Jadwal Terdekat (UPDATED - include kategori) ───────────────────────────
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


# ─── Randomize Dalam Gedung (NEW) ───────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def randomize_dalam_gedung(request):
    from .randomize_logic import generate_jadwal_dalam_gedung

    bulan = request.data.get('bulan')
    tahun = request.data.get('tahun')
    minggu = request.data.get('minggu')
    loka_karya = request.data.get('loka_karya', False)

    if not all([bulan, tahun, minggu]):
        return Response({'error': 'bulan, tahun, dan minggu diperlukan'}, status=400)

    try:
        bulan = int(bulan)
        tahun = int(tahun)
        minggu = int(minggu)
    except ValueError:
        return Response({'error': 'bulan, tahun, minggu harus angka'}, status=400)

    jadwal_list, skipped = generate_jadwal_dalam_gedung(bulan, tahun, minggu, loka_karya)

    if not jadwal_list:
        return Response({'error': 'Gagal generate jadwal', 'skipped': skipped}, status=400)

    preview = request.data.get('preview', True)

    if preview:
        return Response({
            'message': f'Berhasil generate {len(jadwal_list)} jadwal',
            'jadwal': jadwal_list,
            'skipped': skipped
        })
    else:
        saved = 0
        for j in jadwal_list:
            if not Kegiatan.objects.filter(
                tanggal=j['tanggal'],
                lokasi=j['lokasi'],
                kegiatan=j['kegiatan']
            ).exists():
                Kegiatan.objects.create(
                    tanggal=j['tanggal'],
                    lokasi=j['lokasi'],
                    kegiatan=j['kegiatan'],
                    penyerta=j['penyerta'],
                    kategori=j['kategori'],
                    is_auto_generated=True
                )
                saved += 1

        return Response({
            'message': f'Berhasil menyimpan {saved} jadwal',
            'skipped': skipped
        })


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