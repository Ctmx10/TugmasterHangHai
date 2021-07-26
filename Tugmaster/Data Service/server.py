print("计算服务初始化...")
##### Web服务 #####
import json
import uuid
import main
from flask import Flask, request, jsonify
import settings

app = Flask(__name__)
app.config.from_object(settings)
from flask_cors import CORS
CORS(app, supports_credentials=True) #允许跨域请求
import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)#设置Flask的Log输出级别，减少回显信息

import numpy as np
import scipy.integrate as si

from ship import Ship
import compute

cache = {} #全局计算实例缓存

def add():
    ship = Ship() #新建船舶实例
    id = str(uuid.uuid1())
    cache[id] = ship
    return id

#####新建一个计算实例####
@app.route('/add', methods=['POST'])
def add_handler():
    data = json.loads(request.get_data(as_text=True))
    id = add()
    return jsonify(id=id,status=0)

#####删除一个计算实例####
@app.route('/delete', methods=['GET'])
def delete_handler():
    id = request.args.get('id')
    if id in cache:
        del cache[id]
    return "delete "+id

#####修改计算实例的参数####
@app.route('/modify', methods=['POST'])
def modify_handler():
    data = json.loads(request.get_data(as_text=True))
    id = data['id']
    del data['id']
    if not id in cache:
        return jsonify(status=1)

    for k in data.keys():
        if isinstance(data[k],list):
            setattr(cache[id],k,np.array(data[k]))
        else:
            setattr(cache[id],k,data[k])
    return jsonify(status=0)

#####对指定的计算实例完成一次优化计算####
@app.route('/update', methods=['POST'])
def update_handler():
    data = json.loads(request.get_data(as_text=True))
    id = data['id']
    if not id in cache:
        return jsonify(status = 1)
    
    cache[id].x0 = np.array(data['state'])
    compute.update(cache[id])

    state = cache[id].x_et[0:6].tolist() #预期状态
    speed = np.linalg.norm(cache[id].x_et[3:5])
    points = []
    for i in range(cache[id].steps):
        points.append(cache[id].x_et[i*6:i*6+2].tolist())
    return jsonify(status = 0,state = state,speed = speed,points = points)

import pymysql
conn = pymysql.connect(host='localhost', user="root", passwd="root",
                         database='ship_data')


@app.route('/findall_ship', methods=['GET','POST'])
def findall():
    # cur = conn.cursor()
    cur = conn.cursor(cursor=pymysql.cursors.DictCursor)

    cur.execute('select * from ship')
    results = cur.fetchall()
    return jsonify(results)
    #print(results['id'])
@app.route('/findpart_info', methods=['GET','POST'])
def findpartinfo():
    cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
    list1 = []
    cur.execute('select * from ship')
    results = cur.fetchall()
    for row in results:
        MMSI = row['mmsi']
        Speed = row['speed']
        Lon = row['lon']
        Lat = row['lat']
        Heading = row['heading']

        dict1 = {"MMSI": MMSI,
                 "Speed": Speed,
                 "Lon": Lon,
                 "Lat": Lat,
                 "Heading": Heading}
        list1.append(dict1)
    print(list1)
    return jsonify(list1)

@app.route('/findpart_ship', methods=['GET','POST'])
def findpartship():
    cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
    list1 = []
    list2 = []
    list3 = []
    list4 = []

    cur.execute('select * from ship')
    results = cur.fetchall()
    for row in results:
        MMSI = row['mmsi']
        Speed = row['speed']
        Lon = row['lon']
        Lat = row['lat']
        Heading = row['heading']

        # dict1 = {"MMSI": MMSI,
        #          "Speed": Speed,
        #          "Lon": Lon,
        #          "Lat": Lat,
        #          "Heading": Heading}
        dict1 = {"MMSI":MMSI}
        dict2 = {'Speed':Speed}
        dict3 = {'Lon':Lon}
        dict4 = {'Lat':Lat}
        list1.append(dict1)
        list2.append(dict2)
        list3.append(dict3)
        list4.append(dict4)
        #data_part = list1.append(dict1)
    return jsonify(MMSI=list1,Speed=list2,Lon=list3,Lat = list4)
    # return data_part

@app.route('/choose_ship/<name>',methods=['GET','POST'])
def choose_part(name):
    cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
    list1 = []

    cur.execute('select * from ship')
    results = cur.fetchall()
    print(results)
    for row in results:
        MMSI = row[name]

        # 打印结果

        # print("MMSI:%s,Speed:%s,Lon:%d,Lat:%s,Heading:%d" %
        #       (MMSI, Speed, Lon, Lat, Heading))
        dict1={}
        dict1 = {name:MMSI}
        list1.append(dict1)
    print(list1)
    return jsonify(list1)

@app.route('/choose_oneship/<id>',methods=['GET','POST'])
def choose_one(id):
    cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
    list1 = []

    cur.execute('select * from ship')
    results = cur.fetchall()
    #print(results)
    id = int(id)
    #print(results[id-1])
    ship_data = results[id-1]
    ID = ship_data['id']
    MMSI = ship_data['mmsi']
    Speed = ship_data['speed']
    Lon = ship_data['lon']
    Lat = ship_data['lat']
    Heading = ship_data['heading']
    dict1 = {"ID":ID,
             "MMSI": MMSI,
             "Speed": Speed,
             "Lon": Lon,
             "Lat": Lat,
             "Heading": Heading}
    list1.append(dict1)
    #p = json.dumps(list1)
    print(list1)
    #print(p)
    return jsonify(id=id,ship = list1)


#存放接收视频的地址
#video_data
import get_video as gv
video = gv.Video()
path = 'D:/Desktop/ctmx/IceRadar/data/camera'
# ['D:/Desktop/ctmx/IceRadar/data/camera/video_for_test/left-1.mp4',
#  'D:/Desktop/ctmx/IceRadar/data/camera/video_for_test/left.mp4',
#  'D:/Desktop/ctmx/IceRadar/data/camera/video_for_test/right-1.mp4',
#  'D:/Desktop/ctmx/IceRadar/data/camera/video_for_test/right.mp4']
@app.route('/show_video1', methods=['GET','POST'])
def show_leftup():
    #当前端发送请求后，后端接收请求，并将视频取出
    #get_video()
    # video = '/video_for_test/left.mp4'
    # result = path+video
    videos = video.get_video()
    result_1 = videos[1]#video_leftup

    name = result_1.split('/')[-1]
    format_1 = name.split('.')[-1]
    if format_1 != 'mp4':
        result_1 = '视频格式有误'
        return result_1 ,format_1
    #
    return jsonify(result_1)
    #return result

@app.route('/show_video2', methods=['GET','POST'])
def show_rightup():
    videos = video.get_video()
    result_2 = videos[3]  # video_leftup

    name = result_2.split('/')[-1]
    format_2 = name.split('.')[-1]
    if format_2 != 'mp4':
        result_2 = '视频格式有误'
        return result_2, format_2

    return result_2, format_2
    # video = '/video_for_test/right.mp4'
    # result_2 = video + path
    # format_2 = 'mp4'
    # return result_2,format_2

@app.route('/show_video3', methods=['GET','POST'])
def show_leftdown():
    videos = video.get_video()
    result_3 = videos[0]  # video_leftup

    name = result_3.split('/')[-1]
    format_3 = name.split('.')[-1]
    if format_3 != 'mp4' :
        result_3 = '视频格式有误'
        return result_3, format_3

    return result_3, format_3
@app.route('/show_video4', methods=['GET','POST'])#id=" show_video4 "
def show_rightdown():
    videos = video.get_video()
    result_4 = videos[2]  # video_leftup

    name = result_4.split('/')[-1]
    format_4 = name.split('.')[-1]
    if format_4 != 'mp4':
        result_4 = '视频格式有误'
        return result_4

    return result_4

@app.route('/Stitching', methods=['GET','POST'])
def Stitching():
    # video_path_1 = 'D:/Desktop/ctmx/IceRadar/data/camera/video_for_test/left.mp4'
    # video_path_2 = 'D:/Desktop/ctmx/IceRadar/data/camera/video_for_test/right.mp4'
    videos = video.get_video()
    video_path_1 = videos[0]
    video_path_2 = videos[1]
    result_5 = main.stitch(video_path_1,video_path_2)
    name = result_5.split('/')[-1]
    fomrat_5 = name.split('.')[-1]
    print(result_5)
    return result_5

#####启动服务####
#进行一次预计算，以初始化计算库
# if __name__ == '__main__':
id = add()
cache[id].rough_path = np.array([[0,0],[40,0],[90,40]])
cache[id].x0 = np.array([0,0,0,0.8,0,0])
compute.update(cache[id])

print("初始化完成，服务运行中...")
#启动Web服务
app.run(debug = False, host='127.0.0.1', port=8081 ,threaded=False)
#app.run( debug = False,host='0.0.0.0', port=8080)#由于求解器要运行在主线程，所以Flask只能以单线程模式运行
