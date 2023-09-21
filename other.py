# -*- coding: utf-8 -*-
import cv2
from PIL import Image
from detectron2.data import MetadataCatalog
from detectron2.utils.visualizer import Visualizer
import sys
import requests
import tarfile
import json
import numpy as np
from os import path
from PIL import ImageFont, ImageDraw
from glob import glob
from matplotlib import pyplot as plt
import pytesseract
import random
from PIL import Image, ImageDraw  


class_labels = ['text', 'title', 'logo', 'sign', 'seal', 'date','name']

#Array of all models with paths to cfg and .pth files 
models_pack = {'faster_rcnn_R_50_FPN_3x': {'model_path' : "models/faster_rcnn_R_50_FPN_3x.pth", 'model_cfg' : "COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml"},
        'faster_rcnn_R_101_FPN_3x' : {'model_path' : "models/faster_rcnn_R_101_FPN_3x.pth", 'model_cfg' : "COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml"},
        'MaskRCNN_Resnet50_FPN_3X' : {'model_path' : "models/MaskRCNN_Resnet50_FPN_3X.pth", 'model_cfg' : "COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml"},
        'MaskRCNN_Resnet101_FPN_3X' : {'model_path' : "models/MaskRCNN_Resnet101_FPN_3X.pth", 'model_cfg' : "COCO-InstanceSegmentation/mask_rcnn_R_101_FPN_3x.yaml"},
        'MaskRCNN_Resnext101_32x8d_FPN_3X' : {'model_path' : "models/MaskRCNN_Resnet101_32x8d_FPN_3X.pth", 'model_cfg' : "COCO-InstanceSegmentation/mask_rcnn_R_101_32x8d_FPN_3x.yaml"},
        'my_model' : {'model_path' : "models/model_final_no_noise.pth", 'model_cfg' : "COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml"},
		'my_model_noise' : {'model_path' : "models/model_final.pth", 'model_cfg' : "COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml"},
        '101_on_gen': {'model_path' : "models/frcnn101_on_gen_data.pth", 'model_cfg' : "COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml"
                      }}



def debug_image_cv(img):
    cv2.namedWindow('out', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('out', 900,900)
    cv2.imshow('out',img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

colors1 = {'title': (1, 0, 0),
          'text': (0, 1, 0,),
          'seal': (0, 0, 1),
          'logo': (1, 1, 0),
          'sign': (0, 1, 1),
		  'date': (0, 0, 0),
		  'name': (1, 0, 1)}

colors = {'title': (255, 0, 0),
          'text': (0, 255, 0),
          'seal': (0, 0, 255),
          'logo': (255, 255, 0),
          'sign': (0, 255, 255),
		  'name': (255, 0, 255),
		  'date': (0, 0, 0)}

def visualize_outputs(cfg, in_name, image_cv, outputs):
    	   
    v = Visualizer(image_cv[:, :, ::-1], MetadataCatalog.get(cfg.DATASETS.TRAIN[0]), scale=1.2)
    instances = outputs["instances"].to("cpu")
    pred_boxes = instances.pred_boxes
    scores = instances.scores
    pred_classes = instances.pred_classes
    
    doc_repres = {'text': []}
    
    for i in range(0, len(pred_boxes)):
        box = pred_boxes[i].tensor.numpy()[0]
        score = round(float(scores[i].numpy()), 4)
        label_key = int(pred_classes[i].numpy())
        label = class_labels[label_key]
        x = int(box[0])
        y = int(box[1])
        w = int(box[2] - box[0])
        h = int(box[3] - box[1])

        print('Detected object of label=' + str(label) + ' with score=' + str(score) + ' and in box={x=' + str(x) + ', y=' + str(y) + ', w=' + str(w) + ', h=' + str(h) + '}')
        
        image = Image.open(in_name)
        box = pred_boxes[i].tensor.numpy()[0]            
        crop_image = image.crop(box)
        
        if(label in ['text', 'title', 'date','name']):                
            string = pytesseract.image_to_string(crop_image, lang='rus')
            if(label == 'text'):
                doc_repres['text'].append(string)
            elif(label == 'date'):
                doc_repres['date'] = string
            elif(label == 'name'):
                doc_repres['name'] = string
            elif(label == 'title'):
                if(y < 650):
                    doc_repres['org'] = string
                else:
                    doc_repres['title'] = string
        else:
            crop_image.save('static/' + label +'_crop_image.jpg')
            
        v.draw_box(box , edge_color = colors1[label])
        v.draw_text(str(label) + ' score ' + str(score), tuple([x,y]),color = colors1[label])
        
		
    print(doc_repres)
    v = v.get_output()
    img =  v.get_image()[:, :, ::-1]
    #debug_image_cv(img)
    return img, doc_repres
        

        
        