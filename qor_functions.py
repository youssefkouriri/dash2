import csv
import json
import pandas as pd

#chnage qor to table lines
def getCsvData(qor):
    with open(qor) as qorFp:
        data =qorFp.readlines()
        table1 =[]
        for x in data:
           table1.append(x)
        table1 = [x.strip() for x in table1 if x] 
        return table1 

def stringToDouble(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        pass

    return s or None # assume value is a string 

#change each line in qor to dictionary
def parse(d):
    segments = d.strip().split(':')
    qor_data = segments[-1]
    test = ':'.join(segments[:-1])
    result = {}
    retval = []
    result['Design'] = test.strip()
    for qor in [q.strip() for q in qor_data.strip(';').split(';')]:
        metric, value = [d.strip() for d in qor.split('=', 1)]
        result[metric] = stringToDouble(value)
    result.pop("Design")    
    return result

#append all qor lines dicts in a table
def change_to_table(filename):    
    retval = []    
    for i in range(len(getCsvData(filename))): 
        retval.append(parse(getCsvData(filename)[i]).copy())
    return retval       


#change final table (exit to status)
def change(table):
    table_modified = []
    dic_modified = {}
    for i in range(len(table)):
        #print(i)
        for key in  table[i].keys():
            if key == 'exit' and table[i][key] == 0:
                   dic_modified.update({key.replace("exit","status"):'PASS'})
            elif key == 'exit' and table[i][key] == 1:
                   dic_modified.update({key.replace("exit","status"):'FAIL'})
            else:
                dic_modified.update({key:stringToDouble(table[i][key])})          
        table_modified.append(dic_modified)
        dic_modified={}
    return table_modified

#get all metrics in qor
def get_qor_metrics(filename):
    retval = change(change_to_table(filename))
    headers = []
    for i in range(len(retval)):
       for key in  retval[i].keys():
           headers.append(key)
    final_headers = list(dict.fromkeys(headers)) 
    return final_headers    
#return >table    
def get_taller_table(table1,table2):
    if len(table1)>= len(table2):
        return table1
    else:
        return table2 
#return <table
def get_shorter_table(table1,table2):
    if len(table1)< len(table2):
        return table1
    else:
        return table2  
#change the name of metrics to create multicolumn table with dash
def change_table(table,version):
    table_mod = []
    dict1={}
    for dict in table:
       for key in dict:
           dict1.update({key + version: dict[key]})
       table_mod.append(dict1)
       dict1={}
    return table_mod 
#merge two qor in one table (two lines of qor in one dict)
def merge_qor(table1,table2,version1,version2):
    table_pro = change_table(get_taller_table(table1,table2),version1)
    for i in range(len(table_pro)):
        for j in  range(len(change_table(get_shorter_table(table1,table2), version2))):
           if table_pro[i]["Design-testname" + version1] == change_table(get_shorter_table(table1,table2), version2)[j]["Design-testname" + version2]:
               table_pro[i].update(change_table(get_shorter_table(table1,table2), version2)[j])
    for i in table_pro:
        i.pop("Design-testname" + version2, "done")
    return table_pro  

def perc_change(x,y):
	try:
				
		diff_per = round(((float(x) - float(y)))/float(y),4)
	except:	
		diff_per = ""
	return diff_per      

def completion_rate(table):
    i=0
    for dic in table:
        for key in dic:
            if key =="status" and dic[key] == "PASS":
                i += 1
    return (i/len(table))*100 
    
def append_diff(table1,table2,version1,version2):
    table_final =[]
    dict1={}
    for dict in merge_qor(table1,table2,version1,version2):
        dict1.update(dict)
        for key in dict:
         for key2 in dict:
           if key.replace(version1,"") == key2.replace(version2,""):
               dict1.update({key.replace(version1,"") + "diff" : perc_change(dict[key2],dict[key]) })
        table_final.append(dict1)
        dict1 = {}
    return table_final    

def get_all_columns(table1,table2,version1,version2):
    vid2= []
    for dict in append_diff(table1,table2,version1,version2):
        for key in dict:
          vid2.append(key) 
    return vid2    

def get_diff_headers(table1,table2,version1,version2):
    vid = []
    for dict in append_diff(table1,table2,version1,version2):
      for key in dict:
        if key.endswith("diff") and dict[key] !="" :
            vid.append(key)
    final_vid = list(dict.fromkeys(vid))         
    return final_vid 

def show_degradation(num,records,version1,version2):
    table = []
    dic1 = {}
    for dict in records:
        for key in dict:
            if key.endswith("diff"):
                try:
                   if dict[key] >= num:
                        dic1.update({"Design-testname"+ version1:dict["Design-testname"+version1]})
                        dic1.update({"status"+version1:dict["status"+ version1]})
                        dic1.update({"status"+version2:dict["status"+version2]})
                        dic1.update({key.replace("diff",version1): dict[key.replace("diff",version1)]})
                        dic1.update({key.replace("diff",version2): dict[key.replace("diff",version2)]})
                        dic1.update({key:dict[key]})
                        table.append(dic1)
                        dic1 ={}
                        
                    
                          
                except:
                    continue        

                        
    return  pd.DataFrame(table) 

def show_improvement(num,records,version1,version2):
    table = []
    dic1 = {}
    for dict in records:
        for key in dict:
            if key.endswith("diff"):
                try:
                   if dict[key] <= num:
                        dic1.update({"Design-testname"+version1:dict["Design-testname"+version1]})
                        dic1.update({"status"+version1:dict["status"+version1]})
                        dic1.update({"status"+version2:dict["status"+version2]})
                        dic1.update({key.replace("diff",version1): dict[key.replace("diff",version1)]})
                        dic1.update({key.replace("diff",version2): dict[key.replace("diff",version2)]})
                        dic1.update({key:dict[key]})
                        table.append(dic1)
                        dic1 ={}
                        
                    
                          
                except:
                    continue        

                        
    return  pd.DataFrame(table)   

def show_range(min,max,records,version1,version2):
    table = []
    dic1 = {}
    for dict in records:
        for key in dict:
            if key.endswith("diff"):
                try:
                   if dict[key] < max and dict[key]> min:
                        dic1.update({"Design-testname"+version1:dict["Design-testname"+version1]})
                        dic1.update({"status"+version1:dict["status"+version1]})
                        dic1.update({"status"+version1:dict["status"+version1]})
                        dic1.update({key.replace("diff",version1): dict[key.replace("diff",version1)]})
                        dic1.update({key.replace("diff",version2): dict[key.replace("diff",version2)]})
                        dic1.update({key:dict[key]})
                        table.append(dic1)
                        dic1 ={}
                        
                         
                    
                          
                except:
                    continue        

                        
    return  pd.DataFrame(table)             