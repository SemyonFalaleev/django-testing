from model_bakery import baker
from students.models import Student, Course
import pytest
from rest_framework.test import APIClient

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)
    return factory

@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)
    return factory

@pytest.mark.django_db
def test_get_fist_course(client, course_factory):
    course = course_factory(_quantity=1)[0]
    response = client.get(f'/api/v1/courses/{course.id}/')
    data = response.json()
    assert response.status_code == 200
    assert course.id == data['id']

@pytest.mark.django_db
def test_course_list(client, course_factory):
    n = 50
    count_courses = Course.objects.count()
    courses = course_factory(_quantity=n)
    response = client.get(f'/api/v1/courses/')
    data = response.json()
    assert response.status_code == 200
    assert Course.objects.count() == count_courses+n
    for i, cours in enumerate(data):
        assert cours['id'] == courses[i].id

@pytest.mark.django_db
def test_filter_id_course(client, course_factory):
    course = course_factory(_quantity=1)[0]
    response = client.get(f'/api/v1/courses/?id={course.id}')
    data = response.json()
    assert response.status_code == 200
    assert data[0]['id'] == course.id
    
@pytest.mark.django_db
def test_filter_name_course(client, course_factory):
    course = course_factory(_quantity=1)[0]
    response = client.get(f'/api/v1/courses/?id={course.id}')
    data = response.json()
    assert response.status_code == 200
    assert data[0]['name'] == course.name

@pytest.mark.django_db
def test_create_course(client):
    count = Course.objects.count()
    name_course = "Course1"
    response = client.post(
        "/api/v1/courses/", 
        data ={
            "name" : name_course
        })
    data = Course.objects.filter(name=name_course).all()
    assert response.status_code == 201
    assert len(data) != 0
    assert Course.objects.count() == count+1

#Пример неудачного теста 
@pytest.mark.django_db
def test_update_course_false(client, student_factory, settings):
    name_course = "Course1"
    settings.MAX_STUDENTS_PER_COURSE = 1
    students = student_factory(_quantity=2)
    students_ids = [s.id for s in students]
    client.post(
        "/api/v1/courses/", 
        data ={
            "name" : name_course
        })
    data = Course.objects.filter(name=name_course).all()[0]
    response = client.put(
        f"/api/v1/courses/{data.id}/",
        data=({"name": name_course, "students": students_ids})
    )
    data = response.json()
    assert response.status_code == 400 # ожидаю что произойдет ошибка валидации

#Пример удачного теста 
@pytest.mark.django_db
def test_update_course_true(client, student_factory):
    name_course = "Course1"
    students = student_factory(_quantity=20)
    students_ids = [s.id for s in students]
    client.post(
        "/api/v1/courses/", 
        data ={
            "name" : name_course
        })
    data = Course.objects.filter(name=name_course).all()[0]
    response = client.put(
        f"/api/v1/courses/{data.id}/",
        data=({"name": name_course, "students": students_ids})
    )
    data = response.json()
    assert response.status_code == 200 # ожидаю что сценарий отрабаотает без ошибок
    assert data['students'] == students_ids



@pytest.mark.django_db
def test_delete_course(client):
    name_course = "Course1"
    client.post(
        "/api/v1/courses/", 
        data ={
            "name" : name_course
        })
    data = Course.objects.filter(name=name_course).all()[0]
    count = Course.objects.count()
    response = client.delete(f"/api/v1/courses/{data.id}/")
    assert response.status_code == 204
    assert len(Course.objects.filter(name=name_course).all()) == 0
    assert Course.objects.count() == count - 1

