from dataclasses import field
import os
import json
import shutil
from tqdm import tqdm
import random
import cv2

lines = []
images = []

key_folder = '/home/v-labs-test-server1/AB/donut/dataset/Sample_Donut_Data/Jsons/'
out_folder = '/home/v-labs-test-server1/AB/donut/dataset/Sample_Donut_Data/Donut_data/'
img_folder = '/home/v-labs-test-server1/AB/donut/dataset/Sample_Donut_Data/Images/'


if not os.path.isdir(out_folder):
    os.mkdir(out_folder)
if not os.path.isdir(os.path.join(out_folder,'train')):
    os.mkdir(os.path.join(out_folder,'train'))
if not os.path.isdir(os.path.join(out_folder,'test')):
    os.mkdir(os.path.join(out_folder,'test'))
if not os.path.isdir(os.path.join(out_folder,'validation')):
    os.mkdir(os.path.join(out_folder,'validation'))


data_dict = dict()
wrong_img =0
for img in tqdm(os.listdir(img_folder)):
    ann = img.split('.')[0]+'.json'
    if os.path.exists(os.path.join(key_folder,ann)):

        with open(os.path.join(key_folder,ann)) as f:
            data = json.load(f)
        line = {"gt_parse": data}
        lines.append(line)
        images.append(img)
        data_dict[img] = line
    else:
        wrong_img +=1


print("Json not found error : ",wrong_img)
        
    
dict_keys = list(data_dict.keys())
random.shuffle(dict_keys)
train_ratio = int(len(dict_keys) *0.8)
print("train_ratio : ",train_ratio)


train_images = dict_keys[:train_ratio]
test_images = dict_keys[train_ratio:]


with open(os.path.join(out_folder,"train", "metadata.jsonl"), 'w') as f:
    for imgs in train_images:
        line = {"file_name": imgs, "ground_truth": json.dumps(data_dict[imgs])}
        f.write(json.dumps(line) + "\n")
        shutil.copyfile(os.path.join(img_folder,imgs),os.path.join(out_folder,"train", imgs))


with open(os.path.join(out_folder,"test", "metadata.jsonl"), 'w') as f:
    for imgs in test_images:        
        line = {"file_name": imgs, "ground_truth": json.dumps(data_dict[imgs])}
        f.write(json.dumps(line) + "\n")
        shutil.copyfile(os.path.join(img_folder,imgs),os.path.join(out_folder,"test", imgs))
        shutil.copyfile(os.path.join(img_folder,imgs),os.path.join(out_folder,"validation", imgs))


shutil.copyfile(os.path.join(out_folder,"test", "metadata.jsonl"),os.path.join(out_folder,"validation", "metadata.jsonl"))


print(f"Train images : {len(train_images)}   Test Images : {len(test_images)}")