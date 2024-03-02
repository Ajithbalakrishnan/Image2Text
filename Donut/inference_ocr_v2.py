import argparse
import json
import os
import re
from pathlib import Path

import numpy as np
import torch
import datasets
from datasets import load_dataset, Image, Dataset
from tqdm import tqdm
import cv2

from donut import DonutModel, JSONParseEvaluator, load_json, save_json
from collections import OrderedDict

import json

def test(args):
   
    pretrained_model = DonutModel.from_pretrained(args.pretrained_model_name_or_path)

    if torch.cuda.is_available():
        pretrained_model.half()
        pretrained_model.to("cuda")
    else:
        pretrained_model.encoder.to(torch.bfloat16)

    pretrained_model.eval()

    if args.save_path:
        os.makedirs(os.path.dirname(args.save_path), exist_ok=True)

    predictions = []
    ground_truths = []
    accs = []
    output_key_order = CLASS

    evaluator = JSONParseEvaluator()

    for i, sample in tqdm(enumerate(os.listdir(args.dataset_name_or_path)), total=len(os.listdir(args.dataset_name_or_path))):
        #print("Image: ", sample)
        img = Dataset.from_dict({"image": [os.path.join(args.dataset_name_or_path,sample)]}).cast_column("image", Image())
        #print(img['image'][0])
       
        output = pretrained_model.inference(image=img['image'][0],  prompt=f"<s_{args.task_name}>",return_attentions = False)["predictions"][0]
        print(output)
        output['image'] = sample

        Ordered_Dict = {}
        for key in output_key_order:
            if key in output.keys():
                Ordered_Dict[key]=output[key]
        predictions.append(Ordered_Dict)

    scores = {}

    if args.save_path:
        scores["predictions"] = predictions
        save_json(args.save_path, scores)

    return predictions


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
