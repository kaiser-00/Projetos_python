import Sistema 
from Sistema import Sensor, janela, iniciar_monitor_externo
import tkinter as tk
from tkinter import ttk
import psutil
import os
import sys

if getattr(sys, 'frozen', False):
    application_path = sys._MEIPASS
elif __file__:
    application_path = os.path.dirname(__file__)

class MenuPrincipal:
    def __init__(self):
        iconFile = 'placa_circuito.ico'
        self.menu = tk.Tk()
        self.menu.protocol("WM_DELETE_WINDOW", self.ao_fechar)

        self.menu.iconbitmap(default=os.path.join(application_path, iconFile)) 
        self.menu.title("HUD Pc")
        self.menu.geometry("300x250")
        
        # Aqui é o segredo: guardamos a aba como um atributo da CLASSE Menu
        self.info_aba = None 

        # Botão Iniciar
        self.formato_CPU = ["-------------","Normal", "Detalhado"]
        self.formato = ttk.Combobox(self.menu, values= self.formato_CPU , state="readonly",width=11)
        self.formato.place(y= 46, x=105)
        self.formato.current(0)

        self.formato.bind("<<ComboboxSelected>>", self.conferir)
            
        self.botao_play = tk.Button(self.menu, text="Iniciar Monitor", bg="#0D59BD", fg="white", command=self.play)

        self.botao_play_DT = tk.Button(self.menu, text="Iniciar Monitor", bg="#0D59BD", fg="white", command=self.play_detalhado)
    
        # Botão Travar/Destravar
        tk.Button(self.menu, text="Travar/Destravar HUD",font=("Arial",9, "bold"),
                  command=self.alternar_movimento).place(y=75, x=80)
        
        tk.Label(self.menu,text="Nível de transparencia:", font=("Arial",9, "bold")).place(y=150, x=80)

        self.nivel_tp = tk.Entry(self.menu)
        self.nivel_tp.place(y=175, x=85)
        
    def ao_fechar(self):
        # Mata o processo do Open Hardware Monitor
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] == 'OpenHardwareMonitor.exe':
                    proc.kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        self.menu.destroy()    

    def conferir(self, event):
        resultado = self.formato.get()

        if resultado == "Normal":
            self.botao_play_DT.place_forget()
            self.botao_play.place(y=21, x=105)
        elif resultado == "Detalhado":
            self.botao_play.place_forget()
            self.botao_play_DT.place(y=21, x=105)
        elif resultado == "-------------":
            self.botao_play.place_forget()
            self.botao_play_DT.place_forget()


    def play(self):
        # --- AQUI ESTÁ A MÁGICA ---
        if self.info_aba and self.info_aba.jl_desempenho.winfo_exists():
            self.info_aba.jl_desempenho.destroy()
        
        cpu_real = Sensor(tipo="CPU")
        ram_real = Sensor(tipo="RAM")
        temp_cpu_real = Sensor(tipo="TEMP_CPU")
        gpu_ohm_real = Sensor(tipo="GPU_ohm")
        temp_gpu_real = Sensor(tipo="TEMP_GPU")
        gpu_real = Sensor(tipo="GPU")

        valor_tp = self.nivel_tp.get()

        self.info_aba = janela("160x65", "#0EC235", cpu_real, ram_real, temp_cpu_real, gpu_ohm_real, temp_gpu_real, valor_tp)
        self.info_aba.exibir()

    def play_detalhado(self):
        # --- REPETE A MÁGICA AQUI TAMBÉM ---
        if self.info_aba and self.info_aba.jl_desempenho.winfo_exists():
            self.info_aba.jl_desempenho.destroy()
            
        cpu_real_2 = Sensor(tipo="CPU_dt")
        ram_real = Sensor(tipo="RAM")
        temp_cpu_real = Sensor(tipo="TEMP_CPU")
        gpu_ohm_real = Sensor(tipo="GPU_ohm")
        temp_gpu_real = Sensor(tipo="TEMP_GPU")
        gpu_real = Sensor(tipo="GPU")

        valor_tp = self.nivel_tp.get()
        
        self.info_aba = janela("360x65", "#0EC235", cpu_real_2, ram_real, temp_cpu_real, gpu_ohm_real, temp_gpu_real, valor_tp)
        self.info_aba.exibir()
        
    def alternar_movimento(self):
        # Agora este def consegue ver a janela porque ambos usam o 'self' do Menu!
        if self.info_aba:
            self.info_aba.permitir_movimento()
        else:
            print("O monitor ainda não foi iniciado!")

    def iniciar(self):
        self.menu.mainloop() 

# Primeiro: Liga o monitor de hardware no Windows
# No final do arquivo menu.py, deixe APENAS assim:
if __name__ == "__main__":
    # Chamamos aqui, e APENAS aqui, para não duplicar
    iniciar_monitor_externo() 
    
    meu_menu = MenuPrincipal()
    meu_menu.iniciar()