import pandas as pd
from pysus.online_data.SIAB import download
from pathlib import Path

# ============================================
# CONFIGURAÇÕES
# ============================================

UF = "DF"
ANO = 2023

PASTA_BRUTA = Path("dados_brutos")
PASTA_TRATADA = Path("dados_tratados")

PASTA_BRUTA.mkdir(exist_ok=True)
PASTA_TRATADA.mkdir(exist_ok=True)

# ============================================
# DOWNLOAD
# ============================================

print(f"Baixando dados SIAB {UF} {ANO}...")

try:

    df = download(UF, ANO)

    print("Download concluído.")

except Exception as e:

    print(f"Erro no download: {e}")

    raise

# ============================================
# LIMPEZA
# ============================================

print("Tratando dados...")

df.columns = [
    col.strip()
    for col in df.columns
]

# ============================================
# SALVAR BRUTO
# ============================================

arquivo_bruto = (
    PASTA_BRUTA /
    f"siab_{UF}_{ANO}.csv"
)

df.to_csv(
    arquivo_bruto,
    index=False,
    encoding="utf-8-sig"
)

print(f"Arquivo salvo: {arquivo_bruto}")

# ============================================
# EXEMPLO DE TRATAMENTO
# ============================================

df_tratado = df.copy()

# remover colunas totalmente vazias
df_tratado = df_tratado.dropna(
    axis=1,
    how='all'
)

# ============================================
# SALVAR TRATADO
# ============================================

arquivo_tratado = (
    PASTA_TRATADA /
    f"siab_tratado_{UF}_{ANO}.csv"
)

df_tratado.to_csv(
    arquivo_tratado,
    index=False,
    encoding="utf-8-sig"
)

print(f"Tratado salvo: {arquivo_tratado}")

print("Processo finalizado.")