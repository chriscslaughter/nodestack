from django.urls import path
from coldstoragetransfers import views

urlpatterns = [
    path('transfers/', views.transfer_list, name='transfers'),
    path('transfers/new', views.NewTransferView.as_view(), name='new_transfer'),
    path('transfers/sign/<slug:transfer_id>', views.SignTransferView.as_view(), name='sign_transfer')
]
