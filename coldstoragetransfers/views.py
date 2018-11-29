from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views import View
from django.shortcuts import render
from django.contrib.auth.models import User

from nodestack.resource import get_redis
from coldstoragetransfers.models import TransferRequest, TransferRequestSignature
from coldstoragetransfers.forms import TransferRequestForm, TransferRequestSignatureForm

@user_passes_test(lambda u: u.is_superuser, login_url='/admin')
def transfer_list(request):
    transfers = TransferRequest.objects.order_by('-created_at').all()
    context = {'transfers': transfers}
    return render(request, 'transfers.html', )
    pass

class NewTransferView(View):
    def get(self, request):
        return render(request,
                      'new_transfer.html',
                      {'form': TransferRequestForm})

    def post(self, request):
        form = TransferRequestForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user
            transfer_request = form.save()
            return redirect('sign_transfer', transfer_id=transfer_request.id)
        return render(request,
                      'new_transfer.html',
                      {'form': form})

class SignTransferView(View):
    def get(self, request, transfer_id):
        form = TransferRequestSignatureForm
        lock_key = 'multisig-sign-%s' % transfer_id
        if get_redis().get(lock_key):
            return HttpResponse('someone else is signing this transfer at the moment')
        print(get_redis().get(lock_key))
        with get_redis().lock(lock_key, timeout=300):
            render (request, 'sign_transfer.html', {'form': form})

    def post(self, request):
        pass
