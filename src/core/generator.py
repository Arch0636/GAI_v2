import os
import random
import string
import time
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from PyQt6.QtCore import QThread, pyqtSignal
from .file_creator import get_eicar_content, generate_random_content, randomize_file_dates, create_file_on_disk

# Constantes de extensões (para dry run, se custom_exts estiver vazio)
EXTENSOES_PADRAO_DRY_RUN = [".txt", ".json", ".csv", ".html", ".log", ".xml", ".mp4", ".mp3", ".png", ".jpg",
                            ".dll", ".exe", ".zip", ".rar", ".bin", ".dat", ".ini", ".bat", ".py", ".js",
                            ".php", ".java", ".cpp", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"]

class GeneratorThread(QThread):
    progresso = pyqtSignal(str)
    status_barra = pyqtSignal(int, str)
    finalizado = pyqtSignal(dict)

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.is_running = True
        self.total_gerado_bytes = 0
        self.arquivos_criados = 0
        self.pastas_criadas = 0
        self.tempo_inicio = None
        
        # Calcular total esperado para barra de progresso
        self.total_esperado_arquivos = config["total_pastas"] * config["arquivos_por_pasta"]
        if self.total_esperado_arquivos == 0: # Evitar divisão por zero
            self.total_esperado_arquivos = 1

    def stop(self):
        self.is_running = False

    def run(self):
        self.tempo_inicio = time.time()
        timestamp = datetime.now().strftime("Lote_%Y%m%d_%H%M%S")
        pasta_raiz = os.path.join(self.config["destino"], timestamp)
        
        log_file = None
        try:
            if not self.config.get("dry_run", False):
                os.makedirs(pasta_raiz, exist_ok=True)
                self.pastas_criadas += 1
                
                base_log = os.path.join("gai_pro/data/log")
                os.makedirs(base_log, exist_ok=True)
                log_path = os.path.join(base_log, f"log_{timestamp}.txt")
                log_file = open(log_path, "w", encoding="utf-8")
                log_file.write(f"--- Início da Geração: {datetime.now()} ---\n")
                log_file.write(f"Configurações: {json.dumps(self.config, indent=2)}\n\n")
            else:
                self.progresso.emit("🔍 Modo Simulação (Dry Run) ATIVADO")

            # Usar ThreadPoolExecutor para geração paralela de arquivos
            max_workers = os.cpu_count() * 2 if not self.config.get("dry_run", False) else 1
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures_map = {}
                for i in range(1, self.config["total_pastas"] + 1):
                    if not self.is_running: break
                    
                    nome_pasta = f"Pasta_{i:03d}"
                    caminho_pasta = os.path.join(pasta_raiz, nome_pasta)
                    
                    if not self.config.get("dry_run", False):
                        os.makedirs(caminho_pasta, exist_ok=True)
                        self.pastas_criadas += 1
                        if log_file: log_file.write(f"[{datetime.now()}] Pasta: {caminho_pasta}\n")
                    
                    self.progresso.emit(f"📁 Pasta: {nome_pasta}")

                    subpastas = [caminho_pasta]
                    if self.config["usar_subpastas"]:
                        for j in range(random.randint(1, 3)):
                            nome_sub = f"Sub_{j+1}"
                            caminho_sub = os.path.join(caminho_pasta, nome_sub)
                            if not self.config.get("dry_run", False):
                                os.makedirs(caminho_sub, exist_ok=True)
                                subpastas.append(caminho_sub)
                                self.pastas_criadas += 1
                                if log_file: log_file.write(f"[{datetime.now()}] Subpasta: {caminho_sub}\n")

                    for _ in range(self.config["arquivos_por_pasta"]):
                        if not self.is_running: break
                        
                        # Selecionar extensão
                        extensoes = self.config["extensoes_custom"] if self.config["extensoes_custom"] else EXTENSOES_PADRAO_DRY_RUN
                        ext = random.choice(extensoes)
                        if not ext.startswith("."): ext = "." + ext
                        
                        # Nome do arquivo baseado no padrão
                        nome = self._gerar_nome_arquivo(ext)
                        
                        # Destino (raiz da pasta ou subpasta)
                        destino = random.choice(subpastas) if self.config["distribuir"] else caminho_pasta
                        caminho_arquivo = os.path.join(destino, nome)
                        
                        conteudo = b""
                        is_av_test = False
                        if self.config["av_test"] and random.random() < 0.1: # 10% de chance para arquivos AV
                            conteudo = get_eicar_content()
                            nome = f"AV_TEST_{random.randint(100,999)}.com"
                            caminho_arquivo = os.path.join(destino, nome)
                            is_av_test = True
                        else:
                            # Tamanho do arquivo normal
                            tamanho = 1024 if self.config["limite_1kb"] else random.randint(1024, 1024 * 1024 * 2) # 1KB a 2MB
                            conteudo = generate_random_content(ext, tamanho)

                        # Verificar limite total de tamanho antes de submeter a tarefa
                        if self.config["limite_bytes"] and (self.total_gerado_bytes + len(conteudo) > self.config["limite_bytes"]):
                            self.progresso.emit("⛔ Limite de tamanho total atingido.")
                            self.is_running = False
                            break

                        if not self.config.get("dry_run", False):
                            future = executor.submit(create_file_on_disk, caminho_arquivo, conteudo, self.config["random_dates"])
                            futures_map[future] = (nome, caminho_arquivo, is_av_test)
                        else:
                            # No dry run, apenas simula a criação e atualiza o progresso
                            self.total_gerado_bytes += len(conteudo)
                            self.arquivos_criados += 1
                            self._update_progress_ui(nome, is_av_test)

                # Processar resultados das threads se não for dry run
                if not self.config.get("dry_run", False):
                    for future in as_completed(futures_map):
                        if not self.is_running: break
                        nome, caminho_arquivo, is_av_test = futures_map[future]
                        try:
                            bytes_written = future.result()
                            self.total_gerado_bytes += bytes_written
                            self.arquivos_criados += 1
                            self._update_progress_ui(nome, is_av_test)
                            if log_file: log_file.write(f"[{datetime.now()}] {'🛡️' if is_av_test else '📝'} Criado: {caminho_arquivo}\n")
                        except Exception as exc:
                            self.progresso.emit(f"❌ Erro ao criar arquivo {nome}: {exc}")

            if log_file:
                log_file.write(f"\n--- Fim da Geração: {datetime.now()} ---\n")
                log_file.write(f"Total de Pastas: {self.pastas_criadas}\n")
                log_file.write(f"Total de Arquivos: {self.arquivos_criados}\n")
                log_file.write(f"Tamanho Total: {self.total_gerado_bytes / (1024**2):.2f} MB\n")
                log_file.close()

        except Exception as e:
            self.progresso.emit(f"❌ Erro geral na geração: {str(e)}")
        finally:
            if log_file and not log_file.closed: log_file.close()
        
        tempo_total = time.time() - self.tempo_inicio
        resumo = {
            "pastas": self.pastas_criadas,
            "arquivos": self.arquivos_criados,
            "tamanho_mb": self.total_gerado_bytes / (1024**2),
            "tempo": tempo_total,
            "status": "Concluído" if self.is_running else "Interrompido",
            "dry_run": self.config.get("dry_run", False)
        }
        self.finalizado.emit(resumo)

    def _gerar_nome_arquivo(self, ext):
        padrao = self.config["padrao_nome"]
        if padrao == "Aleatório":
            return "".join(random.choices(string.ascii_lowercase + string.digits, k=8)) + ext
        elif padrao == "Sequencial":
            return f"arq_{self.arquivos_criados + 1:05d}{ext}"
        else: # Timestamp
            return datetime.now().strftime("%H%M%S_") + "".join(random.choices(string.digits, k=4)) + ext

    def _update_progress_ui(self, nome_arquivo, is_av_test):
        # Atualiza a UI a cada 10 arquivos ou se for um arquivo AV para feedback imediato
        if self.arquivos_criados % 10 == 0 or is_av_test:
            p = int((self.arquivos_criados / self.total_esperado_arquivos) * 100)
            status_text = f"Gerados: {self.arquivos_criados}/{self.total_esperado_arquivos} ({self.total_gerado_bytes / (1024**2):.2f} MB)"
            self.progresso.emit(f"{'🛡️' if is_av_test else '📝'} Criado: {nome_arquivo}")
            self.status_barra.emit(p, status_text)
