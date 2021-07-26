import compileall
import os
import shutil

if __name__=='__main__':
    compileall.compile_dir('.')
    for file in os.listdir(os.getcwd() + "/__pycache__"):
        print(os.path.splitext(file))
        shutil.copyfile("./__pycache__/"+file, "../Release/DataService/"+file[0:file.find('.')]+".pyc")
    os.remove("../Release/DataService/compile.pyc")

