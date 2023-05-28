from rest_framework import serializers


class ResponsesStatisticsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    relevant = serializers.IntegerField()
    irrelevant = serializers.IntegerField()


class CountLabelSerializer(serializers.Serializer):
    label = serializers.CharField()
    count = serializers.IntegerField()


class EducationStatisticsSerializer(serializers.Serializer):
    by_name = CountLabelSerializer(many=True)
    by_type = CountLabelSerializer(many=True)


class VacancyStatisticsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    by_department = CountLabelSerializer(many=True)


class StatisticsSerializer(serializers.Serializer):
    responses = ResponsesStatisticsSerializer()
    age = CountLabelSerializer(many=True)
    education = EducationStatisticsSerializer()
    direction_statistics = CountLabelSerializer(many=True)
    work_experience = CountLabelSerializer(many=True)
    vacancy = VacancyStatisticsSerializer(many=True)
