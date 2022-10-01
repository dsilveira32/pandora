from django.forms.models import model_to_dict
from rest_framework.decorators import api_view
from rest_framework.response import Response


from shared.models import Contest
from shared.serializers import ContestSerializer

@api_view(['POST'])
def api_home(request, *args, **kwargs):
    """
    DRF API View
    """
    serializer = ContestSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        # instance = serializer.save()
        # instance = form.save()
        print(serializer.data)
        return Response(serializer.data)
    return Response({"invalid": "not good data"}, status=400)


