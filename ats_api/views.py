from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import Job, Application
from .serializers import JobSerializer, ApplicationSerializer, ApplicationListSerializer
from .tasks import process_resume


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    @action(detail=True, methods=['get'], url_path='rankings')
    def rankings(self, request, pk=None):
        """
        Fetches all applications for this specific job and 
        ranks them automatically from highest AI score to lowest.
        URL path: /api/v1/jobs/<job_id>/rankings/
        """
        # 'pk' is automatically the job_id extracted from the URL
        ranked_applicants = Application.objects.filter(job_id=pk).order_by('-ai_score')
        
        if not ranked_applicants.exists():
            return Response(
                {"message": f"No applications found for job ID {pk}."}, 
                status=404
            )
            
        serializer = ApplicationSerializer(ranked_applicants, many=True)
        return Response({
            "job_id": pk,
            "total_applicants": ranked_applicants.count(),
            "rankings": serializer.data
        })


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