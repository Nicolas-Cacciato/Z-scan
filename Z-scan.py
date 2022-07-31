"""
Created on Sun Jul  3 16:43:50 2022

@author: Nicolas Cacciato
"""

import serial
import pyvisa
import numpy as np
from tqdm import tqdm
import seaborn as sns
import pandas as pd
from matplotlib import pyplot as plt

# -------User Input--------------

lengt_pas = 0.5  # Mesure tout les x mm

path_sauvegarde = "C:/Users/32478/Desktop/"  # dossier désiré pour la sauvegarde

name_csv = "Z-scan"  # nom du fichier csv

name_lineplot = "line_plot"  # nom du fichier png

# --------------------------------

nbr_pas = 130 / lengt_pas

sns.set_style("darkgrid")  # définit le style du plot

rm = pyvisa.ResourceManager()

power_meter = rm.open_resource('USB0::0x1313::0x8022::M00429312::INSTR')  # Nom du power meter

power_meter.read_termination = '\n'
power_meter.write_termination = '\n'

mesure = []
reference = []
position = []

print('--- start ok ---')

ser = serial.Serial('COM6')  # Canal utilisé
ser.write(b'MO\n')           # allumage du moteur
ser.write(b'3OR,3TP\n')      # Retour à la position initiale

anti_bug = ser.readline()

print('--- init ok ---')

ser.write(b'3PR65,3WS,3TP\n')  # Déplacement de 65mm

value = ser.readline()

for _ in tqdm(range(int(nbr_pas))):
    position.append(float(value[3:]))
    mesure.append(float(power_meter.query(":POW1:VAL?")))  # Prise de mesure sur le canal 1 (mesure)
    reference.append(float(power_meter.query(":POW2:VAL?")))  # Prise de mesure sur le canal 2 (référence)
    commande = f'3PR-{lengt_pas},3WS,3TP\n'           # Déplacement
    ser.write(commande.encode())
    value = ser.readline()

value = np.array(np.array(mesure) / np.array(reference))  # Calcul par rapport à la référence

sns.lineplot(position, value)  # mise en graphique
plt.xlabel("Position (nm)")
plt.show()

plt.savefig('path_sauvegarde'+'name_lineplot')  # sauvegarde graphique

ser.write(b'3OR,3TP\n')  # retour point de départ

tableau = pd.DataFrame()

tableau['position (nm)'] = position
tableau['mesure (mW)'] = mesure
tableau['reference (mW)'] = reference

tableau.to_csv('path_sauvegarde'+'name_csv'+'.csv')  # sauvegarde en csv

ser.close()
