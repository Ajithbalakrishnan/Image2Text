import os
import torch
import logging
from tqdm import tqdm
import requests
import concurrent.futures
from PIL import Image
from transformers import AutoProcessor, Pix2StructForConditionalGeneration
import time
import configparser
import json
from datetime import datetime
import pandas as pd
import re
import sys
import traceback

from lar2car_excel_V7_1 import post_process_LAR
current_datetime = datetime.now()

config = configparser.ConfigParser()
config.read("./config.cfg")

MODEL_PATH = str(config["INFERENCE_CONFIG"]["MODEL_PATH"])
DATASET_DIR = str(config["INFERENCE_CONFIG"]["DATASET_DIR"])
OUTPUT_CSV_PATH = str(config["INFERENCE_CONFIG"]["OUTPUT_CSV_PATH"])
CLASSES= config["INFERENCE_CONFIG"]["CLASSES"]
CLASSES= CLASSES.split(',')
OUTPUT_JSON_ENABLE = config.getboolean('INFERENCE_CONFIG', 'OUTPUT_JSON_ENABLE')
OUTPUT_JSON_PATH = str(config["INFERENCE_CONFIG"]["OUTPUT_JSON_PATH"])

device = "cuda" if torch.cuda.is_available() else "cpu"

processor = AutoProcessor.from_pretrained(MODEL_PATH)
model = Pix2StructForConditionalGeneration.from_pretrained(MODEL_PATH).to(device)
model = torch.compile(model)
# model.to("cuda")
#torch_dtype=torch.bfloat16

def process_image(img_path):
    image = Image.open(img_path)
    inputs = processor(images=image, return_tensors="pt").to(device)
    generated_ids = model.generate(**inputs, max_new_tokens=512, early_stopping=True, use_cache=True)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return generated_text

def traceback_error():
    _, _, tb = sys.exc_info()
    traceback.print_tb(tb)
    tb_info = traceback.extract_tb(tb)
    return tb_info[-1]

def inference_main():
    predictions = list()
    error_cases = list()
    for i, img in enumerate(tqdm(os.listdir(DATASET_DIR))):
        try:
            t0 = time.time()
            print(f"Processing Image : {img}")
            image = Image.open(os.path.join(DATASET_DIR,img))  

            # image.thumbnail((800, 300))
            inputs = processor(images=image, return_tensors="pt").to(device)

            t4 = time.time()

            #with torch.backends.cuda.sdp_kernel(enable_flash=True, enable_math=False):   # TODO kernal leval optimization for HF-pytorch inference.
            generated_ids = model.generate(**inputs, max_new_tokens=512, early_stopping=True, do_sample=True, use_cache=True).to(device)
            t5 = time.time()
            generated_text = processor.decode(generated_ids[0],skip_special_tokens=True)
        #    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0] # TODO need to see whats the inference time difference between these apis.
            t6 = time.time()

            try:

                p = re.compile('(?<!\\\\)\'')
                generated_text = p.sub('\"', generated_text)
                # generated_text.encode('unicode_escape')
                generated_text = json.loads(generated_text)
                

                Ordered_Dict = dict()

                Ordered_Dict = {}
                Ordered_Dict['img_name'] = img
                Ordered_Dict['img_size'] = str(image.size)
                Ordered_Dict['infr_time'] = str(t6-t0)

                for key in CLASSES:

                    if key in generated_text.keys():

                        Ordered_Dict[key]=generated_text[key]

                        if key=='lar':
        
                            try:
                                Ordered_Dict['lar_n'] = str(post_process_LAR(generated_text[key]))

                            except:
                                Ordered_Dict['lar_n'] = ""
                                continue

                    else:
                        Ordered_Dict[key]= None

                print(f"{Ordered_Dict}")
                predictions.append(Ordered_Dict)

                scores = dict()

                if OUTPUT_JSON_ENABLE:
                    scores["predictions"] = generated_text
                    with open(os.path.join(OUTPUT_JSON_PATH,img.split('.')[0]+'.json'), "w") as outfile:
                        json.dump(scores, outfile)

            except Exception as e:
                error_cases.append(img)
                print(f"Error while processing Image : {img}  {e}")
                filename, line, func, text = traceback_error()
                logging.error(f"Error in Processing. Failed at {filename} {line}  {func} {text} {e}")

                scores = dict()

                if OUTPUT_JSON_ENABLE:
                    scores["predictions"] = generated_text
                    with open(os.path.join(OUTPUT_JSON_PATH,img.split('.')[0]+'.json'), "w") as outfile:
                        json.dump(scores, outfile)

                continue

            print("")
            print("")
    
        except Exception as e:
            error_cases.append(img)
            print(f"Error while processing Image : {img}")
            print(e)
            filename, line, func, text = traceback_error()
            logging.error(f"Error in Processing. Failed at {filename} {line}  {func} {text} {e}")
            continue



    df = pd.DataFrame(predictions)
    df.to_csv(os.path.join(OUTPUT_CSV_PATH,os.path.basename(MODEL_PATH)+'_'+os.path.basename(DATASET_DIR)+'_'+
                            str(current_datetime.strftime("%d%m%Y_%H%M%S"))+'_.csv'),index=False)

    print(f"Error cases : {error_cases}")

if __name__ == "__main__":

    predictions = inference_main()



    # conditional generation
    # text = "A picture of"
    # inputs = processor(text=text, images=image, return_tensors="pt", add_special_tokens=False)

    # generated_ids = model.generate(**inputs, max_new_tokens=50)
    # generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    # print(generated_text)