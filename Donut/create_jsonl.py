from dataclasses import field
import os
import json
import shutil
from tqdm import tqdm


lines = []
images = []


#### Create JSONL files ########
key_folder = 'dataset/synthetic_data_v5/key/'
out_folder = 'dataset/synthetic_data_v5/donut_data/test/'
img_folder = 'dataset/synthetic_data_v5/img/'

for ann in tqdm(os.listdir(key_folder)[14500:]):
    if ann != ".ipynb_checkpoints":
        with open(key_folder + ann) as f:
            data = json.load(f)
    images.append(ann[:-4] + "png")
    line = {"gt_parse": data}
    lines.append(line)

#print(images)
#print(lines)

# f = open(out_folder + "metadata.jsonl")
with open(out_folder + "metadata.jsonl", 'w') as f:
    for i, gt_parse in enumerate(lines):
        #print(images[i])
        line = {"file_name": images[i], "ground_truth": json.dumps(gt_parse)}
        f.write(json.dumps(line) + "\n")
        shutil.copyfile(img_folder + images[i], out_folder + images[i])


# ##### Create synthetic data in SROIE format ########
# base_json_folder = 'dataset/synthetic_data_v5/json'
# base_img_folder = 'dataset/synthetic_data_v5/img'
# base_key_folder = 'dataset/synthetic_data_v5/key'

# for file in tqdm(os.listdir(base_json_folder)):
#     out_json  = {}
#     json_file = os.path.join(base_json_folder,file)
#     json_data = json.load(open(json_file))
#     field_data = json_data['fields']
#     f = open(os.path.join(base_key_folder,file),'w')
#     for data in field_data:
#         #print(data)
#         if(len(data['value_id'])!=0):
#             out_json[data['field_name']] = data['value_text'][0]
#     json.dump(out_json, f,indent=4)

