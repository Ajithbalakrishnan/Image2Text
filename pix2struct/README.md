# Introduction 

This Repo Contains Huggingface transformers pipeline for training \
and inference. Implimentations are mainly for Lockbox Img2Txt requirements.\
We have training and inference pipeline based on huggingface pluggins. We also \
implemented Accelerate and PEFT in the same pipeline. This pipeline is in its pilimininary stage \

implemented Models- \
    1. Pix2Struct base \
    2. Pix2Struct large \


TODO: Evaluation pipeline integration



# Getting Started

Use docker HFT_Pipeline:v1 \
Keep the data in data folder in MPTR/Donut format \
Update the hyper parameters in config.cfg file as given below, \
    1. Model name \
    2. Data dir \
    3. PEFT parameters if its required. \
    4. Epochs needed \
    5. Batch size (prefer 4/2) \
    6. Save dir \

Run Start_training.sh \

