from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'kegiatan', views.KegiatanViewSet, basename='kegiatan')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', views.login_view),
    path('logout/', views.logout_view),
    path('sync-sheets/', views.sync_google_sheets),
    path('search-admin/', views.search_admin),
    path('search-user/', views.search_user),
    path('jadwal-terdekat/', views.jadwal_terdekat),
    path('verify-token/', views.verify_token),
    path('delete-by-date/', views.delete_kegiatan_by_date),
    path('randomize-dalam-gedung/', views.randomize_dalam_gedung, name='randomize-dalam-gedung'),
    path('hari-libur/', views.hari_libur_list, name='hari-libur-list'),
    path('hari-libur/<int:pk>/', views.hari_libur_detail, name='hari-libur-detail'),
    path('randomize-luar-gedung-bok/', views.randomize_luar_gedung_bok, name='randomize_luar_gedung_bok'),
    path('randomize-luar-gedung-lainnya/', views.randomize_luar_gedung_lainnya, name='randomize_luar_gedung_lainnya'),
    path('simpan-jadwal-with-edit/', views.simpan_jadwal_with_edit, name='simpan_jadwal_with_edit'),
    path('sync-hari-libur-api/', views.sync_hari_libur_api, name='sync-hari-libur-api'),
    path('hari-libur-tahun/<int:tahun>/', views.list_hari_libur_tahun, name='hari-libur-tahun'),
    path('auto-sync-hari-libur-tahun-depan/', views.auto_sync_hari_libur_tahun_depan, name='auto-sync-hari-libur-tahun-depan'),
    path('sync-hari-libur-range/', views.sync_hari_libur_range, name='sync-hari-libur-range'),
]