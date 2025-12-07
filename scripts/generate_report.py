#!/usr/bin/env python3
"""
Gera relatório final do experimento com base nos resultados coletados.
"""

import pandas as pd
import json
import os
import sys
import glob
from datetime import datetime

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')

def find_latest_results():
    """Encontra o arquivo de resultados mais recente."""
    csv_files = glob.glob(os.path.join(RESULTS_DIR, 'benchmark_results_*.csv'))
    if not csv_files:
        return None
    return max(csv_files, key=os.path.getmtime)

def load_statistical_results():
    """Carrega resultados estatísticos."""
    stats_file = os.path.join(OUTPUT_DIR, 'statistical_results.json')
    if os.path.exists(stats_file):
        with open(stats_file, 'r') as f:
            return json.load(f)
    return None

def get_scenario_description(scenario):
    """Retorna descrição do cenário."""
    descriptions = {
        1: "Consulta Simples - Buscar um usuário por ID",
        2: "Lista Simples - Buscar todos os usuários",
        3: "Lista com Filtros - Buscar usuários com filtros (status, limit)",
        4: "Recursos Relacionados - Buscar usuário com seus posts",
        5: "Consulta Seletiva - Buscar apenas campos específicos (id, name)",
        6: "Múltiplos Recursos - Buscar users, posts e comments em uma requisição"
    }
    return descriptions.get(scenario, f"Cenário {scenario}")

def generate_report():
    """Gera relatório final."""
    
    # Carregar dados
    results_file = find_latest_results()
    if not results_file:
        print("❌ Nenhum arquivo de resultados encontrado!")
        print("   Execute primeiro: python scripts/benchmark.py")
        return None
    
    df = pd.read_csv(results_file)
    stats = load_statistical_results()
    
    if not stats:
        print("⚠️  Resultados estatísticos não encontrados!")
        print("   Execute primeiro: python scripts/statistical_analysis.py")
        stats = None
    
    # Gerar relatório
    report = []
    report.append("# Relatório Final - Experimento GraphQL vs REST\n")
    report.append(f"**Data de Geração**: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
    
    # 1. Introdução
    report.append("## 1. Introdução\n")
    report.append("Este relatório apresenta os resultados de um experimento controlado ")
    report.append("realizado para comparar quantitativamente as APIs GraphQL e REST. ")
    report.append("O experimento foi conduzido com o objetivo de responder às seguintes ")
    report.append("perguntas de pesquisa:\n\n")
    report.append("- **RQ1**: Respostas às consultas GraphQL são mais rápidas que respostas às consultas REST?\n")
    report.append("- **RQ2**: Respostas às consultas GraphQL têm tamanho menor que respostas às consultas REST?\n\n")
    
    report.append("### Hipóteses\n\n")
    report.append("**RQ1 - Tempo de Resposta:**\n")
    report.append("- H₀₁: Não há diferença estatisticamente significativa no tempo de resposta entre consultas GraphQL e REST.\n")
    report.append("- Hₐ₁: Consultas GraphQL apresentam tempo de resposta estatisticamente menor que consultas REST.\n\n")
    
    report.append("**RQ2 - Tamanho da Resposta:**\n")
    report.append("- H₀₂: Não há diferença estatisticamente significativa no tamanho da resposta entre consultas GraphQL e REST.\n")
    report.append("- Hₐ₂: Consultas GraphQL apresentam tamanho de resposta estatisticamente menor que consultas REST.\n\n")
    
    # 2. Metodologia
    report.append("## 2. Metodologia\n\n")
    report.append("### 2.1 Ambiente Experimental\n\n")
    report.append("- **Sistema Operacional**: macOS (darwin 25.1.0)\n")
    report.append("- **APIs**: Localhost\n")
    report.append("  - REST: http://localhost:8000\n")
    report.append("  - GraphQL: http://localhost:8001\n")
    report.append("- **Banco de Dados**: SQLite\n")
    report.append("- **Dataset**: 1000 usuários, 5000 posts, 15000 comentários, 50 categorias\n\n")
    
    report.append("### 2.2 Cenários de Teste\n\n")
    for i in range(1, 7):
        report.append(f"{i}. **Cenário {i}**: {get_scenario_description(i)}\n")
    report.append("\n")
    
    report.append("### 2.3 Procedimento Experimental\n\n")
    report.append("- **Replicações**: 30 por combinação de tratamento-cenário\n")
    report.append("- **Total de execuções**: 360 (2 APIs × 6 cenários × 30 replicações)\n")
    report.append("- **Delay entre requisições**: 1 segundo\n")
    report.append("- **Cache**: Desabilitado em ambas as APIs\n")
    report.append("- **Métricas coletadas**:\n")
    report.append("  - Tempo de resposta (ms)\n")
    report.append("  - Tamanho da resposta (bytes)\n\n")
    
    report.append("### 2.4 Análise Estatística\n\n")
    report.append("Para cada métrica, foram realizados:\n")
    report.append("- Teste de normalidade (Shapiro-Wilk)\n")
    report.append("- Teste de hipóteses (teste t de Student ou Mann-Whitney U, conforme apropriado)\n")
    report.append("- Cálculo de intervalos de confiança (bootstrap, 95%)\n")
    report.append("- Cálculo do tamanho do efeito (Cohen's d)\n\n")
    
    # 3. Resultados
    report.append("## 3. Resultados\n\n")
    
    df_success = df[df['success'] == True].copy()
    total_requests = len(df)
    successful_requests = len(df_success)
    success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
    
    report.append(f"### 3.1 Validação dos Dados\n\n")
    report.append(f"- Total de requisições: {total_requests}\n")
    report.append(f"- Requisições bem-sucedidas: {successful_requests} ({success_rate:.1f}%)\n")
    report.append(f"- Requisições com falha: {total_requests - successful_requests}\n\n")
    
    if stats:
        # RQ1
        report.append("### 3.2 RQ1: Tempo de Resposta\n\n")
        rq1 = stats['overall']['overall_time']
        report.append("**Resultados Gerais:**\n\n")
        report.append(f"- **REST**: Média = {rq1['rest_mean']:.2f} ms, Mediana = {rq1['rest_median']:.2f} ms, DP = {rq1['rest_std']:.2f} ms\n")
        report.append(f"- **GraphQL**: Média = {rq1['graphql_mean']:.2f} ms, Mediana = {rq1['graphql_median']:.2f} ms, DP = {rq1['graphql_std']:.2f} ms\n")
        report.append(f"- **Diferença média**: {rq1['mean_difference']:.2f} ms (GraphQL - REST)\n")
        report.append(f"- **Intervalo de confiança 95%**: [{rq1['ci_lower']:.2f}, {rq1['ci_upper']:.2f}] ms\n")
        report.append(f"- **Tamanho do efeito (Cohen's d)**: {rq1['effect_size']:.3f}\n\n")
        
        report.append(f"**Teste Estatístico:**\n\n")
        report.append(f"- Teste utilizado: {rq1['test_type']}\n")
        report.append(f"- Estatística: {rq1['test_statistic']:.4f}\n")
        report.append(f"- p-valor: {rq1['p_value']:.6f}\n\n")
        
        if rq1['p_value'] < 0.05:
            if rq1['mean_difference'] < 0:
                report.append("**Conclusão**: Rejeita-se H₀₁. GraphQL é significativamente mais rápido que REST (p < 0.05).\n\n")
            else:
                report.append("**Conclusão**: Rejeita-se H₀₁. REST é significativamente mais rápido que GraphQL (p < 0.05).\n\n")
        else:
            report.append("**Conclusão**: Não se rejeita H₀₁. Não há diferença estatisticamente significativa (p ≥ 0.05).\n\n")
        
        # RQ2
        report.append("### 3.3 RQ2: Tamanho da Resposta\n\n")
        rq2 = stats['overall']['overall_size']
        report.append("**Resultados Gerais:**\n\n")
        report.append(f"- **REST**: Média = {rq2['rest_mean']:.0f} bytes, Mediana = {rq2['rest_median']:.0f} bytes, DP = {rq2['rest_std']:.0f} bytes\n")
        report.append(f"- **GraphQL**: Média = {rq2['graphql_mean']:.0f} bytes, Mediana = {rq2['graphql_median']:.0f} bytes, DP = {rq2['graphql_std']:.0f} bytes\n")
        report.append(f"- **Diferença média**: {rq2['mean_difference']:.0f} bytes (GraphQL - REST)\n")
        report.append(f"- **Intervalo de confiança 95%**: [{rq2['ci_lower']:.0f}, {rq2['ci_upper']:.0f}] bytes\n")
        report.append(f"- **Tamanho do efeito (Cohen's d)**: {rq2['effect_size']:.3f}\n\n")
        
        report.append(f"**Teste Estatístico:**\n\n")
        report.append(f"- Teste utilizado: {rq2['test_type']}\n")
        report.append(f"- Estatística: {rq2['test_statistic']:.4f}\n")
        report.append(f"- p-valor: {rq2['p_value']:.6f}\n\n")
        
        if rq2['p_value'] < 0.05:
            if rq2['mean_difference'] < 0:
                report.append("**Conclusão**: Rejeita-se H₀₂. GraphQL tem tamanho significativamente menor que REST (p < 0.05).\n\n")
            else:
                report.append("**Conclusão**: Rejeita-se H₀₂. REST tem tamanho significativamente menor que GraphQL (p < 0.05).\n\n")
        else:
            report.append("**Conclusão**: Não se rejeita H₀₂. Não há diferença estatisticamente significativa (p ≥ 0.05).\n\n")
        
        # Análise por cenário
        report.append("### 3.4 Análise por Cenário\n\n")
        report.append("| Cenário | Descrição | Tempo REST (ms) | Tempo GraphQL (ms) | Diferença (ms) | p-valor |\n")
        report.append("|---------|-----------|------------------|---------------------|----------------|----------|\n")
        
        for scenario in range(1, 7):
            time_key = f'scenario_{scenario}_time'
            if time_key in stats['by_scenario']:
                rq1_scenario = stats['by_scenario'][time_key]
                desc = get_scenario_description(scenario).split(' - ')[1] if ' - ' in get_scenario_description(scenario) else get_scenario_description(scenario)
                report.append(f"| {scenario} | {desc[:30]}... | {rq1_scenario['rest_mean']:.2f} | {rq1_scenario['graphql_mean']:.2f} | {rq1_scenario['mean_difference']:.2f} | {rq1_scenario['p_value']:.4f} |\n")
        
        report.append("\n")
    
    # 4. Discussão
    report.append("## 4. Discussão\n\n")
    
    if stats:
        rq1 = stats['overall']['overall_time']
        rq2 = stats['overall']['overall_size']
        
        report.append("### 4.1 Interpretação dos Resultados\n\n")
        
        # Tempo
        if rq1['p_value'] < 0.05:
            if rq1['mean_difference'] < 0:
                report.append(f"Os resultados indicam que GraphQL é significativamente mais rápido que REST, ")
                report.append(f"com uma diferença média de {abs(rq1['mean_difference']):.2f} ms. ")
            else:
                report.append(f"Os resultados indicam que REST é significativamente mais rápido que GraphQL, ")
                report.append(f"com uma diferença média de {rq1['mean_difference']:.2f} ms. ")
        else:
            report.append("Os resultados não mostram diferença estatisticamente significativa no tempo de resposta ")
            report.append("entre GraphQL e REST. ")
        
        report.append(f"O tamanho do efeito (Cohen's d = {rq1['effect_size']:.3f}) indica ")
        if abs(rq1['effect_size']) < 0.2:
            report.append("um efeito muito pequeno.\n\n")
        elif abs(rq1['effect_size']) < 0.5:
            report.append("um efeito pequeno.\n\n")
        elif abs(rq1['effect_size']) < 0.8:
            report.append("um efeito médio.\n\n")
        else:
            report.append("um efeito grande.\n\n")
        
        # Tamanho
        if rq2['p_value'] < 0.05:
            if rq2['mean_difference'] < 0:
                report.append(f"Em relação ao tamanho das respostas, GraphQL produz respostas significativamente menores, ")
                report.append(f"com uma diferença média de {abs(rq2['mean_difference']):.0f} bytes ({abs(rq2['mean_difference'])/rq2['rest_mean']*100:.1f}% menor). ")
            else:
                report.append(f"Em relação ao tamanho das respostas, REST produz respostas significativamente menores, ")
                report.append(f"com uma diferença média de {rq2['mean_difference']:.0f} bytes ({rq2['mean_difference']/rq2['rest_mean']*100:.1f}% menor). ")
        else:
            report.append("Não há diferença estatisticamente significativa no tamanho das respostas entre GraphQL e REST. ")
        
        report.append(f"O tamanho do efeito (Cohen's d = {rq2['effect_size']:.3f}) indica ")
        if abs(rq2['effect_size']) < 0.2:
            report.append("um efeito muito pequeno.\n\n")
        elif abs(rq2['effect_size']) < 0.5:
            report.append("um efeito pequeno.\n\n")
        elif abs(rq2['effect_size']) < 0.8:
            report.append("um efeito médio.\n\n")
        else:
            report.append("um efeito grande.\n\n")
    
    report.append("### 4.2 Limitações\n\n")
    report.append("- O experimento foi realizado em ambiente local, podendo não refletir condições de produção.\n")
    report.append("- O dataset utilizado é sintético e pode não representar dados reais.\n")
    report.append("- Apenas 6 cenários de uso foram testados, não cobrindo todos os casos possíveis.\n")
    report.append("- O experimento não considera aspectos como cache em produção, CDN, ou otimizações específicas.\n\n")
    
    report.append("### 4.3 Trabalhos Futuros\n\n")
    report.append("- Realizar experimento em ambiente de produção.\n")
    report.append("- Testar com volumes maiores de dados.\n")
    report.append("- Incluir mais cenários de uso.\n")
    report.append("- Avaliar outros aspectos como complexidade de queries, uso de memória, etc.\n\n")
    
    # 5. Conclusão
    report.append("## 5. Conclusão\n\n")
    
    if stats:
        rq1 = stats['overall']['overall_time']
        rq2 = stats['overall']['overall_size']
        
        report.append("Com base nos resultados obtidos:\n\n")
        
        if rq1['p_value'] < 0.05:
            if rq1['mean_difference'] < 0:
                report.append("- **RQ1**: GraphQL apresenta tempo de resposta significativamente menor que REST.\n")
            else:
                report.append("- **RQ1**: REST apresenta tempo de resposta significativamente menor que GraphQL.\n")
        else:
            report.append("- **RQ1**: Não há diferença estatisticamente significativa no tempo de resposta.\n")
        
        if rq2['p_value'] < 0.05:
            if rq2['mean_difference'] < 0:
                report.append("- **RQ2**: GraphQL produz respostas com tamanho significativamente menor que REST.\n")
            else:
                report.append("- **RQ2**: REST produz respostas com tamanho significativamente menor que GraphQL.\n")
        else:
            report.append("- **RQ2**: Não há diferença estatisticamente significativa no tamanho das respostas.\n")
    else:
        report.append("Os resultados completos estão disponíveis nos arquivos de análise estatística e visualizações geradas.\n")
    
    report.append("\n---\n\n")
    report.append("*Relatório gerado automaticamente a partir dos resultados do experimento.*\n")
    
    return ''.join(report)

def main():
    """Função principal."""
    print("Gerando relatório final...")
    
    report = generate_report()
    
    if report:
        output_file = os.path.join(OUTPUT_DIR, 'relatorio_final.md')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ Relatório gerado: {output_file}")
    else:
        print("\n❌ Erro ao gerar relatório")

if __name__ == '__main__':
    main()

