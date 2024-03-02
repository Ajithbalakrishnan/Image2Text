import os
from pathlib import Path
import torch
import datasets
from datasets import load_dataset, Image, Dataset
# from PIL import Image
from tqdm import tqdm
from donut import DonutModel, JSONParseEvaluator, load_json, save_json
import configparser
from datetime import datetime
import pandas as pd

from lar2car_excel_V7_1 import post_process_LAR
current_datetime = datetime.now()

config = configparser.ConfigParser()
config.read("./config.cfg")

CLASS= config["INFER_CONFIG"]["CLASS"]
CLASS= CLASS.split(',')
MODEL_PATH= str(config["INFER_CONFIG"]["MODEL_PATH"])
DATASET= str(config["INFER_CONFIG"]["DATASET"])
SPLIT= str(config["INFER_CONFIG"]["SPLIT"])
TASK_NAME= str(config["INFER_CONFIG"]["TASK_NAME"])
SAVE_JSON_PATH= os.path.join(str(config["INFER_CONFIG"]["SAVE_JSON_PATH"]))

out_dict = dict()
class_list = list()
for label in CLASS:
    out_dict[label] = list()

def test():

    pretrained_model = DonutModel.from_pretrained(MODEL_PATH)

    if torch.cuda.is_available():
        pretrained_model.half()
        pretrained_model.to("cuda")
    else:
        pretrained_model.encoder.to(torch.bfloat16)

    pretrained_model.eval()

    if SAVE_JSON_PATH:
        os.makedirs(os.path.dirname(SAVE_JSON_PATH), exist_ok=True)

    predictions = []
    ground_truths = []
    accs = []
    output_key_order = CLASS

    evaluator = JSONParseEvaluator()

    for i, sample in tqdm(enumerate(os.listdir(DATASET)), total=len(os.listdir(DATASET))):
        try:
            img = Dataset.from_dict({"image": [os.path.join(DATASET,sample)]}).cast_column("image", Image())
                
            output = pretrained_model.inference(image=img['image'][0],  prompt=f"<s_{TASK_NAME}>",return_attentions = False)["predictions"][0]

            output['img_name'] = sample
            print(output)
            Ordered_Dict = {}
            for key in output_key_order:
                if key in output.keys():
                    Ordered_Dict[key]=output[key]

                    if key=='lar':
                        try:
                            Ordered_Dict['lar_n'] = str(post_process_LAR(output[key]))
                        except:
                            Ordered_Dict['lar_n'] = ""
                            continue
                        
        except Exception as e:
            print(f"Exception Occured {e}")
        
        else:    
            predictions.append(Ordered_Dict)

    df = pd.DataFrame(predictions)
    df.to_csv(os.path.join(SAVE_JSON_PATH,os.path.basename(MODEL_PATH)+'_'+os.path.basename(DATASET)+'_'+
                           str(current_datetime.strftime("%d%m%Y_%H%M%S"))+'_''.csv'))

    scores = {}
    if SAVE_JSON_PATH:
        scores["predictions"] = predictions
        save_json(os.path.join(SAVE_JSON_PATH,os.path.basename(MODEL_PATH)+'_'+os.path.basename(DATASET)+'.json'), scores)


    return predictions


if __name__ == "__main__":

    predictions = test()
