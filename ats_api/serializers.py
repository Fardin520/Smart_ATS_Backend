from rest_framework import serializers
from .models import Job, Application


class JobSerializer(serializers.ModelSerializer):
    application_count = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'requirements', 'is_active', 'created_at', 'application_count']

    def get_application_count(self, obj):
        return obj.applications.count()


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = ['status', 'ai_score', 'ai_feedback', 'applied_at', 'updated_at']


class ApplicationListSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job.title', read_only=True)

    class Meta:
        model = Application
        fields = ['id', 'candidate_name', 'candidate_email', 'job_title', 'status', 'ai_score', 'applied_at']