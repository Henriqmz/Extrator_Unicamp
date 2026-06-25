import os
import json
import re

def auditar_pasta(nome_pasta, num_questoes_esperado=72):
    print(f"\n==========================================")
    print(f"AUDITANDO PASTA: {nome_pasta}")
    print(f"==========================================")
    
    if not os.path.exists(nome_pasta):
        print(f"Erro: Pasta {nome_pasta} não existe.")
        return

    jsons = [f for f in os.listdir(nome_pasta) if f.endswith('.json') and '_COMP_' not in f]
    print(f"Total de arquivos JSON encontrados (excluindo textos compartilhados): {len(jsons)} (Esperado: {num_questoes_esperado})")
    
    anomalias = []
    questoes_com_imagens = []
    
    # Ordenar por número
    def extrair_numero(nome):
        match = re.search(r'_(\d+)\.json$', nome)
        return int(match.group(1)) if match else 0
        
    jsons.sort(key=extrair_numero)
    
    for nome_arq in jsons:
        caminho = os.path.join(nome_pasta, nome_arq)
        num = extrair_numero(nome_arq)
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                dados = json.load(f)
        except Exception as e:
            anomalias.append(f"Q{num}: Erro ao ler JSON: {e}")
            continue
            
        enunciado = dados.get('conteudo', {}).get('enunciado', '')
        alternativas = dados.get('alternativas', {})
        url_img_enunciado = dados.get('conteudo', {}).get('url_img', [])
        
        # 1. Verificar enunciado vazio ou muito curto
        if not enunciado or len(enunciado.strip()) < 10:
            anomalias.append(f"Q{num}: Enunciado vazio ou muito curto: '{enunciado}'")
            
        # 2. Verificar alternativas
        letras_verificar = ['a', 'b', 'c', 'd']
        if 'e' in alternativas and alternativas['e'] is not None:
            letras_verificar.append('e')
            
        alternativa_correta_marcada = False
        
        for letra in letras_verificar:
            alt_info = alternativas.get(letra, {})
            if not alt_info:
                anomalias.append(f"Q{num}: Alternativa {letra} ausente ou vazia.")
                continue
                
            texto = alt_info.get('texto', '') or ''
            url_img_alt = alt_info.get('url_img', [])
            correta = alt_info.get('correta', False)
            
            if correta:
                alternativa_correta_marcada = True
                
            # Verificar texto vazio se não houver imagem
            if not texto.strip() and not url_img_alt:
                anomalias.append(f"Q{num}: Alternativa {letra} completamente vazia (sem texto e sem imagem).")
                
            # Verificar contaminações comuns
            for outra_letra in letras_verificar:
                if outra_letra != letra and re.search(rf'\b{outra_letra}\s*\)', texto):
                    anomalias.append(f"Q{num}: Alternativa {letra} contém referência indevida '{outra_letra})' no texto: '{texto[:40]}...'")
            
            # Verificar número de página ou ruído comum
            if re.search(r'\n\d+\s*$', texto.strip()):
                anomalias.append(f"Q{num}: Alternativa {letra} termina com número de página suspeito: '{texto[-20:]}'")
                
            if "Nas questões de" in texto or "sempre que necessário" in texto:
                anomalias.append(f"Q{num}: Alternativa {letra} contêm instrução do caderno: '{texto[:40]}...'")
                
            if url_img_alt:
                questoes_com_imagens.append((num, f"alt {letra}", url_img_alt))
                
        # Verificar se gabarito foi aplicado
        if not alternativa_correta_marcada:
            anomalias.append(f"Q{num}: Nenhuma alternativa marcada como correta (gabarito ausente ou anulado).")
            
        if url_img_enunciado:
            questoes_com_imagens.append((num, "enunciado", url_img_enunciado))

    # Relatório de anomalias
    if anomalias:
        print("\nAnomalias encontradas:")
        for anom in anomalias:
            print(f"  - {anom}")
    else:
        print("\nNenhuma anomalia estrutural detectada nos JSONs!")
        
    # Relatório de Imagens
    if questoes_com_imagens:
        print("\nDistribuição de Imagens mapeadas:")
        for q, local, imgs in questoes_com_imagens:
            print(f"  - Q{q:02d} ({local}): {imgs}")
    else:
        print("\nNenhuma imagem mapeada nas questões.")

# Executar nas pastas pendentes
if __name__ == '__main__':
    pastas = [
        "unicamp_2022_test_Q-X",
        "unicamp_2024_test_Q-Y",
        "unicamp_2025_test_Q-Z",
        "unicamp_2026_test_Q-X"
    ]
    for p in pastas:
        if os.path.exists(p):
            auditar_pasta(p)
        else:
            caminho_abs = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", p)
            if os.path.exists(caminho_abs):
                auditar_pasta(caminho_abs)
            else:
                print(f"Pasta {p} não encontrada.")
