from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.viewsets import ModelViewSet

from apps.accounts.models import Group
from apps.accounts.serializers import GroupSerializer
from apps.events.models import BaseEvent, Training, Exchange, Workshop, Travel, IMW
from apps.events.serializers import TravelSerializer, event_list_serializer_factory, \
    event_serializer_factory, event_public_serializer_factory
from common.permissions import can_change, can_add

__author__ = 'Sebastian Wozny'
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


class EventViewSet(ModelViewSet):
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    model = BaseEvent
    queryset = BaseEvent.objects.all()

    def get_serializer_class(self):
        if self.serializer_class:
            return self.serializer_class
        if can_add(self.request.user, self.model):
            return event_serializer_factory(self.model)
        if can_change(self.request.user, self.get_object()):
            return event_serializer_factory(self.model)
        return event_public_serializer_factory(self.model)

    def list(self, request, *args, **kwargs):
        self.serializer_class = event_list_serializer_factory(self.model)
        return super(EventViewSet, self).list(request, *args, **kwargs)


class TrainingViewSet(EventViewSet):
    queryset = Training.objects.all()
    model = Training


class ExchangeViewSet(EventViewSet):
    queryset = Exchange.objects.all()
    model = Exchange


class WorkshopViewSet(EventViewSet):
    queryset = Workshop.objects.all()
    model = Workshop
class IMWViewSet(EventViewSet):
    queryset = IMW.objects.all()
    model = IMW


class GroupViewSet(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]


class TravelViewSet(ModelViewSet):
    queryset = Travel.objects.all()
    serializer_class = TravelSerializer
