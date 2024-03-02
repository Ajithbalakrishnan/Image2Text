from donut import DonutModel
import torch
from PIL import Image
import time
import os

pretrained_model = DonutModel.from_pretrained("pretrained_weights/models--naver-clova-ix--donut-base")#,ignore_mismatched_sizes=True)
if torch.cuda.is_available():
    pretrained_model.half()
    device = torch.device("cuda")
    pretrained_model.to(device)
else:
    pretrained_model.encoder.to(torch.bfloat16)
pretrained_model.eval()

task_name = "iitcdip"


pretrained_model.eval()



for imgs in os.listdir("/opt/donut/dataset/SROIE-Test"):
    input_img = Image.open(os.path.join("/opt/donut/dataset/SROIE-Test",imgs))
    print("")
    print("")
    t1 = time.time() 
    output = pretrained_model.inference(image=input_img, prompt=f"<s_{task_name}>", return_json=False)["predictions"]    #['attentions']
    t2 = time.time()
    print(output)
    print("")
    print("")
    print("time : ",(t2-t1))
