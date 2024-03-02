from dataclasses import field
import os
import json
import shutil
from tqdm import tqdm
import random
import cv2

lines = []
images = []

out_folder = "dataset/Doc_Classifier/v1/Donut_data"

root_folder = "dataset/Doc_Classifier/Raw"

list_dir = os.listdir(root_folder)

if not os.path.isdir(out_folder):
    os.mkdir(out_folder)
if not os.path.isdir(os.path.join(out_folder,'train')):
    os.mkdir(os.path.join(out_folder,'train'))
if not os.path.isdir(os.path.join(out_folder,'test')):
    os.mkdir(os.path.join(out_folder,'test'))
if not os.path.isdir(os.path.join(out_folder,'validation')):
    os.mkdir(os.path.join(out_folder,'validation'))

# for subdir in list_dir:
#     for img  in tqdm(os.listdir(os.path.join(root_folder,subdir))):
#         try:
#             if subdir == img.split('_')[0]:
#                 continue
#             image_data = cv2.imread(os.path.join(root_folder,subdir,img))
                
#             new_img_name = subdir+"_"+img
#             cv2.imwrite(os.path.join(root_folder,subdir,new_img_name),image_data)
#             os.remove(os.path.join(root_folder,subdir,img))
#         except Exception as E:
#             print(f"Error : {E}   image name : {img}")
#             continue

# exit()

data_dict = dict()
for subdir in list_dir:
    
    for img  in tqdm(os.listdir(os.path.join(root_folder,subdir))):
        data = {"class" : subdir}
        line = {"gt_parse": data}
        lines.append(line)
        images.append(img)
        
        data_dict[img] = line

dict_keys = list(data_dict.keys())
random.shuffle(dict_keys)
train_ratio = int(len(dict_keys) *0.7)
print("train_ratio : ",train_ratio)

train_images = dict_keys[:train_ratio]
test_images = dict_keys[train_ratio:]

with open(os.path.join(out_folder,"train", "metadata.jsonl"), 'w') as f:
    for imgs in train_images:
        line = {"file_name": imgs, "ground_truth": json.dumps(data_dict[imgs])}
        f.write(json.dumps(line) + "\n")
        class_name = imgs.split('_')[0]
        shutil.copyfile(os.path.join(root_folder,class_name,imgs),os.path.join(out_folder,"train", imgs))

print(f"Train images : {len(train_images)}   Test Images : {len(test_images)}")

with open(os.path.join(out_folder,"test", "metadata.jsonl"), 'w') as f:
    for imgs in test_images:        
        line = {"file_name": imgs, "ground_truth": json.dumps(data_dict[imgs])}
        f.write(json.dumps(line) + "\n")
        class_name = imgs.split('_')[0]
        shutil.copyfile(os.path.join(root_folder,class_name,imgs),os.path.join(out_folder,"test", imgs))
        shutil.copyfile(os.path.join(root_folder,class_name,imgs),os.path.join(out_folder,"validation", imgs))

shutil.copyfile(os.path.join(out_folder,"test", "metadata.jsonl"),os.path.join(out_folder,"validation", "metadata.jsonl"))
