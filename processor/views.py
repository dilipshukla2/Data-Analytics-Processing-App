from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RawDataSerializer
from .services import step1_ingest_and_clean, step2_transform_and_aggregate, step3_calculate_score, step4_save_to_db

class Step1View(APIView):
    def post(self, request):
        raw_data = request.data.get('data', [])
        cleaned = step1_ingest_and_clean(raw_data)
        return Response({"step": 1, "cleaned_data": cleaned}, status=status.HTTP_200_OK)

class Step2View(APIView):
    def post(self, request):
        cleaned_data = request.data.get('cleaned_data', [])
        aggregated = step2_transform_and_aggregate(cleaned_data)
        return Response({"step": 2, "aggregated_data": aggregated}, status=status.HTTP_200_OK)

class Step3View(APIView):
    def post(self, request):
        aggregated_data = request.data
        scored = step3_calculate_score(aggregated_data)
        return Response({"step": 3, "scored_data": scored}, status=status.HTTP_200_OK)

class Step4View(APIView):
    def post(self, request):
        scored_data = request.data
        report = step4_save_to_db(scored_data)
        return Response({"step": 4, "message": "Saved", "report_id": report.report_id}, status=status.HTTP_201_CREATED)




class MasterPipelineView(APIView):
    def post(self, request):
        serializer = RawDataSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        raw_data = serializer.validated_data['data']

        # Chain of dependencies
        cleaned_data = step1_ingest_and_clean(raw_data)
        aggregated_data = step2_transform_and_aggregate(cleaned_data)
        scored_data = step3_calculate_score(aggregated_data)
        final_report = step4_save_to_db(scored_data)

        return Response({
            "message": "Pipeline executed successfully. Server load generated.",
            "report_id": final_report.report_id
        }, status=status.HTTP_200_OK)