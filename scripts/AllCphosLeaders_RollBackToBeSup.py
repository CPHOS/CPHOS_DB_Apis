from db_api import customTransaction
from db_api.DataQueryApis.GetTeacherInfoApis import *
from db_api.DataManagingApis.ChangeTeacherInfoApis import *
from db_api.DataManagingApis.ChangeSchoolInfoApis import *
from db_api.DataQueryApis.GetSchoolInfoApis import *
from db_api.DataQueryApis.GetStudentInfoApis import *
from db_api.DataQueryApis.GetAreaInfoApis import *

cphosl = customTransaction.executeOperation(GetSchoolInfoByName('组委会'))
cphos = cphosl[0]

all_teacher = customTransaction.executeOperation(GetTeacherInfoBySchoolId(cphos['id']))

for teacher in all_teacher:
    print(teacher['user_name'])
    teacher_id = teacher['id']
    customTransaction.executeOperation(MakeAllTypesToBeSupTeacher(teacher_id))
    customTransaction.executeOperation(ChangeAllTypesMarkingSubject(teacher_id,10))
# customTransaction.commit()