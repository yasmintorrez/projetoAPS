import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import mysql.connector
import numpy as np
from sklearn.linear_model import LinearRegression
import math


def conectar_banco():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="yasmio123",
        database="clima"
    )


def registrar_usuario():
    conn = conectar_banco()
    cursor = conn.cursor()

    nome_usuario = entry_nome_usuario.get()
    senha = entry_senha.get()

    if nome_usuario == "" or senha == "":
        messagebox.showerror("Erro", "Todos os campos são obrigatórios")
    else:
        cursor.execute("INSERT INTO usuarios (nome, senha) VALUES (%s, %s)", (nome_usuario, senha))
        conn.commit()
        conn.close()
        messagebox.showinfo("", "Usuário registrado com sucesso")


def login_usuario():
    conn = conectar_banco()
    cursor = conn.cursor()

    nome_usuario = entry_nome_usuario.get()
    senha = entry_senha.get()

    cursor.execute("SELECT * FROM usuarios WHERE nome = %s AND senha = %s", (nome_usuario, senha))
    row = cursor.fetchone()

    if row:
        messagebox.showinfo("", f"Bem-vindo, {nome_usuario}!")
        tela_login.destroy()
        mostrar_tela_principal()
    else:
        messagebox.showerror("Erro", "Nome de usuário ou senha incorretos")

    conn.close()


def mostrar_tela_principal():
    def calcular():

        conn = conectar_banco()
        cursor = conn.cursor()

        query1 = "SELECT AVG(temperatura), AVG(umidade), AVG(vento) FROM indicadores"
        query2 = "SELECT temperatura FROM indicadores"

        cursor.execute(query1)
        result = cursor.fetchone()

        cursor.execute(query2)
        temperaturas = cursor.fetchall()

        conn.close()

        media_temperatura = result[0]
        media_umidade = result[1]
        media_vento = result[2]

        faixas_temperatura = {
            'Milho': (24, 30),
            'Trigo': (15, 20),
            'Arroz': (20, 35),
            'Soja': (20, 30),
            'Café': (18, 22),
            'Algodão': (21, 37),
            'Uva': (10, 20),
            'Batata': (10, 22),
            'Banana': (20, 44),
            'Tomate': (10, 34)
        }

        temperatura_atual = media_temperatura

        culturas_selecionadas = [cultura for cultura, var in variaveis.items() if var.get()]

        resultados = ""
        for cultura in culturas_selecionadas:
            faixa = faixas_temperatura[cultura]
            temperatura_minima, temperatura_maxima = faixa
            if temperatura_minima <= temperatura_atual <= temperatura_maxima:
                resultados += f"A temperatura atual de {round(temperatura_atual, 2)}°C é adequada para o cultivo de {cultura}.\n"
            else:
                resultados += f'A temperatura atual de {round(temperatura_atual, 2)}°C não é adequada para o cultivo de {cultura}.\n'

        temperaturas = np.array(temperaturas).reshape(-1, 1)

        modelo = LinearRegression()
        modelo.fit(temperaturas[:-1], temperaturas[1:])

        proxima_temperatura = modelo.predict(temperaturas[-1].reshape(1, -1))

        resultados += f"\nPróxima temperatura prevista: {round(proxima_temperatura[0][0], 2)}°C\n"

        def umidade_absoluta(media_temperatura, media_umidade):
            a = 17.27
            b = 237.7
            R_v = 0.3
            pressao_saturacao = 6.11 * math.exp((a * media_temperatura) / (b + media_temperatura))
            pressao_parcial = (media_umidade / 100) * pressao_saturacao
            umidade_absoluta = (pressao_parcial * 100) / (R_v * (media_temperatura + 273.15))
            return umidade_absoluta

        umidade = umidade_absoluta(media_temperatura, media_umidade)
        resultados += f"Umidade absoluta: {round(umidade, 2)} g/m³\n"

        resultado_label.config(text=resultados)


    tela_principal = tk.Tk()
    tela_principal.title("Tela Principal")
    tela_principal.geometry("700x600")
    tela_principal.configure(bg="#8FC1B5")

    # Opções que o usuário for escolher
    variaveis = {
        'Milho': tk.BooleanVar(),
        'Trigo': tk.BooleanVar(),
        'Arroz': tk.BooleanVar(),
        'Soja': tk.BooleanVar(),
        'Café': tk.BooleanVar(),
        'Algodão': tk.BooleanVar(),
        'Uva': tk.BooleanVar(),
        'Batata': tk.BooleanVar(),
        'Banana': tk.BooleanVar(),
        'Tomate': tk.BooleanVar()
    }

    # Checkbox para selecionar culturas
    frame_culturas = tk.Frame(tela_principal, bg="#F2F2F2")
    frame_culturas.pack(pady=20)

    tk.Label(frame_culturas, text="Selecione as culturas:", bg="#8FC1B5", font=("Arial", 16)).pack()

    for cultura, var in variaveis.items():
        ttk.Checkbutton(frame_culturas, text=cultura, variable=var).pack(anchor='w')

    ttk.Button(tela_principal, text="Calcular", command=calcular).pack(pady=20)


    resultado_label = tk.Label(tela_principal, text="", justify="left", bg="#8FC1B5", fg="black", font=("Arial", 14))
    resultado_label.pack(pady=20)

    tela_principal.mainloop()

tela_login = tk.Tk()
tela_login.title("Tela de Login")
tela_login.geometry("500x400")
tela_login.configure(bg="#8FC1B5")


style = ttk.Style()
style.configure("TLabel", background="#8FC1B5", font=("Arial", 16))
style.configure("TButton", background="white", font=("Arial", 16))
style.configure("TEntry", font=("Arial", 16))


ttk.Label(tela_login, text="Nome de Usuário").pack(pady=5)
entry_nome_usuario = ttk.Entry(tela_login)
entry_nome_usuario.pack(pady=5)


ttk.Label(tela_login, text="Senha").pack(pady=5)
entry_senha = ttk.Entry(tela_login, show="*")
entry_senha.pack(pady=5)


ttk.Button(tela_login, text="Login", command=login_usuario).pack(pady=10)
ttk.Button(tela_login, text="Cadastrar", command=registrar_usuario).pack(pady=10)

tela_login.mainloop()