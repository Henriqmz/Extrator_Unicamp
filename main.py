import os
import sys
import re
import threading
import tempfile
from tkinter import Tk, Label, Button, Entry, StringVar, BooleanVar, messagebox, filedialog, Text, Frame, Radiobutton
from tkinter.ttk import Progressbar, Separator
from extractor import *
from processor import *
from saver import *

class StdOutRedirector:
    """Redireciona a saída do console (stdout) para um widget Text do Tkinter de forma thread-safe."""
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.configure(state='normal')
        self.text_widget.insert('end', string)
        self.text_widget.see('end')
        self.text_widget.configure(state='disabled')

    def flush(self):
        pass

class ExtratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Extrator de Provas - Vestibular")
        self.root.geometry("700x650")
        self.root.resizable(True, True)
        self.root.configure(bg="#f4f6f9")
        
        # Centralizar a janela
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        # Variáveis do Tkinter
        self.caminho_prova = StringVar()
        self.caminho_gabarito = StringVar()
        self.fase_prova = StringVar(value="1")  # "1" = Objetiva, "2" = Dissertativa
        self.usar_ia = BooleanVar(value=False)
        self.chave_gemini = StringVar()

        # Carregar variáveis do .env se existirem
        carregar_env()
        env_key = os.getenv("GEMINI_API_KEY")
        if env_key and env_key != "INSIRA_SUA_CHAVE_GEMINI_AQUI":
            self.chave_gemini.set(env_key)

        self._criar_layout()
        
        # Redirecionar stdout para a caixa de logs
        self.stdout_original = sys.stdout
        sys.stdout = StdOutRedirector(self.txt_log)

    def _criar_layout(self):
        # 1. Cabeçalho / Banner
        header = Frame(self.root, bg="#2c3e50", height=60)
        header.pack(fill="x", side="top")
        
        lbl_titulo = Label(
            header, 
            text="Extrator Estruturado de Provas", 
            font=("Arial", 16, "bold"), 
            fg="white", 
            bg="#2c3e50"
        )
        lbl_titulo.pack(pady=15, padx=20, side="left")

        # 2. Painel de Configurações
        frame_config = Frame(self.root, bg="#f4f6f9", padx=20, pady=15)
        frame_config.pack(fill="x")

        # Linha 1: Seleção da Prova (PDF)
        Label(frame_config, text="Arquivo da Prova (PDF):", font=("Arial", 10, "bold"), bg="#f4f6f9").grid(row=0, column=0, sticky="w", pady=5)
        Entry(frame_config, textvariable=self.caminho_prova, width=60, font=("Arial", 10)).grid(row=0, column=1, padx=5, pady=5)
        Button(frame_config, text="Buscar...", command=self._buscar_prova, font=("Arial", 9)).grid(row=0, column=2, padx=5, pady=5)

        # Linha 2: Fase da Prova
        Label(frame_config, text="Fase da Prova:", font=("Arial", 10, "bold"), bg="#f4f6f9").grid(row=1, column=0, sticky="w", pady=5)
        frame_radio = Frame(frame_config, bg="#f4f6f9")
        frame_radio.grid(row=1, column=1, columnspan=2, sticky="w", pady=5)
        
        Radiobutton(
            frame_radio, 
            text="1ª Fase (Objetiva / Múltipla Escolha)", 
            variable=self.fase_prova, 
            value="1", 
            command=self._atualizar_estado_gabarito,
            bg="#f4f6f9",
            font=("Arial", 10)
        ).pack(side="left", padx=5)
        
        Radiobutton(
            frame_radio, 
            text="2ª Fase (Dissertativa)", 
            variable=self.fase_prova, 
            value="2", 
            command=self._atualizar_estado_gabarito,
            bg="#f4f6f9",
            font=("Arial", 10)
        ).pack(side="left", padx=15)

        # Linha 3: Seleção do Gabarito (PDF)
        self.lbl_gabarito = Label(frame_config, text="Gabarito Oficial (PDF):", font=("Arial", 10, "bold"), bg="#f4f6f9")
        self.lbl_gabarito.grid(row=2, column=0, sticky="w", pady=5)
        
        self.entry_gabarito = Entry(frame_config, textvariable=self.caminho_gabarito, width=60, font=("Arial", 10))
        self.entry_gabarito.grid(row=2, column=1, padx=5, pady=5)
        
        self.btn_gabarito = Button(frame_config, text="Buscar...", command=self._buscar_gabarito, font=("Arial", 9))
        self.btn_gabarito.grid(row=2, column=2, padx=5, pady=5)

        # Separador
        Separator(self.root, orient="horizontal").pack(fill="x", padx=20, pady=5)

        # 3. Painel de Inteligência Artificial
        frame_ia = Frame(self.root, bg="#f4f6f9", padx=20, pady=10)
        frame_ia.pack(fill="x")

        # Checkbox Usar IA
        Radiobutton(
            frame_ia,
            text="Enriquecer com IA (Google Gemini - Área, Disciplinas, Dicas e Resoluções)",
            variable=self.usar_ia,
            value=True,
            bg="#f4f6f9",
            font=("Arial", 10, "bold")
        ).pack(anchor="w", pady=2)
        
        Radiobutton(
            frame_ia,
            text="Não usar enriquecimento por IA (Manter campos do Schema vazios)",
            variable=self.usar_ia,
            value=False,
            bg="#f4f6f9",
            font=("Arial", 10, "bold")
        ).pack(anchor="w", pady=2)

        # Chave API Gemini
        frame_key = Frame(frame_ia, bg="#f4f6f9")
        frame_key.pack(fill="x", pady=5)
        Label(frame_key, text="Chave API Gemini:", font=("Arial", 10), bg="#f4f6f9").pack(side="left", padx=5)
        Entry(frame_key, textvariable=self.chave_gemini, width=45, show="*", font=("Arial", 10)).pack(side="left", padx=5)
        Label(frame_key, text="*(Salva automaticamente no .env)", font=("Arial", 8, "italic"), bg="#f4f6f9", fg="#7f8c8d").pack(side="left", padx=5)

        # Separador
        Separator(self.root, orient="horizontal").pack(fill="x", padx=20, pady=5)

        # 4. Ação Principal (Botão)
        self.btn_iniciar = Button(
            self.root, 
            text="🚀 INICIAR EXTRAÇÃO", 
            font=("Arial", 12, "bold"), 
            bg="#2ecc71", 
            fg="white", 
            activebackground="#27ae60",
            activeforeground="white",
            relief="raised",
            command=self._iniciar_fluxo
        )
        self.btn_iniciar.pack(pady=15)

        # 5. Painel de Status / Logs
        frame_logs = Frame(self.root, bg="#f4f6f9", padx=20, pady=5)
        frame_logs.pack(fill="both", expand=True)

        Label(frame_logs, text="Progresso da Execução:", font=("Arial", 10, "bold"), bg="#f4f6f9").pack(anchor="w", pady=2)
        
        self.txt_log = Text(
            frame_logs, 
            height=12, 
            font=("Consolas", 9), 
            bg="#2c3e50", 
            fg="#ecf0f1", 
            state="disabled",
            wrap="word"
        )
        self.txt_log.pack(fill="both", expand=True, pady=5)

        # Inicializar estado do gabarito baseado no default
        self._atualizar_estado_gabarito()

    def _buscar_prova(self):
        caminho = filedialog.askopenfilename(
            title="Selecione o PDF da Prova",
            filetypes=[("Arquivos PDF", "*.pdf")]
        )
        if caminho:
            self.caminho_prova.set(caminho)

    def _buscar_gabarito(self):
        caminho = filedialog.askopenfilename(
            title="Selecione o PDF do Gabarito",
            filetypes=[("Arquivos PDF", "*.pdf")]
        )
        if caminho:
            self.caminho_gabarito.set(caminho)

    def _atualizar_estado_gabarito(self):
        if self.fase_prova.get() == "1":
            self.lbl_gabarito.configure(fg="black")
            self.entry_gabarito.configure(state="normal")
            self.btn_gabarito.configure(state="normal")
        else:
            self.lbl_gabarito.configure(fg="#bdc3c7")
            self.entry_gabarito.configure(state="disabled")
            self.btn_gabarito.configure(state="disabled")
            self.caminho_gabarito.set("")

    def _iniciar_fluxo(self):
        prova_path = self.caminho_prova.get().strip()
        if not prova_path or not os.path.exists(prova_path):
            messagebox.showerror("Erro", "Por favor, selecione um arquivo PDF de prova válido.")
            return

        # Validar chave Gemini se IA estiver ativa
        if self.usar_ia.get():
            key = self.chave_gemini.get().strip()
            if not key or key == "INSIRA_SUA_CHAVE_GEMINI_AQUI":
                messagebox.showerror(
                    "Erro", 
                    "Você selecionou enriquecimento por IA, mas não inseriu uma chave API do Gemini válida.\n"
                    "Insira a chave no campo correspondente."
                )
                return
            # Gravar no .env para sessões futuras
            self._salvar_chave_env(key)

        # Desabilitar botão para evitar cliques múltiplos
        self.btn_iniciar.configure(state="disabled", text="⏳ PROCESSANDO...", bg="#95a5a6")
        
        # Limpar logs anteriores
        self.txt_log.configure(state="normal")
        self.txt_log.delete("1.0", "end")
        self.txt_log.configure(state="disabled")

        # Rodar o pipeline em uma thread separada para não travar a interface gráfica
        t = threading.Thread(target=self._executar_pipeline)
        t.daemon = True
        t.start()

    def _salvar_chave_env(self, key):
        caminho_env = ".env"
        conteudo = f"GEMINI_API_KEY={key}\n"
        if os.path.exists(caminho_env):
            with open(caminho_env, "r", encoding="utf-8") as f:
                linhas = f.readlines()
            nova_chave = False
            for idx, linha in enumerate(linhas):
                if linha.strip().startswith("GEMINI_API_KEY="):
                    linhas[idx] = f"GEMINI_API_KEY={key}\n"
                    nova_chave = True
                    break
            if not nova_chave:
                linhas.append(conteudo)
            with open(caminho_env, "w", encoding="utf-8") as f:
                f.writelines(linhas)
        else:
            with open(caminho_env, "w", encoding="utf-8") as f:
                f.write(conteudo)
        # Recarregar env no python
        carregar_env()

    def _executar_pipeline(self):
        try:
            prova_path = self.caminho_prova.get().strip()
            gabarito_path = self.caminho_gabarito.get().strip()
            fase = self.fase_prova.get()
            enriquecer_ia = self.usar_ia.get()
            
            print(f"Iniciando extração do PDF: {os.path.basename(prova_path)}")
            edital, ano, tipo_prova = detectar_edital_ano(prova_path)
            pasta_saida = f"{edital}_{ano}"
            
            print("Passo 1: Extraindo páginas do documento...")
            paginas, doc = extrair_pdf(prova_path)
            
            print("Passo 2: Extraindo e analisando imagens...")
            prefixo_img = f"{edital}_{ano}_{tipo_prova.replace('/', '-')}"
            if fase == "2":
                prefixo_img += "_2fase"
            imagens = extrair_imagens(doc, output_dir=f"{pasta_saida}/imgs", prefixo=prefixo_img)
            
            print("Passo 3: Processando textos e agrupamentos...")
            texto = extrair_texto(paginas, imagens)
            textos_comp = extrair_textos_comp(texto)
            
            print("Passo 4: Realizando o parsing das questões...")
            if fase == "1":
                questoes = extrair_questoes(texto, edital=edital, ano=ano, tipo_prova=tipo_prova)
            else:
                questoes = extrair_questoes_dissertativas(texto, edital=edital, ano=ano, tipo_prova=tipo_prova)

            mapa_textos = mapear_textos_comp(textos_comp)
            questoes = enriquecer(questoes, mapa_textos, {})
            mapear_imagens_a_questoes_e_alternativas(questoes, imagens, doc)

            # Aplicar gabarito se for objetiva e gabarito for fornecido
            if fase == "1" and gabarito_path and os.path.exists(gabarito_path):
                print("Passo 5: Analisando e aplicando gabarito oficial...")
                gabarito_res = extrair_gabarito(gabarito_path)
                
                if isinstance(gabarito_res, list):
                    # Se houver múltiplos gabaritos, usar o compatível com a prova selecionada
                    gabarito_respostas = None
                    keys = [k.strip().lower() for k in re.findall(r'[a-zA-Z]', tipo_prova) if k.lower() != 'e']
                    for respostas, tipo in gabarito_res:
                        if any(k in tipo.lower() for k in keys):
                            gabarito_respostas = respostas
                            break
                    if not gabarito_respostas:
                        msg_aviso = f"Nenhum gabarito correspondente ao tipo '{tipo_prova}' foi encontrado no PDF de gabarito fornecido. As respostas não serão aplicadas."
                        print(f"[Aviso] {msg_aviso}")
                        self.root.after(0, lambda: messagebox.showwarning("Aviso de Gabarito", msg_aviso))
                    else:
                        questoes = aplicar_gabarito(questoes, gabarito_respostas)
                else:
                    respostas, _ = gabarito_res
                    questoes = aplicar_gabarito(questoes, respostas)

            # Enriquecimento com IA
            if enriquecer_ia:
                print("Passo 6: Iniciando enriquecimento com IA Google Gemini...")
                api_key = os.getenv("GEMINI_API_KEY")
                questoes = enriquecer_questoes_com_ia(questoes, api_key, mapa_textos=mapa_textos)
            else:
                print("Passo 6: Enriquecimento por IA pulado pelo usuário.")

            print("Passo 7: Salvando questões e textos complementares em JSON...")
            salvar_questoes(questoes, pasta=pasta_saida)
            salvar_textos(textos_comp, pasta=pasta_saida, edital=edital, ano=ano, tipo_ou_cor=tipo_prova)
            
            print("\n==========================================")
            print("🎉 EXTRAÇÃO CONCLUÍDA COM SUCESSO!")
            print(f"Arquivos salvos no diretório: {os.path.abspath(pasta_saida)}")
            print("==========================================")
            
            messagebox.showinfo("Sucesso", f"Extração concluída com sucesso!\n\nDados salvos em:\n{pasta_saida}")
            
        except Exception as e:
            print(f"\n❌ ERRO DURANTE A EXTRAÇÃO:\n{str(e)}")
            messagebox.showerror("Erro Crítico", f"Ocorreu um erro durante a execução:\n\n{str(e)}")
            
        finally:
            # Reabilitar o botão
            self.root.after(0, self._reabilitar_botao)

    def _reabilitar_botao(self):
        self.btn_iniciar.configure(state="normal", text="🚀 INICIAR EXTRAÇÃO", bg="#2ecc71")

    def __del__(self):
        # Restaurar stdout original ao fechar
        sys.stdout = self.stdout_original

def main():
    root = Tk()
    app = ExtratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
