from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from .models import Venda
from .serializers import VendaSerializer


class VendaViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   GenericViewSet):
    """Registro (RF-06), listagem (RF-07) e consulta (RF-08) de vendas.

    Vendas não são atualizadas nem excluídas pela API.
    """
    queryset = Venda.objects.prefetch_related('itens__produto').order_by('id')
    serializer_class = VendaSerializer
