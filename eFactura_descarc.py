import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import requests
import datetime as dt
import time
import json
from tkinter import messagebox
from dateentry import *

bground = 'lightgrey'
font1 = ('Calibri',12)
font2 = ('Calibri',10)
write_file_zip = 'Nu exista cale pentru salvare'

if os.path.isfile('director.json'):
    try:
        file = open('director.json','r')
        jsonfile = json.load(file)
        write_file_zip = jsonfile['write_zip']
    except:
        pass

def changedir():
    global write_file_zip
    try:
        file = open('director.json','w')
        dictionary = { "write_zip": write_file_zip }
        jsonfile = json.dumps(dictionary)
        file.write(jsonfile)
        file.close()
    except:
        pass

def writezip():
    global write_file_zip
    global lbl_export_zip
    write_file_zip=filedialog.askdirectory()
    lbl_export_zip.config(text=str(write_file_zip),fg='BLACK')
    changedir()
    
def descarc():
    
    global from_date
    global to_date
    global cmb_tip
    global lbl_mesage
    global write_file_zip

    mesaje_facturi = []
    pagina = 1
    numar_pagini=1
    from_date_unix = int(time.mktime(from_date.get_date().timetuple())*1e3)
    date_now = int(time.mktime(dt.datetime.today().timetuple())*1e3)
    from_date_max = date_now-5184000000
    to_date_unix = int(time.mktime(to_date.get_date().timetuple())*1e3)+86400000
    if to_date_unix>date_now:
        to_date_unix=date_now
    url_mesaje='https://api.anaf.ro/prod/FCTEL/rest/listaMesajePaginatieFactura?startTime='+str(from_date_unix)+'&endTime='+str(to_date_unix)+'&cif=8574327&pagina='+str(pagina)
    url_download='https://api.anaf.ro/prod/FCTEL/rest/descarcare?id='
    header = {'Authorization':'Bearer 333187115c58ff2e27a0b647903a900dfd011552540b9da31d794b74eea9cb9c'}
    if cmb_tip.get() == 'trimise':
        tip_factura = 'TRIMISA'
    elif cmb_tip.get() == 'primite':
        tip_factura = 'PRIMITA'
    else:
        tip_factura = 'FACTURA'
    print(url_mesaje)
    
    if os.path.isdir(write_file_zip) == False:
        messagebox.showerror('Eroare','Director pentru salvare inexistent')
        return

    if from_date_unix>=to_date_unix:
        lbl_mesage.configure(text='Data de sfarsit nu poate fi mai veche decat data de inceput',fg='RED')
        lbl_mesage.update()
        return

    if from_date_unix<from_date_max:
        lbl_mesage.configure(text='Data de inceput nu poate fi mai vechi de 60 de zile',fg='RED')
        lbl_mesage.update()
        return

    lbl_mesage.configure(text='Descarcare fisiere',fg='RED')
    lbl_mesage.update()

    while pagina<=numar_pagini:
        url_mesaje='https://api.anaf.ro/prod/FCTEL/rest/listaMesajePaginatieFactura?startTime='+str(from_date_unix)+'&endTime='+str(to_date_unix)+'&cif=8574327&pagina='+str(pagina)
        result = requests.get(url_mesaje,headers=header)
        print(result.text)
        mesaje_facturi.append(json.loads(result.text))
        try:
            numar_pagini=mesaje_facturi[pagina-1]["numar_total_pagini"]
        except KeyError:
            lbl_mesage.configure(text='Au fost descarcate 0 fisiere',fg='BLACK')
            lbl_mesage.update()
            return
        pagina += 1

    downloaded = 0
    downloaded_id = []
    for pagina in mesaje_facturi:
        for factura in pagina["mesaje"]:
            if tip_factura in factura["tip"]:
                try:
                    result = requests.get(url_download+factura["id"],headers=header)
                    file_name = write_file_zip+'/'+factura["id"]+'.zip'
                    is_downloaded = False
                    for former in downloaded_id:
                        if former==factura["id"]:
                            is_downloaded=True
                            break
                    if is_downloaded==False:
                        downloaded+=1
                        downloaded_id.append(factura["id"])
                    file=open(file_name,'wb')
                    file.write(result.content)
                except:
                    print('nu s-a salvat')

    lbl_mesage.configure(text='Au fost descarcate '+str(downloaded)+' fisiere',fg='BLACK')
    lbl_mesage.update()

def lbl_command(event):
    global write_file_zip
    path = os.path.normpath(write_file_zip)
    try:
        os.startfile(path)
    except:
        pass

main_window = tk.Tk()
main_window.configure(padx=20,pady=20,background=bground)
main_window.title('Descarcare eFactura')

fr_top = tk.Frame(main_window,bg=bground)
fr_top.pack(side='top')
fr_bottom = tk.Frame(main_window,bg=bground)
fr_bottom.pack(side='top') 

label_from=tk.Label(fr_top,text='Data inceput perioada',bg=bground,font=font1,pady=10)
label_from.grid(row=1,column=1,sticky='W')
from_date=DateEntry(fr_top,selectmode='day')
from_date.grid(row=1,column=2,sticky='E')

label_to=tk.Label(fr_top,text='Data sfarsit perioada',bg=bground,font=font1,pady=10)
label_to.grid(row=2,column=1,sticky='W')
to_date=DateEntry(fr_top,selectmode='day')
to_date.grid(row=2,column=2,sticky='E')

label_tip=tk.Label(fr_top,text='Selectati tipul facturii',bg=bground,font=font1,pady=10)
label_tip.grid(row=3,column=1,sticky='W')
cmb_tip=ttk.Combobox(fr_top,background=bground,state='readonly',font=font1,width=10,values=['primite','trimise','toate'])
cmb_tip.set('primite')
cmb_tip.grid(row=3,column=2,sticky='E')

btn_export_zip=tk.Button(fr_bottom,text='Selectare locatie ZIP',font=font1,command=lambda:writezip(),width=35)
btn_export_zip.pack()
if write_file_zip == 'Nu exista cale pentru salvare':
    color = 'RED'
else:
    color = 'BLACK'
lbl_export_zip=tk.Label(fr_bottom,font=font2,wraplength=380,background=bground,fg=color,text=write_file_zip)
lbl_export_zip.pack(expand=True)
lbl_export_zip.bind('<Button>',lbl_command)

button_export=tk.Button(fr_bottom,text='Descarcare',width=10,font=font1,command=lambda:
                        descarc())
button_export.pack(pady=10)

lbl_mesage=tk.Label(fr_bottom,text='Nu au fost descarcate fisiere',font=font2,bg=bground,fg='BLACK',wraplength=300) 
lbl_mesage.pack(expand=True)

button_quit=tk.Button(fr_bottom,text='Iesire',width=10,font=font1,command=lambda:main_window.destroy())
button_quit.pack(pady=10)

main_window.mainloop()