#!/usr/bin/env python3
"""
Análise estatística completa dos resultados do experimento.
Realiza testes de hipóteses, calcula intervalos de confiança e gera relatório estatístico.
"""

import pandas as pd
import numpy as np
from scipy import stats
import os
import sys
import glob
import json
from pathlib import Path

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')

def find_latest_results():
    """Encontra o arquivo de resultados mais recente."""
    csv_files = glob.glob(os.path.join(RESULTS_DIR, 'benchmark_results_*.csv'))
    
    if not csv_files:
        print("❌ Nenhum arquivo de resultados encontrado!")
        print(f"   Execute primeiro: python scripts/benchmark.py")
        return None
    
    latest = max(csv_files, key=os.path.getmtime)
    return latest

def test_normality(data):
    """Testa normalidade usando Shapiro-Wilk."""
    if len(data) < 3:
        return None, None
    
    # Limitar a 5000 amostras (limite do Shapiro-Wilk)
    test_data = data[:5000] if len(data) > 5000 else data
    statistic, p_value = stats.shapiro(test_data)
    return statistic, p_value

def perform_statistical_tests(rest_data, graphql_data, metric_name):
    """
    Realiza testes estatísticos comparando REST vs GraphQL.
    
    Returns:
        dict com resultados dos testes
    """
    results = {
        'metric': metric_name,
        'rest_mean': np.mean(rest_data),
        'graphql_mean': np.mean(graphql_data),
        'rest_median': np.median(rest_data),
        'graphql_median': np.median(graphql_data),
        'rest_std': np.std(rest_data, ddof=1),
        'graphql_std': np.std(graphql_data, ddof=1),
        'rest_n': len(rest_data),
        'graphql_n': len(graphql_data)
    }
    
    # Teste de normalidade
    rest_shapiro_stat, rest_shapiro_p = test_normality(rest_data)
    graphql_shapiro_stat, graphql_shapiro_p = test_normality(graphql_data)
    
    results['rest_normal'] = rest_shapiro_p > 0.05 if rest_shapiro_p else False
    results['graphql_normal'] = graphql_shapiro_p > 0.05 if graphql_shapiro_p else False
    results['rest_shapiro_p'] = rest_shapiro_p
    results['graphql_shapiro_p'] = graphql_shapiro_p
    
    # Decidir qual teste usar
    both_normal = results['rest_normal'] and results['graphql_normal']
    
    if both_normal:
        # Teste t de Student (dados normais)
        t_stat, t_pvalue = stats.ttest_ind(rest_data, graphql_data, equal_var=False)
        results['test_type'] = 't-test (Welch)'
        results['test_statistic'] = t_stat
        results['p_value'] = t_pvalue
    else:
        # Teste de Mann-Whitney U (dados não normais)
        u_stat, u_pvalue = stats.mannwhitneyu(rest_data, graphql_data, alternative='two-sided')
        results['test_type'] = 'Mann-Whitney U'
        results['test_statistic'] = u_stat
        results['p_value'] = u_pvalue
    
    # Intervalo de confiança da diferença (bootstrap)
    differences = []
    n_bootstrap = 1000
    for _ in range(n_bootstrap):
        rest_sample = np.random.choice(rest_data, size=len(rest_data), replace=True)
        graphql_sample = np.random.choice(graphql_data, size=len(graphql_data), replace=True)
        diff = np.mean(graphql_sample) - np.mean(rest_sample)
        differences.append(diff)
    
    ci_lower = np.percentile(differences, 2.5)
    ci_upper = np.percentile(differences, 97.5)
    results['ci_lower'] = ci_lower
    results['ci_upper'] = ci_upper
    results['mean_difference'] = np.mean(graphql_data) - np.mean(rest_data)
    
    # Efeito (Cohen's d ou similar)
    pooled_std = np.sqrt((np.var(rest_data, ddof=1) + np.var(graphql_data, ddof=1)) / 2)
    if pooled_std > 0:
        cohens_d = (np.mean(graphql_data) - np.mean(rest_data)) / pooled_std
        results['effect_size'] = cohens_d
    else:
        results['effect_size'] = 0
    
    return results

def analyze_by_scenario(df):
    """Análise estatística por cenário."""
    scenario_results = {}
    
    for scenario in range(1, 7):
        rest_data = df[(df['api_type'] == 'REST') & 
                       (df['scenario'] == scenario) & 
                       (df['success'] == True)]['response_time_ms'].values
        graphql_data = df[(df['api_type'] == 'GRAPHQL') & 
                          (df['scenario'] == scenario) & 
                          (df['success'] == True)]['response_time_ms'].values
        
        if len(rest_data) > 0 and len(graphql_data) > 0:
            scenario_results[f'scenario_{scenario}_time'] = perform_statistical_tests(
                rest_data, graphql_data, 'response_time_ms'
            )
            
            # Tamanho da resposta
            rest_size = df[(df['api_type'] == 'REST') & 
                           (df['scenario'] == scenario) & 
                           (df['success'] == True)]['response_size_bytes'].values
            graphql_size = df[(df['api_type'] == 'GRAPHQL') & 
                              (df['scenario'] == scenario) & 
                              (df['success'] == True)]['response_size_bytes'].values
            
            scenario_results[f'scenario_{scenario}_size'] = perform_statistical_tests(
                rest_size, graphql_size, 'response_size_bytes'
            )
    
    return scenario_results

def analyze_overall(df):
    """Análise estatística geral (todos os cenários combinados)."""
    rest_time = df[(df['api_type'] == 'REST') & (df['success'] == True)]['response_time_ms'].values
    graphql_time = df[(df['api_type'] == 'GRAPHQL') & (df['success'] == True)]['response_time_ms'].values
    
    rest_size = df[(df['api_type'] == 'REST') & (df['success'] == True)]['response_size_bytes'].values
    graphql_size = df[(df['api_type'] == 'GRAPHQL') & (df['success'] == True)]['response_size_bytes'].values
    
    results = {
        'overall_time': perform_statistical_tests(rest_time, graphql_time, 'response_time_ms'),
        'overall_size': perform_statistical_tests(rest_size, graphql_size, 'response_size_bytes')
    }
    
    return results

def print_results(overall_results, scenario_results):
    """Imprime resultados formatados."""
    print("\n" + "=" * 80)
    print("ANÁLISE ESTATÍSTICA - RESULTADOS GERAIS")
    print("=" * 80)
    
    # RQ1: Tempo de Resposta
    print("\n--- RQ1: Tempo de Resposta (ms) ---")
    rq1 = overall_results['overall_time']
    print(f"REST:    Média = {rq1['rest_mean']:.2f} ms, Mediana = {rq1['rest_median']:.2f} ms, DP = {rq1['rest_std']:.2f} ms")
    print(f"GraphQL: Média = {rq1['graphql_mean']:.2f} ms, Mediana = {rq1['graphql_median']:.2f} ms, DP = {rq1['graphql_std']:.2f} ms")
    print(f"\nDiferença média: {rq1['mean_difference']:.2f} ms (GraphQL - REST)")
    print(f"Intervalo de confiança 95%: [{rq1['ci_lower']:.2f}, {rq1['ci_upper']:.2f}] ms")
    print(f"Tamanho do efeito (Cohen's d): {rq1['effect_size']:.3f}")
    print(f"\nTeste: {rq1['test_type']}")
    print(f"Estatística: {rq1['test_statistic']:.4f}")
    print(f"p-valor: {rq1['p_value']:.6f}")
    
    if rq1['p_value'] < 0.05:
        if rq1['mean_difference'] < 0:
            print("✅ Rejeita H₀: GraphQL é significativamente mais rápido que REST")
        else:
            print("✅ Rejeita H₀: REST é significativamente mais rápido que GraphQL")
    else:
        print("❌ Não rejeita H₀: Não há diferença estatisticamente significativa")
    
    # RQ2: Tamanho da Resposta
    print("\n--- RQ2: Tamanho da Resposta (bytes) ---")
    rq2 = overall_results['overall_size']
    print(f"REST:    Média = {rq2['rest_mean']:.0f} bytes, Mediana = {rq2['rest_median']:.0f} bytes, DP = {rq2['rest_std']:.0f} bytes")
    print(f"GraphQL: Média = {rq2['graphql_mean']:.0f} bytes, Mediana = {rq2['graphql_median']:.0f} bytes, DP = {rq2['graphql_std']:.0f} bytes")
    print(f"\nDiferença média: {rq2['mean_difference']:.0f} bytes (GraphQL - REST)")
    print(f"Intervalo de confiança 95%: [{rq2['ci_lower']:.0f}, {rq2['ci_upper']:.0f}] bytes")
    print(f"Tamanho do efeito (Cohen's d): {rq2['effect_size']:.3f}")
    print(f"\nTeste: {rq2['test_type']}")
    print(f"Estatística: {rq2['test_statistic']:.4f}")
    print(f"p-valor: {rq2['p_value']:.6f}")
    
    if rq2['p_value'] < 0.05:
        if rq2['mean_difference'] < 0:
            print("✅ Rejeita H₀: GraphQL tem tamanho significativamente menor que REST")
        else:
            print("✅ Rejeita H₀: REST tem tamanho significativamente menor que GraphQL")
    else:
        print("❌ Não rejeita H₀: Não há diferença estatisticamente significativa")
    
    # Análise por cenário
    print("\n" + "=" * 80)
    print("ANÁLISE POR CENÁRIO")
    print("=" * 80)
    
    for scenario in range(1, 7):
        print(f"\n--- Cenário {scenario} ---")
        
        time_key = f'scenario_{scenario}_time'
        size_key = f'scenario_{scenario}_size'
        
        if time_key in scenario_results:
            rq1_scenario = scenario_results[time_key]
            print(f"Tempo: REST={rq1_scenario['rest_mean']:.2f}ms, GraphQL={rq1_scenario['graphql_mean']:.2f}ms, "
                  f"Diferença={rq1_scenario['mean_difference']:.2f}ms, p={rq1_scenario['p_value']:.4f}")
        
        if size_key in scenario_results:
            rq2_scenario = scenario_results[size_key]
            print(f"Tamanho: REST={rq2_scenario['rest_mean']:.0f}B, GraphQL={rq2_scenario['graphql_mean']:.0f}B, "
                  f"Diferença={rq2_scenario['mean_difference']:.0f}B, p={rq2_scenario['p_value']:.4f}")

def save_results(overall_results, scenario_results, output_file):
    """Salva resultados em JSON."""
    all_results = {
        'overall': overall_results,
        'by_scenario': scenario_results
    }
    
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print(f"\n✅ Resultados salvos em: {output_file}")

def main():
    """Função principal."""
    if len(sys.argv) > 1:
        results_file = sys.argv[1]
    else:
        results_file = find_latest_results()
    
    if not results_file:
        sys.exit(1)
    
    print(f"\nCarregando resultados de: {results_file}")
    
    try:
        df = pd.read_csv(results_file)
        print(f"✅ Arquivo carregado: {len(df)} registros")
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        sys.exit(1)
    
    # Filtrar apenas sucessos
    df_success = df[df['success'] == True].copy()
    print(f"✅ Requisições bem-sucedidas: {len(df_success)}")
    
    # Análise geral
    print("\nRealizando análise estatística geral...")
    overall_results = analyze_overall(df_success)
    
    # Análise por cenário
    print("Realizando análise por cenário...")
    scenario_results = analyze_by_scenario(df_success)
    
    # Imprimir resultados
    print_results(overall_results, scenario_results)
    
    # Salvar resultados
    output_file = os.path.join(OUTPUT_DIR, 'statistical_results.json')
    save_results(overall_results, scenario_results, output_file)
    
    print("\n" + "=" * 80)
    print("Análise estatística concluída!")
    print("=" * 80)

if __name__ == '__main__':
    main()

