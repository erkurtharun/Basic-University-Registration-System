from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('adminLogin',views.adminLogin,name="adminLogin"),
    path('instructorLogin',views.instructorLogin,name="instructorLogin"),
    path('studentLogin',views.studentLogin,name="studentLogin"),

    path('aLogin',views.aLogin,name="aLogin"),
    path('sLogin',views.sLogin,name="sLogin"),
    path('iLogin',views.iLogin,name="iLogin"),

    path('adminHome',views.adminHome,name="adminHome"),
    path('insHome',views.insHome,name="insHome"),
    path('stHome',views.stHome,name="stHome"),
    
    path('adminHome/Course',views.adminCourse,name="adminCourse"),
    path('adminHome/Grades',views.adminGrade,name="adminGrade"),
    path('adminHome/Instructor',views.adminInstructor,name="adminInstructor"),
    path('adminHome/Student',views.adminStudent,name="adminStudent"),
    path('adminHome/addStudent',views.addStudent,name="addStudent"),
    path('adminHome/addInstructor',views.addInstructor,name="addInstructor"),
    path('adminHome/deleteStudent',views.deleteStudent,name="deleteStudent"),
    path('adminHome/updateTitleOfInstructor',views.updateTitleOfInstructor,name="updateTitleOfInstructor"),
    path('adminHome/Grades/showGrades',views.showGrades,name="showGrades"),
    path('adminHome/Grades/showAverageGrade',views.showAverageGrade,name="showAverageGrade"),
    path('adminHome/Grades/showCourses',views.showCourses,name="showCourses"),


    path('insHome/Classrooms',views.insClassroom,name="insClassroom"),
    path('insHome/Classrooms/showClassrooms',views.showClassrooms,name="showClassrooms"),
    path('insHome/Course',views.insCourse,name="insCourse"),
    path('insHome/Course/addCourse',views.addCourse,name="addCourse"),
    path('insHome/Course/addPreReq',views.addPreReq,name="addPreReq"),
    path('insHome/Course/updateNameOfCourse',views.updateNameOfCourse,name="updateNameOfCourse"),
    path('insHome/Student',views.insStudent,name="insStudent"),
    path('insHome/Student/showStudents',views.showStudents,name="showStudents"),
    path('insHome/Student/giveGrade',views.giveGrade,name="giveGrade"),



    path('stHome/stAllCourses',views.stAllCourses,name="stAllCourses"),
    path('stHome/stMyCourses',views.stMyCourses,name="stMyCourses"),
    path('stHome/stAddCourse',views.stAddCourse,name="stAddCourse"),
    

    
    
    
    
    
    
    
    
    
    


] 