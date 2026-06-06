from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.throttling import AnonRateThrottle
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Kegiatan
from .serializers import KegiatanSerializer
from .utils import capitalisasi_judul
import pandas as pd
import requests
from io import StringIO


# ─── Throttle khusus untuk login ─────────────────────────────────────────────
class LoginRateThrottle(AnonRateThrottle):
    scope = 'login'


# ─── ViewSet CRUD (hanya admin dengan token) ─────────────────────────────────
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


# ─── Login → kembalikan token ────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([LoginRateThrottle])
def login_view(request):
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '')

    # Validasi input dasar
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
        # Buat atau ambil token yang sudah ada
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


# ─── Logout → hapus token ────────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    # Hapus token dari database sehingga tidak bisa dipakai lagi
    try:
        request.user.auth_token.delete()
    except Exception:
        pass
    return Response({'message': 'Logout berhasil'})


# ─── Sync Google Sheets ──────────────────────────────────────────────────────
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_google_sheets(request):
    url = request.data.get('csv_url', '').strip()
    if not url:
        return Response({'error': 'Parameter csv_url diperlukan'}, status=400)

    try:
        # Normalisasi URL Google Sheets ke format CSV
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

        # Normalisasi nama kolom (lowercase + strip spasi)
        df.columns = [c.lower().strip() for c in df.columns]

        required = ['tanggal', 'lokasi', 'kegiatan', 'penyerta']
        missing = [col for col in required if col not in df.columns]
        if missing:
            return Response(
                {'error': f'Kolom tidak ditemukan: {missing}. Kolom yang ada: {list(df.columns)}'},
                status=400
            )

        # Bersihkan baris kosong
        df = df.dropna(subset=['tanggal', 'lokasi'])

        # Overwrite semua data
        Kegiatan.objects.all().delete()
        created = 0
        errors = []
        for i, row in df.iterrows():
            try:
                Kegiatan.objects.create(
                    tanggal=pd.to_datetime(row['tanggal']).date(),
                    lokasi=str(row['lokasi']).strip(),
                    kegiatan=capitalisasi_judul(str(row['kegiatan']).strip()),
                    penyerta=str(row['penyerta']).strip()
                )
                created += 1
            except Exception as e:
                errors.append(f'Baris {i+2}: {e}')

        result = {'message': f'{created} data berhasil diimpor.'}
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
    tgl  = request.query_params.get('tanggal')
    lok  = request.query_params.get('lokasi')
    keg  = request.query_params.get('kegiatan')
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


# ─── Pencarian User Umum (publik, tidak perlu token) ─────────────────────────
@api_view(['GET'])
@permission_classes([AllowAny])
def search_user(request):
    qs = Kegiatan.objects.all()
    tgl  = request.query_params.get('tanggal')
    nama = request.query_params.get('nama')

    if tgl:
        qs = qs.filter(tanggal=tgl)
    if nama:
        qs = qs.filter(penyerta__icontains=nama)

    data = [
        {
            'tanggal': str(k.tanggal),
            'lokasi': k.lokasi,
            'kegiatan': k.kegiatan,
            'penyerta': k.penyerta,
        }
        for k in qs
    ]
    return Response(data)


# ─── Jadwal Terdekat (publik) ─────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([AllowAny])
def jadwal_terdekat(request):
    from django.utils import timezone
    today = timezone.now().date()
    qs = Kegiatan.objects.filter(tanggal__gte=today).order_by('tanggal')[:10]
    data = [
        {
            'tanggal': str(k.tanggal),
            'lokasi': k.lokasi,
            'kegiatan': k.kegiatan,
            'penyerta': k.penyerta,
        }
        for k in qs
    ]
    return Response(data)

# --- Verifikasi Token (untuk session persisten di FE) ---
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_token(request):
    return Response({'username': request.user.username})