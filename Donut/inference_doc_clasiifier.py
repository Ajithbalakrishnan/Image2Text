"""
Donut
Copyright (c) 2022-present NAVER Corp.
MIT License
"""
import argparse
import json
import os
import re
from pathlib import Path
import time
import numpy as np
import torch
import datasets
from datasets import load_dataset, Image, Dataset
# from PIL import Image
from tqdm import tqdm
import cv2
import pandas as pd


from donut import DonutModel, JSONParseEvaluator, load_json, save_json
from collections import OrderedDict

import configparser
import json
config = configparser.ConfigParser()
config.read("./config.cfg")

CLASS= config["INFER_CONFIG"]["CLASS"]
CLASS = json.loads(CLASS) 


def test(args):
    # dataset1 = load_dataset("dataset/synth_donut", split="train").cast_column("image", Image(decode=False))
    # print(dataset1[0])
    pretrained_model = DonutModel.from_pretrained(args.pretrained_model_name_or_path)

    if torch.cuda.is_available():
        pretrained_model.half()
        pretrained_model.to("cuda")
    else:
        pretrained_model.encoder.to(torch.bfloat16)

    pretrained_model.eval()

    if args.save_path:
        os.makedirs(os.path.dirname(args.save_path), exist_ok=True)

    predictions = list()
    #ground_truths = []
    #accs = []
    #output_key_order = CLASS
    image_list = list()
    #evaluator = JSONParseEvaluator()
    prediction_dict = dict()

    for i, sample in tqdm(enumerate(os.listdir(args.dataset_name_or_path)), total=len(os.listdir(args.dataset_name_or_path))):
        
        try:

        
            img = Dataset.from_dict({"image": [os.path.join(args.dataset_name_or_path,sample)]}).cast_column("image", Image())
            #print(img['image'][0])
        
            output = pretrained_model.inference(image=img['image'][0],  prompt=f"<s_{args.task_name}>")["predictions"][0]
            print(f"{sample} : {output['class']}")

            image_list.append(sample)
            predictions.append(output['class'])
        except Exception as e:
            print("Error in infr : ",e)
            continue



    prediction_dict['Images'] = image_list
    prediction_dict['prediction'] = predictions
    create_excel(prediction_dict,args.save_path)


def create_excel(data_dict,save_path):

    df = pd.DataFrame(data_dict)
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    writer = pd.ExcelWriter(os.path.join(save_path,'results'+str(time.time())+'.xlsx'), engine='xlsxwriter')

    # Convert the dataframe to an XlsxWriter Excel object.
    df.to_excel(writer, sheet_name='Sheet1', index=False)

    # Close the Pandas Excel writer and output the Excel file.
    writer.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pretrained_model_name_or_path", type=str)
    parser.add_argument("--dataset_name_or_path", type=str)
    parser.add_argument("--split", type=str, default="test")
    parser.add_argument("--task_name", type=str, default=None)
    parser.add_argument("--save_path", type=str, default=None)
    args, left_argv = parser.parse_known_args()

    if args.task_name is None:
        args.task_name = os.path.basename(args.dataset_name_or_path)

    predictions = test(args)
