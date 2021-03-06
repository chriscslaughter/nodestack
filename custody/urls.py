from django.conf.urls import url, include
from django.views.decorators.csrf import csrf_exempt
from django.urls import path

from rest_framework.schemas import get_schema_view
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from . import views

urlpatterns = [
  url(r'^$', get_schema_view()),
  path("<slug:coin>/transactions", views.list_transactions, name='transactions'),
  path("<slug:coin>/status", views.get_status, name='status'),
  path("<slug:coin>/deposits/address", views.get_deposit_address, name='deposits_address'),
  path("<slug:coin>/withdrawals/submit", csrf_exempt(views.submit_withdrawal), name='submit_withdrawal'),
  # path("<slug:coin>/deposits", views.Deposits.as_view(), name='deposits'),
  # path("<slug:coin>/deposits/cold_storage_transfer", views.DepositsColdStorageTransfer.as_view(), name='deposits_cold_storage_transfer'),
  # path("<slug:coin>/withdrawals", views.Withdrawals.as_view(), name='withdrawals'),
  # path("<slug:coin>/withdrawals/address", views.WithdrawalsAddress.as_view(), name='withdrawals_address'),
  # path("<slug:coin>/withdrawals/withdrawal", views.WithdrawalsWithdrawal.as_view(), name='withdrawals_withdrawal')
]

urlpatterns += staticfiles_urlpatterns()
