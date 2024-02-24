from transformers import AutoProcessor
from optimum.onnxruntime import ORTModelForPix2Struct
from PIL import Image
import requests

processor = AutoProcessor.from_pretrained("dist/results/v4")
model = ORTModelForPix2Struct.from_pretrained("dist/results/v4", export=True, use_io_binding=True)


for img in tqdm(os.listdir("Dataset/Inference_Data/Test_Dataset_MP")):
    
    t1 = time.time()
    image = Image.open("Dataset/Inference_Data/Test_Dataset_MP/"+img)  
    print(image.size)

    inputs = processor(images=image, return_tensors="pt").to("cuda")

    gen_tokens = model.generate(**inputs).to("cuda")
    outputs = processor.batch_decode(gen_tokens, skip_special_tokens=True)[0]

    print(outputs)



# from transformers import AutoProcessor
# from optimum.onnxruntime import ORTModelForPix2Struct
# from PIL import Image
# import requests

# processor = AutoProcessor.from_pretrained("google/pix2struct-ai2d-base")
# model = ORTModelForPix2Struct.from_pretrained("google/pix2struct-ai2d-base", export=True, use_io_binding=True)

# url = "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/transformers/tasks/ai2d-demo.jpg"
# image = Image.open(requests.get(url, stream=True).raw)
# question = "What does the label 15 represent? (1) lava (2) core (3) tunnel (4) ash cloud"
# inputs = processor(images=image, text=question, return_tensors="pt")

# gen_tokens = model.generate(**inputs)
# outputs = processor.batch_decode(gen_tokens, skip_special_tokens=True)