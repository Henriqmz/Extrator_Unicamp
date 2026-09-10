import os
import sys
import tempfile
import pytest

# Adicionar caminhos ao sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from extractor import validar_e_abrir_pdf, extrair_pdf
from processor import (
    detectar_edital_ano,
    detectar_metadados_gabarito,
    validar_compatibilidade_prova_gabarito,
)

PDF_2025_PATH = os.path.join(
    BASE_DIR, "Provas", "2-provas-e-gabaritos-unicamp-2025", "provas-e-gabaritos-unicamp-2025",
    "provas-e-gabaritos-unicamp-vestibular-2025", "1-fase-provas-gabaritos-unicamp-vestibular-2025",
    "prova-q-z-1-fase-unicamp-2025.pdf"
)

GABARITO_2025_PATH = os.path.join(
    BASE_DIR, "Provas", "2-provas-e-gabaritos-unicamp-2025", "provas-e-gabaritos-unicamp-2025",
    "provas-e-gabaritos-unicamp-vestibular-2025", "1-fase-provas-gabaritos-unicamp-vestibular-2025",
    "gabarito-q-z-1-fase-unicamp-2025.pdf"
)

GABARITO_2023_PATH = os.path.join(
    BASE_DIR, "Provas", "1-provas-e-gabaritos-unicamp-2023", "provas-gabaritos-vestibular-unicamp-2023",
    "1º Fase", "gabaritos-1-fase-vestibular-2023-unicamp.pdf"
)


def test_problema_1_detectar_ano_2025_caminho_real():
    """Problema 1: Garante que a prova de 2025 é detectada como 2025 (e não 2026)."""
    assert os.path.exists(PDF_2025_PATH), f"Arquivo não encontrado: {PDF_2025_PATH}"
    edital, ano, tipo = detectar_edital_ano(PDF_2025_PATH)
    assert edital == "unicamp"
    assert ano == 2025, f"Esperado 2025, obteve {ano}"
    assert tipo == "Q-Z", f"Esperado Q-Z, obteve {tipo}"


def test_problema_1_detectar_ano_2025_nome_generico_ou_upload():
    """Problema 1: Garante que mesmo com nome genérico (como upload da API 'tmp_xyz.pdf' ou 'prova.pdf'), o ano 2025 é lido da capa do PDF."""
    edital, ano, tipo = detectar_edital_ano(PDF_2025_PATH, nome_original="prova.pdf")
    assert edital == "unicamp"
    assert ano == 2025, f"Esperado 2025 via capa do PDF, obteve {ano}"
    assert tipo == "Q-Z", f"Esperado Q-Z via capa do PDF, obteve {tipo}"


def test_problema_2_pasta_saida_nao_colide_com_2026():
    """Problema 2: Garante que a pasta de saída é 'unicamp_2025' e os arquivos têm prefixo 2025."""
    edital, ano, tipo = detectar_edital_ano(PDF_2025_PATH)
    pasta_saida = f"{edital}_{ano}"
    assert pasta_saida == "unicamp_2025"
    assert pasta_saida != "unicamp_2026"


def test_problema_3_verificacao_anos_diferentes_prova_gabarito():
    """Problema 3: Garante que prova de 2025 com gabarito de 2023 dispara erro de incompatibilidade."""
    _, ano_prova, _ = detectar_edital_ano(PDF_2025_PATH)
    _, ano_gabarito, _ = detectar_metadados_gabarito(GABARITO_2023_PATH)

    assert ano_prova == 2025
    assert ano_gabarito == 2023

    with pytest.raises(ValueError) as exc_info:
        validar_compatibilidade_prova_gabarito(ano_prova, ano_gabarito)
    assert "Incompatibilidade detectada" in str(exc_info.value)
    assert "2025" in str(exc_info.value)
    assert "2023" in str(exc_info.value)


def test_problema_3_verificacao_anos_iguais_prova_gabarito():
    """Problema 3: Garante que prova de 2025 com gabarito de 2025 é aceita sem erro."""
    _, ano_prova, _ = detectar_edital_ano(PDF_2025_PATH)
    _, ano_gabarito, _ = detectar_metadados_gabarito(GABARITO_2025_PATH)

    assert ano_prova == 2025
    assert ano_gabarito == 2025
    # Não deve lançar exceção
    validar_compatibilidade_prova_gabarito(ano_prova, ano_gabarito)


def test_problema_4_rejeitar_arquivo_inexistente():
    """Problema 4: Arquivo inexistente deve lançar FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        validar_e_abrir_pdf("caminho_inexistente_12345.pdf")


def test_problema_4_rejeitar_pdf_vazio():
    """Problema 4: Arquivo de 0 bytes deve ser rejeitado com ValueError claro."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        path = f.name

    try:
        with pytest.raises(ValueError) as exc_info:
            validar_e_abrir_pdf(path)
        assert "vazio ou corrompido (0 bytes)" in str(exc_info.value)
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_problema_4_rejeitar_arquivo_nao_pdf():
    """Problema 4: Arquivo que não é PDF (sem cabeçalho %PDF-) deve ser rejeitado."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"Conteudo de texto simples que nao eh PDF")
        path = f.name

    try:
        with pytest.raises(ValueError) as exc_info:
            validar_e_abrir_pdf(path)
        assert "cabeçalho '%PDF-' ausente" in str(exc_info.value)
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_problema_4_rejeitar_pdf_corrompido():
    """Problema 4: Arquivo com cabeçalho PDF mas bytes corrompidos/truncados deve ser rejeitado."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        f.write(b"%PDF-1.4\nbytes_completamente_corrompidos_sem_xref_nem_trailer")
        path = f.name

    try:
        with pytest.raises(ValueError) as exc_info:
            validar_e_abrir_pdf(path)
        assert "corrompido" in str(exc_info.value)
    finally:
        import gc
        gc.collect()
        if os.path.exists(path):
            try:
                os.unlink(path)
            except Exception:
                pass
