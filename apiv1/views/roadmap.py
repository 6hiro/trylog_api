from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from roadmap.models import RoadMapModel, StepModel, LookBackModel
from ..serializers import RoadMapSerializer, StepSerializer, LookBackSerializer
from ..permissions import IsOwnRoadmapOrReadOnly, IsOwnStepOrReadOnly,  IsOwnLookBackOrReadOnly


class RoadMapViewSet(viewsets.ModelViewSet):
    queryset = RoadMapModel.objects.all()
    serializer_class = RoadMapSerializer
    permission_classes = (IsOwnRoadmapOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(challenger=self.request.user)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return RoadMapModel.objects.filter(Q(is_public="public") | Q(challenger=self.request.user))
        return RoadMapModel.objects.filter(is_public="public")


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def roadmap_user(request, id):
    roadmaps = RoadMapModel.objects.filter(Q(challenger=id), Q(
        is_public="public") | Q(challenger=request.user))
    serializer = RoadMapSerializer(roadmaps, many=True)
    return Response(serializer.data)


class StepViewSet(viewsets.ModelViewSet):
    queryset = StepModel.objects.all()
    serializer_class = StepSerializer
    permission_classes = (IsOwnStepOrReadOnly,)

    def perform_create(self, serializer):
        roadmap = RoadMapModel.objects.get(id=self.request.data["roadmap"])
        steps = roadmap.step.all()
        order_list = [step.order for step in steps]
        max_order = max(order_list, default=0)
        serializer.save(
            roadmap=roadmap, order=(max_order+1))

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return StepModel.objects.filter(Q(roadmap__is_public="public") | Q(roadmap__challenger__id=self.request.user.id))
        return StepModel.objects.filter(roadmap__is_public="public")


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def steps(request, id):
    steps = StepModel.objects.filter(Q(roadmap__id=id), Q(roadmap__is_public="public")
                                     | Q(roadmap__challenger__id=request.user.id))
    serializer = StepSerializer(steps, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
def change_step_order(request):
    roadmap = RoadMapModel.objects.get(id=request.data[0]["roadmap"])

    if request.user == roadmap.challenger:
        serializer = StepSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        old_steps = StepModel.objects.filter(
            roadmap__id=request.data[0]["roadmap"])
        new_steps = request.data
        update_list = []
        for i in range(len(old_steps)):
            new_step = list(filter(lambda x: x["id"] ==
                                   str(old_steps[i].id), new_steps))[0]
            if old_steps[i].order != new_step["order"]:
                old_steps[i].order = new_step["order"]
                update_list.append(old_steps[i])

        StepModel.objects.bulk_update(update_list, fields=["order"])
        return Response(serializer.data)
    return Response(status=status.HTTP_403_FORBIDDEN)


class LookBackViewSet(viewsets.ModelViewSet):
    # queryset = LookBackModel.objects.filter(step__roadmap__is_public="public")
    queryset = LookBackModel.objects.all()
    serializer_class = LookBackSerializer
    permission_classes = (IsOwnLookBackOrReadOnly,)

    def perform_create(self, serializer):
        step = StepModel.objects.get(
            id=self.request.data["step"])
        serializer.save(step=step)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return LookBackModel.objects.filter(Q(step__roadmap__is_public="public") | Q(step__roadmap__challenger__id=self.request.user.id))
        return LookBackModel.objects.filter(step__roadmap__is_public="public")


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def lookbacks(request, id):
    lookbacks = LookBackModel.objects.filter(
        step__id=id, step__roadmap__challenger__id=request.user.id)
    serializer = LookBackSerializer(lookbacks, many=True)
    return Response(serializer.data)
