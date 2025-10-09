import pandas as pd

def analisar_dataset_prognostico(caminho_do_arquivo):
    """
    Realiza uma análise exploratória inicial em um dataset de prognóstico/sintomas.

    Args:
        caminho_do_arquivo (str): O caminho para o arquivo CSV.
    """
    
    print(f"--- Lendo o arquivo: {caminho_do_arquivo} ---\n")
    
    try:
        # 1. Lê o arquivo
        # O snippet sugere que o separador é uma vírgula (padrão)
        df = pd.read_csv(caminho_do_arquivo)
    except FileNotFoundError:
        print(f"ERRO: Arquivo não encontrado no caminho: {caminho_do_arquivo}")
        return
    except Exception as e:
        print(f"ERRO ao ler o arquivo: {e}")
        return

    # 2. Exibe as primeiras 5 linhas
    print("### 1. Primeiras 5 Linhas do Dataset:\n")
    print(df.head())
    
    print("\n" + "="*50 + "\n")

    # 3. Exibe um resumo das informações (tipos e valores nulos)
    print("### 2. Informações do Dataset (Tipos de Dados e Não-Nulos):\n")
    df.info()

    print("\n" + "="*50 + "\n")

    # 4. Análise da coluna 'Prognóstico' (Distribuição da Classe Alvo)
    if 'Prognóstico' in df.columns:
        print("### 3. Distribuição da Coluna 'Prognóstico':\n")
        contagem = df['Prognóstico'].value_counts()
        print(contagem)
        
        # Opcional: Mostrar a porcentagem para entender o balanceamento
        print("\n--- Porcentagem de cada Prognóstico (para balanceamento) ---\n")
        porcentagem = df['Prognóstico'].value_counts(normalize=True) * 100
        print(porcentagem.round(2).astype(str) + '%')
        
    else:
        print("AVISO: Coluna 'Prognóstico' não encontrada.")


def analisar_sintomas_por_prognostico(caminho_do_arquivo):
    """
    Realiza uma análise exploratória de dados, focando na frequência dos sintomas
    para cada tipo de prognóstico (doença).
    """
    
    print(f"--- Lendo e Analisando o arquivo: {caminho_do_arquivo} ---\n")
    
    try:
        df = pd.read_csv(caminho_do_arquivo)
    except FileNotFoundError:
        print(f"ERRO: Arquivo não encontrado no caminho: {caminho_do_arquivo}")
        return
    except Exception as e:
        print(f"ERRO ao ler o arquivo: {e}")
        return

    # 1. Informações básicas (mantido da análise anterior)
    print("### 1. Estrutura e Primeiras Linhas do Dataset:\n")
    print(df.head())
    print("\nTotal de linhas:", len(df))
    
    print("\n" + "="*70 + "\n")

    # 2. Análise dos Sintomas por Prognóstico
    if 'Prognóstico' in df.columns:
        print("### 2. Análise da Frequência dos Sintomas por Doença:\n")
        
        # Cria uma cópia do DataFrame, removendo a coluna 'Prognóstico' 
        # para que apenas os sintomas (0s e 1s) sejam somados.
        sintomas_df = df.drop(columns=['Prognóstico'], errors='ignore')
        
        # Agrupa os dados pela coluna 'Prognóstico' e soma os valores.
        # O resultado é a contagem de vezes que cada sintoma ocorreu
        # para cada uma das doenças.
        analise_agrupada = df.groupby('Prognóstico').sum()
        
        # Exibe o resultado
        print("Soma total de ocorrências de cada sintoma por doença:\n")
        print(analise_agrupada)
        
        print("\n" + "="*70 + "\n")
        
        # 3. Análise da Coluna Alvo ('Prognóstico')
        print("### 3. Distribuição da Coluna 'Prognóstico' (Balanceamento):\n")
        contagem = df['Prognóstico'].value_counts()
        print(contagem)
        
    else:
        print("AVISO: Coluna 'Prognóstico' não encontrada. Verifique o cabeçalho.")



# Define a variável global para armazenar a matriz de frequências.
# Isso evita recalcular a matriz toda vez que a função 'diagnosticar' é chamada.
MATRIZ_FREQUENCIA = None

def preprocessar_dataset(caminho_do_arquivo):
    """
    Lê o dataset e calcula a matriz de frequência de sintomas por prognóstico.
    """
    global MATRIZ_FREQUENCIA
    
    try:
        df = pd.read_csv(caminho_do_arquivo)
    except Exception as e:
        print(f"ERRO ao ler o arquivo para pré-processamento: {e}")
        return None

    # Certifica-se de que a coluna 'Prognóstico' existe
    if 'Prognóstico' not in df.columns:
        print("ERRO: Coluna 'Prognóstico' não encontrada.")
        return None

    # Agrupa e soma: Total de ocorrências de cada sintoma por doença
    MATRIZ_FREQUENCIA = df.groupby('Prognóstico').sum()
    print("Pré-processamento concluído. Matriz de Frequência de Sintomas calculada.")
    
    return MATRIZ_FREQUENCIA


def diagnosticar_doenca(sintomas_do_paciente):
    """
    Recebe uma lista de sintomas e retorna o ranking das possíveis doenças.

    Args:
        sintomas_do_paciente (list): Lista de strings com os sintomas informados.
    
    Returns:
        pd.Series: Ranking de doenças possíveis por pontuação de correspondência.
    """
    global MATRIZ_FREQUENCIA
    
    if MATRIZ_FREQUENCIA is None:
        print("ERRO: A matriz de frequência não foi carregada. Execute 'preprocessar_dataset(caminho)' primeiro.")
        return pd.Series()

    # 1. Filtra os sintomas: remove sintomas inválidos (que não estão nas colunas)
    sintomas_validos = [
        sintoma for sintoma in sintomas_do_paciente 
        if sintoma in MATRIZ_FREQUENCIA.columns
    ]

    if not sintomas_validos:
        print("Nenhum sintoma válido encontrado no dataset. Por favor, verifique a grafia.")
        return pd.Series()
    
    print(f"\n--- Diagnóstico para {len(sintomas_validos)} Sintoma(s) Válido(s) ---")
    print(f"Sintomas analisados: {', '.join(sintomas_validos)}")


    # 2. Calcula a Pontuação de Correspondência (Score)
    # A pontuação é a soma da frequência dos sintomas presentes para cada doença.
    # Ex: Se o paciente tem 'Coceira' e 'Tremores':
    # - Doença A: (Frequência de Coceira em A) + (Frequência de Tremores em A)
    # - Doença B: (Frequência de Coceira em B) + (Frequência de Tremores em B)
    
    ranking_de_probabilidade = MATRIZ_FREQUENCIA[sintomas_validos].sum(axis=1)

    # 3. Ordena e Exibe o Resultado
    # Ordena da maior pontuação (mais provável) para a menor
    ranking_ordenado = ranking_de_probabilidade.sort_values(ascending=False)

    return ranking_ordenado



# --- Execução da Função com o seu arquivo ---
caminho = 'files/SymbiPredict2022.pt-br.csv'

# Análise Exploratória Inicial
#analisar_dataset_prognostico(caminho)

#analisar_sintomas_por_prognostico(caminho)


# 1. Pré-processamento (Executar APENAS uma vez)
# Isso prepara a base de dados para o diagnóstico
preprocessar_dataset(caminho)

# 2. Teste o Diagnóstico

# Exemplo 1: Sintomas de 'Infecção Fúngica'
sintomas_exemplo_1 = ['Coceira', 'Erupção cutânea', 'Erupções cutâneas nodais']
ranking_1 = diagnosticar_doenca(sintomas_exemplo_1)

print("\n\n--- Ranking de Doenças para o Exemplo 1 ---")
print(ranking_1.head()) # Exibe as 5 doenças com maior score

# Exemplo 2: Sintomas de 'Alergia'
sintomas_exemplo_2 = ['Espirros contínuos', 'Tremores', 'Calafrios']
ranking_2 = diagnosticar_doenca(sintomas_exemplo_2)

print("\n\n--- Ranking de Doenças para o Exemplo 2 ---")
print(ranking_2.head()) # Exibe as 5 doenças com maior score
