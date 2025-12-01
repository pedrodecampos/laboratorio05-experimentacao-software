#!/usr/bin/env python3
"""
Script para análise inicial dos resultados do benchmark.
Valida os dados coletados e gera estatísticas descritivas.
"""

import pandas as pd
import numpy as np
import os
import sys
import glob
from pathlib import Path

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')

def find_latest_results():
    """Encontra o arquivo de resultados mais recente."""
    csv_files = glob.glob(os.path.join(RESULTS_DIR, 'benchmark_results_*.csv'))
    
    if not csv_files:
        print("❌ Nenhum arquivo de resultados encontrado!")
        print(f"   Procurando em: {RESULTS_DIR}")
        return None
    
    # Retornar o arquivo mais recente
    latest = max(csv_files, key=os.path.getmtime)
    return latest

def validate_data(df: pd.DataFrame) -> bool:
    """Valida os dados coletados."""
    print("=" * 60)
    print("Validação dos Dados")
    print("=" * 60)
    
    issues = []
    
    # Verificar colunas necessárias
    required_columns = ['api_type', 'scenario', 'replication', 
                       'response_time_ms', 'response_size_bytes', 'success']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        issues.append(f"Colunas faltando: {missing_columns}")
    
    # Verificar número esperado de linhas
    expected_rows = 2 * 6 * 30  # 2 APIs × 6 cenários × 30 replicações
    if len(df) != expected_rows:
        issues.append(f"Número de linhas esperado: {expected_rows}, encontrado: {len(df)}")
    
    # Verificar valores faltantes
    missing_values = df[required_columns].isnull().sum()
    if missing_values.any():
        issues.append(f"Valores faltantes:\n{missing_values[missing_values > 0]}")
    
    # Verificar taxa de sucesso
    success_rate = df['success'].mean()
    if success_rate < 0.95:
        issues.append(f"Taxa de sucesso baixa: {success_rate*100:.1f}%")
    
    # Verificar valores negativos ou inválidos
    if (df['response_time_ms'] < 0).any():
        issues.append("Encontrados tempos de resposta negativos!")
    
    if (df['response_size_bytes'] < 0).any():
        issues.append("Encontrados tamanhos de resposta negativos!")
    
    # Verificar outliers extremos
    time_q99 = df['response_time_ms'].quantile(0.99)
    time_max = df['response_time_ms'].max()
    if time_max > time_q99 * 5:
        issues.append(f"Possível outlier em tempo de resposta: {time_max:.2f}ms")
    
    # Reportar resultados
    if issues:
        print("\n⚠️  PROBLEMAS ENCONTRADOS:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        return False
    else:
        print("\n✅ Validação passou! Dados parecem consistentes.")
        return True

def descriptive_statistics(df: pd.DataFrame):
    """Gera estatísticas descritivas por API e cenário."""
    print("\n" + "=" * 60)
    print("Estatísticas Descritivas")
    print("=" * 60)
    
    # Filtrar apenas sucessos
    df_success = df[df['success'] == True].copy()
    
    if len(df_success) == 0:
        print("❌ Nenhum resultado bem-sucedido para analisar!")
        return
    
    # Estatísticas por API
    print("\n--- Por Tipo de API ---")
    stats_by_api = df_success.groupby('api_type').agg({
        'response_time_ms': ['count', 'mean', 'median', 'std', 'min', 'max'],
        'response_size_bytes': ['mean', 'median', 'std', 'min', 'max']
    })
    
    print("\nTempo de Resposta (ms):")
    print(stats_by_api['response_time_ms'])
    print("\nTamanho da Resposta (bytes):")
    print(stats_by_api['response_size_bytes'])
    
    # Estatísticas por API e Cenário
    print("\n--- Por API e Cenário ---")
    stats_by_scenario = df_success.groupby(['api_type', 'scenario']).agg({
        'response_time_ms': ['mean', 'median', 'std'],
        'response_size_bytes': ['mean', 'median', 'std']
    })
    
    print("\nEstatísticas detalhadas:")
    print(stats_by_scenario)
    
    # Comparação REST vs GraphQL por cenário
    print("\n--- Comparação REST vs GraphQL (por Cenário) ---")
    for scenario in range(1, 7):
        rest_data = df_success[(df_success['api_type'] == 'REST') & 
                               (df_success['scenario'] == scenario)]
        graphql_data = df_success[(df_success['api_type'] == 'GRAPHQL') & 
                                 (df_success['scenario'] == scenario)]
        
        if len(rest_data) > 0 and len(graphql_data) > 0:
            rest_time_mean = rest_data['response_time_ms'].mean()
            graphql_time_mean = graphql_data['response_time_ms'].mean()
            rest_size_mean = rest_data['response_size_bytes'].mean()
            graphql_size_mean = graphql_data['response_size_bytes'].mean()
            
            time_diff = ((graphql_time_mean - rest_time_mean) / rest_time_mean) * 100
            size_diff = ((graphql_size_mean - rest_size_mean) / rest_size_mean) * 100
            
            print(f"\nCenário {scenario}:")
            print(f"  Tempo (ms):")
            print(f"    REST:    {rest_time_mean:.2f}")
            print(f"    GraphQL: {graphql_time_mean:.2f}")
            print(f"    Diferença: {time_diff:+.1f}%")
            print(f"  Tamanho (bytes):")
            print(f"    REST:    {rest_size_mean:.0f}")
            print(f"    GraphQL: {graphql_size_mean:.0f}")
            print(f"    Diferença: {size_diff:+.1f}%")

def check_outliers(df: pd.DataFrame):
    """Identifica possíveis outliers nos dados."""
    print("\n" + "=" * 60)
    print("Análise de Outliers")
    print("=" * 60)
    
    df_success = df[df['success'] == True].copy()
    
    if len(df_success) == 0:
        return
    
    # Usar IQR para identificar outliers
    for api_type in ['REST', 'GRAPHQL']:
        for metric in ['response_time_ms', 'response_size_bytes']:
            data = df_success[(df_success['api_type'] == api_type)][metric]
            
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = data[(data < lower_bound) | (data > upper_bound)]
            
            if len(outliers) > 0:
                print(f"\n{api_type} - {metric}:")
                print(f"  Outliers encontrados: {len(outliers)}")
                print(f"  Limites: [{lower_bound:.2f}, {upper_bound:.2f}]")
                print(f"  Valores: {outliers.tolist()[:5]}")  # Mostrar apenas os 5 primeiros

def main():
    """Função principal."""
    if len(sys.argv) > 1:
        results_file = sys.argv[1]
    else:
        results_file = find_latest_results()
    
    if not results_file:
        print("\nUso: python analyze_results.py [caminho_do_arquivo.csv]")
        sys.exit(1)
    
    print(f"\nLendo resultados de: {results_file}")
    
    try:
        df = pd.read_csv(results_file)
        print(f"✅ Arquivo carregado: {len(df)} registros")
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        sys.exit(1)
    
    # Validar dados
    is_valid = validate_data(df)
    
    # Estatísticas descritivas
    descriptive_statistics(df)
    
    # Verificar outliers
    check_outliers(df)
    
    print("\n" + "=" * 60)
    print("Análise concluída!")
    print("=" * 60)
    print(f"\nPróximos passos:")
    print("  1. Revisar outliers e decidir se devem ser removidos")
    print("  2. Realizar testes estatísticos (teste t, Mann-Whitney)")
    print("  3. Calcular intervalos de confiança")
    print("  4. Gerar visualizações (Sprint 2)")

if __name__ == '__main__':
    main()

