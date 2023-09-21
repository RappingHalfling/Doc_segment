
import os
import glob
import numpy as np
import warnings
warnings.filterwarnings('ignore')
import json
from flask import Flask, render_template, request
from flask import json as fJson
from PIL import Image

import cv2
import numpy
from detectron2 import model_zoo
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from other import visualize_outputs, models_pack, markup
from detectron2.evaluation import COCOEvaluator, inference_on_dataset, coco_evaluation
from detectron2.data import build_detection_test_loader, DatasetCatalog
from detectron2.data.datasets import register_coco_instances



################################################################################

# Приложение для наглядной демонстрации полученных результатов.

app = Flask(__name__)
# app.config['SOLALCHEMY_DATABASE_URI'] = "sqlite:///pic.db"
# db = SQLAlchemy
@app.route("/", methods=['GET','POST'])
def predict():
    doc_repres = {'text': ['?'], 'org': '?', 'title': '?', 'date': '?', 'name': '?'}
    mAPres = {'bbox': {'AP': "?",'AP50': "?",'AP75': "?",'AP-text': "?",'AP-title': "?",'AP-logo': "?",'AP-seal': "?",'AP-sign': "?",'AP-date': "?",'AP-name': "?"}}
    
    if request.method == 'GET':
        
        files = glob.glob('static/*')
        for f in files:
            os.remove(f)
        return render_template('index.html', mAPres = mAPres, doc_repres = doc_repres)
    else:
        files = glob.glob('static/*')
        for f in files:
            os.remove(f)
        
        model = models_pack['my_model_noise']
        model_zoo_config_name = model['model_cfg']
        prediction_score_threshold = 0.7
    
        cfg = get_cfg()
        cfg.merge_from_file(model_zoo.get_config_file(model_zoo_config_name))
        cfg.MODEL.WEIGHTS = model['model_path']
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = prediction_score_threshold
        cfg.MODEL.ROI_HEADS.NUM_CLASSES = 7
    
        predictor = DefaultPredictor(cfg)
        image_pil = request.files["image"]
        ann = request.files["ann"]
        
		
        image_cv = cv2.imdecode(np.frombuffer(image_pil.read(), np.uint8), cv2.IMREAD_COLOR)
        outputs = predictor(image_cv)
    
    
        jsonsaveddict = coco_evaluation.instances_to_coco_json(outputs["instances"].to("cpu"),0)
        with open("static/annotation.json", "w") as outfile:
            json.dump(jsonsaveddict, outfile)
        
        in_name = 'static/' + image_pil.filename
        cv2.imwrite(in_name, image_cv)
        
        img, doc_repres = visualize_outputs(cfg, in_name, image_cv, outputs)
        if(ann):
            annot = fJson.load(ann)
            with open("static/ann_gen.json", "w") as outfile:
                json.dump(annot, outfile)
            img2 = markup(Image.open(in_name),annot)
            img2.save('static/gen_image.jpg')
            
            register_coco_instances	("my_dataset_val", {}, 'static/ann_gen.json', 'static')

            evaluator = COCOEvaluator("my_dataset_val", cfg, False, output_dir="")
            val_loader = build_detection_test_loader(cfg, "my_dataset_val")

            mAPres = inference_on_dataset(predictor.model, val_loader, evaluator)
            DatasetCatalog.remove("my_dataset_val")
		
        cv2.imwrite('static/out_image.jpg', img)
		
        return render_template('index.html', inname = image_pil.filename, mAPres = mAPres, doc_repres = doc_repres)#, box_content =box_content)
                                       
if __name__ == "__main__":
    app.run(debug=False)

    

