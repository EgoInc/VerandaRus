from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AccommodationSerializer


class HousesListView(APIView):
    serializer_class = AccommodationSerializer

    def get(self, request):
        # TODO: return list of accommodations with filters/pagination
        return Response(
            {"detail": "TODO: implement accommodations list"},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )
