from rest_framework import views, permissions
from django.http import JsonResponse

class Status(views.APIView):
    """
    Get the status of the specific node.
    """
    def get(self, request, coin, format=None):
        return JsonResponse({'coin': coin}, safe=False)