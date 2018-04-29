from config import db, cursor
import jpype
from jpype import *

# jvmPath = jpype.getDefaultJVMPath()
# jpype.startJVM(jvmPath)
# jpype.java.lang.System.out.println('hello')
# jpype.shutdownJVM()

jvmPath = jpype.get_default_jvm_path()
jpype.startJVM(jvmPath, "-Djava.class.path=/media/hp/0F1C075C0F1C075C/pycharm-project/database_homework/studentBySno.jar")
JDClass = JClass("Temp.stu")
jd = JDClass()
jselect = jd.sno
print(jselect)
jpype.shutdownJVM()