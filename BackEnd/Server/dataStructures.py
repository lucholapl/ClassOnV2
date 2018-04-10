from typing import Mapping, Sequence
import time
from PIL import Image
import uuid

class Student:
    'Represents a student'
    name = ''
    lastName = ''
    secondLastName = ''
    NIA = ''
    picture : Image

    def __init__(self, db_id, nia, name, lastName, seccondLastName = '', email = '', passwordHash = '', pictureSrc = ''):
        self.db_id = db_id
        self.NIA = nia
        self.name = name
        self.lastName = lastName
        self.email = email
        self.passwordHash = passwordHash
        self.secondLastName = seccondLastName

        if (pictureSrc is not ''):
            try:
                self.picture = Image.open(pictureSrc)
            except:
                raise Exception('error opening picture: ' + pictureSrc)

    def __dict__(self):
        result = {}
        result['db_id'] = self.db_id
        result['name'] = self.name
        result['lastName']  = self.lastName

        return result

    def JSON(self):
        result = '{\n'
        result += '\"db_id\":\"' + str(self.db_id) + '\", \n'
        result += '\"name\":\"' + str(self.name) + '\", \n'
        result += '\"lastName\":\"' + str(self.lastName) + '\", \n'
        result += '\n}'
        return result

class Course:
    'Defines a course'
    def __init__(self, degree = 'na', courseName = 'na', year = 'na'):
        self.degree = degree
        self.name = courseName
        self.year = year

class Section:
    'Defines a section of an Assigment'
    def __init__(self, db_id, name, orderInAssigment, sectionText):
        self.name = name
        if (orderInAssigment > 0):
            self.order = orderInAssigment
        else:
            raise ValueError('orderInAssigment must be bigger than zero')
        self.text = sectionText
        self.db_id = db_id

class Assigment:
    'Defines an assigment'
    def __init__(self, sections : Sequence[Section], course : Course = None, name : str = '', db_id = 0):
        self.name = name
        self.sections = sections            # : List[Sections]
        self.course = course                # : String
        self.db_id = db_id

    def sections_dict(self):
        result = []
        for section in self.sections:
            result.append(vars(section))
        return result

class Professor():
    def __init__(self, db_id, name, lastName, lastNameSecond, email, passwordHash = ''):
        self.db_id = db_id
        self.name = name
        self.lastName = lastName
        self.lastNameSecond = lastNameSecond
        self.email = email
        self.passwordHash = passwordHash

class Classroom:

    def __init__(self, classSize : (int,int), professor : Professor, assigment : Assigment, room =''):
        self.classSize = classSize
        self.professor = professor
        self.assigment = assigment
        self.studentGroups = dict()             # Groups in class
        self.doubts = []
        self.doubtsSolved = []
        self.__doubtsIdCounter = 0
        self.room = room

    def newDoubtID(self) -> int:
        self.__doubtsIdCounter += 1
        return self.__doubtsIdCounter

    def resolDoubt(self, id : int):
        for tupleDoubt in self.doubts:
            if(tupleDoubt[0] == id):
                # Resolve doubt
                tupleDoubt[1].solveDoubt(id)
                self.doubtsSolved.append(tupleDoubt)
                self.doubtsSolved.remove(tupleDoubt)
                break

    def addStudentToPlace(self, student :Student, place : (int, int)):
        '''
        Adds an student to a given place in the classroom, if there is a group already assign the student to the
        group, if not crates the group.
        :param student:
        :param place:
        :return: The group object the student belongs to.
        '''
        added = False
        for group_id, group in self.studentGroups.items():                    # Check if is a group for the desired place
            tmpPlace = group.positionInClass
            if tmpPlace == place:
                added = True
                # group.students.append(student)            # Add student to
                group.addStudent(student)
                return group

        if added == False:                                  # There is no group, create with one student
            tmpGroup = StudentGroup([student], place)
            self.studentGroups[tmpGroup.groupID] = tmpGroup         # Add group to global object
            return tmpGroup

class StudentGroup:
    def __init__(self, students : [Student], position : (int, int) = (0, 0)):
        self.students = students
        self.positionInClass = position
        self.assigmentProgress = 0
        self.professorTime = 0
        self.doubts = []
        self.doubtsSolved = []
        self.unansweredDoubt = False
        self.groupID = str(uuid.uuid4())        # Generates an ID

    def JSON(self):
        result = '{\n'
        result += '\"position\":\"' + str(self.positionInClass[0]) + ',' + str(self.positionInClass[1]) + '\", \n'
        result += '\"id\":\"' + str(self.groupID) + '\", \n'
        result += '\"students\": [ \n'
        for student in self.students:
            result += student.JSON() + ','
        result = result[:-1]                    # Remove last comma
        result += ' ] \n'
        result += '}'

        return result

    def addStudent(self, student : Student):
        '''
        Adds an student to the given group if is not in the group
        :param student: Student to add
        :return: void
        '''
        # any(x.name == "t2" for x in l)
        if (not any(studentInGroup.db_id == student.db_id for studentInGroup in self.students)):
            # Is not in the group
            self.students.append(student)

    def solveDoubt(self, doubtID : int):
        self.doubts.remove(id)
        self.doubtsSolved.append(id)
        if (len(self.doubts) < 1):
            # No doubts
            self.unansweredDoubt = False

class Doubt:

    'Defines a group\'s doubt'
    def __init__(self, doubtText, section : Section, studentGroup : StudentGroup, postToDB = True, answerText = ''):
        self.db_id = -1
        self.doubtText = doubtText
        self._section = section
        self._postTime = 0
        self._studentGroup = studentGroup
        self.postTime = 0
        self.answerText = answerText
        if (answerText is ''):
            self._answered = False
        else:
            self._answered = True

    def postToDB(self):
        from classOn import DBUtils
        DBUtils.putDoubt(self, self._studentGroup)


    def set_Answer(self, answerText, resolver, postToDB = True):
        from classOn import DBUtils

        self._answerText = answerText
        self._answered = True

        if postToDB:
            DBUtils.answerDoubt(self, resolver)

    def _set_UnanseredTime(self):
        'Calculates the difference between post time and now'
        self._unanswerdTime = time.time() - self._postTime

