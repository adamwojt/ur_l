from rest_framework import status
from rest_framework.generics import GenericAPIView, ListAPIView
from rest_framework.response import Response

from .models import Url
from .serializers import UrlSerializer


class UrlList(ListAPIView):
    """
    get:
    Return a list of all the existing urls.

    post:
    Create a new short url.
    """

    queryset = Url.objects.all()
    serializer_class = UrlSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED,)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UrlDetail(GenericAPIView):
    """
    get:
    Return the given url using token.

    put:
    Update long url (long_url body needed)

    delete:
    Delete url and clear cache
    """

    lookup_field = "token"
    queryset = Url.objects.all()
    serializer_class = UrlSerializer

    def get(self, request, token):
        long_url = Url.objects.get_long_url(token)
        if not long_url:
            return Response(status=status.HTTP_404_NOT_FOUND)
        data = {
            "token": token,
            "long_url": long_url,
            "short_url": token,
        }
        if request.query_params.get("clicks") == "1":
            # Calling db, cache only not possible.
            # That's why it's optional
            url = Url.objects.get(token=token)
            data.update(click_count=url.clicks.count(), click_limit=url.click_limit)

        serializer = self.get_serializer(data, context={"request": request})

        return Response(serializer.data)

    def put(self, request, **kwargs):
        url = self.get_object()
        serializer = self.get_serializer(url, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, *args, **kwargs):
        url = self.get_object()
        url.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
