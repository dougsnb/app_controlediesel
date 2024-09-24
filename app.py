import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
from datetime import datetime
from openpyxl import Workbook  # Importa a biblioteca openpyxl

# Classes para cálculo e armazenamento dos dados
class DadosAbastecimento:
    def __init__(self, arquivo_dados='dados_abastecimento.json'):
        self.arquivo_dados = arquivo_dados
        self.quantidade_no_tanque = 0
        self.ultima_bomba_final = None
        self.historico = []
        self.carregar_dados()

    def carregar_dados(self):
        """Carrega os dados do arquivo JSON, se existir."""
        if os.path.exists(self.arquivo_dados):
            with open(self.arquivo_dados, 'r') as f:
                dados = json.load(f)
                self.quantidade_no_tanque = dados.get('quantidade_no_tanque', 0)
                self.ultima_bomba_final = dados.get('ultima_bomba_final')
                self.historico = dados.get('historico', [])
        else:
            self.salvar_dados()

    def salvar_dados(self):
        """Salva os dados em um arquivo JSON."""
        dados = {
            'quantidade_no_tanque': self.quantidade_no_tanque,
            'ultima_bomba_final': self.ultima_bomba_final,
            'historico': self.historico
        }
        with open(self.arquivo_dados, 'w') as f:
            json.dump(dados, f)

    def adicionar_historico(self, registro):
        """Adiciona um registro ao histórico e salva os dados."""
        self.historico.append(registro)
        self.salvar_dados()


class CalculadoraAbastecimento:
    def __init__(self, capacidade_tanque=15000):
        self.capacidade_tanque = capacidade_tanque

    def calcular_consumo_dia(self, bomba_inicial, bomba_final):
        """Calcula o consumo do dia."""
        return bomba_final - bomba_inicial

    def calcular_saldo_pos_abastecimento(self, quantidade_no_tanque, consumo_dia):
        """Calcula o saldo após o abastecimento."""
        return quantidade_no_tanque - consumo_dia

    def calcular_diferenca_visor(self, saldo_pos_abastecimento, visor_final):
        """Calcula a diferença entre o saldo e o visor."""
        return saldo_pos_abastecimento - visor_final


class SistemaAbastecimento:
    def __init__(self):
        self.dados = DadosAbastecimento()
        self.calculadora = CalculadoraAbastecimento()

    def registrar_abastecimento(self, bomba_inicial, bomba_final, visor_final, quantidade_inicial):
        """Registra o abastecimento e retorna os cálculos."""
        if self.dados.ultima_bomba_final is not None and bomba_inicial != self.dados.ultima_bomba_final:
            print(f"Aviso: diferença entre a bomba final do dia anterior ({self.dados.ultima_bomba_final}) e a inicial do dia atual ({bomba_inicial})")

        consumo_dia = self.calculadora.calcular_consumo_dia(bomba_inicial, bomba_final)
        saldo_pos_abastecimento = self.calculadora.calcular_saldo_pos_abastecimento(quantidade_inicial, consumo_dia)
        diferenca_visor = self.calculadora.calcular_diferenca_visor(saldo_pos_abastecimento, visor_final)

        self.dados.quantidade_no_tanque = saldo_pos_abastecimento
        self.dados.ultima_bomba_final = bomba_final
        
        # Adicionando registro ao histórico com a data atual
        registro = {
            'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'bomba_inicial': bomba_inicial,
            'bomba_final': bomba_final,
            'visor_final': visor_final,
            'quantidade_inicial': quantidade_inicial,
            'consumo_dia': consumo_dia,
            'saldo_pos_abastecimento': saldo_pos_abastecimento,
            'diferenca_visor': diferenca_visor
        }
        self.dados.adicionar_historico(registro)

        return consumo_dia, saldo_pos_abastecimento, diferenca_visor


# Interface Gráfica com Tkinter
class App:
    def __init__(self, root):
        self.sistema = SistemaAbastecimento()
        self.root = root
        self.root.title("Controle de Abastecimento")

        # Tela de Entrada
        self.frame_calculo = tk.Frame(root)
        self.frame_calculo.pack(pady=20)

        self.label_titulo = tk.Label(self.frame_calculo, text="CONTROLE DE ABASTECIMENTO", font=("Helvetica", 16))
        self.label_titulo.pack()




        self.label_bomba_inicial = tk.Label(self.frame_calculo, text="Número da bomba inicial:")
        self.label_bomba_inicial.pack()
        self.entry_bomba_inicial = tk.Entry(self.frame_calculo)
        self.entry_bomba_inicial.pack()

        self.label_bomba_final = tk.Label(self.frame_calculo, text="Número da bomba final:")
        self.label_bomba_final.pack()
        self.entry_bomba_final = tk.Entry(self.frame_calculo)
        self.entry_bomba_final.pack()

        self.label_visor_final = tk.Label(self.frame_calculo, text="Número do visor:")
        self.label_visor_final.pack()
        self.entry_visor_final = tk.Entry(self.frame_calculo)
        self.entry_visor_final.pack()

        self.button_calcular = tk.Button(self.frame_calculo, text="Calcular", command=self.calcular)
        self.button_calcular.pack(pady=10)

        # Tela de Resultados
        self.frame_resultados = tk.Frame(root)
        
        self.label_resultados_titulo = tk.Label(self.frame_resultados, text="RESULTADOS", font=("Helvetica", 16))
        self.result_label = tk.Label(self.frame_resultados, text="")
        self.button_novo_calculo = tk.Button(self.frame_resultados, text="Novo Cálculo", command=self.mostrar_calculo)
        self.button_historico = tk.Button(self.frame_resultados, text="Histórico", command=self.mostrar_historico)

        # Tela de Histórico
        self.frame_historico = tk.Frame(root)
        self.label_historico_titulo = tk.Label(self.frame_historico, text="HISTÓRICO", font=("Helvetica", 16))
        self.historico_texto = tk.Text(self.frame_historico, width=80, height=15)
        self.button_voltar = tk.Button(self.frame_historico, text="Voltar", command=self.mostrar_resultados)
        self.button_download = tk.Button(self.frame_historico, text="Baixar Planilha", command=self.baixar_planilha)

    def calcular(self):
        """Realiza o cálculo e exibe os resultados."""
        try:
            bomba_inicial = float(self.entry_bomba_inicial.get())
            bomba_final = float(self.entry_bomba_final.get())
            visor_final = float(self.entry_visor_final.get())
            quantidade_inicial = float(self.entry_quantidade_inicial.get())

            # Validações
            if bomba_final <= bomba_inicial:
                messagebox.showerror("Erro", "A bomba final deve ser maior que a bomba inicial!")
                return
            if quantidade_inicial < 0:
                messagebox.showerror("Erro", "A quantidade inicial não pode ser negativa!")
                return

            consumo_dia, saldo_pos_abastecimento, diferenca_visor = self.sistema.registrar_abastecimento(
                bomba_inicial, bomba_final, visor_final, quantidade_inicial)

            resultado = (
                f"Consumo do dia: {consumo_dia:.2f} litros\n"
                f"Saldo do tanque: {saldo_pos_abastecimento:.2f} litros\n"
                f"Diferença de visor: {diferenca_visor:.2f} litros"
            )
            self.result_label.config(text=resultado)

            self.frame_calculo.pack_forget()
            self.label_resultados_titulo.pack()
            self.result_label.pack()
            self.button_novo_calculo.pack(pady=5)
            self.button_historico.pack(pady=5)
            self.frame_resultados.pack(pady=20)
        
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira valores válidos!")

    def mostrar_calculo(self):
        """Exibe a tela de cálculo novamente."""
        self.frame_resultados.pack_forget()
        self.frame_calculo.pack(pady=20)

    def mostrar_historico(self):
        """Exibe o histórico de abastecimento."""
        self.frame_resultados.pack_forget()
        self.label_historico_titulo.pack()
        self.historico_texto.delete(1.0, tk.END)  # Limpa o campo de histórico

        # Ordenando o histórico por data, com validação para garantir que 'data' está presente
        registros_ordenados = sorted(
            (registro for registro in self.sistema.dados.historico if 'data' in registro),
            key=lambda x: x['data'], reverse=True
        )

        for registro in registros_ordenados:
            self.historico_texto.insert(tk.END, f"Data: {registro['data']}\n"
                                                 f"Bomba Inicial: {registro['bomba_inicial']}\n"
                                                 f"Bomba Final: {registro['bomba_final']}\n"
                                                 f"Visor Final: {registro['visor_final']}\n"
                                                 f"Quantidade Inicial: {registro['quantidade_inicial']}\n"
                                                 f"Consumo do Dia: {registro['consumo_dia']:.2f} litros\n"
                                                 f"Saldo Pós-Abastecimento: {registro['saldo_pos_abastecimento']:.2f} litros\n"
                                                 f"Diferença de Visor: {registro['diferenca_visor']:.2f} litros\n"
                                                 f"{'-'*40}\n"
                                                 )
        self.historico_texto.pack()
        self.button_voltar.pack(pady=5)
        self.button_download.pack(pady=5)
        self.frame_historico.pack(pady=20)

    def mostrar_resultados(self):
        """Exibe a tela de resultados novamente."""
        self.frame_historico.pack_forget()
        self.frame_resultados.pack(pady=20)

    def baixar_planilha(self):
        """Baixa a planilha do histórico em formato Excel."""
        caminho_arquivo = filedialog.asksaveasfilename(defaultextension='.xlsx', 
                                                         filetypes=[("Excel files", '*.xlsx'), ("All files", '*.*')])
        if caminho_arquivo:
            workbook = Workbook()
            sheet = workbook.active
            sheet.title = "Histórico de Abastecimento"
            # Adicionando cabeçalho
            cabecalho = ["Data", "Bomba Inicial", "Bomba Final", "Visor Final", 
                         "Quantidade Inicial", "Consumo do Dia", 
                         "Saldo Pós-Abastecimento", "Diferença de Visor"]
            sheet.append(cabecalho)

            for registro in self.sistema.dados.historico:
                linha = [
                    registro['data'],
                    registro['bomba_inicial'],
                    registro['bomba_final'],
                    registro['visor_final'],
                    registro['quantidade_inicial'],
                    registro['consumo_dia'],
                    registro['saldo_pos_abastecimento'],
                    registro['diferenca_visor']
                ]
                sheet.append(linha)

            workbook.save(caminho_arquivo)
            messagebox.showinfo("Sucesso", "Planilha salva com sucesso!")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
