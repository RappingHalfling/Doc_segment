# Описание
Цель проекта - обучить модель faster_rcnn_R_101_FPN_3x для решения задачи сегментации отдельных смысловых частей документов. 
# Обучение
Обучение проходит на основе библиотеки [Detectron2](https://github.com/facebookresearch/detectron2).

На первом этапе модель учится на наборе [PubLayNet](https://github.com/ibm-aur-nlp/PubLayNet). Итоговая точность по метрике mAP - 0.842.

На втором этапе проводится дообучение на наборе "реальных документов". В моём случае это набор сгенерированный немного измененным алгоритмом [decree_gen](https://github.com/RappingHalfling/decree_gen) (Повышена совместимость готовых наборов с Detectron2; Повышена точность аннотаций генерируемых наборов). Итоговая точность по метрике mAP - 0.863.

# Ссылки 
Полный отчет по проекту: https://drive.google.com/file/d/1iAp_cJhb325flJXvrCmXPBVbgri1GMYB/view?usp=sharing

Обученые модели: https://drive.google.com/file/d/1l5cMVbLvpFgfVCbj9MHRAVeIUUy53Jps/view?usp=sharing

# Пример работы

<p>
<img src="https://github.com/RappingHalfling/Document_segmentation/blob/main/Screenshots/0_0.pdf.jpg" alt="drawing1" width="400"/> 
<img src="https://github.com/RappingHalfling/Document_segmentation/blob/main/Screenshots/out_image.jpg" alt="drawing2" width="400"/>
</p>

