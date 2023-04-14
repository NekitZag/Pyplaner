# from rest_framework import serializers
from .models import Instructors, KRS_according_staff_schedule, KRS_LIS_air_squadrons_according_staffing_table,freelance_instructor_pilots_check, freelance_instructor_pilots

class InstructorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructors
        fields = '__all__'

class KRSSerializer(serializers.ModelSerializer):
    class Meta:
        model = KRS_according_staff_schedule
        fields = '__all__'

class KRSandLISSerializer(serializers.ModelSerializer):
    class Meta:
        model = KRS_LIS_air_squadrons_according_staffing_table
        fields = '__all__'

class FreelansePilots_CheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = freelance_instructor_pilots_check
        fields = '__all__'

class FreelansePilots_Serializer(serializers.ModelSerializer):
    class Meta:
        model = freelance_instructor_pilots
        fields = '__all__'
