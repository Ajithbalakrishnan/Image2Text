import os
import torch
import re
from tqdm import tqdm
from donut import DonutModel
import cv2
import numpy as np
from PIL import Image
from datetime import datetime
import pandas as pd

current_datetime = datetime.now()

import configparser

config = configparser.ConfigParser()
config.read("./config.cfg")

MODEL_PATH= str(config["INFER_CONFIG"]["MODEL_PATH"])

DATASET= os.path.join(str(config["INFER_CONFIG"]["DATASET"]))

TASK_NAME= str(config["INFER_CONFIG"]["TASK_NAME"])

SAVE_JSON_PATH= os.path.join(str(config["INFER_CONFIG"]["SAVE_JSON_PATH"]))

class Img2TxtInferClass:

    def __init__(self,model_dir:str):
        self.model_path = model_dir
        self.load_model(self.model_path)
        
    def load_model(self,model_dir:str):
        '''
        Load the model from the given directory
        '''
        self.trained_model = DonutModel.from_pretrained(model_dir)
        if torch.cuda.is_available():
            self.trained_model.half()
            self.trained_model.to("cuda")
        else:
            self.trained_model.encoder.to(torch.bfloat16)
        self.trained_model.eval()

    def inference_main(self,task:str,np_img:np.ndarray):
        img = cv2.cvtColor(np_img, cv2.COLOR_BGR2RGB)
        im_pil = Image.fromarray(img)
        pred = self.trained_model.inference(image=im_pil,  prompt=f"<s_{task}>",return_attentions = False)["predictions"][0]
        return pred
    
    def clean_predictions(self,data_dict:dict, name:str):
        '''
        Clean the predicted string by using regex.
        
        '''
        data_dict['image'] = name
        if 'text_sequence' in data_dict.keys():

                filterd_car = re.sub(r"[^.0-9]+", '', data_dict['text_sequence'])
                filterd_car = filterd_car.strip()
                data_dict['odometer'] = filterd_car
                data_dict.pop('text_sequence')
                
        else:
            data_dict['odometer'] = 'NA'

        return data_dict

            
if __name__ == "__main__":
    '''
    This function initializes the model and loads the data.
    supported image formats are tif, png, jpg, jpeg
    
    '''
    img2txt_instance = Img2TxtInferClass(model_dir=os.path.join(MODEL_PATH))
    predictions = []
    
    for i, sample in tqdm(enumerate(os.listdir(DATASET)), total=len(os.listdir(DATASET))):
        
        if sample.endswith(('tif', 'png', 'jpg', 'jpeg')):
        
            try:
                image = cv2.imread(os.path.join(DATASET, sample))
                extraction = img2txt_instance.inference_main(task=TASK_NAME, np_img=image)
                
                final_out = img2txt_instance.clean_predictions(data_dict=extraction, name=sample)

                print(final_out)

            except Exception as e:
                print(f"error processing test sample : {sample}")
                print("Error : ", e)
                
            else:
                predictions.append(final_out)
                
                
        else:
            print("Invalid Image format/extension : ", sample)
            
    df = pd.DataFrame(predictions)
    df.to_csv(os.path.join(SAVE_JSON_PATH,os.path.basename(MODEL_PATH)+'_'+os.path.basename(DATASET)+'_'+
                            str(current_datetime.strftime("%d%m%Y_%H%M%S"))+'_''.csv'))
