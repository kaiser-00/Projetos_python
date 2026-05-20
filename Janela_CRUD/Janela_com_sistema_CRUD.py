import os
os.system("cls")

import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from tkinter import ttk
from tkinter import END
from tkinter import scrolledtext
import sqlite3
import fpdf
from fpdf import FPDF

from cryptography.fernet import Fernet

ico = r"C:\Users\Usuário\Documents\Meus scripts python\Ferramentas_python\chave-de-fenda.ico"

def carregar_ou_criar_chave():
    if not os.path.exists("mestra.key"):
        chave = Fernet.generate_key()
        with open("mestra.key", "wb") as f:
            f.write(chave)
    return open("mestra.key", "rb").read()

chave = carregar_ou_criar_chave()
cipher = Fernet(chave)

def abrir_banco():
    caminho = "Minhas_experiencias_Pc/assistencia_camboriu.db"
    if os.path.exists(caminho):
        with open(caminho, "rb") as f:
            dados_trancados = f.read()
        
        try:
            dados_abertos = cipher.decrypt(dados_trancados)
            with open(caminho, "wb") as f:
                f.write(dados_abertos)
            print("Arquivo pronto para uso!")
        except:
            print("O arquivo já está aberto ou a chave é inválida.")

try:
    abrir_banco()
except Exception as e:
    print(f"Aviso: O banco já estava aberto ou ocorreu um erro: {e}")

conexao = sqlite3.connect("Minhas_experiencias_Pc/assistencia_camboriu.db")
cursor = conexao.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,       
        nome TEXT NOT NULL,
        cpf TEXT UNIQUE,
        Telefone TEXT
    )
    """)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS servico (
        data TEXT,  
        cpf TEXT,              
        servico TEXT,
        problema TEXT,
        processador TEXT,
        memoria_ram TEXT
    )
    """)

# 2. FERRAMENTA: Trancar o arquivo
def trancar_banco():
    caminho = "Minhas_experiencias_Pc/assistencia_camboriu.db"
    if os.path.exists(caminho):
        with open(caminho, "rb") as f:
            dados_abertos = f.read()
        
        dados_trancados = cipher.encrypt(dados_abertos)
        
        with open(caminho, "wb") as f:
            f.write(dados_trancados)
        print("Arquivo trancado com sucesso!")

# 3. FERRAMENTA: Abrir o arquivo

def verificar_servico(event):
    escolha = lista_de_servicos.get()
    
    if escolha == "Problema tecnico":
        label_especifico.place(x=12, y=205)
        problema_especifico.place(x=15, y=230)
        label_processador.place(x=12,y=405)
        lista_processador.place(x=15, y=430)
        label_memoria_ram.place(x=212, y=405)
        lista_memoria_ram.place(x=215, y=430)
    else:
        # Se for outra coisa, ele "desempacota" (esconde) os campos
        label_especifico.place_forget()
        problema_especifico.place_forget()
        label_processador.place_forget()
        lista_processador.place_forget()
        label_memoria_ram.place_forget()
        lista_memoria_ram.place_forget()
        
def executar_limpeza_real():
    """Apenas limpa os campos, sem janelas ou perguntas."""
    aba_atual = abas.index("current")

    if aba_atual == 0:
        entrada_nome.delete(0, END)
        entrada_cpf.delete(0, END)
        telefone.delete(0, END)
    
    elif aba_atual == 1:
        problema_especifico.delete("1.0", tk.END)
        entrada_cpf_servico.delete(0, END)
        lista_de_servicos.set('')
        lista_processador.set('')
        lista_memoria_ram.set('')

    elif aba_atual == 2:  # ABA DE BUSCA
        entrada_busca.delete(0, END)
        deletar_ID.delete(0, END)
        # Limpa a área de texto (ScrolledText)
        text_area.config(state="normal")
        text_area.delete("1.0", END)
        text_area.config(state="disabled")
        print("Busca resetada!")

def limpar_campos_cadastro():
    """Função para o botão vermelho: Pergunta antes de limpar."""
    if messagebox.askyesno("AVISO!", "Deseja limpar todas as informações?"):
        executar_limpeza_real() # Chama a limpeza real

def formatar_cpf(event):
    campo_atual = event.widget
    texto = campo_atual.get()
    # Remove qualquer coisa que não seja número (evita letras no CPF)
    apenas_numeros = "".join(filter(str.isdigit, texto))

    # Formatação conforme o tamanho
    novo_texto = ""
    if len(apenas_numeros) <= 3:
        novo_texto = apenas_numeros
    elif len(apenas_numeros) <= 6:
        novo_texto = f"{apenas_numeros[:3]}.{apenas_numeros[3:]}"
    elif len(apenas_numeros) <= 9:
        novo_texto = f"{apenas_numeros[:3]}.{apenas_numeros[3:6]}.{apenas_numeros[6:]}"
    elif len(apenas_numeros) <= 11:
        novo_texto = f"{apenas_numeros[:3]}.{apenas_numeros[3:6]}.{apenas_numeros[6:9]}-{apenas_numeros[9:]}"
    else:
        # Limita a 11 números (tamanho padrão do CPF)
        novo_texto = f"{apenas_numeros[:3]}.{apenas_numeros[3:6]}.{apenas_numeros[6:9]}-{apenas_numeros[9:11]}"

    campo_atual.delete(0, tk.END)
    campo_atual.insert(0, novo_texto)

def formatar_telefone(event): # Adicionei o 'event' porque o bind precisa dele
    campo_atual = event.widget
    texto_2 = campo_atual.get()

    # 1. Limpeza: deixa só o que é número
    apenas_numeros_2 = "".join(filter(str.isdigit, texto_2))

    novo_texto_2 = ""
    
    # 2. A Lógica dos Degraus (Checkpoints)
    if len(apenas_numeros_2) <= 2:
        # Até 2 números: mostra só o DDD (ex: 47)
        novo_texto_2 = apenas_numeros_2
        
    elif len(apenas_numeros_2) <= 6:
        # De 3 a 6 números: começa a colocar o parêntese
        # Ex: (47) 9
        novo_texto_2 = f"({apenas_numeros_2[:2]}) {apenas_numeros_2[2:]}"
        
    elif len(apenas_numeros_2) <= 10:
        # Formato Telefone Fixo: (47) 3333-4444 (10 dígitos)
        novo_texto_2 = f"({apenas_numeros_2[:2]}) {apenas_numeros_2[2:6]}-{apenas_numeros_2[6:]}"
        
    else:
        # Formato Celular: (47) 98888-7777 (11 dígitos)
        # Corta do início até o 2 | do 2 até o 7 | do 7 até o 11
        novo_texto_2 = f"({apenas_numeros_2[:2]}) {apenas_numeros_2[2:7]}-{apenas_numeros_2[7:11]}"

    # 3. Atualiza a tela
    campo_atual.delete(0, tk.END)
    campo_atual.insert(0, novo_texto_2)
#(47) 98888-7777
    # Atualiza o campo de texto com a máscara


def salvar_serviço_em_SQlite():
    scs_gerais = lista_de_servicos.get()
    date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    cpf_servico = entrada_cpf_servico.get()

    problema = problema_especifico.get("1.0", tk.END).strip()
    ram = lista_memoria_ram.get()
    processador = lista_processador.get()

    if scs_gerais == "Problema tecnico":

        if  scs_gerais == "" or cpf_servico == "" or problema == "":
            messagebox.showerror("AVISO!","Preencha os campos CPF, serviço e detalhes!")

        else:
             
            resumo = f" ANEXADO A\t: {cpf_servico}\n\n SERVIÇO\t: {scs_gerais}\n DETALHES\t: {problema}\n CPU\t: {processador}\n RAM\t: {ram}"
            messagebox.showinfo("CONFIRA!", resumo)

            resposta = messagebox.askyesno("AVISO","Deseja salvar as infomações atuais?")

            if resposta == True:

                try: 
                    cursor.execute("""
                    INSERT INTO servico (data, cpf, servico, problema, processador, memoria_ram) 
                    VALUES (?, ?, ?, ?, ?, ?)
                    """, (date, cpf_servico, scs_gerais, problema, processador, ram))
    
                    conexao.commit()

                    executar_limpeza_real()
            
                    print(f"Serviço de {scs_gerais} foi anotado com sucesso!")

                except Exception as e:
                # Se o erro for QUALQUER OUTRA COISA (ex: faltou luz, banco sumiu)
                    messagebox.showerror("Erro Inesperado", f"Ocorreu um problema técnico: {e}")

    elif scs_gerais == "" or cpf_servico == "":
        messagebox.showerror("AVISO!","Preencha os campos CPF e serviço!")
    else:
        # 3. O "Parafuso Final" (Salvar no arquivo .db)
        resumo = f" ANEXADO A\t: {cpf_servico}\n SERVIÇO\t: {scs_gerais}"

        resposta = messagebox.askyesno("AVISO","Deseja salvar as infomações atuais?")

        if resposta == True:

            try: 
                cursor.execute("""
                INSERT INTO servico (data, cpf, servico) 
                VALUES (?, ?, ?)
                """, (date, cpf_servico, scs_gerais))
   
                conexao.commit()

                executar_limpeza_real()
        
                print(f"Serviço de {scs_gerais} foi anotado com sucesso!")

            except Exception as e:
                # Se o erro for QUALQUER OUTRA COISA (ex: faltou luz, banco sumiu)
                messagebox.showerror("Erro Inesperado", f"Ocorreu um problema técnico: {e}")

def salvar_cadastro_em_SQlite():
    cliente_name = entrada_nome.get()
    cpf = entrada_cpf.get()
    tel = telefone.get()

    if cliente_name == "" or cpf == "" or tel == "":
        messagebox.showerror("AVISO!","Topicos vazios!")
    else:
        apenas_numeros = "".join(filter(str.isdigit, cpf))
        if len(apenas_numeros) < 11:
            messagebox.showwarning("Erro", "O CPF deve ter 11 dígitos!")
            return

        # 3. O "Parafuso Final" (Salvar no arquivo .db)
        resumo = f" NOME\t: {cliente_name}\n CPF\t: {cpf}\n TEL\t: {tel}"
        messagebox.showinfo("CONFIRA AS INFORMAÇÔES:", resumo)

        resposta = messagebox.askyesno("AVISO","Deseja salvar as infomações atuais?")

        if resposta == True:

            try: 
                cursor.execute("""
                INSERT INTO clientes (nome, cpf, telefone) 
                VALUES (?, ?, ?)
                """, (cliente_name, cpf, tel))
   
                conexao.commit()

                executar_limpeza_real()
        
                print(f"Cliente {cliente_name} foi cadastrado com sucesso!")

            except sqlite3.IntegrityError:
                # Se o Banco disser "Ei, esse CPF já existe!"
                messagebox.showwarning("Aviso", "CPF já cadastrado!")
            except Exception as e:
                # Se o erro for QUALQUER OUTRA COISA (ex: faltou luz, banco sumiu)
                messagebox.showerror("Erro Inesperado", f"Ocorreu um problema técnico: {e}")

            

# 1. Criar a Janela Principal (Gabinete)
janela = tk.Tk()
janela.iconbitmap(ico) 
janela.title("Assistência Técnica Camboriú")
janela.geometry("375x500")

# 2. Criar o Gerenciador de Abas (Notebook) dentro da janela
abas = ttk.Notebook(janela)
abas.pack(expand=True, fill="both") # O pack faz ele ocupar a tela toda

# 3. Criar as "páginas" (Frames)
aba1 = tk.Frame(abas)
aba2 = tk.Frame(abas)
aba3 = tk.Frame(abas)
aba4 = tk.Frame(abas)
# 4. Adicionar as páginas ao Notebook com um nome
abas.add(aba1, text="Cadastro")
abas.add(aba4, text="Serviço")
abas.add(aba2, text="Busca")
abas.add(aba3, text="Editar/Excluir")

tk.Label(aba1, text="", font=("Arial", 15, "bold")).pack(anchor="w",pady=1,padx=40)

tk.Label(aba1, text=""" Cadastrase em nossa loja
    e receba descontos exclusivos!""", font=("Arial", 13, "bold")).pack(anchor="w",pady=1,padx=40)

tk.Label(aba1, text="-------------------------------------------------------------------").pack(pady=1)

tk.Label(aba1, text="", font=("Arial", 10, "bold")).pack(anchor="w",pady=1,padx=40)

tk.Label(aba1, text="Nome do Cliente:", font=("Arial", 10, "bold")).pack(anchor="w",pady=5,padx=45)
entrada_nome = tk.Entry(aba1, width=30)
entrada_nome.pack(anchor="w",padx=45,pady=1)

tk.Label(aba1, text="", font=("Arial", 10, "bold")).pack(anchor="w",pady=1,padx=40)

tk.Label(aba1, text="CPF:", font=("Arial", 10, "bold")).pack(anchor="w",pady=5,padx=45) 
entrada_cpf = tk.Entry(aba1, width=30)
entrada_cpf.pack(anchor="w", padx=45, pady=1)

tk.Label(aba1, text="", font=("Arial", 10, "bold")).pack(anchor="w",pady=1,padx=40)

tk.Label(aba1, text="Numero de telefone:", font=("Arial", 10, "bold")).pack(anchor="w",pady=5,padx=45) 
telefone = tk.Entry(aba1, width=30)
telefone.pack(anchor="w", padx=45, pady=1)


# Esta linha é o segredo! <KeyRelease> significa "quando soltar a tecla"
entrada_cpf.bind("<KeyRelease>", formatar_cpf)
telefone.bind("<KeyRelease>", formatar_telefone)

#---------------------------------------------------------------------------------------------------

tk.Label(aba1, text="", font=("Arial", 15, "bold")).pack(anchor="w",pady=1,padx=40)

botao1 = tk.Button(aba1, text="Salvar Ordem de Serviço", bg="blue", fg="white", command=salvar_cadastro_em_SQlite)
botao1.place(x=45, y=375)


tk.Label(aba1, text="", font=("Arial", 15, "bold")).pack(anchor="w",pady=1,padx=40)

# Adicione este botão na sua interface (ajuste o x e y)
btn_reset = tk.Button(aba1, text="Limpar Campos", bg= "#FF0000",fg="white", command=limpar_campos_cadastro)
btn_reset.place(x=200,y=375) # Coloque onde ficar melhor no seu layout


#aba2 \/------------------------------------------------------------------------------------------------

from fpdf import FPDF

def gerar_ordem_servico():
    # 1. Pega o ID que o funcionário digitou no campo de imprimir
    id_alvo = entrada_busca_id_pdf.get() # <--- Atenção ao nome da sua Entry!
    
    if not id_alvo:
        messagebox.showwarning("Aviso", "Digite o ID do cliente para imprimir!")
        return

    # 2. Busca os dados desse cliente específico
    cursor.execute("SELECT nome, cpf, telefone FROM clientes WHERE id = ?", (id_alvo,))
    cliente = cursor.fetchone()

    if not cliente:
        messagebox.showerror("Erro", "ID não encontrado!")
        return

    # 3. Busca o ÚLTIMO serviço desse cliente (pelo CPF dele)
    cpf_cliente = cliente[1]
    cursor.execute("SELECT data, servico, problema FROM servico WHERE cpf = ? ORDER BY data DESC LIMIT 1", (cpf_cliente,))
    servico = cursor.fetchone()
    
    detalhes_servico = servico[1] if servico else "Nenhum serviço registrado"
    problema_texto = servico[2] if (servico and servico[2]) else ""

    try:
        # --- INÍCIO DA MONTAGEM DO PDF ---
        pdf = FPDF()
        pdf.add_page()
        
        # Cabeçalho
        pdf.set_font("Arial", "B", 20)
        pdf.cell(0, 15, "ASSISTENCIA TECNICA CAMBORIU", ln=True, align="C")
        pdf.line(10, 25, 200, 25)
        pdf.ln(10)
        
        # Corpo do Texto
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "COMPROVANTE DE ENTRADA / ORDEM DE SERVICO", ln=True)
        
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 8, f"ID do Registro: {id_alvo}", ln=True)
        pdf.cell(0, 8, f"Cliente: {cliente[0]}", ln=True)
        pdf.cell(0, 8, f"CPF: {cliente[1]}", ln=True)
        pdf.cell(0, 8, f"Telefone: {cliente[2]}", ln=True)
        
        pdf.ln(5)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "DETALHES DO CHAMADO:", ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 8, f"Servico: {detalhes_servico}\nDescricao: {problema_texto}")

        # Rodapé com Data
        pdf.ln(20)
        data_hoje = datetime.now().strftime("%d/%m/%Y")
        pdf.cell(0, 10, f"Camboriu, {data_hoje}", ln=True, align="R")
        pdf.cell(0, 10, "__________________________", ln=True, align="C")
        pdf.cell(0, 5, "Assinatura do Tecnico", ln=True, align="C")

        # Salva o arquivo
        nome_arquivo = f"OS_ID_{id_alvo}.pdf"
        pdf.output(nome_arquivo)
        
        messagebox.showinfo("Sucesso", f"PDF Gerado: {nome_arquivo}")
        os.startfile(nome_arquivo) # <--- Isso abre o PDF na hora para você ver!

    except Exception as e:
        messagebox.showerror("Erro no PDF", f"Falha ao gerar arquivo: {e}")
        
def executar_pesquisa():
    text_area.config(state="normal")
    text_area.delete(1.0, tk.END)
    nome_para_buscar = entrada_busca.get()
    filtro = f"%{nome_para_buscar}%"
    
    # 1. Busca os dados do Cliente
    cursor.execute("SELECT * FROM clientes WHERE nome LIKE ?", (filtro,))
    todos_os_clientes = cursor.fetchall()
    
    if not todos_os_clientes:
        text_area.insert(tk.END, "Nenhum cliente encontrado.")
    else:

        for cliente in todos_os_clientes:
            # cliente[0]=ID, [1]=Nome, [2]=CPF, [3]=Telefone
            id_cliente = cliente[0]
            nome = cliente[1]
            cpf_bruto = cliente[2]
            telefone_cli = cliente[3]

            if len(cpf_bruto) >= 14:
                # Pega os 3 primeiros caracteres (123)
                inicio = cpf_bruto[:3]
                # Pega os 2 últimos caracteres (01)
                fim = cpf_bruto[-2:]
                # Monta a versão mascarada
                cpf_protegido = f"{inicio}.***.***-{fim}"

            # Exibe o Cabeçalho do Cliente
            text_area.insert(tk.END, f"{'='*45}\n")
            text_area.insert(tk.END, f"ID: {id_cliente} | NOME: {nome}\n")
            text_area.insert(tk.END, f"CPF: {cpf_protegido} | TEL: {telefone_cli}\n")
            text_area.insert(tk.END, f"{'-'*45}\n")
            text_area.insert(tk.END, f" HISTÓRICO DE SERVIÇOS:\n\n")

            # 2. O PULO DO GATO: Busca serviços usando o CPF do cliente atual
            cursor.execute("SELECT data, servico, problema, processador, memoria_ram FROM servico WHERE cpf = ?", (cpf_bruto,))
            servicos = cursor.fetchall()

            if not servicos:
                text_area.insert(tk.END, "  > Nenhum serviço registrado para este CPF.\n")
            else:
                for s in servicos:
                    # s[0]=Data, s[1]=Serviço, s[2]=Problema
                    data_s = s[0]
                    tipo_s = s[1]
                    detalhe_s = s[2] if s[2] else "Sem detalhes"
                    processador = s[3]
                    ram = s[4] 


                    # Formata a exibição do serviço
                    text_area.insert(tk.END, f" [{data_s}] {tipo_s}\n")
                    text_area.insert(tk.END, f" Detalhe: {detalhe_s}\n")
                    text_area.insert(tk.END, f" CPU\t:{processador}\n RAM\t:{ram}\n")
                    text_area.insert(tk.END, f"{'.'*40}\n")
            
            text_area.insert(tk.END, "\n") # Espaço entre um cliente e outro

    text_area.config(state="disabled")

def deletar_registro():
    # 1. Pega o ID
    id_para_deletar = deletar_ID.get()
    
    # 2. Verifica se o campo está vazio
    if not id_para_deletar:
        messagebox.showwarning("Erro", "Por favor, digite um ID!")
        return

    # 3. Pergunta se tem certeza
    if messagebox.askyesno("CONFIRMAÇÃO", f"Deseja apagar o registro ID {id_para_deletar}?"):
        
        # O PULO DO GATO: Executa o delete
        cursor.execute("DELETE FROM clientes WHERE id = ?", (id_para_deletar,))
        
        # O rowcount diz quantas linhas foram apagadas
        if cursor.rowcount == 0:
            messagebox.showwarning("AVISO", f"O ID {id_para_deletar} não existe no banco de dados!")
        else:
            conexao.commit()
            messagebox.showinfo("Sucesso", f"Registro ID {id_para_deletar} removido!")
            deletar_ID.delete(0, END)
            executar_pesquisa() # Atualiza a lista na tela        

def buscar_ID():
    id_info = entrada_busca_ID.get()

    if id_info == "":
        messagebox.showwarning("AVISO!","Digite o ID antes de buscar!")
        
    else:    
        cursor.execute("SELECT * FROM clientes WHERE id = ?", (id_info,))
        
        # 4. Pega todos os resultados que o cursor encontrou
        id_cliente = cursor.fetchall()
        
        # 5. Prepara a área de texto (ScrolledText) para exibir
        # Destrava para escrever
            # Limpa o que tinha antes
    
        if not id_cliente:
            messagebox.showwarning("AVISO!","Este ID não existe!")
        else:
            def cancelar():
                janela_info.destroy()

                entrada_busca_ID.delete(0,END)

            def editar_info():
                    # .get() para pegar o texto, senão ele tenta salvar a 'caixa' inteira
                name_edit = entrada_nome_2.get()
                tel_edit = telefone_2.get()
                cpf_edit = entrada_cpf_2.get()
                id_alvo = entrada_busca_ID.get() # Precisamos do ID para saber QUEM atualizar

                try:
                    cursor.execute("""
                        UPDATE clientes 
                        SET nome = ?, cpf = ?, telefone = ? 
                        WHERE id = ?
                    """, (name_edit, cpf_edit, tel_edit, id_alvo))
                        
                    conexao.commit()
                    messagebox.showinfo("Sucesso", f"Cliente {name_edit} atualizado!")
                    janela_info.destroy() # Fecha a janelinha depois de salvar
                except Exception as e:
                    messagebox.showerror("Erro", f"Não foi possível salvar: {e}")

            janela_info = tk.Toplevel()
            janela_info.title("ALTERAR INFORMAÇÕES:")
            janela_info.geometry("280x300")
            janela_info.iconbitmap(ico)

            tk.Label(janela_info, text="", font=("Arial", 10, "bold")).pack(anchor="w",pady=1,padx=40)

            tk.Label(janela_info, text="Nome do Cliente:", font=("Arial", 10, "bold")).pack(anchor="w",pady=5,padx=45)
            entrada_nome_2 = tk.Entry(janela_info, width=30)
            entrada_nome_2.pack(anchor="w",padx=45,pady=1)

            tk.Label(janela_info, text="", font=("Arial", 10, "bold")).pack(anchor="w",pady=1,padx=40)

            tk.Label(janela_info, text="CPF:", font=("Arial", 10, "bold")).pack(anchor="w",pady=5,padx=45) 
            entrada_cpf_2 = tk.Entry(janela_info, width=30)
            entrada_cpf_2.pack(anchor="w", padx=45, pady=1)

            tk.Label(janela_info, text="", font=("Arial", 10, "bold")).pack(anchor="w",pady=1,padx=40)

            tk.Label(janela_info, text="Numero de telefone:", font=("Arial", 10, "bold")).pack(anchor="w",pady=5,padx=45) 
            telefone_2 = tk.Entry(janela_info, width=30)
            telefone_2.pack(anchor="w", padx=45, pady=1)

            botao2 = tk.Button(janela_info, text="Salvar alterações:", bg="#000BAC", fg="white", command=editar_info)
            botao2.place(x=45,y=240)

            botao2 = tk.Button(janela_info, text="Cancelar:", bg="#FF0000", fg="white", command=cancelar)
            botao2.place(x=170,y=240)
        
            entrada_cpf_2.bind("<KeyRelease>", formatar_cpf)
            telefone_2.bind("<KeyRelease>", formatar_telefone)

            for cliente in id_cliente:
                nome = f"{cliente[1]}"
                cpf = f"{cliente[2]}"
                tel = f"{cliente[3]}"

                entrada_nome_2.insert(0,nome)
                entrada_cpf_2.insert(0,cpf)
                telefone_2.insert(0,tel)

tk.Label(aba2, text="").pack(pady=1)

tk.Label(aba2, text="PESQUISAR HISTÓRICO DE CLIENTES:", font=("Arial", 10, "bold")).pack(pady=1,padx=40)

tk.Label(aba2, text="-------------------------------------------------------------------").pack(pady=1)

tk.Label(aba2, text="Nome do Cliente:", font=("Arial", 10, "bold")).place(x=37,y=78)
entrada_busca = tk.Entry(aba2, width=18)
entrada_busca.place(x=40,y=104)

botao = tk.Button(aba2, text="Buscar:", bg="#000080", fg="white", command=executar_pesquisa)
botao.place(x=40,y=130)

botao_del = tk.Button(aba2, text="Limpar", bg="#FF0000", fg="white", command=executar_limpeza_real)
botao_del.place(x=105,y=130)

tk.Label(aba2, text="Imprimir INFO:(ID)", font=("Arial", 10, "bold")).place(x=197,y=78)
entrada_busca_id_pdf = tk.Entry(aba2, width=18)
entrada_busca_id_pdf.place(x=200,y=104)

botao_pdf = tk.Button(aba2, text="Imprimir:", bg="#000080", fg="white", command=gerar_ordem_servico)
botao_pdf.place(x=200,y=130)

text_area = scrolledtext.ScrolledText(aba2, width=42, height=18)
text_area.place(x=13,y=170)

#aba3 \/ ------------------------------------------------------------------------------------------------

tk.Label(aba3, text="").pack(pady=1)

tk.Label(aba3, text="""     EDITAR / DELETAR 
    INFOMAÇÔES DE CLIENTES:""", font=("Arial", 13, "bold")).pack(pady=1,padx=40)

tk.Label(aba3, text="-------------------------------------------------------------------").pack(pady=1)

tk.Label(aba3, text="ID do cliente:", font=("Arial", 10, "bold")).place(x=37,y=134)
entrada_busca_ID = tk.Entry(aba3, width=18)
entrada_busca_ID.place(x=40,y=160)

botao_del = tk.Button(aba3, text="Deletar:", bg="#FF0000", fg="white", command=deletar_registro)
botao_del.place(x=200,y=186)

tk.Label(aba3, text="Deletar ID:", font=("Arial", 10, "bold")).place(x=197,y=134)
deletar_ID = tk.Entry(aba3, width=18)
deletar_ID.place(x=200,y=160)

botao2 = tk.Button(aba3, text="Editar:", bg="#000BAC", fg="white", command=buscar_ID)
botao2.place(x=40,y=186)

#Aba_4 \/ -----------------------------------------------------------------------------------------
tk.Label(aba4, text="", font=("Arial", 15, "bold")).pack(anchor="w",pady=1,padx=40)

tk.Label(aba4, text="Descreva o tipo de serviço:", font=("Arial", 15, "bold")).pack(pady=1)

tk.Label(aba4, text="-------------------------------------------------------------------").pack(pady=1)

tk.Label(aba4, text="CPF: (Onde o serviço sera anexado)", font=("Arial", 10, "bold")).pack(anchor="w",pady=5,padx=45) 
entrada_cpf_servico = tk.Entry(aba4, width=30)
entrada_cpf_servico.pack(anchor="w", padx=45, pady=1)

entrada_cpf_servico.bind("<KeyRelease>", formatar_cpf)

tk.Label(aba4, text="Serviços comuns", font=("Arial", 10, "bold")).pack(anchor="w",pady=5,padx=45)
entrada_servico_2 = ["Problema tecnico", "Limpeza preventiva", "Upgrade de Pc", "Troca de pasta termica"]
lista_de_servicos = ttk.Combobox(aba4, values= entrada_servico_2, state="readonly",width=26)
lista_de_servicos.current()
lista_de_servicos.pack(anchor="w",pady=1,padx=45)

botao_sc = tk.Button(aba4, text="Salvar pedido:", bg="#000BAC", fg="white", command=salvar_serviço_em_SQlite)
botao_sc.place(x=270,y=170)

# Criamos o Label e a Entrada, mas NÃO damos pack ainda!
label_especifico = tk.Label(aba4, text="Descreva oque aconteceu:", font=("Arial", 10, "bold"))
problema_especifico = tk.Text(aba4, width=42, height=10)

label_processador = tk.Label(aba4, text="Processador?(Se solber)", font=("Arial", 10, "bold"))
entrada_Processador = ["Não sei","Intel","AMD","Apple"]
lista_processador = ttk.Combobox(aba4, values= entrada_Processador, state="readonly",width=10)
lista_processador.current()

label_memoria_ram = tk.Label(aba4, text="Tipo de memoria ram?", font=("Arial", 10, "bold"))
entrada_memoria_ram = ["Não sei","DDR4","DDR5"]
lista_memoria_ram = ttk.Combobox(aba4, values= entrada_memoria_ram, state="readonly",width=10)
lista_memoria_ram.current()

# O PULO DO GATO: Avisar a Combobox para chamar a função quando mudar de valor
lista_de_servicos.bind("<<ComboboxSelected>>", verificar_servico)

# 2. Criamos uma função especial para o fechamento
def ao_fechar_janela():
    if messagebox.askyesno("Sair", "Deseja salvar e fechar o sistema com segurança?"):
        conexao.close() # Primeiro fechamos a conexão do banco
        trancar_banco() # Depois trancamos o arquivo (o envelope)
        janela.destroy() # Por fim, fechamos a janela
# 3. Conectamos essa função ao botão "X" da janela
janela.protocol("WM_DELETE_WINDOW", ao_fechar_janela)

janela.mainloop()