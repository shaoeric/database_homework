from flask import Blueprint, render_template, redirect, request
from config import db, cursor

bp = Blueprint('cms', __name__, url_prefix='/cms')

@bp.route('/')
def index():
    male_num = "select count(Sno) from S where Sgender='男'"
    female_num = "select count(Sno) from S where Sgender='女'"
    cursor.execute(male_num)
    male_num = cursor.fetchall()[0][0]

    cursor.execute(female_num)
    female_num = cursor.fetchall()[0][0]

    dict = {
        'male_num': male_num,
        'female_num': female_num
    }
    return render_template('cms/index.html', **dict)


@bp.route('/tab_panel/')
def tab_panel():
    return render_template('cms/tab-panel.html')


@bp.route('/student/', methods=['GET', 'POST'])
def student():
    resultHasGrade = False   # 查询结果是否含有成绩的标志

    # 查询出课程名
    course = "select Cname from C"
    cursor.execute(course)
    courses = cursor.fetchall()  # (('高等数学',), ('线性代数',), ('数据库原理',)
    #     需要把courses转换成字符串 "高等数学，线性代数，数据库原理"
    courses = list(map(lambda x: x[0], courses))
    courses = "'{}'".format(",".join(courses))

    # 查询出班级
    Sclass = "select distinct Sclass  from S"
    cursor.execute(Sclass)
    Sclass = cursor.fetchall()
    # 同理，班级也要转换格式
    Sclass = list(map(lambda x: x[0], Sclass))
    Sclass = "'{}'".format(",".join(Sclass))

    if request.method == 'GET':
        student = "select * from S"
        cursor.execute(student)
        students = cursor.fetchall()

    else:
        sql = "select * from S "

        gender = request.values.get('Sgender')
        if gender != '男' and gender != '女':  # 如果未选择学生性别，则把性别设为空
            sql = sql + "where 1=1"
        else:
            sql = sql + "where Sgender='{}'".format(gender)
        option = request.values.get('provinces')  # 得到选择查询的类别

        if option == '0':  # 按照学号查询
            SnoInput = request.values.get('textInput')
            sql = sql + " and SNO='{}'".format(SnoInput)
        elif option == '1':  # 按照班级查询
            Sclass = request.values.get('city')
            sql = sql + " and Sclass='{}'".format(Sclass)

        elif option == '2':  # 按照成绩查询
            gradeMin = request.values.get('textInput')  # 分数下线
            gradeMax = request.values.get('low')   # 分数上线
            subject = request.values.get('city')  # 学科
            CNO_sql = "select CNO from C where Cname='{}'".format(subject)
            cursor.execute(CNO_sql)
            CNO = cursor.fetchone()[0]
            sql = """
                select S.SNO, S.Sname, S.Sgender, S.Sclass, C.Cname, SC.grade 
                from S, C, SC
                where S.SNO=SC.SNO and C.CNO=SC.CNO and C.CNO='{}' and SC.grade>={} and SC.grade<={} 
            """.format(CNO, gradeMin, gradeMax)
            resultHasGrade = True

        elif option == '3':  # 按照姓名查询
            Sname = request.values.get('textInput')
            sql = sql + " and Sname='{}'".format(Sname)

        elif option == '4':  # 按照选修课查询
            subject = request.values.get('city')
            CNO_sql = "select CNO from C where Cname='{}'".format(subject)
            cursor.execute(CNO_sql)
            CNO = cursor.fetchone()[0]
            sql = """
                select S.SNO, S.Sname, S.Sgender, S.Sclass, C.Cname, SC.grade 
                from S, C, SC
                where S.SNO=SC.SNO and C.CNO=SC.CNO and C.CNO='{}'
            """.format(CNO)
            resultHasGrade = True

        cursor.execute(sql)
        students = cursor.fetchall()

    dict = {
        'results': students,
        'courses': courses,
        'Sclass': Sclass,
        'flag': resultHasGrade
    }
    return render_template('cms/student.html', **dict)


@bp.route('/teacher/', methods=['GET', 'POST'])
def teacher():
    # 查询出老师的专业/系
    Tdepts = "select distinct depart from T"
    cursor.execute(Tdepts)
    Tdepts = cursor.fetchall()  # (('物联网',), ('计算机',), ('微电子',))
    Tdepts = list(map(lambda x: x[0], Tdepts))
    Tdepts = "'{}'".format(",".join(Tdepts))

    # 查询出课程名
    course = "select Cname from C"
    cursor.execute(course)
    courses = cursor.fetchall()  # (('高等数学',), ('线性代数',), ('数据库原理',)
    #     需要把courses转换成字符串 "高等数学，线性代数，数据库原理"
    courses = list(map(lambda x: x[0], courses))
    courses = "'{}'".format(",".join(courses))

    studentGradeSql = ''  # 查询学生成绩的sql
    studentGrade = ()
    courseGradeChart = []  # 成绩 作图使用
    SnameChart = []  # 学生姓名作图使用
    courseNameChart = ""  # 课程名称 作图使用

    TnameFlag = False   # 是否显示教师姓名

    if request.method == 'GET':
        sql = "select * from T"
        cursor.execute(sql)
        results = cursor.fetchall()

    else:
        sql = "select * from T"
        Tgender = request.values.get("Tgender")
        if Tgender != '男' and Tgender != '女':
            sql = sql + " where 1=1"
        else:
            sql = sql + " where Tgender='{}'".format(Tgender)

        option = request.values.get("provinces2")  # 获得选取的查询方式
        if option == '1':  # 按照姓名查找
            Tname = request.values.get("inputLow")
            sql = sql + " and Tname='{}'".format(Tname)
        elif option == '2':  # 按照工号查找
            TNO = request.values.get("inputLow")
            radio = request.values.get("radio")
            if radio == '1':  # 选择 查询学生成绩
                studentGradeSql = """
                    select S.SNO, S.Sname, C.Cname, SC.grade
                    from S, C, SC, TC
                    where S.SNO=SC.SNO and C.CNO=SC.CNO and TC.CNO=SC.CNO and TC.TNO='{}'
                    order by SC.grade desc
                """.format(TNO)
                cursor.execute(studentGradeSql)
                studentGrade = cursor.fetchall()

                courseGradeChart = list(map(lambda x: int(x[3]), studentGrade))  # 把学生成绩放进作图使用的成绩列表里
                SnameChart = list(map(lambda x: x[1], studentGrade))  # 把学生姓名放进作图使用的姓名列表里
                courseNameChart = "'{}'".format(studentGrade[0][2])  # 作图使用的课程名称

                print(courseGradeChart)
                print(SnameChart)
                print(courseNameChart)

            sql = sql + " and TNO='{}'".format(TNO)
        elif option == '3':  # 按照课程查找
            subject = request.values.get("city2")
            radio = request.values.get("radio")
            if radio == '1':
                studentGradeSql = """
                                    select S.SNO, S.Sname, C.Cname, SC.grade,T.Tname
                                    from S, C, SC, TC, T
                                    where S.SNO=SC.SNO and C.CNO=SC.CNO and TC.CNO=SC.CNO and T.TNO=TC.TNO and C.Cname='{}'
                                    order by SC.grade desc
                                """.format(subject)
                TnameFlag = True  # 显示出教师的姓名
                cursor.execute(studentGradeSql)
                studentGrade = cursor.fetchall()

                courseGradeChart = list(map(lambda x: int(x[3]), studentGrade))  # 把学生成绩放进作图使用的成绩列表里
                SnameChart = list(map(lambda x: x[1], studentGrade))  # 把学生姓名放进作图使用的姓名列表里
                courseNameChart = "'{}'".format(studentGrade[0][2])  # 作图使用的课程名称

            if Tgender == '男' or Tgender == '女':
                sql = """
                    select * from T where TNO in(
                        select TNO from TC where CNO in(
                          select CNO from C where Cname='{}'
                        )) and Tgender='{}'
                """.format(subject, Tgender)
            else:
                sql = """
                    select * from T where TNO in(
                        select TNO from TC where CNO in(
                          select CNO from C where Cname='{}'
                        ))
                """.format(subject)
        elif option == '4':  # 按照部门查找
            dept = request.values.get("city2")
            sql = sql + " and depart='{}'".format(dept)

        elif option == '6':  # 按照是否授课查找
            dept = request.values.get("city2")
            radio = request.values.get("radio")
            sql = sql + " and depart='{}' and stat='{}'".format(dept, radio)
        print(sql)
        cursor.execute(sql)
        results = cursor.fetchall()
    dict = {
        'results': results,  #  教师信息查询结果（必有）
        'Tdepts': Tdepts,  # 教师专业/系/部门（必有）
        'courses': courses,   # 所有课程名称 （必有）
        'studentGrade': studentGrade,   # 学生成绩（可能为空）
        'TnameFlag': TnameFlag,   # 是否显示教师姓名
        'courseGradeChart': courseGradeChart,  # 作图使用的成绩列表
        'SnameChart': SnameChart,  # 作图使用的姓名列表
        'courseNameChart': courseNameChart  # 作图使用的课程名称
    }
    return render_template('cms/teacher.html', **dict)
