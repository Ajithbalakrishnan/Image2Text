import re
import wordninja as wn
import sys
import traceback
from num2words import num2words
from difflib import get_close_matches
import copy
import logging

class WordAmount2Numerics:
    def __init__(self, text):
        self.text = text.lower().replace("-", " ").replace(" and ", " ").replace("  "," ").replace(" hundred", "_hundred").split(" ")           # convert to list
        self.text.append("zero")            
        self.num = 0            
        self.Million = []              
        self.Thousand = []
        self.Hundred = []

    def Million_separator(self, text):
        x = 0
        Num_M = 0           
        for i in text:
            if i == "million":
                Num_M = text.index(i)
        new_text = []
        while x < Num_M:
            new_text.append(text[x])
            x += 1
        self.Million = new_text

    
    def Thousand_seprator(self, text):
        x = 1
        Num_M = 0           
        Num_T = 0               
        for i in text:
            if i == "thousand":
                Num_T = text.index(i)
            if i == "million":
                Num_M = text.index(i)
                x += Num_M
        if "million" not in text:
            Num_M = -1
            x = 0
        new_text = []
        while Num_M < x < Num_T :
            new_text.append(text[x])
            x += 1
        self.Thousand = new_text

    def Hundred_seprator(self, text):
        x = 1
        Num_T = 0           
        if "thousand" in text:
            for i in text:
                if i == "thousand":
                    Num_T = text.index(i)
                    x += Num_T
        if "thousand" not in text and "million" in text:
            for i in text:
                if i == "million":
                    Num_T = text.index(i)
                    x += Num_T
        if "thousand" not in text and "million" not in text:
            x= 0
            Num_T = -1
        new_text = []
        while x > Num_T and x < len(text):
            new_text.append(text[x])
            x += 1
            self.Hundred = new_text

    
    def counter(self, text , sep):          
        all_dic = {"a_hundred": 100,"one_hundred": 100, "two_hundred": 200, "three_hundred": 300, "four_hundred": 400,
                   "five_hundred": 500, "six_hundred": 600, "seven_hundred": 700, "eight_hundred": 800,
                   "nine_hundred": 900,"eleven_hundred":1100,"twelve_hundred":1200,"thirteen_hundred":1300,"fourteen_hundred":1400,"fifteen_hundred":1500,
                   "sixteen_hundred":1600,"seventeen_hundred":1700,"eighteen_hundred":1800,"nineteen_hundred":1900,
                   "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80,
                   "ninety": 90,"ninty":90,"fourty":40,
                   "ten": 10,"zero" : 0 ,"a" : 1,"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
                   "nine": 9,
                   "eleven": 11, "twelve": 12, "thirteen": 13, "forteen": 14, "fifteen": 15, "sixteen": 16,"fourteen": 14,
                   "seventeen": 17, "eighteen": 18, "nineteen": 19}
        textlist = text.split(" ")
        for i in textlist:
            if i in all_dic:
                self.num += all_dic[i] * sep

    def duplicate_error(self , text):
        Rhundred = 0
        Rtens = 0
        Rteens = 0
        Rones = 0
        hundred = ["one_hundred","two_hundred","three_hundred","four_hundred","six_hundred","seven_hundred",
                   "eight_hundred","nine_hundred","eleven_hundred","twelve_hundred","thirteen_hundred","fourteen_hundred","fifteen_hundred",
                   "sixteen_hundred","seventeen_hundred","eighteen_hundred","nineteen_hundred"]
        tens = ["twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety", "ten", ]
        ones = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
        teens = ["eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]
        for i in text:
            if i in hundred:
                Rhundred +=1
            if i in tens:
                Rtens += 1
            if i in teens :
                Rteens += 1
            if i in ones:
                Rones += 1
        if Rhundred > 1 or Rones > 1 or Rteens> 1 or Rtens> 1 :
            self.dup = "yes"
        else:
            self.dup = "no"

    #Calculate the final results
    def results(self):
        s = " "        
        if "million" in self.text :
            self.Million_separator(self.text)
            million_str = s.join(self.Million)
            self.counter(million_str, 1000000)
            self.duplicate_error(self.Million)
        if "thousand" in self.text :
            self.Thousand_seprator(self.text)
            thousand_str = s.join(self.Thousand)
            self.counter(thousand_str, 1000)
            self.duplicate_error(self.Thousand)

        self.Hundred_seprator(self.text)        
        hundred_str = s.join(self.Hundred)
        self.counter(hundred_str , 1)
        self.duplicate_error(self.Hundred)

def cent_words2numeric(cent_test):
    matches_cent = ["cent", "cents"]
    cent_amount_numeric=0
    cent_in_words_test = "zero"
    if any(x in cent_test for x in matches_cent):     
        if len(cent_test) >= 4 and ((cent_test[-4]=="dollar" and cent_test[-3]=="and") or (cent_test[-3]=="and") or (cent_test[-3]=="dollar")):
            cent_in_words_test=cent_test[-2:-1] 
        elif len(cent_test) >= 5 and ((cent_test[-5]=="dollar" and cent_test[-4]=="and") or (cent_test[-4]=="and") or (cent_test[-4]=="dollar")):			
            cent_in_words_test=cent_test[-3:-1]
        cent_in_words = " ".join(cent_in_words_test)
        if cent_in_words.isdigit():
            return int(cent_in_words)
        else:
            centObject = WordAmount2Numerics(cent_in_words)    
            centObject.results()
            return int(centObject.num)
    else:
        return 0

def lar_to_car_HW(amount_in_words_upper,CheckPath):
    # MODIFIED BY RIMMON v7.1
    ####################
    matches_cent = ["cent", "cents"]
    amount_in_words = amount_in_words_upper.lower()    
    amount_in_words = amount_in_words.replace("&", "and")
    amount_in_words1=amount_in_words.split()
    dollars_only= ["dollars"]
    if any(x in amount_in_words for x in dollars_only):
        amount_in_words = amount_in_words.replace("dollars", "dollar")
    matches_only = ["only"]
    # if any(x in amount_in_words for x in matches_only):
    #     amount_in_words="".join(amount_in_words.split("only")[:-1])
    ####################          
    matches_dollars = ["dollar"]
    cent_test = amount_in_words.split()
    match_words = ["thousand","hundred","million"]
    match_digit = ["one","two","three","four","five","six","seven","eight","nine"]
    match_tens = ["twenty","thirty","forty","fifty","sixty","seventy","eighty","ninety"]
    
    if cent_test: 
        if cent_test[0] in match_words:
            amount_in_words="one "+amount_in_words
        try:        
            if any(x in amount_in_words for x in match_words) or any(x in amount_in_words for x in match_tens):      
                try:                     
                    if any(x in amount_in_words for x in matches_dollars):                                                  
                        if cent_test[1] in match_tens and cent_test[0] in match_digit:                        
                            index = amount_in_words.index(cent_test[1])                        
                            amount_in_words=amount_in_words[:index] + "hundred " + amount_in_words[index:]                        
                            lar_check="".join(amount_in_words.split("dollar")[:-1])
                            lar=lar_check.strip()                                                                        
                        else:                        
                            lar_check="".join(amount_in_words.split("dollar")[:-1])
                            lar=lar_check.strip()                                                
                    elif len(cent_test)>=4 and cent_test[-4]=="and" and any(x in cent_test for x in matches_cent) :
                        lar_check=cent_test[:-4]
                        lar=" ".join(lar_check)                    
                    elif len(cent_test)>=3 and cent_test[-3]=="and" and any(x in cent_test for x in matches_cent):
                        lar_check=cent_test[:-3]
                        lar=" ".join(lar_check)                                
                    elif any(x in amount_in_words for x in matches_only):
                        lar_check = amount_in_words      
                        lar=lar_check.strip()                                                                
                    else:
                        lar_check = amount_in_words      
                        lar=lar_check.strip()                                
                except Exception as e:					
                    #print("Exception: Invalid amount of LAR for ID: ")
                    pass
                cent_amount_numeric=cent_words2numeric(cent_test)
                larObject = WordAmount2Numerics(lar)    
                larObject.results()
                car=larObject.num
                total_car=car+cent_amount_numeric/100.0        
            else:    
                lar=amount_in_words  
                if any(x in amount_in_words for x in matches_dollars):            
                    lar="".join(amount_in_words.split("dollar")[:-1])  
                lar_in_words = lar.split()        
                total_car=0        
                for i in range(len(lar_in_words)):      
                    lar_words_ind=lar_in_words[i]                  
                    wordObject = WordAmount2Numerics(lar_words_ind)                
                    wordObject.results()
                    car=wordObject.num  
                    #print(car)                                           
                    total_car+=car*pow(10,(len(lar_in_words)-i-1))   
                
                cent_amount_numeric=cent_words2numeric(cent_test)
                total_car+=cent_amount_numeric/100.0
            total_car = "{:.2f}".format(total_car)        
            return total_car                
        except Exception as e:			
            #print("Exception: Invalid amount for LAR to CAR conversion for ID: ",e)
            total_car = 0

'''def post_process(string):
    new_string=''
    dot_count=0
    for char in "".join(string.split()):
        if char in ['0','1','2','3','4','5','6','7','8','9',',','x','-']:
            if char == 'x':
                char='0'
            if char == '-':
                char='00'
            new_string+=char
        elif len(new_string) > 0 and new_string[-1]!='.' :
            new_string+='.'
            dot_count+=1
            if dot_count==2:
                new_string=new_string[:-1]
                break  

    return new_string'''

def LAR2CAR_output(LAR_input):	
    LAR_input = LAR_input.replace('- ','')
    LAR_output=LAR_input
    try:
        # MODIFIED BY RIMMON
        ####################
        Larwithciqf=(f'{lar_to_car_HW(LAR_input)}') # added in v7.1
        #LAR_input, ciqf = LAR_input.split('\\frac')
        LAR_input = LAR_input.split('\\frac')
        if len(LAR_input)>1:
            ciqf = LAR_input[1]
            ciqf_check = "".join(ciqf.split())
            if  ciqf_check[1] in ['}','n']:
                Larwithciqf=(f'{lar_to_car_HW(LAR_input,".")}')
            else:
                ciqf=post_process('0' + '\\frac' + ciqf)			
                Larwithciqf=(f'{lar_to_car_HW(LAR_input,".")[:-2]}{ciqf[2:]}')
                if Larwithciqf[-2]=='.':
                    Larwithciqf = Larwithciqf +'0'
                elif Larwithciqf[-1]=='.':
                    Larwithciqf = Larwithciqf +'00'	
            LAR_output=LAR_input+ "and "+num2words(ciqf[2:])+" cents"
            LAR_output = LAR_output.replace('-',' ')
        else:
            ciqf=''
        LAR_input = LAR_input[0]
        		
        ####################
    except:
        #print('here')
        Larwithciqf=(f'{lar_to_car_HW(LAR_input,".")}')
    
    dot_position = 	Larwithciqf.find('.')
    Larwithciqf = Larwithciqf[:dot_position] + Larwithciqf[dot_position:dot_position+3]
    #print(LAR_input,dot_position,Larwithciqf,LAR_output)
    return Larwithciqf,LAR_output

# import openpyxl

def remove_replace_decimal(total_car_without,CAR_input):
    total_car_without_lst=total_car_without.split(".")
    total_car_without_int=total_car_without_lst[0]
    total_car_without_dec=total_car_without_lst[1]

    CAR_input=str(CAR_input)
    CAR_input_lst=CAR_input.split(".")
    CAR_input_int=CAR_input_lst[0]
    CAR_input_dec=CAR_input_lst[1]

    total_car_with=str(total_car_without_int +"."+CAR_input_dec)

    return total_car_with


combination_label_list=['forty one', 'forty two', 'forty three', 'forty four', 'forty five', 'forty six', 'forty seven', 'forty eight', 'forty nine', 'seventy one', 'seventy two', 'seventy three', 'seventy four', 'seventy five', 'seventy six', 'seventy seven', 'seventy eight', 'seventy nine', 'ninety one', 'ninety two', 'ninety three', 'ninety four', 'ninety five', 'ninety six', 'ninety seven', 'ninety eight', 'ninety nine', 'twenty one', 'twenty two', 'twenty three', 'twenty four', 'twenty five', 'twenty six', 'twenty seven', 'twenty eight', 'twenty nine', 'sixty one', 'sixty two', 'sixty three', 'sixty four', 'sixty five', 'sixty six', 'sixty seven', 'sixty eight', 'sixty nine', 'fifty one', 'fifty two', 'fifty three', 'fifty four', 'fifty five', 'fifty six', 'fifty seven', 'fifty eight', 'fifty nine', 'eighty one', 'eighty two', 'eighty three', 'eighty four', 'eighty five', 'eighty six', 'eighty seven', 'eighty eight', 'eighty nine', 'thirty one', 'thirty two', 'thirty three', 'thirty four', 'thirty five', 'thirty six', 'thirty seven', 'thirty eight', 'thirty nine']


def lar_pp_comb(lar):

    lar_list = lar.lower().split(' ')
    new_lar = []
    for i in range(len(lar_list)-1):
        single_word_label_list = ['one','two','three','four','five','six','seven','eight','nine']
        if lar_list[i] in single_word_label_list and lar_list[i+1] in single_word_label_list:
            two_words = (' '.join(lar_list[i:i+2]))

            new_word = get_close_matches(two_words,combination_label_list)[0].split(' ')[0]
            new_lar.append(new_word)
        else:
            new_lar.append(lar_list[i])
    new_lar.append(lar_list[-1])

    return (' '.join(new_lar))


def lar_pp(LAR_input):
    # Removed 'billion' in v7.1 as it is rare but causes issue when the word 'bill' is in the predictions
    label_list=['twelve', 'nineteen', 'forty', 'fourteen', 'two', 'seventy', 'ciqf', 'six', 'ninety', 'five', 'fifteen', 'twenty', 'sixty', 'lakh', 'seven', 'thirteen', 'and', 'thousand', 'eight', 'three', 'nine', 'four', 'zero', 'fifty', 'only', 'hundred', 'eighteen', 'sixteen', 'cents', 'dollars', 'seventeen', 'eighty', 'ten', 'thirty', 'one', 'eleven', 'million']
    LAR_input_Prepro=[]
    LAR_input_Prepro2=""
    cent_part2=0
    LAR_input = LAR_input.replace("-"," ")

    LAR_input = LAR_input.replace('0.',' ')
    LAR_input = LAR_input.replace('cent',' cent')
    cent_part=[int(s) for s in re.findall(r'\b\d+\b', LAR_input)]
    LAR_input_split = LAR_input.split(" ")
    # ######bp()
    for i in range(len(LAR_input_split)):
        if LAR_input_split[i].isdigit():
            temp_match=[LAR_input_split[i]]
            if len(temp_match)>0 and len(temp_match[0])>0 :
                # #print(f'{i}, |{LAR_input_split[i]}|, {temp_match[0]}')
                LAR_input_Prepro.append(temp_match[0])		
                #print(f'1: {LAR_input_Prepro}')
                # continue	

        else:
            split_list = wn.split(LAR_input_split[i])
            split_list_verified = []
            for split_list_word in split_list:
                if split_list_word in label_list:
                    split_list_verified.append(split_list_word)
            if len(split_list_verified) != len(split_list):
                split_list_verified= [LAR_input_split[i]]


            for splitted_word in split_list_verified: #wn.split(LAR_input_split[i]):
                
                temp_match=get_close_matches(splitted_word,label_list)
                if len(temp_match)>0 and len(temp_match[0])>0 :
                    # #print(f'{i}, |{LAR_input_split[i]}|, {temp_match[0]}')
                    LAR_input_Prepro.append(temp_match[0])		
                    #print(f'2: {LAR_input_Prepro}')	
    # #print("INPUT: ",LAR_input_Prepro)
    # ######bp()

    LAR_input_Prepro2=' '.join(LAR_input_Prepro)
    if len(cent_part)>=1:
        cent_part2=cent_part[0]%100		

    LAR_input_Prepro2 = re.split(r'(\d+)',LAR_input_Prepro2 )[0]

    # #print(f'[{LAR_input_Prepro2}],[{cent_part2}]')
    LAR_input_Prepro2 = lar_pp_comb(LAR_input_Prepro2)
    ################################
    # eight three --> eighty three
    LAR_input_Prepro2 = lar_pp_comb(LAR_input_Prepro2)
    ################################
    #print (f'def lar_pp({LAR_input}): ||{LAR_input_Prepro2}||{cent_part2}')
    return LAR_input_Prepro2,cent_part2


def close_matching_anik(predicton,dictionary):
    x=[j for j in predicton.split()]
    z=[]
    for i in ((x)):        
        try:
            y=get_close_matches(i,dictionary,cutoff=0.1)
            z.append(y[0])
        except:
            z.append(i)
    return " ".join(z)



# Removed 'billion' in v7.1 as it is rare but causes issue when the word 'bill' is in the predictions
dictionary_lar_words = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen', 'twenty', 'thirty', 'fifty', 'forty', 'fourty', 'sixty', 'seventy', 'eighty', 'ninety', 'ninty', 'hundred', 'thousand', 'million', 'and', 'cents', 'dollars', 'only', 'no', 'exactly', 'pay', 'only', 'the', 'sum', 'of', 'dols', 'cts']

####################

from num2words import num2words
def check_for_CAR(final_string_to_return):
    base_string = final_string_to_return
    final_string_to_return_new=''
    # ######bp()
    dot_count=0
    # final_string_to_return = final_string_to_return.replace(' ','')
    for char in  final_string_to_return:
        if char in ['.','0', '1', '2', '3', '4','5','6', '7','8','9']:
            final_string_to_return_new+=char
            # #print(f'char: {char} if: {final_string_to_return_new}')
        
        elif char in ['a', 'c', 'd', 'e', 'l', 'n', 'o', 'r','s','t']:
            if dot_count < 2:
                final_string_to_return_new+='.'
                dot_count+=1
            # #print(f'char: {char} elif: {final_string_to_return_new}')
        elif char in [' ']:
            pass
        else:
            final_string_to_return_new=final_string_to_return
            # #print(f'char: {char} else: {final_string_to_return_new}')
            break
            
    output1 = (final_string_to_return_new.replace('..','.'))
    # #print(output1)
    try:
        # #print(output1.split('.'))
        output = output1.split('.')[0]
        output = num2words(output).split(' ')
        # #print(output)
        #return [i.replace('point','dollar') for i in output]
        output_list=[]
        for i in output:
            if i == 'point':
                i = 'dollars'
            output_list.append(i)
        # #print(output_list)
        return_string =  ' '.join(output_list)
        if 'dollars' not in output_list:
            # #print(output_list.append('dollars'))
            return_string =  ' '.join(output_list)+' dollars'
        # else:
        try:
            return return_string+' and '+output1.split('.')[1]+' cents'
        except:
            return return_string
        # #print(output_list)
        # return output_list

    except:
        return output1
    
# check_for_CAR('ten and 00 dollars')
def Lar_cleaning(LAR_field, printing=0, close_match_required = 0):
    if printing ==1: 
        print('Actual LAR field: ', LAR_field)
    LAR_field = str(LAR_field).lower()

    LAR_field = LAR_field.replace(' / ','/')
    LAR_field = LAR_field.replace('no ','no')
    LAR_field = LAR_field.replace('the sum of ','')
    LAR_field = LAR_field.replace('pay','')
    LAR_field = LAR_field.replace('only','')
    LAR_field = LAR_field.replace(' .',' ')
    LAR_field = LAR_field.replace('&','and')    
    LAR_field = LAR_field.replace(' .', ' ')
    LAR_field = LAR_field.replace('ciscis', '')
    

    #######################
    try:
        _ = int(LAR_field.split(',')[0][-1])
        LAR_field = LAR_field.replace(',', '')
    except:
        LAR_field = LAR_field.replace(',', ' ')
        
    #######################    
    

    LAR_field_new=''
    for char in LAR_field:
        if char in [' ', '.', '/','-','0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'l', 'm', 'n', 'o', 'p', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']:
            LAR_field_new = LAR_field_new + char 
        else:
            char=' '
            LAR_field_new = LAR_field_new + char

    if printing ==1: 
        print('symbols cleaned LAR field: ', LAR_field_new)



    LAR_field_new = LAR_field_new.replace('-', ' ')
    LAR_field_new = LAR_field_new.replace('no', '00')
    LAR_field_new = LAR_field_new.replace('xx', '00')
    LAR_field_new = LAR_field_new.replace(' x', ' 0')
    LAR_field_new = LAR_field_new.replace(' and', ' and ')
    LAR_field_new = LAR_field_new.replace('pay', ' pay ')
    LAR_field_new = LAR_field_new.replace('only', ' only ')
    LAR_field_new = LAR_field_new.replace('dol', ' dol')
    LAR_field_new = LAR_field_new.replace('dols','dols ')
    LAR_field_new = LAR_field_new.replace('cts',' cts')
    LAR_field_new = LAR_field_new.replace(' us', ' ')
    LAR_field_new = LAR_field_new.replace(' .0', ' 0')
    
    LAR_field_new = ' '.join(LAR_field_new.split())

    if printing ==1: 
        print(' - no xx x and-spacing cleaned LAR field: ', LAR_field_new)

    LAR_splitted_by_and = LAR_field_new.split(' and')
    if len(LAR_splitted_by_and)==1:
        LAR_field_new_before_and = LAR_splitted_by_and[0]
        ciqf_part=''
    elif len(LAR_splitted_by_and)==2:
        LAR_field_new_before_and = LAR_splitted_by_and[0]
        ciqf_part= LAR_splitted_by_and[-1]
    elif len(LAR_splitted_by_and)> 2:
        ##print(LAR_splitted_by_and)
        LAR_field_new_before_and = ' '.join(LAR_splitted_by_and[0:-1])
        ciqf_part= LAR_splitted_by_and[-1]
    
    if close_match_required==1:
        predicted_text = close_matching_anik(LAR_field_new_before_and,dictionary_lar_words)   
    else:
        predicted_text = LAR_field_new_before_and
           
    predicted_text = predicted_text.replace('exactly ','')
    if len(ciqf_part)>0:
        try:
            final_string_to_return = predicted_text+ ' and'+ (ciqf_part)
        except:
            final_string_to_return = predicted_text+ ' and'+ (ciqf_part)
    else:
        final_string_to_return = predicted_text
    ciqf_part=''
    if printing ==1: 
        print('cleaned LAR field: ', final_string_to_return)
    return final_string_to_return


def dollar_shifting(lar):
    # lar= 'Nineteen and 93/100 dollars'

    lar_list = lar.split(' ')
    lar_list_new=[]
    if lar_list[-1]=='dollars' or lar_list[-1]=='dollars':
        for words in lar_list[:-1]:
            if words == 'and':
                words = 'dollars and'
            try:
                lar_list_new.append(num2words(words))
            except:
                lar_list_new.append((words))            
        return (' '.join(lar_list_new))+ ' cents'
    else:
        return lar
        

################################################

def word_spliting(lar):
    new_lar=[]
    for word in lar.split(' '):
        if len(word)>1:
            for splitted_word in wn.split(word):
                new_lar.append(splitted_word)
        else:
            new_lar.append(word)
    return ' '.join(new_lar)

def my_split(s):
    return filter(None, re.split(r'(\d+)', s))


# if __name__=="__main__":
def LAR_to_CAR(LAR_input):
    if 1:
        # ######bp()
        LAR_input_orig= LAR_input
        LAR_input = check_for_CAR(LAR_input)
        if len(LAR_input)>0 and LAR_input[0]=='.':
            LAR_input = LAR_input_orig
        LAR_input=LAR_input.lower()

        LAR_input_Prepro,cent_part=lar_pp(LAR_input)
        
        #print("here",LAR_input_Prepro,cent_part)
        # #print(LAR_input_Prepro)
        # ######bp()
        # LAR_input_Prepro = (' '.join([word_spliting(word) for word in list(my_split(LAR_input_Prepro))])).replace(' / ', '/')
        LAR_input_Prepro = LAR_input_Prepro.replace(' and dollars','')
        LAR_input_Prepro = LAR_input_Prepro.replace(' and cents','')
        ######bp()
        # #print(LAR_input_Prepro)

        # MODIFIED BY RIMMON v7.1
        ####################
        if len(LAR_input_Prepro)>0:
            if LAR_input_Prepro.split()[-1]=='and':
                LAR_input_Prepro= ' '.join(LAR_input_Prepro.split()[:-1])
        ####################
        Larwithciqf,LAR_output=LAR2CAR_output(LAR_input_Prepro)
        # ######bp()
        try:
            total_car=str(round(float(Larwithciqf)+cent_part/100,2))
        except:
            Larwithciqf = '0.00'
            total_car=str(round(float(Larwithciqf)+cent_part/100,2))

        if total_car[-2]=='.':
            total_car+='0'
        LAR_output_split=LAR_output.split(" ")

        return total_car


def post_process1(string):
    new_string=''
    dot_count=0

    for char in "".join(string.split()):
        if char in ['0','1','2','3','4','5','6','7','8','9',',','x']:#,'-']:
            if char == 'x':
                char='0'
            new_string+=char
        elif len(new_string) > 0 and new_string[-1]!='.' :
            new_string+='.'
            dot_count+=1
            if dot_count==2:
                new_string=new_string[:-1]
                break  
    if len(new_string) > 0 and new_string[-1]=='.':
        new_string+='00'

    if new_string[-3] == ',' or new_string[-2] == ',' or new_string[-1] == ',':
        new_string = new_string.replace(',','.')

    if '.' not in new_string:
        new_string+='.00'			
    new_string = new_string.replace(',','')
    return new_string

def post_process(LAR_input):
    LAR_input = LAR_input.replace('- ','')
    LAR_input = LAR_input.replace('$',' ')
    LAR_input = LAR_input.replace('*',' ')
    LAR_input = LAR_input.replace('#',' ')
    LAR_input = LAR_input.replace(',','')		
    #LAR_input = LAR_input.replace('^','\\frac')
    try:
        # MODIFIED BY RIMMON
        ####################
        Larwithciqf=(f'{LAR_to_CAR(LAR_input)}')
        #LAR_input, ciqf = LAR_input.split('\\frac')
        LAR_input = LAR_input.split('\\frac')
        if len(LAR_input)>1:
            ciqf = LAR_input[1]
            ciqf_check = "".join(ciqf.split())
            if  ciqf_check[1] in ['}','n']:

                Larwithciqf=(f'{LAR_to_CAR(LAR_input)}')
            else:

                ciqf=post_process1('0' + '\\frac' + ciqf)


                Larwithciqf=(f'{str(LAR_to_CAR(LAR_input))[:-2]}{ciqf[2:]}')
                if Larwithciqf[-2]=='.':
                    Larwithciqf = Larwithciqf +'0'
                elif Larwithciqf[-1]=='.':
                    Larwithciqf = Larwithciqf +'00'		
        else:
            ciqf = ''
        LAR_input = LAR_input[0]
        ####################
    except:
        Larwithciqf=(f'{LAR_to_CAR(LAR_input)}')

    dot_position = 	Larwithciqf.find('.')
    Larwithciqf = Larwithciqf[:dot_position] + Larwithciqf[dot_position:dot_position+3]	
    return Larwithciqf.replace(" ", "")	


def post_process_CAR(input):
    car_value = input

    if len(car_value)>2 and (car_value[-1]).isdigit() and  car_value[-2]== '.':
        car_value = car_value + '0'

    try:
        car_value = ' '.join(car_value.split())
        # #print('multiple space to single space: ',car_value)
        # ######bp()
        if len(car_value)>3 and car_value[-2].isdigit() and car_value[-4].isdigit() and car_value[-3]==' ':
            car_value = car_value[:-3]+'.'+ car_value[-2:]
        # #print('additional dot:', car_value)
    except:
        #print('~~~~~~~~~~~~~~~~~~~~ car_value: ', car_value)
        pass

    new_car_value = ''
    
    for char in str(car_value).lower():
        if char in ['i','l']:
            char='1'
        if char in ['0','1','2','3','4','5','6','7','8','9',',','.']:
            new_car_value+= char

    new_car_value = new_car_value.replace('i','1')
    if len(new_car_value)>2 and new_car_value [-3] == ',':
        new_car_value = new_car_value[:-3]+ '.'+new_car_value[-2:]

    if len(new_car_value)>6 and new_car_value [-6] == ',' and new_car_value [-3] != '.':
            new_car_value = new_car_value[:-2]+ '.'+new_car_value[-2:]

    new_car_value = new_car_value.replace(',','')
    if len(new_car_value)>7:
        # ######bp()
        if new_car_value[-7]=='.':
            new_car_value= new_car_value[:-7]+ new_car_value[-6:]


    if len(new_car_value) ==0:
        new_car_value = '0'

    final_car=''
    if len(new_car_value)>0:
        #print('Input to CAR module: ', new_car_value)
        final_car = post_process(new_car_value)
    return final_car

#################################################################
def post_process_LAR(input):   
    string = input.lower()
    # MODIFIED BY RIMMON v7.1 
    # Removed 'billion' in v7.1 as it is rare but causes issue when the word 'bill' is in the predictions
    ####################
    joined_words_sublist = ['hundred', 'thousand', 'cent', 'dollar', 'million', 'twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety', 'lakh']#['twelve', 'nineteen', 'forty', 'fourteen', 'two', 'seventy', 'ciqf', 'six', 'ninety', 'five', 'fifteen', 'twenty', 'sixty', 'lakh', 'seven', 'thirteen', 'and', 'thousand', 'eight', 'three', 'nine', 'four', 'zero', 'fifty', 'only', 'hundred', 'eighteen', 'sixteen', 'cents', 'dollars', 'seventeen', 'eighty', 'ten', 'thirty', 'one', 'eleven', 'million']
    for word in joined_words_sublist:
        if word in string:
            string = string.replace(word,' '+word+' ')
    string =' '.join(string.split())
    ####################          
    string = string.split('no/')[0]
    string = string.split('no /')[0] 
    string = string.split('xx/')[0]
    string = string.split('xx /')[0]

    string = string.replace('pay','')
    string = string.replace(',',' ')
    string = string.replace('exactly','')
    string = string.replace('the sum of','')
    string = string.replace('&','and')
    string = string.replace('and.','and ')
    string = string.replace('and .','and ') 
    # MODIFIED BY RIMMON v7.0
    ####################
    string = ' '.join(string.split())
    if len(string.split(' '))>3 and string.split(' ')[1] =='and':
        if string.split(' ')[-1] in ['dollar','dollars', 'u.s.dollars']:
            string = ' '.join(string.split(' ')[:-1])
        string = string.replace(' and ', ' dollar and ')
    elif len(string.split(' '))>3 and 'and' in string:
        if string.split(' ')[-1] in ['dollar','dollars', 'u.s.dollars']:
            string = ' '.join(string.split(' ')[:-1])
        string = string.replace(' and ', ' dollar and ')
    ####################
    string = string.replace('hundredths', ' cents')
    string = string.replace('thousand hundred', 'thousand')

    try:
        if 'cent' in string and len(string.split('cent'))>1:
            if string.split('cent')[1] != '':
                if string.split('cent')[1][0] not in ['e','y']:
                    string = string.split('cent')[0]+'cents'
    except:
        print('Cent_Error')
        print(string.split('cent'))
    if '/' in string:# or '/ 1' in string:
        string = string.split('/')[0]+' cents'
    string_splitted = string.split(' ')
    if len(string_splitted) >1 and  string_splitted[1]=='and':
        string = string_splitted[0] + ' dollar '+ ' '.join(string_splitted[1:])
    
    final_lar=''
    if len(string)>0:
        #print('Input to LAR module: ', string)
        final_lar = (post_process(string))


    return final_lar

def lar2_car_raw_string(input_str):
    if type(input_str) == list:
        input_str = " ".join(input_str)
    if input_str == " " or input_str == None:
        return None
    else:
        return post_process_LAR(input_str)


def lar_2_car_main(json_obj):
    try:
        field_box_list = json_obj["fields"]
        for field_box in field_box_list:
            if field_box["field_name"] == "TOTAL_WITH_TAX":
                input_str = field_box["value_text"]  
                break
        # input_str = re.sub(r"^\s+|\s+$", "", input_str)
        input_str = input_str.strip()  #CHECK no need of 2 stripping
        if len(input_str.split()) == 0 or len(input_str.split()) == 1:
            processed_data = ""

        else:
            processed_data = post_process_LAR(input_str)
            
            # processed_data = force_zero(processed_data)
        if len(processed_data) == 0:
            processed_data = " "   #FIXME space as return value logic 
        flag = False  #TODO remove flag logic
        new_json_obj = copy.deepcopy(json_obj)
        for fields in json_obj["fields"]:
            if fields["field_name"] == "LAR2CAR":
                flag = True
        if not flag:
            new_field = {
                "field_name": "LAR2CAR",
                "key_id": [],
                "key_text": [],
                "value_id": [],
                "value_text": str(processed_data),
            }
            new_json_obj["fields"].append(new_field)

        

    except Exception as e:
        logging.error(f"Module-6.7 Error")




# input = "3486 Dollars and 00 Cents"#7e  Two and 72/100 Dollars
# print(input)
# print(post_process_LAR(input))

'''
1 hundred 72 cents --> 0.01
Buggy Predictions in v7.0:
    One	Hundred	FortyDollar(s)	and	0/100	Cents --> 100.00
    Pay	Only	One	Hundred	Seventy	Eight	And	97	/	100	Dollars --> 0.97



Buggy Predictions in v6:
    7e  Two and 72/100 Dollars --> 20.72
    Two and 72/100 Dollars --> 2.71
    KACTLY	42	DOLLARS	AND	61	CENTS --> 0.42
    42	DOLLARS	AND	61	CENTS --> 0.42
    PAY ~SEVEN HUNDRED FORTY-TWO AND 89 _ 100 8 3^r` --> error
    LAR_input = LAR_input.replace('^','\\frac') --> error   # commented in v7_1 --> LAR_input = LAR_input.replace('^','\\frac')
'''