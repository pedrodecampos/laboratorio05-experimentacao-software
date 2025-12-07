#!/usr/bin/env python3
"""
Dashboard de visualização dos resultados do experimento.
Gera gráficos e tabelas comparando REST vs GraphQL.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
import glob
import json
from pathlib import Path

# Configuração de estilo
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')

def find_latest_results():
    """Encontra o arquivo de resultados mais recente."""
    csv_files = glob.glob(os.path.join(RESULTS_DIR, 'benchmark_results_*.csv'))
    
    if not csv_files:
        print("❌ Nenhum arquivo de resultados encontrado!")
        return None
    
    latest = max(csv_files, key=os.path.getmtime)
    return latest

def load_statistical_results():
    """Carrega resultados estatísticos se existirem."""
    stats_file = os.path.join(OUTPUT_DIR, 'statistical_results.json')
    if os.path.exists(stats_file):
        with open(stats_file, 'r') as f:
            return json.load(f)
    return None

def create_boxplot_time(df, output_file):
    """Cria boxplot comparando tempo de resposta."""
    df_success = df[df['success'] == True].copy()
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Boxplot geral
    ax1 = axes[0]
    data_to_plot = [
        df_success[df_success['api_type'] == 'REST']['response_time_ms'],
        df_success[df_success['api_type'] == 'GRAPHQL']['response_time_ms']
    ]
    bp = ax1.boxplot(data_to_plot, labels=['REST', 'GraphQL'], patch_artist=True)
    bp['boxes'][0].set_facecolor('#3498db')
    bp['boxes'][1].set_facecolor('#e74c3c')
    ax1.set_ylabel('Tempo de Resposta (ms)', fontsize=12)
    ax1.set_title('Tempo de Resposta - Comparação Geral', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Boxplot por cenário
    ax2 = axes[1]
    scenarios = sorted(df_success['scenario'].unique())
    rest_data = [df_success[(df_success['api_type'] == 'REST') & 
                            (df_success['scenario'] == s)]['response_time_ms'].values 
                 for s in scenarios]
    graphql_data = [df_success[(df_success['api_type'] == 'GRAPHQL') & 
                               (df_success['scenario'] == s)]['response_time_ms'].values 
                    for s in scenarios]
    
    positions_rest = np.arange(len(scenarios)) * 3 - 0.4
    positions_graphql = np.arange(len(scenarios)) * 3 + 0.4
    
    bp1 = ax2.boxplot(rest_data, positions=positions_rest, widths=0.6, 
                     patch_artist=True, labels=[f'C{i}' for i in scenarios])
    bp2 = ax2.boxplot(graphql_data, positions=positions_graphql, widths=0.6, 
                     patch_artist=True)
    
    for patch in bp1['boxes']:
        patch.set_facecolor('#3498db')
    for patch in bp2['boxes']:
        patch.set_facecolor('#e74c3c')
    
    ax2.set_xticks(np.arange(len(scenarios)) * 3)
    ax2.set_xticklabels([f'Cenário {s}' for s in scenarios])
    ax2.set_ylabel('Tempo de Resposta (ms)', fontsize=12)
    ax2.set_title('Tempo de Resposta por Cenário', fontsize=14, fontweight='bold')
    ax2.legend([bp1['boxes'][0], bp2['boxes'][0]], ['REST', 'GraphQL'], loc='upper right')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Gráfico salvo: {output_file}")

def create_boxplot_size(df, output_file):
    """Cria boxplot comparando tamanho da resposta."""
    df_success = df[df['success'] == True].copy()
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Boxplot geral
    ax1 = axes[0]
    data_to_plot = [
        df_success[df_success['api_type'] == 'REST']['response_size_bytes'],
        df_success[df_success['api_type'] == 'GRAPHQL']['response_size_bytes']
    ]
    bp = ax1.boxplot(data_to_plot, labels=['REST', 'GraphQL'], patch_artist=True)
    bp['boxes'][0].set_facecolor('#3498db')
    bp['boxes'][1].set_facecolor('#e74c3c')
    ax1.set_ylabel('Tamanho da Resposta (bytes)', fontsize=12)
    ax1.set_title('Tamanho da Resposta - Comparação Geral', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Boxplot por cenário
    ax2 = axes[1]
    scenarios = sorted(df_success['scenario'].unique())
    rest_data = [df_success[(df_success['api_type'] == 'REST') & 
                            (df_success['scenario'] == s)]['response_size_bytes'].values 
                 for s in scenarios]
    graphql_data = [df_success[(df_success['api_type'] == 'GRAPHQL') & 
                               (df_success['scenario'] == s)]['response_size_bytes'].values 
                    for s in scenarios]
    
    positions_rest = np.arange(len(scenarios)) * 3 - 0.4
    positions_graphql = np.arange(len(scenarios)) * 3 + 0.4
    
    bp1 = ax2.boxplot(rest_data, positions=positions_rest, widths=0.6, 
                     patch_artist=True, labels=[f'C{i}' for i in scenarios])
    bp2 = ax2.boxplot(graphql_data, positions=positions_graphql, widths=0.6, 
                     patch_artist=True)
    
    for patch in bp1['boxes']:
        patch.set_facecolor('#3498db')
    for patch in bp2['boxes']:
        patch.set_facecolor('#e74c3c')
    
    ax2.set_xticks(np.arange(len(scenarios)) * 3)
    ax2.set_xticklabels([f'Cenário {s}' for s in scenarios])
    ax2.set_ylabel('Tamanho da Resposta (bytes)', fontsize=12)
    ax2.set_title('Tamanho da Resposta por Cenário', fontsize=14, fontweight='bold')
    ax2.legend([bp1['boxes'][0], bp2['boxes'][0]], ['REST', 'GraphQL'], loc='upper right')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Gráfico salvo: {output_file}")

def create_bar_chart_comparison(df, output_file):
    """Cria gráfico de barras comparando médias."""
    df_success = df[df['success'] == True].copy()
    
    # Calcular médias por API e cenário
    summary = df_success.groupby(['api_type', 'scenario']).agg({
        'response_time_ms': 'mean',
        'response_size_bytes': 'mean'
    }).reset_index()
    
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    # Tempo de resposta
    ax1 = axes[0]
    scenarios = sorted(summary['scenario'].unique())
    rest_times = [summary[(summary['api_type'] == 'REST') & 
                          (summary['scenario'] == s)]['response_time_ms'].values[0] 
                  if len(summary[(summary['api_type'] == 'REST') & 
                                (summary['scenario'] == s)]) > 0 else 0 
                  for s in scenarios]
    graphql_times = [summary[(summary['api_type'] == 'GRAPHQL') & 
                            (summary['scenario'] == s)]['response_time_ms'].values[0] 
                     if len(summary[(summary['api_type'] == 'GRAPHQL') & 
                                   (summary['scenario'] == s)]) > 0 else 0 
                     for s in scenarios]
    
    x = np.arange(len(scenarios))
    width = 0.35
    
    ax1.bar(x - width/2, rest_times, width, label='REST', color='#3498db')
    ax1.bar(x + width/2, graphql_times, width, label='GraphQL', color='#e74c3c')
    ax1.set_xlabel('Cenário', fontsize=12)
    ax1.set_ylabel('Tempo Médio (ms)', fontsize=12)
    ax1.set_title('Tempo Médio de Resposta por Cenário', fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels([f'Cenário {s}' for s in scenarios])
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # Tamanho da resposta
    ax2 = axes[1]
    rest_sizes = [summary[(summary['api_type'] == 'REST') & 
                         (summary['scenario'] == s)]['response_size_bytes'].values[0] 
                  if len(summary[(summary['api_type'] == 'REST') & 
                                (summary['scenario'] == s)]) > 0 else 0 
                  for s in scenarios]
    graphql_sizes = [summary[(summary['api_type'] == 'GRAPHQL') & 
                            (summary['scenario'] == s)]['response_size_bytes'].values[0] 
                     if len(summary[(summary['api_type'] == 'GRAPHQL') & 
                                   (summary['scenario'] == s)]) > 0 else 0 
                     for s in scenarios]
    
    ax2.bar(x - width/2, rest_sizes, width, label='REST', color='#3498db')
    ax2.bar(x + width/2, graphql_sizes, width, label='GraphQL', color='#e74c3c')
    ax2.set_xlabel('Cenário', fontsize=12)
    ax2.set_ylabel('Tamanho Médio (bytes)', fontsize=12)
    ax2.set_title('Tamanho Médio da Resposta por Cenário', fontsize=14, fontweight='bold')
    ax2.set_xticks(x)
    ax2.set_xticklabels([f'Cenário {s}' for s in scenarios])
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Gráfico salvo: {output_file}")

def create_summary_table(df, output_file):
    """Cria tabela resumo dos resultados."""
    df_success = df[df['success'] == True].copy()
    
    summary = df_success.groupby(['api_type', 'scenario']).agg({
        'response_time_ms': ['mean', 'median', 'std', 'count'],
        'response_size_bytes': ['mean', 'median', 'std']
    }).round(2)
    
    # Salvar como CSV
    summary.to_csv(output_file)
    print(f"✅ Tabela salva: {output_file}")
    
    # Também criar uma versão mais legível
    readable_file = output_file.replace('.csv', '_readable.csv')
    summary_readable = df_success.groupby(['api_type', 'scenario']).agg({
        'response_time_ms': lambda x: f"{x.mean():.2f} ± {x.std():.2f}",
        'response_size_bytes': lambda x: f"{x.mean():.0f} ± {x.std():.0f}"
    })
    summary_readable.to_csv(readable_file)
    print(f"✅ Tabela legível salva: {readable_file}")

def main():
    """Função principal."""
    if len(sys.argv) > 1:
        results_file = sys.argv[1]
    else:
        results_file = find_latest_results()
    
    if not results_file:
        print("Execute primeiro: python scripts/benchmark.py")
        sys.exit(1)
    
    print(f"\nCarregando resultados de: {results_file}")
    
    try:
        df = pd.read_csv(results_file)
        print(f"✅ Arquivo carregado: {len(df)} registros")
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        sys.exit(1)
    
    # Criar gráficos
    print("\nGerando visualizações...")
    
    create_boxplot_time(df, os.path.join(OUTPUT_DIR, 'boxplot_tempo_resposta.png'))
    create_boxplot_size(df, os.path.join(OUTPUT_DIR, 'boxplot_tamanho_resposta.png'))
    create_bar_chart_comparison(df, os.path.join(OUTPUT_DIR, 'comparacao_medias.png'))
    create_summary_table(df, os.path.join(OUTPUT_DIR, 'tabela_resumo.csv'))
    
    print("\n" + "=" * 60)
    print("Dashboard gerado com sucesso!")
    print("=" * 60)
    print(f"\nArquivos gerados em: {OUTPUT_DIR}")
    print("  - boxplot_tempo_resposta.png")
    print("  - boxplot_tamanho_resposta.png")
    print("  - comparacao_medias.png")
    print("  - tabela_resumo.csv")

if __name__ == '__main__':
    main()

