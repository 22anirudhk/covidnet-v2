# -*- coding: utf-8 -*-
"""Untitled1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1tFJ8maCBhaO72hNb3qRlVtzahQHsiIU9
"""

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
import numpy as np
# from google.colab import drive




# np.random.seed(42)
# tf.random.set_seed(42)
print(tf.__version__)

# drive.mount("/content/drive")
data_frame = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv")
data_frame = data_frame[5:] #ignore puerto rico and stuff
dates = pd.to_datetime(data_frame.columns[11:])#Dates
#Group by state
grouped = data_frame.groupby("Province_State", as_index=False)
#Stores all of the data by state instead
state_data = pd.DataFrame()
new_data = pd.DataFrame()

#Sum cities into the same state

for group_name, group in grouped:
    #Get cases for the state
    casesInit = group[11:]
    #Sum the cases for each day (making it from city count per day to state amount per day)
    summed_cases = casesInit.sum(axis=0)[11:] 
    state_data[group_name] = summed_cases

state_data["Date"] = dates
#display(state_data)
print(len(state_data["Arizona"]))

data_frame = state_data 


data_frame = data_frame[5:] #ignore puerto rico and stuff


# General algorithmic functions I wrote for data preprocessing
def normalize(data, maxnum):
  oned = np.squeeze(data)
  min_data = min(oned)
  max_data = max(oned)
  normalized_data = (oned - min_data) / (maxnum - min_data)
  return normalized_data, min_data, max_data

def denormalize(norm_data, max_d, min_d):
  denormalized_d = np.squeeze(norm_data) * (max_d - min_d) + min_d
  return denormalized_d

#Plot cases for a given state
def get_cases(state_name):
  dates = pd.to_datetime(data_frame["Date"])
  cases =  data_frame[state_name]
  cases = np.array(cases.values).reshape(len(cases), 1)
  phase_time = np.arange(len(dates)).reshape(len(dates), 1)

  scaler = StandardScaler()
  phase_time = scaler.fit_transform(phase_time)
  cases = scaler.transform(cases).reshape(len(cases), 1)
#   print(f"Debugging Information: Max cases = {max(cases)}")
  
  
#   print(f"Length of cases & time arrays are {len(cases)}, {len(phase_time)}")
  #plt.plot(np.squeeze(phase_time), np.squeeze(cases))

  return phase_time,cases, scaler

#The net is trained on individual states
curr_state = "New York"

#print(np.sin(phase_time))
#cases = np.add(np.squeeze(np.sin(phase_time)),np.squeeze(np.random.normal(scale=0.5, size=len(time))))
#print(cases)
#plt.plot(phase_time, cases)

#print(phase_time)
maxn = 11000000
maxp = 575
#cases = tf.keras.utils.normalize(np.squeeze(cases))[0]
#phase_time = tf.keras.utils.normalize(np.squeeze(phase_time))[0]
#cases, minc, maxc = normalize(cases, maxn)
#phase_time, minphase, maxphase = normalize(phase_time, maxp)
#print(max(denormalize(cases, maxn, 0)))

#Useful for many things
from tensorflow import keras
from keras import Sequential
from keras.models import load_model
from keras.layers import LSTM, Dropout, Dense, Activation
from keras.preprocessing.sequence import TimeseriesGenerator
import pickle 

#Gets a single prediction based on a value 
def single_predict(value, given_model,  delt, scaler, n_input=5):
  

  
  inputs = np.arange(value, value-delt*(n_input-0.5),  -delt)
  inputs = inputs.reshape((1, n_input, 1))

  prediction = given_model.predict(inputs)
  #print(f"Value is {value}, prediction is {prediction}")
  return np.squeeze(prediction)


#graphs cases for a current model 
def graph_cases(given_model, phase_time, cases, delt, scaler):
  
  #x_axis = np.squeeze(scaler.transform(np.arange(0, len(cases)+30).reshape(len(cases)+30, 1)))
  
  x_axis = np.arange(phase_time[0],phase_time[0]+(len(cases)+30)*delt,delt)


  #x_axis2 = np.array([x_axis[i:i+n_input] for i in range(0, len(x_axis) - n_input)])
  #x_axis3 = [x_axis[i:i+n_input].reshape((1, n_input, 1)) for i in range(0, len(x_axis)-n_input)]
  #predictions = [model.predict(i) for i in x_axis3]

  predictions = [single_predict(i, given_model, delt, scaler) for i in x_axis]

  #print(np.squeeze(predictions))
#   fig, ax = plt.subplots()
#   yaxes = np.squeeze(predictions)
#   xes = x_axis[:len(yaxes)]

#   plt.figure()
  
                    
  #n = int(input("What day past January 22nd do you want to predict coronavirus cases for the state of {?"))
  #print(f"Prediction for day {n} of coronavirus outbreak returned approximately {int(single_predict(n, model))} cases")

  ax.plot(scaler.inverse_transform(xes), scaler.inverse_transform(yaxes))
  
  ax.plot(scaler.inverse_transform(phase_time),scaler.inverse_transform(cases))
#   print(f"Cases today was probably like {np.squeeze(scaler.inverse_transform(yaxes))[171]}")


def run_state_model(state_name, batch_size = 5, n_input = 5, num_epochs=25, num_per_epoch=100, qverbose=2, graph=0, base_path="/content/drive/My Drive/"):
#   path = f"{base_path}{state_name}"
  path = str(base_path) + str(state_name)
  model = None
  #This try catch block either gets a preexisting model or creates a new one
  try:
    model = load_model(path)
  except:
    print("python 2.7?")
#     print(f"Path {path} not found, training new model for {state_name}")
  
  if (model == None):
    model = Sequential()
    model.add(LSTM(100, activation='relu', input_shape=(n_input,1), return_sequences=True))
    model.add(LSTM(100, activation='relu', input_shape=(1, n_input)))
    model.add(Dropout(0.3))

   
    model.add(Dense(1))
    model.compile(loss="mse", optimizer="adam")

  #Data preprocessing block
  phase_time, cases, scaler = get_cases(state_name)
  plt.plot(phase_time, cases)
  print(max(scaler.inverse_transform(cases)))


  phase_time =  phase_time.reshape((len(phase_time), 1))
  


  cases = cases.reshape((len(cases), 1))
  print(len(cases), len(phase_time))
  #print(cases)
  data_gen = TimeseriesGenerator(phase_time, cases,
                                length=n_input, batch_size=5)
  


#   print(f"RUNNING TRAINING FOR {state_name}")
  
  model.fit_generator(data_gen, steps_per_epoch=100, epochs=15, verbose=0)


#   filename = f"{state_name}"
  filename = str(state_name)
#   print(f"TRAINING FOR {state_name} FINISHED, WRITING OUT MODEL TO FILE")
  model.save(str(base_path) + str(filename)) #f"{base_path}{filename}")
  delt = abs(phase_time[1]-phase_time[0])
  if (graph == 1):
      graph_cases(model, phase_time, cases, delt, scaler)
  
 
  predictslist = scaler.inverse_transform([single_predict(i, model, delt, scaler) for i in np.arange(phase_time[0],phase_time[0]+(len(cases)+30)*delt,delt)])

#   new_data[f'{state_name} Predict'] = np.squeeze(predictslist)
  new_data[state_name + ' Predict'] = np.squeeze(predictslist)



def run_entire_model():
  total_states = data_frame.columns.values
  print(len(total_states))

  for state in total_states:
    run_state_model(state, graph=0)
  
  

import traceback
import sys

try:
  run_entire_model()
except Exception:
  full_tb = traceback.print_exc()
#   print(f"\n\n{full_tb}")
  sys.exit(0)

#Write outs
nan_frame = pd.DataFrame(index=range(30),columns=range(state_data.shape[1]))
state_data = pd.concat(axis=0, objs=[state_data, nan_frame])
state_data["Date"] = pd.date_range(start='1/22/2020', periods=len(state_data), freq='D')
state_data.to_csv("Data/state_data.csv", index=True)
print(new_data)
new_data.to_csv("Data/predicted_data.csv")





  





  



  



#print(cases)

'''
model = Sequential()
epoch_num = 25
#model.add(LSTM(50, activation='relu', input_shape=(n_input,1), return_sequences=True))
#model.add(LSTM(50, activation='relu', input_shape=(1, n_input)))
#model.add(Dropout(0.3))
#model.add(LSTM(50))
#model.add(Dropout(0.5))
#model.add(Dense(1))


model.fit_generator(data_gen, steps_per_epoch=100, epochs=epoch_num, verbose=2)
import datetime
filename = f"{curr_state}_{datetime.datetime.now()}"
model.save(f"/content/drive/My Drive/{filename}")
print(f"Model saved as {filename}")


#Graphical Analysis - Trivial, trivial, trivial
day = 0
phase_time = np.squeeze(phase_time)

day = day*phase_time[1]
print(phase_time[1])
print(day)


predictions = []
#x_axis = np.squeeze(scaler.transform(np.arange(0, len(cases)+30).reshape(len(cases)+30, 1)))
delt = phase_time[1] - phase_time[0]
x_axis = np.arange(phase_time[0],phase_time[0]+200*abs(delt),abs(delt))
#print(x_axis)

x_axis2 = np.array([x_axis[i:i+n_input] for i in range(0, len(x_axis) - n_input)])
x_axis3 = [x_axis[i:i+n_input].reshape((1, n_input, 1)) for i in range(0, len(x_axis)-n_input)]

predictions = [model.predict(i) for i in x_axis3]
#print(np.squeeze(predictions))
fig, ax = plt.subplots()
xes = np.squeeze([i[-1]+phase_time[1] for i in x_axis2])

yaxes = np.squeeze(predictions)
xes = x_axis[:len(yaxes)]
plt.figure()
plt.plot(xes, yaxes)
plt.plot(phase_time, cases)


#Runs a single prediction on a given time to determine what the model's
#Estimated cases during that time are


  #return float(denormalize(np.squeeze(prediction), maxn, 0))
                   
n = int(input("What day past January 22nd do you want to predict coronavirus cases for the state of {?"))
print(f"Prediction for day {n} of coronavirus outbreak returned approximately {int(single_predict(n, model))} cases")
ax.plot(scaler.inverse_transform(xes), scaler.inverse_transform(yaxes))
ax.plot(scaler.inverse_transform(phase_time),scaler.inverse_transform(cases))'''


