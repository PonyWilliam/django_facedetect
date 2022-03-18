'''
    功能：从数据库中获取信息，并将数据下载到本地进行人脸识别。

'''
from os import system
import pymysql
import requests
def init_download():
    # 删除Face里所有文件
    system("rm -rf ./FaceDatabase/*.*")
    conn = pymysql.connect(
    host='sh-cynosdbmysql-grp-2o1mkprk.sql.tencentcdb.com',
    port=21270,
    user='root',
    password='Xiaowei123',
    database='gostudy'
    )
    return conn
def start_download():
    conn = init_download()
    # 创建游标对象执行sql语句
    cur = conn.cursor()
    # 查询员工表
    sqli = "select * from workers"

    result = cur.execute(sqli)

    info = cur.fetchall()

    # 基于id从阿里云OSS上获取对应人脸数据,获取人脸数据后再通过数据库内数据改名为对应名字

    for i in info:
        if(i[0] == 1):
            # 忽略admin账号
            continue
        # 下载图片到FaceDatabase目录
        url = 'https://arcsoft.oss-cn-guangzhou.aliyuncs.com/face/%d.png'%i[0]
        print(url)
        r = requests.get(url)
        with open("./FaceDatabase/%s.png"%i[1],"wb") as f:
            f.write(r.content)
