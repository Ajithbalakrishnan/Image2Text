import os
import re
import json
import torch
import random
import numpy as np
import multiprocessing
from tqdm import tqdm, trange
from torch.utils.data import Dataset, DataLoader
from transformers import AutoProcessor, Pix2StructForConditionalGeneration
from typing import Any, List
from datasets import load_dataset
import transformers
import accelerate
from accelerate import Accelerator
import peft
from transformers.optimization import Adafactor, get_cosine_schedule_with_warmup
import matplotlib.pyplot as plt
from pynvml import *
from peft import get_peft_model, LoraConfig, TaskType

from config_parser import (
    TRAIN_DATASET_DIR,
    VAL_DATASET_DIR,
    PRETRAINEDWEIGHT_DIR,
    MAX_PATCHES_INPUT,
    MAX_LENGTH_INPUT,
    PADDINNG_INPUT,
    TRUNCATION_INPUT,
    IS_VQA_INPUT,
    ADD_SPECIAL_TOKENS,
    TOTAL_EPOCHES,
    TRAIN_BATCH_SIZE,
    VAL_BATCH_SIZE,
    LR,
    WARM_UP_STEPS,
    ENABLE_OPTMIZATION,
    R_VALUE,
    ALPHA_VALUE,
    DROPOUT,
    SAVE_MODEL_DIR,
)

# Parameter efficient fine tuning
if ENABLE_OPTMIZATION:
    peft_config = LoraConfig(
        inference_mode=False, r=R_VALUE, lora_alpha=ALPHA_VALUE, lora_dropout=DROPOUT, target_modules=["query", "value"]
    )

# torch.set_float32_matmul_precision('high')
# torch.backends.cuda.matmul.allow_tf32 = True
# torch.backends.cudnn.allow_tf32 = True

MAX_PATCHES = MAX_PATCHES_INPUT
os.environ["TOKENIZERS_PARALLELISM"] = "true"
added_tokens = []

# google/pix2struct-large
processor = AutoProcessor.from_pretrained(PRETRAINEDWEIGHT_DIR)
model = Pix2StructForConditionalGeneration.from_pretrained(PRETRAINEDWEIGHT_DIR, is_encoder_decoder=True)

accelerator = Accelerator(mixed_precision=bf16)

print("")
print(f"Transformers version: {transformers.__version__}")
print(f"Accelerate version: {accelerate.__version__}")
print(f"PEFT version: {peft.__version__}")

print("")
print("")

# model details
print(f"Model Name: {PRETRAINEDWEIGHT_DIR}")
print(f"Model Type: {type(model).__name__}")
print(f"Model Architecture: {model.config.architectures[0]}")
print(f"Number of Parameters: {model.num_parameters():,}")

print("")
print("")

if ENABLE_OPTMIZATION:
    model = get_peft_model(model, peft_config)
    print("Trainable Parameters After Optimization")
    model.print_trainable_parameters()
    print("")
    print("")

num_cores = multiprocessing.cpu_count()
processor.image_processor.is_vqa = IS_VQA_INPUT

graph_x = list()
graph_y = list()

if not os.path.isdir(SAVE_MODEL_DIR):
    os.mkdir(SAVE_MODEL_DIR)

def print_gpu_utilization():
    nvmlInit()
    handle = nvmlDeviceGetHandleByIndex(0)
    info = nvmlDeviceGetMemoryInfo(handle)
    print(f"GPU memory occupied: {info.used//1024**2} MB.")

def draw_loss_graph():
    plt.plot(graph_x, graph_y)
    plt.xlabel('Iterations')
    plt.ylabel('Loss')
    plt.title('Training loss')
    # plt.show(block=False)
    plt.savefig(os.path.join(SAVE_MODEL_DIR,"loss_chart.jpg"))
    plt.pause(0.1)

class ImageCaptioningDataset(Dataset):
    def __init__(self, dataset, processor):
        self.dataset = dataset
        self.processor = processor

    def __len__(self):
        return len(self.dataset)

    def __getitem__(self, idx):
        item = self.dataset[idx]

        if IS_VQA_INPUT:
            encoding = self.processor(images=item["image"], text="extract payement related informations:", return_tensors="pt", add_special_tokens=ADD_SPECIAL_TOKENS, max_patches=MAX_PATCHES,  
                padding=PADDINNG_INPUT, max_length=MAX_LENGTH_INPUT,truncation=TRUNCATION_INPUT).to(device)
        else:
            encoding = self.processor(images=item["image"], return_tensors="pt", add_special_tokens=ADD_SPECIAL_TOKENS, max_patches=MAX_PATCHES, 
                padding=PADDINNG_INPUT, max_length=MAX_LENGTH_INPUT,truncation=TRUNCATION_INPUT).to(device)  

        encoding = {k:v.squeeze() for k,v in encoding.items()}

        gt_parse = json.loads(item["ground_truth"])
        encoding["text"] = str(gt_parse["gt_parse"])
        return encoding

def collator(batch):
  new_batch = {"flattened_patches":[], "attention_mask":[]}
  texts = [item["text"] for item in batch]
  
  text_inputs = processor(text=texts, padding=PADDINNG_INPUT, return_tensors="pt", add_special_tokens=ADD_SPECIAL_TOKENS, max_length=MAX_LENGTH_INPUT, truncation=TRUNCATION_INPUT).to(device)
  
  new_batch["labels"] = text_inputs.input_ids
  
  for item in batch:
    new_batch["flattened_patches"].append(item["flattened_patches"])
    new_batch["attention_mask"].append(item["attention_mask"])
  
  new_batch["flattened_patches"] = torch.stack(new_batch["flattened_patches"])
  new_batch["attention_mask"] = torch.stack(new_batch["attention_mask"])

  return new_batch

def validate(model, val_dataloader, device):
    model.eval()
    correct = 0
    total = 0
    accuracy=0

    with torch.no_grad():
        for batch in tqdm(val_dataloader):
            labels = batch.pop("labels").to(device)
            flattened_patches = batch.pop("flattened_patches").to(device)
            attention_mask = batch.pop("attention_mask").to(device)

            outputs = model(flattened_patches=flattened_patches, attention_mask=attention_mask, labels=labels)
            # print(outputs)
    #         logits = outputs.logits

    #         _, predicted = torch.max(logits, 1)
    #         total += labels.size(0)
    #         correct += (predicted == labels).sum().item()

    # accuracy = 100 * correct / total
    return accuracy

train_dataset_batch = load_dataset(TRAIN_DATASET_DIR, split="train")

val_dataset_batch = load_dataset(VAL_DATASET_DIR, split="validation")

print(train_dataset_batch)
print(train_dataset_batch[0])

train_dataset = ImageCaptioningDataset(train_dataset_batch, processor)
val_dataset = ImageCaptioningDataset(val_dataset_batch, processor)

train_dataloader = DataLoader(train_dataset, shuffle=True, batch_size = TRAIN_BATCH_SIZE , collate_fn=collator)
val_dataloader = DataLoader(val_dataset, batch_size=VAL_BATCH_SIZE, collate_fn=collator)

optimizer = torch.optim.AdamW(model.parameters(), lr = LR)
scheduler = get_cosine_schedule_with_warmup(optimizer, num_warmup_steps=WARM_UP_STEPS, num_training_steps=(len(train_dataloader) * TOTAL_EPOCHES))

device = "cuda" if torch.cuda.is_available() else "cpu"
device = accelerator.device
model, optimizer, train_dataloader,scheduler, val_dataloader = accelerator.prepare(model, optimizer, train_dataloader, scheduler, val_dataloader)

model.to(device)

model.train()

iteration =0
best_val_accuracy = 0.0
best_epoch = -1
pbar = trange(TOTAL_EPOCHES, desc="Training", unit="Training")
print_gpu_utilization()

for epoch in pbar:
    pbar.set_description(f"Epoch {epoch}")

    with tqdm(train_dataloader, unit="batch") as tepoch: 
        for batch in tepoch:
            labels = batch.pop("labels")

            flattened_patches = batch.pop("flattened_patches")
            attention_mask = batch.pop("attention_mask")

            outputs = model(flattened_patches=flattened_patches,
                            attention_mask=attention_mask,
                            labels=labels)
            
            loss = outputs.loss

            accelerator.backward(loss)
            optimizer.step()
            optimizer.zero_grad()

            scheduler.step()  # Update the learning rate scheduler

            tepoch.set_postfix(loss=loss.item())
            tepoch.set_description(f"Epoch {epoch}")

            iteration += 1

            if iteration % 1000 == 0:
                graph_x.append(iteration)
                graph_y.append(loss.item())
                draw_loss_graph()

    if (epoch + 1) % 2 == 0:
        accelerator.wait_for_everyone()  # Wait for all processes to sync
        model.save_pretrained(SAVE_MODEL_DIR)
        processor.save_pretrained(SAVE_MODEL_DIR)

        print(f"Model Saved @ Epoch {epoch+1}")

    if (epoch + 1) % 5 == 0:
        # Validate the model
        accelerator.wait_for_everyone()
        val_accuracy = validate(model, val_dataloader, device)

        # Check if this is the best validation accuracy
        if val_accuracy > best_val_accuracy:
            best_val_accuracy = val_accuracy
            best_epoch = epoch + 1

            # Save the best model
            model.save_pretrained(SAVE_MODEL_DIR)
            processor.save_pretrained(SAVE_MODEL_DIR)

        print(f"Epoch {epoch+1} - Validation Accuracy: {val_accuracy:.2f}%")

# Print the best validation accuracy and epoch
print(f"Best Validation Accuracy: {best_val_accuracy:.2f}% (Epoch {best_epoch})")




