from django.contrib import admin
from django.urls import path, include
from financas import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', views.inicio, name='inicio'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login_view, name='login'),
    path('sair/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('transacoes/', views.transacao_lista, name='transacao_lista'),
    path('transacoes/nova/', views.transacao_criar, name='transacao_criar'),
    path('transacoes/<int:pk>/editar/', views.transacao_editar, name='transacao_editar'),
    path('transacoes/<int:pk>/excluir/', views.transacao_excluir, name='transacao_excluir'),
    path('categorias/', views.categoria_lista, name='categoria_lista'),
    path('categorias/nova/', views.categoria_criar, name='categoria_criar'),
    path('metas/', views.meta_lista, name='meta_lista'),
    path('metas/nova/', views.meta_criar, name='meta_criar'),
    path('metas/<int:pk>/editar/', views.meta_editar, name='meta_editar'),
    path('relatorios/', views.relatorios, name='relatorios'),
]
