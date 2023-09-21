# -*- coding: utf-8 -*-
from detectron2.engine import DefaultTrainer
from detectron2.config import get_cfg
from detectron2 import model_zoo
from detectron2.data.datasets import register_coco_instances
from other import models_pack
import torch

#validation and train datasets registration. 
#register_coco_instances("val_dataset", {}, "publaynet/val.json", "publaynet/val")
#register_coco_instances("train_dataset", {}, "publaynet/train.json", "publaynet/train")
register_coco_instances("val_dataset", {}, "dataset/val/annotations.json", "ds/nv")
register_coco_instances("train_dataset", {}, "dataset/train/annotations.json", "ds/nt")

#config 
model = models_pack['faster_rcnn_R_101_FPN_3x']
model_zoo_config_name = model['model_cfg']

cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file(model_zoo_config_name))
cfg.DATASETS.TRAIN = ('train_dataset')
cfg.DATASETS.TEST = ('val_dataset')
cfg.OUTPUT_DIR = "out"
cfg.DATALOADER.NUM_WORKERS = 8
    #uncomment this for pre-trained model
cfg.MODEL.WEIGHTS = model['model_path']
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.7
cfg.SOLVER.IMS_PER_BATCH = 1
cfg.SOLVER.BASE_LR = 0.001
cfg.SOLVER.MAX_ITER =20000
cfg.SOLVER.STEPS = []
cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 256
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 7
cfg.TEST.DETECTIONS_PER_IMAGE = 20
cfg.INPUT.MIN_SIZE_TRAIN = (580, 612, 644, 676, 708, 740)

#optional. Sometimes torch may use all GPU memory
torch.cuda.empty_cache()

trainer = DefaultTrainer(cfg)
trainer.resume_or_load(resume=False)
trainer.train()