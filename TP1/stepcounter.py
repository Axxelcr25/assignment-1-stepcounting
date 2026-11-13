import numpy as np
import matplotlib.pyplot as plt

#Simple function to visualize 4 arrays that are given to it
def visualize_data(timestamps, x_arr,y_arr,z_arr,s_arr):
  #Plotting accelerometer readings
  plt.figure(1)
  plt.plot(timestamps, x_arr, color = "blue",linewidth=1.0)
  plt.plot(timestamps, y_arr, color = "red",linewidth=1.0)
  plt.plot(timestamps, z_arr, color = "green",linewidth=1.0)
  plt.show()
  #magnitude array calculation
  m_arr = []
  for i, x in enumerate(x_arr):
    m_arr.append(magnitude(x_arr[i],y_arr[i],z_arr[i]))
  plt.figure(2)
  #plotting magnitude and steps
  plt.plot(timestamps, s_arr, color = "black",linewidth=1.0)
  plt.plot(timestamps, m_arr, color = "red",linewidth=1.0)
  plt.show()

#Function to read the data from the log file
#TODO Read the measurements into array variables and return them
def read_data(filename):
  timestamps, x_array, y_array, z_array = [], [], [], []
  with open(filename, "r") as f:          
    for line in f:                        
      values = line.strip().split(",") 
      if len(values) < 4:                  
        continue
      timestamps.append(float(values[0]))  
      x_array.append(float(values[1]))
      y_array.append(float(values[2]))
      z_array.append(float(values[3]))
  return timestamps, x_array, y_array, z_array

#Function to count steps.
#Should return an array of timestamps from when steps were detected
#Each value in this arrray should represent the time that step was made.
def count_steps(timestamps, x_arr, y_arr, z_arr):
  SH = 15   
  SB = 7      
  rv = []
  arme = True       # True = pret a detecter un nouveau pas
  for i, time in enumerate(timestamps):
    m = magnitude(x_arr[i], y_arr[i], z_arr[i])
    if arme and m >= SH:
      rv.append(time)
      arme = False
    elif not arme and m < SB:
      arme = True
  return rv

def count_steps_enhanced(timestamps, x_arr, y_arr, z_arr, fs=100):
  WIN = 100           
  SENS = 2.0        
  T_MIN = 0.25      
  T_MAX = 1.0       
  REG = 4          
  SMOOTH = 15        
  m_arr = [magnitude(x_arr[i], y_arr[i], z_arr[i]) for i in range(len(timestamps))]
  m_arr = list(np.convolve(m_arr, np.ones(SMOOTH) / SMOOTH, mode="same"))
  rv = []
  candidats = []
  seuil = None
  amplitude = 0
  dernier_pas = None
  for i in range(1, len(m_arr)):
    if i % WIN == 0:
      bloc = m_arr[i - WIN:i]
      seuil = (max(bloc) + min(bloc)) / 2
      amplitude = max(bloc) - min(bloc)
    if seuil is None or amplitude < SENS:
      continue 
    if m_arr[i - 1] < seuil <= m_arr[i]:
      t = timestamps[i] / fs
      if dernier_pas is not None and t - dernier_pas < T_MIN:
        continue
      if dernier_pas is not None and t - dernier_pas > T_MAX:
        candidats = []
      dernier_pas = t
      candidats.append(timestamps[i])
      if len(candidats) >= REG:
        rv.extend(candidats)
        candidats = []
  return rv

#Calculate the magnitude of the given vector
def magnitude(x,y,z):
  return np.linalg.norm((x,y,z))

#Function to convert array of times where steps happened into array to give into graph visualization
#Takes timestamp-array and array of times that step was detected as an input
#Returns an array where each entry is either zero if corresponding timestamp has no step detected or 50000 if the step was detected
def generate_step_array(timestamps, step_time):
  s_arr = []
  ctr = 0
  for i, time in enumerate(timestamps):
    if(ctr<len(step_time) and step_time[ctr]<=time):
      ctr += 1
      s_arr.append( 15 )
    else:
      s_arr.append( 0 )
  while(len(s_arr)<len(timestamps)):
    s_arr.append(0)
  return s_arr

#Check that the sizes of arrays match
def check_data(t,x,y,z):
  if( len(t)!=len(x) or len(y)!=len(z) or len(x)!=len(y) ):
    print("Arrays of incorrect length")
    return False
  print("The amount of data read from accelerometer is "+str(len(t))+" entries")
  return True

def main():
  fichiers = {
    "mon_enregistrement_1.csv": 30,
    "mon_enregistrement_2.csv": 52,
    "mon_enregistrement_3.csv": 100,
    "walk_10steps.csv": 10,
    "walk_100steps.csv": 100,
    "walk_300steps.csv": 300,
    "run_10steps.csv": 10,
    "bagwalk_10steps.csv": 10,
  }

  print("Fichier                   | Reel | Simple | Ameliore")
  for nom, reel in fichiers.items():
    t, x, y, z = read_data(nom)
    simple = count_steps(t, x, y, z)
    ameliore = count_steps_enhanced(t, x, y, z, fs=100)
    print(nom.ljust(26) + "| " + str(reel).ljust(5) + "| " + str(len(simple)).ljust(7) + "| " + str(len(ameliore)))

  t, x, y, z = read_data("mon_enregistrement_1.csv")
  st = count_steps_enhanced(t, x, y, z, fs=100)
  s_array = generate_step_array(t, st)
  visualize_data(t, x, y, z, s_array)

main()
