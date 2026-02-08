from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import BookingCreateSerializer


class BookingCreateView(APIView):
    serializer_class = BookingCreateSerializer

    def post(self, request):
        # TODO: create booking, validate dates, compute price, and persist
        return Response(
            {"detail": "TODO: implement booking creation"},
            status=status.HTTP_501_NOT_IMPLEMENTED,
        )
