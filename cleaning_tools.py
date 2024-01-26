'''
@Author: Jiqiao Lu, George
@Email: george6.lu@polyu.edu.hk
@Date: Jun 01 2022
@Description: Provide static utility methods for data analysis, since most of my works is in .ipynb format, there is no strict project
file structure, I will just ommit the complex dependency management and provide static methods only, NB: this not recommended in huge project.
'''
import os
import sys
import pandas as pd
import numpy as np


def fileReader(file_path, infile, usecols=None) -> pd.DataFrame:
  '''
  input
  		file_path: the main file directory.
        infile: the specific dataset file name.
  output
  		concated pandas dataframe
  '''
  data_path = os.path.join(file_path, infile)
  paths = list(filter(lambda x : x.endswith(r".gz"), os.listdir(data_path)))
  datalist = [os.path.join(data_path, p) for p in paths]
  def my_read(data_file):
    print("dealing with {}".format(data_file))
    return pd.read_csv(data_file, compression='gzip', sep='\u0001', quotechar='' , quoting=3 , header=0, encoding = "ISO-8859-1",usecols=usecols)
  	
  file_list = list(map(my_read, datalist))
  return pd.concat(file_list)


def inList(ls, series) -> list:
  '''
  input
  		ls: the target list containig the filter elements.
        series: the series by which to filter the dataframe.
  output
  		list of boolean of weather the element is in the target list.
  '''
  return [s in ls for s in series]


def inRange(t_id,test_result,r_range,lower) -> list:
  '''
  r_range : the dic of each termid lower bound and upperbound for the range of pre-diabetes. 
  lower: it is true if it is diabetes and false otherwise.
  
  '''
  l = []
  for i in range(test_result.shape[0]):
    low = r_range.get(t_id.iloc[i])[0]
    high = r_range.get(t_id.iloc[i])[1]
    if lower:
      l.append(test_result.iloc[i] > high)
    else:
      l.append(test_result.iloc[i] <= high and test_result.iloc[i] >= low)
  return l

def getNum(df,r):
  '''
  input: 
  		df: pandas dataframe
        r: is true if the number is the total episode number and false otherwise
        key: patient key
  '''
  if r:
    n = df['pseudo_episode_key'].nunique()
    print("the number of episode is: {:,}".format(n))
  else:
  	n = df['pseudo_patient_key'].nunique()
  	print("the number of patient is: {:,}".format(n))
def chroDiag(pre, diab, diab_key, time_key):
  
  '''
    This function filters the patients whose pre-diabetes diagnosis are later than
    diabetes diagnosis

    input:
    	 pre: pre-diabetes dataframe.
         diab: diabetes dataframe.
         diab_key: the name of datafield indicating the type of diabetes(pre-diabetes or diabetes)
         time_key: the name of datafield indicating the order of time.

    output:
    		tuple(pre_filtered, diab_fitered)

    '''
  # combine the two group records
  combine = pd.concat([pre,diab])
  # find out the patient in the both group
  pre_id = pd.Series(pre['pseudo_patient_key'].unique()).rename('pseudo_patient_key')
  diab_id = pd.Series(diab['pseudo_patient_key'].unique()).rename('pseudo_patient_key')
  both = pd.merge(pre_id, diab_id, how='inner')
  both_records = pd.merge(both,combine,how='inner',on='pseudo_patient_key')
  diff_hour = both_records.groupby(['pseudo_patient_key', diab_key])[[time_key]].min()
  diff_hour = diff_hour.unstack()
  exclude_patient = diff_hour[diff_hour[time_key].diab < diff_hour[time_key].pre]
  exclude_patient = exclude_patient.index.tolist()
  pre_filtered = pre[~pre.pseudo_patient_key.isin(exclude_patient)]
  diab_filtered = diab[~diab.pseudo_patient_key.isin(exclude_patient)]
	
  return (pre_filtered,diab_filtered)
         
 
def get_patient_record(df, id, field="pseudo_patient_key"):
  
  '''
  input
  		df: the target data frame
        id: patient id if looking for patient record
  
  output -> df
  		the patient record
  
  '''
  return df[df[field] == id]

def getNull(df):
    return df[df["pseudo_patient_key"].isnull()]

def row_number(df, *group_key, sort_key="reference_dtm", ascending=True):
  
    rnk = df.sort_values(by=sort_key, ascending=ascending)\
    	.groupby(by=list(group_key))\
    	.cumcount() + 1
    return rnk 