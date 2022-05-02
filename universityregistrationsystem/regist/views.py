from ctypes import sizeof
from curses import keyname
from keyword import iskeyword
import re
from django.shortcuts import render

from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
from .forms import *
from .db_utils import run_statement
# Create your views here.

keyword=False
filtered=False
xdepartmentId=False
xcampus=False
minCredits=False
maxCredits=False

def index(req):
    #Logout the user if logged 
    if req.session:
        req.session.flush()

    return render(req,'firstPage.html')
    
def adminLogin(req):
    
    isFailed=req.GET.get("fail",False) #Check the value of the GET parameter "fail"
    loginForm=UserLoginForm() #Use Django Form object to create a blank form for the HTML page

    return render(req,'loginIndex.html',{"login_form":loginForm,"action_fail":isFailed})


def studentLogin(req):
    
    
    isFailed=req.GET.get("fail",False) #Check the value of the GET parameter "fail"
    
    loginForm=UserLoginForm() #Use Django Form object to create a blank form for the HTML page

    return render(req,'studentLoginIndex.html',{"login_form":loginForm,"action_fail":isFailed})

def instructorLogin(req):
    
    
    isFailed=req.GET.get("fail",False) #Check the value of the GET parameter "fail"
    
    loginForm=UserLoginForm() #Use Django Form object to create a blank form for the HTML page

    return render(req,'instructorLoginIndex.html',{"login_form":loginForm,"action_fail":isFailed})



def aLogin(req):
    #Retrieve data from the request body
    username=req.POST["username"]
    password=req.POST["password"]
    resultAdmin=run_statement(f"SELECT * FROM DatabaseManager WHERE adminname='{username}' and password=SHA2('{password}',256);") #Run the query in DB
    if resultAdmin: #If a result is retrieved
        req.session["username"]=username #Record username into the current session
        return HttpResponseRedirect('../regist/adminHome') #Redirect user to home page
    else:
        return HttpResponseRedirect('../regist/adminLogin?fail=true')
def sLogin(req):
    #Retrieve data from the request body
    username=req.POST["username"]
    password=req.POST["password"]
    
    
    resultStudent=run_statement(f"SELECT * FROM Student WHERE username='{username}' and password=SHA2('{password}',256);") #Run the query in DB
    
    if resultStudent:
        req.session["username"]=username #Record username into the current session
        return HttpResponseRedirect('../regist/stHome') #Redirect user to home page
    else:
        return HttpResponseRedirect('../regist/studentLogin?fail=true')
def iLogin(req):
    #Retrieve data from the request body
    username=req.POST["username"]
    password=req.POST["password"]
    
    
    resultInstructor=run_statement(f"SELECT * FROM Instructor WHERE username='{username}' and password=SHA2('{password}',256);") #Run the query in DB
    
    
    if resultInstructor:
        req.session["username"]=username #Record username into the current session
        return HttpResponseRedirect('../regist/insHome') #Redirect user to home page
    else:
        return HttpResponseRedirect('../regist/instructorLogin?fail=true')


#DATABASE MANAGER FUNCTIONS
def adminHome(req):
    
    username=req.session["username"] #Retrieve the username of the logged-in user

    return render(req,'adminHome.html',{"username":username})

def adminStudent(req):
    result=run_statement(f"SELECT username, name, surname, email, departmentid, gpa, completedCredits FROM Student ORDER BY completedCredits ASC;") #Run the query in DB
    username=req.session["username"] #Retrieve the username of the logged-in user
    isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False
    isFailedx=req.GET.get("failx",False) #Try to retrieve GET parameter "failx", if it's not given set it to False

    return render(req,'adminStudent.html',{"results":result,"action_fail":isFailed,"action_failx":isFailedx,"username":username})

def adminInstructor(req):
    result=run_statement(f"SELECT username, name, surname, email, departmentid, title FROM Instructor;") #Run the query in DB
    
    username=req.session["username"] #Retrieve the username of the logged-in user
    isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False
    isFailedx=req.GET.get("failx",False) #Try to retrieve GET parameter "failx", if it's not given set it to False

    return render(req,'adminInstructor.html',{"results":result,"action_fail":isFailed,"action_failx":isFailedx,"username":username})

def adminGrade(req):
    username=req.session["username"] #Retrieve the username of the logged-in user
    isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False
    isFailedx=req.GET.get("failx",False) #Try to retrieve GET parameter "failx", if it's not given set it to False

    return render(req,'adminGrade.html',{"action_fail":isFailed,"action_failx":isFailedx,"username":username})

def adminCourse(req):
    username=req.session["username"] #Retrieve the username of the logged-in user
    isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False

    return render(req,'adminCourse.html',{"action_fail":isFailed,"username":username})
def addStudent(req):
    #Retrieve data from the request body
    username=req.POST["st_username"]
    name=req.POST["name"]
    surname=req.POST["surname"]
    email= req.POST["email"]
    password=req.POST["st_password"] 
    departmentid=req.POST["departmentid"]
    try:
        studentid=req.POST["studentid"]
        run_statement(f"CALL AddStudent('{username}','{studentid}','{name}','{surname}','{email}','{password}','{departmentid}')")
        return HttpResponseRedirect("../adminHome/Student")

    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../adminHome/Student?fail=true')

def addInstructor(req):
    #Retrieve data from the request body
    username=req.POST["ins_username"]
    name=req.POST["name"]
    surname=req.POST["surname"]
    email= req.POST["email"]
    password=req.POST["ins_password"] 
    departmentid=req.POST["departmentid"]
    
    try:
        title=req.POST["title"]
        run_statement(f"CALL AddInstructor('{username}','{title}','{name}','{surname}','{email}','{password}','{departmentid}')")
        return HttpResponseRedirect("../adminHome/Instructor")

    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../adminHome/Instructor?fail=true')

#BIR BOSLUK OLACAK STUDENT ID GIRECEK ONA GORE POST DONDURECEK YAPILAN ISLEME GORE. TABI BUNDAN ONCE BU SECENEGE GIRMESI GEREK.
def deleteStudent(req):
    #Retrieve data from the request body
    studentid=req.POST["studentid"]
    temp_result=run_statement(f"SELECT * FROM Student WHERE Student.studentId='{studentid}'")
    if not temp_result:
        return HttpResponseRedirect('../adminHome/Student?failx=true')

    try:
        run_statement(f"CALL DeleteFromStudent('{studentid}')")
        return HttpResponseRedirect("../adminHome/Student")

    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../adminHome/Student?failx=true')
def updateTitleOfInstructor(req):
    #Retrieve data from the request body
    username=req.POST["ins_username"]
    title=req.POST["title"]

    temp_result=run_statement(f"SELECT * FROM Instructor WHERE Instructor.username='{username}'")
    if not temp_result:
        return HttpResponseRedirect('../adminHome/Instructor?failx=true')

    
    try:
        run_statement(f"CALL UpdateTitleOfInstructor('{username}','{title}')")
        return HttpResponseRedirect("../adminHome/Instructor")
    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../adminHome/Instructor?failx=true')

def showGrades(req):
    studentid=req.POST["studentid"]
    username=req.session["username"] #Retrieve the username of the logged-in user
    #Shows the grades of a student for different courses
    result=run_statement(f"SELECT Grades.courseId, Course.name,Grades.grade FROM ((Grades INNER JOIN Course ON Grades.courseId = Course.courseId) INNER JOIN Student ON Student.username = Grades.username) WHERE Student.studentId = '{studentid}' AND Grades.grade IS NOT NULL;") #Run the query in DB    
    if result:
        return render(req,'showGrades.html',{"results":result,"username":username})
    else:
        return HttpResponseRedirect('../Grades?fail=true')
def showAverageGrade(req):
    courseId=req.POST["courseid"]
    username=req.session["username"] #Retrieve the username of the logged-in user
    #Shows average grade for a course
    result=run_statement(f"SELECT Grades.courseId, Course.name, FORMAT(sum(grade)/count(*),2) AS 'Average Grade' FROM (Grades INNER JOIN Course ON Grades.courseId = Course.courseId) WHERE Grades.grade IS NOT NULL AND Grades.courseId='{courseId}' GROUP BY Grades.courseId;") #Run the query in DB    
    if result:
        return render(req,'showAverageGrade.html',{"results":result,"username":username})
    else:
        return HttpResponseRedirect('../Grades?failx=true')

def showCourses(req):
    ins_username=req.POST["ins_username"]
    username=req.session["username"] #Retrieve the username of the logged-in user
    result=run_statement(f"SELECT Course.courseId AS 'Course ID', Course.name AS 'Course Name', Classroom.classroomId AS 'Classroom ID', Classroom.name AS 'Campus', Course.slotNumber AS 'Time Slot' FROM (Course INNER JOIN Classroom ON Course.classroomId=Classroom.classroomId) WHERE Course.username = '{ins_username}';") #Run the query in DB    
    if result:
        return render(req,'showCourses.html',{"results":result,"username":username})
    else:
        return HttpResponseRedirect('../Course?fail=true')


#INSTRUCTOR FUNCTIONS
def insHome(req):
    username=req.session["username"] #Retrieve the username of the logged-in user

    return render(req,'insHome.html',{"username":username})

def insClassroom(req):
    username=req.session["username"] #Retrieve the username of the logged-in user
    isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False
    return render(req,'insClassroom.html',{"action_fail":isFailed,"username":username})

def insCourse(req):
    username=req.session["username"] #Retrieve the username of the logged-in user
    result=run_statement(f"SELECT Course.courseId, Course.name,  Course.classroomId, Course.slotNumber, Course.quota, prereqIds FROM ((Course LEFT JOIN (SELECT courseId,GROUP_CONCAT(prereqId) prereqIds FROM PreReq GROUP BY courseId) p USING(courseId))) WHERE Course.username='{username}' ORDER BY(courseId);") #Run the query in DB
    isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False
    isFailedx=req.GET.get("failx",False) #Try to retrieve GET parameter "failx", if it's not given set it to False
    isFailedy=req.GET.get("faily",False) #Try to retrieve GET parameter "faily", if it's not given set it to False

    return render(req,'insCourse.html',{"results":result,"action_fail":isFailed,"action_failx":isFailedx,"action_faily":isFailedy,"username":username})

def insStudent(req):
    username=req.session["username"] #Retrieve the username of the logged-in user
    isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False
    isFailedx=req.GET.get("failx",False) #Try to retrieve GET parameter "failx", if it's not given set it to False

    return render(req,'insStudent.html',{"action_fail":isFailed,"action_failx":isFailedx,"username":username})

def showClassrooms(req):
    slotNumber=req.POST["slotNumber"]
    username=req.session["username"] #Retrieve the username of the logged-in user
    result=run_statement(f"SELECT Whens.classroomId, Classroom.name,Classroom.capacity FROM ((Whens INNER JOIN Classroom ON Whens.classroomId = Classroom.classroomId)) WHERE Whens.slotNumber = '{slotNumber}';") #Run the query in DB    
    if result:
        return render(req,'insShowClassrooms.html',{"results":result,"username":username})
    else:
        return HttpResponseRedirect('../Classrooms?fail=true')

def addCourse(req):
    #Retrieve data from the request body
    username=req.session["username"] #Retrieve the username of the logged-in user
    courseId=req.POST["courseid"]
    name=req.POST["name"]
    credits=req.POST["credits"]
    classroomId= req.POST["classroomid"]
    slotNumber=req.POST["slotNumber"] 
    quota=req.POST["quota"]
    
    try:
        run_statement(f"CALL AddCourse('{username}','{courseId}','{name}','{credits}','{classroomId}','{slotNumber}','{quota}')")
        return HttpResponseRedirect("../Course")

    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../Course?fail=true')

def addPreReq(req):
    #Retrieve data from the request body
    #username=req.session["username"] #Retrieve the username of the logged-in user
    courseId=req.POST["courseid"]
    prereqId=req.POST["prereqid"]
    try:

        run_statement(f"CALL AddPreReq('{courseId}','{prereqId}')")
        return HttpResponseRedirect("../Course")

    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../Course?failx=true')


def updateNameOfCourse(req):
    #Retrieve data from the request body
    courseId=req.POST["courseid"]
    name=req.POST["name"]

    temp_result=run_statement(f"SELECT * FROM Course WHERE Course.courseId='{courseId}'")
    if not temp_result:
        return HttpResponseRedirect('../Course?faily=true')


    try:
        run_statement(f"CALL UpdateNameOfCourse('{courseId}','{name}')")
        return HttpResponseRedirect("../Course")
    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../Course?faily=true')


def showStudents(req):
    courseId=req.POST["courseid"]
    username=req.session["username"] #Retrieve the username of the logged-in user

    #Return the students who have null values in grade
    result=run_statement(f"SELECT Student.username, Student.studentId, Student.email, Student.name, Student.surname FROM (Grades INNER JOIN Student ON Grades.username = Student.username) WHERE Grades.courseId = '{courseId}' AND Grades.grade IS NULL;") #Run the query in DB    
    if result:
        return render(req,'insShowStudents.html',{"results":result,"username":username})
    else:
        return HttpResponseRedirect('../Student?fail=true')


def giveGrade(req):
    #Retrieve data from the request body
    #username=req.session["username"] #Retrieve the username of the logged-in user
    courseId=req.POST["courseid"]
    studentId=req.POST["studentid"]
    grade=req.POST["grade"]
    temp_studentUsername=run_statement(f"SELECT Student.username FROM Student WHERE '{studentId}'=Student.studentId")
    if not temp_studentUsername:
        return HttpResponseRedirect('../Student?failx=true')

    studentUsername=str(temp_studentUsername)
    temp=studentUsername[3:-5]
    
    
    temp_result=run_statement(f"SELECT * FROM Course WHERE Course.courseId='{courseId}'")
    if not temp_result:
        return HttpResponseRedirect('../Student?failx=true')
    
    try:

        run_statement(f"CALL GiveGrade('{courseId}','{temp}', '{grade}')")
        return HttpResponseRedirect("../Student")

    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../Student?failx=true')
#result=run_statement(f"SELECT Course.courseId, Course.name, Instructor.surname, Instructor.departmentId, credits, GivenIn.classroomId, GivenIn.slotNumber, Course.quota, prereqIds FROM (((Course LEFT JOIN (SELECT courseId,GROUP_CONCAT(prereqId) prereqIds FROM PreReq GROUP BY courseId) p USING(courseId)) LEFT JOIN GivenIn ON Course.courseId=GivenIn.courseId) INNER JOIN TeachesBy ON TeachesBy.courseId=Course.courseId) INNER JOIN Instructor ON Instructor.username=TeachesBy.username ORDER BY(courseId);") #Run the query in DB

#STUDENT FUNCTIONS
def stHome(req):
    global keyword
    global filtered
    global xdepartmentId
    global xcampus
    global minCredits
    global maxCredits

    keyword=False
    filtered=False
    xdepartmentId=False
    xcampus=False
    minCredits=False
    maxCredits=False
    username=req.session["username"] #Retrieve the username of the logged-in user

    return render(req,'stHome.html',{"username":username})



def stAllCourses(req):
    global refresh
    global keyword
    global filtered
    global xdepartmentId
    global xcampus
    global minCredits
    global maxCredits
    username=req.session["username"] #Retrieve the username of the logged-in user
    isKeywordFailed=False
    # isKeyword=req.GET.get("isKeyword",False) #Try to retrieve GET parameter "failx", if it's not given set it to False
    # isFiltered=req.GET.get("isFiltered",False) #Try to retrieve GET parameter "faily", if it's not given set it to False
    isFilteredFailed=False
    filteredChanged=False
    keywordChanged=False

    temp_keyword=keyword
    temp_departmentId=xdepartmentId
    temp_campus=xcampus
    temp_minCredits=minCredits
    temp_maxCredits=maxCredits

    keyword=req.POST.get("keyword",False)
    xdepartmentId=req.POST.get("departmentid",False)
    xcampus=req.POST.get("campus",False)
    minCredits=req.POST.get("mincredits",False)
    maxCredits=req.POST.get("maxcredits",False)
    refresh=req.POST.get("refresh",False)

    if not keyword and xdepartmentId:
        filteredChanged=True
    elif not xdepartmentId and keyword:
        keywordChanged=True
    
    if not keywordChanged:
        keyword=temp_keyword
    if not filteredChanged:
        xdepartmentId=temp_departmentId
        xcampus=temp_campus
        minCredits=temp_minCredits
        maxCredits=temp_maxCredits
    if refresh:
        keyword=False
        xdepartmentId = False
        xcampus = False
        minCredits = False
        maxCredits = False


    if(keyword and xdepartmentId):
        result=run_statement(f"CALL FilterWithKeyword('{keyword}','{xdepartmentId}','{xcampus}', '{minCredits}', '{maxCredits}')") #Run the query in DB
        if not result:
            if filteredChanged:
                # xdepartmentId=temp_departmentId
                # xcampus=temp_campus
                # minCredits=temp_minCredits
                # maxCredits=temp_maxCredits
                # result=run_statement(f"CALL FilterWithKeyword('{keyword}','{xdepartmentId}','{xcampus}', '{minCredits}', '{maxCredits}')") #Run the query in DB
                isFilteredFailed=True
            elif keywordChanged:
                # keyword=temp_keyword
                isKeywordFailed=True
    elif(keyword):
        result=run_statement(f"SELECT Course.courseId, Course.name, Instructor.surname, Instructor.departmentId, credits, Course.classroomId, Course.slotNumber, Course.quota, prereqIds FROM (((Course LEFT JOIN (SELECT courseId,GROUP_CONCAT(prereqId) prereqIds FROM PreReq GROUP BY courseId) p USING(courseId)))) INNER JOIN Instructor ON Instructor.username=Course.username WHERE Course.name LIKE '%{keyword}%' ORDER BY(courseId);") #Run the query in DB
        if not result:
            # keyword=temp_keyword
            # result=run_statement(f"SELECT Course.courseId, Course.name, Instructor.surname, Instructor.departmentId, credits, Course.classroomId, Course.slotNumber, Course.quota, prereqIds FROM (((Course LEFT JOIN (SELECT courseId,GROUP_CONCAT(prereqId) prereqIds FROM PreReq GROUP BY courseId) p USING(courseId)))) INNER JOIN Instructor ON Instructor.username=Course.username WHERE Course.name LIKE '%{keyword}%' ORDER BY(courseId);") #Run the query in DB
            isKeywordFailed=True
    elif(xdepartmentId):
        result=run_statement(f"CALL Filter('{xdepartmentId}','{xcampus}', '{minCredits}', '{maxCredits}')") #Run the query in DB
        if not result:
            # xdepartmentId=temp_departmentId
            # xcampus=temp_campus
            # minCredits=temp_minCredits
            # maxCredits=temp_maxCredits
            # result=run_statement(f"CALL Filter('{xdepartmentId}','{xcampus}', '{minCredits}', '{maxCredits}')") #Run the query in DB
            isFilteredFailed=True
    else:
        result=run_statement(f"SELECT Course.courseId, Course.name, Instructor.surname, Instructor.departmentId, credits, Course.classroomId, Course.slotNumber, Course.quota, prereqIds FROM (((Course LEFT JOIN (SELECT courseId,GROUP_CONCAT(prereqId) prereqIds FROM PreReq GROUP BY courseId) p USING(courseId)))) INNER JOIN Instructor ON Instructor.username=Course.username ORDER BY(courseId);") #Run the query in DB


    return render(req,'stAllCourses.html',{"results":result,"keyword_fail":isKeywordFailed,"filtered_fail":isFilteredFailed,"username":username})

def stMyCourses(req):
    username=req.session["username"] #Retrieve the username of the logged-in user
    isFailed=req.GET.get("fail",False) #Try to retrieve GET parameter "fail", if it's not given set it to False
    result=run_statement(f"SELECT Grades.courseID, Course.name, Grades.grade FROM (Grades INNER JOIN Course ON Grades.courseId=Course.courseId) WHERE Grades.username='{username}';") #Run the query in DB

    return render(req,'stMyCourses.html',{"results":result,"action_fail":isFailed,"username":username})

def stAddCourse(req):
    #Retrieve data from the request body
    courseId=req.POST["courseid"]
    username=req.session["username"] #Retrieve the username of the logged-in user
    try:
        run_statement(f"CALL StAddCourse('{username}','{courseId}')")
        return HttpResponseRedirect("../stHome/stMyCourses")

    except Exception as e:
        print(str(e))
        return HttpResponseRedirect('../stHome/stMyCourses?fail=true')