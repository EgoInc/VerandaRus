from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import EmptySerializer


class HealthView(APIView):
    serializer_class = EmptySerializer

    def get(self, request):
        return Response({"status": "ok"})
