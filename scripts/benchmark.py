#!/usr/bin/env python3
"""
Script de benchmark para realizar medições entre APIs REST e GraphQL.
Coleta tempo de resposta e tamanho das respostas para cada cenário.

Este script executa todas as requisições do experimento e salva os resultados
em CSV para análise posterior.
"""

import requests
import json
import time
import random
import os
import csv
from datetime import datetime
from typing import Dict, List, Tuple
from tqdm import tqdm

# Configuração
REST_URL = "http://localhost:8000"
GRAPHQL_URL = "http://localhost:8001/graphql"

# Número de replicações por cenário
REPLICATIONS = 30

# Delay entre requisições (segundos)
REQUEST_DELAY = 1.0

# Resultados
RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
RESULTS_FILE = os.path.join(RESULTS_DIR, f'benchmark_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')

class BenchmarkResult:
    """Classe para armazenar resultado de uma medição."""
    def __init__(self, api_type: str, scenario: int, replication: int, 
                 response_time: float, response_size: int, success: bool, error: str = None):
        self.api_type = api_type
        self.scenario = scenario
        self.replication = replication
        self.response_time = response_time
        self.response_size = response_size
        self.success = success
        self.error = error
        self.timestamp = datetime.now().isoformat()

def measure_request(url: str, method: str = 'GET', payload: dict = None) -> Tuple[float, int, bool, str]:
    """
    Realiza uma requisição HTTP e mede tempo e tamanho da resposta.
    
    Returns:
        (response_time_ms, response_size_bytes, success, error_message)
    """
    try:
        start_time = time.time()
        
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, json=payload, headers=headers, timeout=10)
        else:
            raise ValueError(f"Método HTTP não suportado: {method}")
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # Converter para ms
        response_size = len(response.content)
        
        response.raise_for_status()
        
        return response_time, response_size, True, None
        
    except Exception as e:
        end_time = time.time()
        response_time = (end_time - start_time) * 1000
        return response_time, 0, False, str(e)

# ============ CENÁRIOS DE TESTE ============

def scenario_1_rest() -> Tuple[str, str, dict]:
    """Cenário 1: Consulta Simples - Buscar um usuário por ID"""
    user_id = random.randint(1, 1000)
    url = f"{REST_URL}/api/users/{user_id}"
    return url, 'GET', None

def scenario_1_graphql() -> Tuple[str, str, dict]:
    """Cenário 1: Consulta Simples - Buscar um usuário por ID"""
    user_id = random.randint(1, 1000)
    query = f"""
    query {{
        user(id: "{user_id}") {{
            id
            name
            email
            status
            createdAt
        }}
    }}
    """
    payload = {"query": query}
    return f"{GRAPHQL_URL}", 'POST', payload

def scenario_2_rest() -> Tuple[str, str, dict]:
    """Cenário 2: Lista Simples - Buscar todos os usuários"""
    url = f"{REST_URL}/api/users"
    return url, 'GET', None

def scenario_2_graphql() -> Tuple[str, str, dict]:
    """Cenário 2: Lista Simples - Buscar todos os usuários"""
    query = """
    query {
        users {
            id
            name
            email
            status
            createdAt
        }
    }
    """
    payload = {"query": query}
    return f"{GRAPHQL_URL}", 'POST', payload

def scenario_3_rest() -> Tuple[str, str, dict]:
    """Cenário 3: Lista com Filtros"""
    limit = random.choice([10, 20, 50])
    status = random.choice(['active', 'inactive'])
    url = f"{REST_URL}/api/users-filtered?status={status}&limit={limit}"
    return url, 'GET', None

def scenario_3_graphql() -> Tuple[str, str, dict]:
    """Cenário 3: Lista com Filtros"""
    limit = random.choice([10, 20, 50])
    status = random.choice(['active', 'inactive'])
    query = f"""
    query {{
        usersFiltered(status: "{status}", limit: {limit}) {{
            id
            name
            email
            status
            createdAt
        }}
    }}
    """
    payload = {"query": query}
    return f"{GRAPHQL_URL}", 'POST', payload

def scenario_4_rest() -> Tuple[str, str, dict]:
    """Cenário 4: Recursos Relacionados - Buscar posts de um usuário"""
    user_id = random.randint(1, 1000)
    url = f"{REST_URL}/api/users/{user_id}/posts"
    return url, 'GET', None

def scenario_4_graphql() -> Tuple[str, str, dict]:
    """Cenário 4: Recursos Relacionados - Buscar usuário com posts"""
    user_id = random.randint(1, 1000)
    query = f"""
    query {{
        user(id: "{user_id}") {{
            id
            name
            email
            posts {{
                id
                title
                content
            }}
        }}
    }}
    """
    payload = {"query": query}
    return f"{GRAPHQL_URL}", 'POST', payload

def scenario_5_rest() -> Tuple[str, str, dict]:
    """Cenário 5: Consulta Seletiva - Apenas id e name"""
    user_id = random.randint(1, 1000)
    url = f"{REST_URL}/api/users/{user_id}/simple"
    return url, 'GET', None

def scenario_5_graphql() -> Tuple[str, str, dict]:
    """Cenário 5: Consulta Seletiva - Apenas id e name"""
    user_id = random.randint(1, 1000)
    query = f"""
    query {{
        user(id: "{user_id}") {{
            id
            name
        }}
    }}
    """
    payload = {"query": query}
    return f"{GRAPHQL_URL}", 'POST', payload

def scenario_6_rest() -> Tuple[str, str, dict]:
    """Cenário 6: Múltiplos Recursos"""
    url = f"{REST_URL}/api/multiple"
    return url, 'GET', None

def scenario_6_graphql() -> Tuple[str, str, dict]:
    """Cenário 6: Múltiplos Recursos"""
    query = """
    query {
        multiple {
            users {
                id
                name
                email
            }
            posts {
                id
                title
            }
            comments {
                id
                text
            }
        }
    }
    """
    payload = {"query": query}
    return f"{GRAPHQL_URL}", 'POST', payload

# Mapeamento de cenários
SCENARIOS = {
    'rest': {
        1: scenario_1_rest,
        2: scenario_2_rest,
        3: scenario_3_rest,
        4: scenario_4_rest,
        5: scenario_5_rest,
        6: scenario_6_rest,
    },
    'graphql': {
        1: scenario_1_graphql,
        2: scenario_2_graphql,
        3: scenario_3_graphql,
        4: scenario_4_graphql,
        5: scenario_5_graphql,
        6: scenario_6_graphql,
    }
}

def check_api_health(api_type: str) -> bool:
    """Verifica se a API está respondendo."""
    try:
        if api_type == 'rest':
            url = f"{REST_URL}/health"
        else:
            url = f"{GRAPHQL_URL.replace('/graphql', '')}/health"
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except:
        return False

def run_benchmark():
    """Executa o benchmark completo."""
    print("=" * 60)
    print("Benchmark: GraphQL vs REST")
    print("=" * 60)
    
    # Verificar se APIs estão rodando
    print("\nVerificando APIs...")
    rest_ok = check_api_health('rest')
    graphql_ok = check_api_health('graphql')
    
    if not rest_ok:
        print("❌ API REST não está respondendo! Certifique-se de que está rodando em http://localhost:8000")
        return
    
    if not graphql_ok:
        print("❌ API GraphQL não está respondendo! Certifique-se de que está rodando em http://localhost:8001")
        return
    
    print("✅ Ambas as APIs estão respondendo!\n")
    
    # Criar diretório de resultados
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    results: List[BenchmarkResult] = []
    
    # Total de execuções
    total_executions = 2 * 6 * REPLICATIONS  # 2 APIs × 6 cenários × 30 replicações
    pbar = tqdm(total=total_executions, desc="Executando benchmark")
    
    # Warm-up: descartar primeiras 10 requisições
    print("\nRealizando warm-up...")
    for _ in range(10):
        try:
            requests.get(f"{REST_URL}/health", timeout=5)
            requests.get(f"{GRAPHQL_URL.replace('/graphql', '')}/health", timeout=5)
        except:
            pass
        time.sleep(0.5)
    
    print("\nIniciando medições...\n")
    
    # Executar para cada API
    for api_type in ['rest', 'graphql']:
        # Executar para cada cenário
        for scenario_num in range(1, 7):
            scenario_func = SCENARIOS[api_type][scenario_num]
            
            # Executar replicações
            for replication in range(1, REPLICATIONS + 1):
                # Gerar URL/query para o cenário
                url, method, payload = scenario_func()
                
                # Realizar requisição e medir
                response_time, response_size, success, error = measure_request(url, method, payload)
                
                # Armazenar resultado
                result = BenchmarkResult(
                    api_type=api_type.upper(),
                    scenario=scenario_num,
                    replication=replication,
                    response_time=response_time,
                    response_size=response_size,
                    success=success,
                    error=error
                )
                results.append(result)
                
                pbar.update(1)
                
                # Delay entre requisições
                time.sleep(REQUEST_DELAY)
    
    pbar.close()
    
    # Salvar resultados em CSV
    print(f"\nSalvando resultados em {RESULTS_FILE}...")
    with open(RESULTS_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['timestamp', 'api_type', 'scenario', 'replication', 
                     'response_time_ms', 'response_size_bytes', 'success', 'error']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow({
                'timestamp': result.timestamp,
                'api_type': result.api_type,
                'scenario': result.scenario,
                'replication': result.replication,
                'response_time_ms': result.response_time,
                'response_size_bytes': result.response_size,
                'success': result.success,
                'error': result.error or ''
            })
    
    # Estatísticas resumidas
    print("\n" + "=" * 60)
    print("Estatísticas Resumidas")
    print("=" * 60)
    
    successful_results = [r for r in results if r.success]
    failed_results = [r for r in results if not r.success]
    
    print(f"\nTotal de execuções: {len(results)}")
    print(f"Sucessos: {len(successful_results)} ({len(successful_results)/len(results)*100:.1f}%)")
    print(f"Falhas: {len(failed_results)} ({len(failed_results)/len(results)*100:.1f}%)")
    
    if failed_results:
        print("\nFalhas por API e Cenário:")
        for api_type in ['REST', 'GRAPHQL']:
            for scenario in range(1, 7):
                failures = [r for r in failed_results if r.api_type == api_type and r.scenario == scenario]
                if failures:
                    print(f"  {api_type} - Cenário {scenario}: {len(failures)} falhas")
    
    print(f"\n✅ Resultados salvos em: {RESULTS_FILE}")

if __name__ == '__main__':
    run_benchmark()

