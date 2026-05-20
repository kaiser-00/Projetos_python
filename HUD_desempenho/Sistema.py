import os 
os.system("cls")
import tkinter as tk
import wmi
import psutil
import win32gui
import win32con
import GPUtil
import subprocess
import sys
import winsound

def obter_caminho_arquivo(caminho_relativo):
    """ Retorna o caminho real para arquivos embutidos pelo PyInstaller """
    try:
        # O PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, caminho_relativo)

# FUNÇÃO PARA ABRIR O MONITOR AUTOMATICAMENTE
def iniciar_monitor_externo():
    # Verifica se o OHM já está rodando para não abrir duplicado
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == 'OpenHardwareMonitor.exe':
            return # Já está aberto, então não faz nada!

    caminho_exe = obter_caminho_arquivo(os.path.join("OHM", "OpenHardwareMonitor", "OpenHardwareMonitor.exe"))
    if os.path.exists(caminho_exe):
        subprocess.Popen(caminho_exe, shell=True) 

class Sensor:
    def __init__(self, tipo):
        self.tipo = tipo
        self.valor = 0.0
        # CONEXÃO ÚNICA: Abre a porta uma vez só quando o sensor é criado
        self.c_ohm = None
        if tipo in ["TEMP_CPU", "GPU_ohm", "TEMP_GPU"]:
            try:
                # Tenta conectar no Open ou Libre Hardware Monitor
                self.c_ohm = wmi.WMI(namespace="root\\OpenHardwareMonitor")
            except:
                self.c_ohm = None

    def atualizar(self):
        if self.tipo == "CPU":
            self.valor = psutil.cpu_percent(interval=None)
        elif self.tipo == "CPU_dt":
            self.valor = psutil.cpu_percent(interval=None, percpu=True)    
        elif self.tipo == "RAM":
            self.valor = psutil.virtual_memory().percent
        
        # Para sensores de Temperatura e GPU:
        elif self.c_ohm is not None:
            try:
                # REUTILIZA a conexão self.c_ohm (muito mais leve!)
                sensores = self.c_ohm.Sensor()
                for s in sensores:
                    
                    if self.tipo == "GPU_ohm" and 'GPU' in s.Name and s.SensorType == u'Load':
                        self.valor = s.Value
                        break
                    elif self.tipo == "TEMP_GPU" and s.SensorType == u'Temperature' and 'GPU' in s.Name:
                        self.valor = s.Value
                        break
                    elif s.Value == None:
                        self.valor = 0.0
            except: 
                self.valor = 0.0

        if self.tipo == "TEMP_CPU":
            sensores = self.c_ohm.Sensor()
            for s in sensores: 
                if s.SensorType == u'Temperature' and 'CPU Package' in s.Name:
                    self.valor = s.Value
                    
                    if s.Value == None or s.Value == 0.0:
                        self.valor = 0.0
                    break 

        elif self.tipo == "GPU": 
            self.valor = GPUtil.getGPUs()
            if self.valor:
                gpu = self.valor[0]
                self.valor = gpu.load * 100  # Retorna o número puro (ex: 15.5)
            else:
                self.valor = 0.0
    
class janela:
    def __init__(self, tm, cor_letra, cpu_ref, ram_ref, cpu_temp_ref, gpu_ref, gpu_temp_ref, tp):
        self.tamanho = tm
        self.cor_letra = cor_letra
        self.cpu = cpu_ref
        self.ram = ram_ref 
        self.cpu_temp = cpu_temp_ref
        self.gpu = gpu_ref
        self.gpu_temp = gpu_temp_ref
        # --- TRATAMENTO DE SEGURANÇA ---
        try:
            # Se 'tp' for vazio ou letras, o int() vai falhar e cair no except
            self.transparencia = int(tp)
            # Garante que não passe de 255 nem seja menor que 0
            self.transparencia = max(0, min(255, self.transparencia))
        except:
            # Se der erro, o padrão é 120
            self.transparencia = 120
        self.pode_mover = False
        self.info_label = None # Vamos guardar o label aqui

        # --- AQUI ESTAVA O SEGREDO ---
        # Criamos uma variável para saber se o sensor é do tipo lista (detalhado)
        self.eh_detalhado = False
        if self.cpu and self.cpu.tipo == "CPU_dt":
            self.eh_detalhado = True
    
    def permitir_movimento(self):
        self.pode_mover = not self.pode_mover # Inverte: se era False vira True
        # 1. Pega o estilo que a janela tem agora (com o fantasma ligado)
        if self.pode_mover == True:
            estilo_atual = win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)

            # 2. Desliga apenas o bit do WS_EX_TRANSPARENT
            # O símbolo ~ inverte o código e o & remove ele da soma
            novo_estilo = estilo_atual & ~win32con.WS_EX_TRANSPARENT

            # 3. Aplica o novo estilo sem o "fantasma"
            win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE, novo_estilo)

        if self.pode_mover == False:
            self.jl_desempenho.update()
            self.hwnd = win32gui.GetParent(self.jl_desempenho.winfo_id())

            estilo_atual = win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)
            win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE, estilo_atual | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED)
        
        # Opcional: mudar a cor do HUD para avisar que está no modo mover
        if self.pode_mover:
            self.jl_desempenho.config(highlightbackground="white", highlightthickness=1)
        else:
            self.jl_desempenho.config(highlightthickness=0)

    def iniciar_movimento(self, event):
        if self.pode_mover: # Só guarda a posição se estiver destravado
            self.x = event.x
            self.y = event.y

    def mover_janela(self, event):
        if self.pode_mover: # Só move se estiver destravado
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.jl_desempenho.winfo_x() + deltax
            y = self.jl_desempenho.winfo_y() + deltay
            self.jl_desempenho.geometry(f"+{x}+{y}")

    def exibir(self):
        self.jl_desempenho = tk.Toplevel()
        cor_invisivel = "#000001" 
        self.jl_desempenho.config(bg=cor_invisivel)
        self.jl_desempenho.attributes("-transparentcolor", cor_invisivel)
        self.jl_desempenho.geometry(self.tamanho)
        self.jl_desempenho.overrideredirect(True)
        self.jl_desempenho.attributes("-topmost", True)
        
        self.jl_desempenho.update()
        self.hwnd = win32gui.GetParent(self.jl_desempenho.winfo_id())

        estilo_atual = win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE, estilo_atual | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED)

        # O valor vai de 0 (totalmente invisível) a 255 (totalmente sólido)
        # 128 seria aproximadamente 50% de transparência 
        win32gui.SetLayeredWindowAttributes(self.hwnd, 0, self.transparencia, win32con.LWA_ALPHA)

        # Dentro do exibir(self)
        self.label_cpu = tk.Label(self.jl_desempenho, text="CPU: 0%", bg=cor_invisivel, fg=self.cor_letra, font=("Consolas", 14, "bold"))
        self.label_cpu.pack(side="top", anchor= "w", padx=5)

        self.label_temp_cpu = tk.Label(self.jl_desempenho, text="TEMP: °C", bg=cor_invisivel, fg=self.cor_letra, font=("Consolas", 14, "bold"))

        self.label_gpu = tk.Label(self.jl_desempenho, text="GPU: 0%", bg=cor_invisivel, fg=self.cor_letra, font=("Consolas", 14, "bold"))
        
        self.label_temp_gpu = tk.Label(self.jl_desempenho, text="TEMP: °C", bg=cor_invisivel, fg=self.cor_letra, font=("Consolas", 14, "bold"))

        self.label_ram = tk.Label(self.jl_desempenho, text="RAM: 0%", bg=cor_invisivel, fg=self.cor_letra, font=("Consolas", 14, "bold"))
        
        self.label_cpu.bind("<Button-1>", self.iniciar_movimento)
        self.label_cpu.bind("<B1-Motion>", self.mover_janela)
        self.label_ram.bind("<Button-1>", self.iniciar_movimento)
        self.label_ram.bind("<B1-Motion>", self.mover_janela)

        self.loop_de_atualizacao()

    def loop_de_atualizacao(self):
 
        altura_final = 65 
        
        # --- BLOCO TEMP CPU ---
        if self.cpu_temp.valor != 0.0:
            altura_final += 25
            self.label_temp_cpu.pack(side="top", anchor="w", padx=5)
        else:
            self.label_temp_cpu.pack_forget()

        # --- BLOCO USO GPU (O que você estava preocupado) ---
        # Aqui, mesmo sem Admin, o GPUtil costuma ler a % de uso!
        if self.gpu.valor != 0.0:
            altura_final += 25
            self.label_gpu.pack(side="top", anchor="w", padx=5)
        else:
            self.label_gpu.pack_forget()

        # --- BLOCO TEMP GPU (Precisa de Admin) ---
        if self.gpu_temp.valor != 0.0:
            altura_final += 25
            self.label_temp_gpu.pack(side="top", anchor="w", padx=5)
        else:
            self.label_temp_gpu.pack_forget()

        # 2. Aplica a altura que foi "construída" peça por peça
        largura = "360" if self.eh_detalhado else "160"
        self.jl_desempenho.geometry(f"{largura}x{altura_final}")

        if not hasattr(self, 'cont_pesado'): 
            self.cont_pesado = 0
            self.cont_medio = 0
            # --- PULO DO GATO ---
            # Na primeira vez, força o contador a ser alto para ler os componentes na hora
            pode_ler_agora = True 
        else:
            pode_ler_agora = False

        # Isso aqui roda SEMPRE (a cada 1s)
        self.cpu.atualizar()
        self.ram.atualizar()
    
        # Só atualiza contador se não for a primeira vez
        if not pode_ler_agora:
            self.cont_pesado += 1
            self.cont_medio += 1

        if pode_ler_agora or self.cont_pesado >= 4: 
            self.gpu_temp.atualizar()
            self.cont_pesado = 0
            if self.gpu_temp.valor != 0.0:

                self.label_temp_gpu.config(text=f"TEMP: {self.gpu_temp.valor:04.1f}°C")

                if self.gpu_temp.valor >= 75 and self.gpu_temp.valor < 90:
                    medium_alert_color = "#FF7300"
                    self.label_temp_gpu.config(fg = medium_alert_color)
                            
                elif self.gpu_temp.valor >= 90:
                    winsound.Beep(1000, 500)
                    alert_color = "#FF0000"
                    self.label_temp_gpu.config(fg = alert_color)

                elif self.gpu_temp.valor < 75:
                    self.label_temp_gpu.config(fg = self.cor_letra)              
            else:
                pass

        if pode_ler_agora or self.cont_medio >= 2:            
            self.cpu_temp.atualizar()
            self.cont_medio = 0
            if self.cpu_temp.valor != 0.0:

                self.label_temp_cpu.config(text= f"TEMP: {self.cpu_temp.valor:04.1f}°C")

                if self.cpu_temp.valor >= 75 and self.cpu_temp.valor < 90:
                    medium_alert_color = "#FF7300"
                    self.label_temp_cpu.config(fg = medium_alert_color)
                                    
                elif self.cpu_temp.valor >= 90:
                    winsound.Beep(1000, 500)
                    alert_color = "#FF0000"
                    self.label_temp_cpu.config(fg = alert_color)

                elif self.cpu_temp.valor < 75:
                    self.label_temp_cpu.config(fg = self.cor_letra)
    
            else:
                pass

        if pode_ler_agora or self.cont_pesado >= 4:
            self.gpu.atualizar()
            self.cont_pesado = 0
            if self.gpu.valor != 0.0:
            
                self.label_gpu.config(text=f"GPU: {self.gpu.valor:04.1f}%")
                       
            else:
                pass
  
        if self.eh_detalhado:
            try:
                v = self.cpu.valor # Aqui 'v' é uma lista [N1, N2, N3, N4]
                texto = f"N1:{v[0]:>2.0f}% N2:{v[1]:>2.0f}% N3:{v[2]:>2.0f}% N4:{v[3]:>2.0f}%"
                self.label_cpu.config(text=f"CPU: {texto}")
            except:
                pass
        
        # Se for o modo NORMAL (Número único)
        else:
            # Aqui usamos o :04.1f porque 'valor' é apenas UM número
            self.label_cpu.config(text=f"CPU: {self.cpu.valor:04.1f}%")

        self.label_ram.config(text=f"RAM: {self.ram.valor:04.1f}%")
        if self.label_temp_cpu.winfo_viewable():
            
            self.label_ram.pack(side="top", anchor= "w", padx=5)
        else:
            pass
        try:
            self.jl_desempenho.after(1000, self.loop_de_atualizacao)
        except:
            pass # A janela foi fechada, então para o loop.