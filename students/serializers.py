from rest_framework import serializers
from rest_framework.validators import ValidationError
from students.models import Course, Student
from django.conf import settings

class CourseSerializer(serializers.ModelSerializer):
    students = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), many=True, required=False)
    class Meta:
        model = Course
        fields = ("id", "name", "students")
    def validate(self, data):
        if self.context['request'].method == "POST":
            students = data.get('students')
            if students == None:
                pass
            elif len(students) > settings.MAX_STUDENTS_PER_COURSE:
                raise ValidationError("На курсе может быть не более 20 студентов")
        elif self.context['request'].method == "PUT":
            course_id = self.context['request'].parser_context['kwargs'].get('pk')
            course = Course.objects.filter(id=course_id).first()
            if course_id == None:
                raise ValidationError('Не верный id курса')
            student = course.students
            new_students = data.get("students")
            new_students = [s.id for s in new_students]
            if type(student) != list:
                if len(new_students) > settings.MAX_STUDENTS_PER_COURSE:
                    raise ValidationError("На курсе может быть не более 20 студентов")
            else: 
                result_students = student.append(new_students)
                if len(result_students) > settings.MAX_STUDENTS_PER_COURSE:
                    raise ValidationError("На курсе может быть не более 20 студентов")
        return data
