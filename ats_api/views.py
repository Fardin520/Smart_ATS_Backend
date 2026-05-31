from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import Job, Application
from .serializers import JobSerializer, ApplicationSerializer, ApplicationListSerializer
from .tasks import process_resume


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.action == 'list':
            return ApplicationListSerializer
        return ApplicationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = serializer.save()

        # Fire background task — does NOT block the response
        process_resume.delay(application.id)

        return Response(
            {
                'message': 'Application submitted! Your resume is being processed.',
                'tracking_id': application.id,
                'status': application.status,
            },
            status=status.HTTP_201_CREATED
        )