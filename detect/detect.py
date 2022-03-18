from time import sleep
from detect.utils import *
from tqdm import tqdm
from paddle import dtype, inference
import os, cv2
import numpy as np
from PIL import ImageDraw, ImageFont, Image
import pickle


class FaceEval:
    def __init__(self):
        # 相似度比例
        self.threshold = 0.35
        self.mtcnn = MTCNN()
        self.mtcnn_input_scale = 0.4  # 缩放图片加快计算
    def Check_face_data(self,paths):
        assert os.path.exists(paths), 'path {} not exist'.format(paths)
        for path in tqdm(os.listdir(paths)):
            temp = os.path.basename(path).split('.')
            if len(temp)!=2 or (temp[1] != 'png' and temp[1] != 'jpg'):
                print('file:%s is not a image,so continue'%path)
                continue
            img_path = os.path.join(paths,path)
            img = cv2.imdecode(np.fromfile(img_path,dtype=np.uint8),-1)
            imgs,_ = self.mtcnn.infer_image(img,img)
            if imgs is None:
                print('无法识别到人脸图片:%s' % img_path)
                continue
            if len(imgs) > 1:
                print('%s 包含了%d张人脸'%(img_path,len(imgs)))
                continue
            print("image:%s is ok"%path)
    def Check_single_face(self,path):
        try:
            img = cv2.imdecode(np.fromfile(path,dtype=np.uint8),-1)
            imgs,_ = self.mtcnn.infer_image(img,img)
        except Exception:
            return False
        
        if imgs is None:
            print('无法识别到人脸图片:%s' % path)
            return False
        if len(imgs) > 1:
            print('%s 包含了%d张人脸'%(path,len(imgs)))
            return False
        print("image:%s is ok"%path)
        return True
    def update_face_data(self):
        '''
        用于更新人脸数据库
        :return:
        '''
        face_db = {}
        assert os.path.exists(self.face_db_path), 'face_db_path {} not exist'.format(self.face_db_path)
        for path in tqdm(os.listdir(self.face_db_path)):
            temp = os.path.basename(path).split('.')
            if len(temp)!=2 or (temp[1] != 'png' and temp[1] != 'jpg'):
                continue
            name = os.path.basename(path).split('.')[0]
            image_path = os.path.join(self.face_db_path, path)
            # print(image_path)
            img = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), -1)
            imgs, _ = self.mtcnn.infer_image(img, img)
            
            if imgs is None:
                print('无法识别图片:%s' % image_path)
                continue
            if len(imgs) > 1:
                print('%s 包含了%d张人脸'%(image_path,len(imgs)))
                continue
            imgs = self.process(imgs)
            feature = self.infer(imgs)
            face_db[name] = feature[0]
        with open(self.face_data_path, "wb") as f:
            pickle.dump(face_db, f)
        print('finished faceDatabase transform!')
        return face_db

    @staticmethod
    def process(imgs):
        imgs1 = []
        for img in imgs:
            img = img.transpose((2, 0, 1))
            img = (img - 127.5) / 127.5
            imgs1.append(img)
        if len(imgs1) > 1:
            imgs = np.array(imgs1).astype('float32')
        else:
            imgs = imgs1[0][np.newaxis, :].astype('float32')
        return imgs

    @staticmethod
    def init_resnet50_predictor(model_dir):
        model_file = model_dir + '.pdmodel'
        params_file = model_dir + '.pdiparams'
        config = inference.Config()
        config.set_prog_file(model_file)
        config.set_params_file(params_file)
        # config.use_gpu()
        # config.enable_use_gpu(500, 0)
        predictor = inference.create_predictor(config)
        return predictor


