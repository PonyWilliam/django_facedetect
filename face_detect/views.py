from genericpath import exists
from django.http import HttpResponse
import json
from detect import detect
import time
from django.utils.deprecation import MiddlewareMixin
import os
from .forms import UploadFileForm
Face = detect.FaceEval()

def index(request):
    return HttpResponse("ok")
    
def check(request):

    if request.method == 'GET':
        return HttpResponse("hi")

    image = request.FILES.get('image')
    millis = int(round(time.time() * 1000))

    if not os.path.exists('./temp_upload'):
        os.mkdir('temp_upload')
    last = image.name.split(".")[-1]
    save_path = "./temp_upload/%s.%s"%(millis,last)

    with open(save_path,'wb') as f:
        f.flush()
        os.fsync(f)
        for content in image.chunks():
            f.write(content)
    f.close()
    # 通过Face接口去检测是否是人脸
    if Face.Check_single_face(save_path) == True:
        obj = HttpResponse(json.dumps({
            "code":200,
            "msg":"ok",
        }))
    else:
        obj = HttpResponse(json.dumps({
            "code":500,
            "msg":"no",
        }))
    # 腾出空间
    os.remove(save_path)
    obj["Access-Control-Allow-Origin"] = "*"
    obj["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    obj["Access-Control-Max-Age"] = "1000"
    obj["Access-Control-Allow-Headers"] = "*"
    return obj
