# encoding: utf8
import os




def createFile(filename):
    if os.path.exists(filename):
        raise Exception("file '%s' exists already" % filename);
    f = open(filename, "w");
    f.close()


def appendText(filename, text):
    f = open(filename, "a");
    f.write(text)
    f.close()
    

def deleteDir(dirpath):
    sub_file_list = os.listdir(dirpath)
    for sub_file in sub_file_list:
        sub_path = os.path.join(dirpath, sub_file)
        if os.path.isfile(sub_path):
            os.remove(sub_path)
        else:
            deleteDir(sub_path)
            os.rmdir(sub_path)
    os.rmdir(dirpath)


if __name__=="__main__":
    deleteDir("D:/work/zhicloud/dev/httpGateway/20141121.1-httpGateway - host_status/src/common_util/dddddddd")


