#!/usr/bin/env python3
"""
Script para executar todo o pipeline da Sprint 2:
1. Análise estatística
2. Geração de dashboard
3. Geração de relatório
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Executa um comando e mostra o resultado."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}\n")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    
    if result.returncode != 0:
        print(f"\n❌ Erro ao executar: {description}")
        return False
    
    return True

def main():
    """Função principal."""
    print("="*60)
    print("EXECUTANDO SPRINT 2 - ANÁLISE COMPLETA")
    print("="*60)
    
    # Verificar se existe arquivo de resultados
    results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
    import glob
    csv_files = glob.glob(os.path.join(results_dir, 'benchmark_results_*.csv'))
    
    if not csv_files:
        print("\n❌ Nenhum arquivo de resultados encontrado!")
        print("   Execute primeiro: python scripts/benchmark.py")
        print("   (Certifique-se de que as APIs estão rodando)")
        sys.exit(1)
    
    print(f"\n✅ Encontrado arquivo de resultados: {max(csv_files, key=os.path.getmtime)}")
    
    # 1. Análise estatística
    if not run_command(
        "python3 scripts/statistical_analysis.py",
        "1. Análise Estatística"
    ):
        sys.exit(1)
    
    # 2. Dashboard
    if not run_command(
        "python3 dashboard/create_dashboard.py",
        "2. Geração de Dashboard"
    ):
        sys.exit(1)
    
    # 3. Relatório
    if not run_command(
        "python3 scripts/generate_report.py",
        "3. Geração de Relatório Final"
    ):
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ SPRINT 2 CONCLUÍDA COM SUCESSO!")
    print("="*60)
    print("\nArquivos gerados em results/:")
    print("  - statistical_results.json")
    print("  - boxplot_tempo_resposta.png")
    print("  - boxplot_tamanho_resposta.png")
    print("  - comparacao_medias.png")
    print("  - tabela_resumo.csv")
    print("  - relatorio_final.md")
    print("\n")

if __name__ == '__main__':
    main()

