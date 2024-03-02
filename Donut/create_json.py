import os,json,glob
import pandas as pd
from tqdm import tqdm

excel_path = r"dataset/MVP-1_1250_templates/doc_gt.xls"
img_dir = r"dataset/MVP-1_1250_templates/img"

data = pd.read_excel(excel_path)
count = 0
for i in tqdm(range(len(data))):
    save_dict = {"payeename" : "","lar" : "","car" : "","date" : "","memo" : "","payername" : "", "AccountNumber" : "","micr" : ""}
    img_path = data["ID"][i]
    # client = str(data["CLIENT_ID"][i])
    # print(os.path.join(img_dir,client,img_path + '.tif'))
    exist_flag = None
    exist_flag = os.path.isfile(os.path.join(img_dir,img_path + '.png'))
    if exist_flag:
        if str(data["payeename"][i]) != "nan" or str(data["payeename"][i]) != "":
            save_dict["payeename"] = str(data["payeename"][i])
        else:
            save_dict["payeename"] = ""

        if str(data["lar"][i]) != "nan":
            save_dict["lar"] = str(data["lar"][i])
        else:
            save_dict["lar"] = ""

        if str(data["car"][i]) != "nan":

            car = "{:.2f}".format(float(data["car"][i]))
            save_dict["car"] = str(car)
        else:
            save_dict["car"] = ""

        if str(data["Raw_date"][i]) != "nan":
            save_dict["date"] = str(data["Raw_date"][i])
        else:
            save_dict["date"] = ""

        if str(data["payerdetails"][i]) != "nan":
            save_dict["payername"] = str(data["payerdetails"][i])
        else:
            save_dict["payername"] = ""

        if str(data["account_number"][i]) != "nan" :
            save_dict["AccountNumber"] = str(data["account_number"][i])
        else:
            save_dict["AccountNumber"] = ""

        if str(data["memo"][i]) != "nan" :
            save_dict["memo"] = str(data["memo"][i])
        else : 
            save_dict["memo"] = ""
        if str(data["micr"][i]) != "nan" :
            save_dict["micr"] = str(data["micr"][i])
        else : 
            save_dict["micr"] = ""

        json_path = os.path.join("dataset/MVP-1_1250_templates","json",img_path + ".json")
        with open(json_path, "w") as outfile:
            json.dump(save_dict, outfile)
        print("############################")
        count+=1
    else:
        print(img_path)
print("json : ",count)


# print(data.columns)