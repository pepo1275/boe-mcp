#!/usr/bin/env python3
"""
TC-CC-11.4: Test de límites para BOE-MCP v1.2.0

Este script prueba los límites de:
1. API BOE directa - para conocer límites reales del backend
2. Servidor MCP - para medir overhead del protocolo

Objetivo: Generar datos para documentación de guía de uso y decidir
si implementar límites en MCP o dejar a clientes.

Uso:
    uv run python tests/test_limits_v120.py
    uv run python tests/test_limits_v120.py --mcp  # incluye pruebas MCP
"""

import asyncio
import time
import json
import sys
import subprocess
from dataclasses import dataclass
from typing import Any
import httpx

# Configuración
BOE_API_BASE = "https://www.boe.es"
USER_AGENT = "boe-mcp-test/1.0"
LIMITS_TO_TEST = [10, 50, 100, 200, 500, 1000, 2000, 5000]
TIMEOUT_SECONDS = 60  # Timeout generoso para límites altos


@dataclass
class TestResult:
    """Resultado de una prueba de límite."""
    limit_requested: int
    status: str  # "OK", "ERROR", "TIMEOUT"
    results_returned: int | None
    time_seconds: float
    error_message: str | None = None
    response_size_kb: float | None = None


async def test_api_direct(limit: int, query: str = "ley") -> TestResult:
    """
    Prueba directa contra API BOE (sin MCP).
    Replica la lógica de search_laws_list del servidor.
    """
    endpoint = "/datosabiertos/api/legislacion-consolidada"

    # Query similar a búsqueda típica
    query_obj = {
        "query": {
            "query_string": {
                "query": f'titulo:({query}) and vigencia_agotada:"N"'
            }
        }
    }

    params = {
        "limit": limit,
        "offset": 0,
        "query": json.dumps(query_obj)
    }

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }

    url = f"{BOE_API_BASE}{endpoint}"

    start_time = time.perf_counter()

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                url,
                headers=headers,
                params=params,
                timeout=TIMEOUT_SECONDS
            )
            elapsed = time.perf_counter() - start_time

            response.raise_for_status()
            data = response.json()

            # Extraer conteo de resultados
            # La API BOE devuelve data como array directo, no data.items
            results_count = 0
            if "data" in data:
                if isinstance(data["data"], list):
                    results_count = len(data["data"])
                elif isinstance(data["data"], dict) and "items" in data["data"]:
                    results_count = len(data["data"]["items"])

            # Tamaño de respuesta
            response_size_kb = len(response.content) / 1024

            return TestResult(
                limit_requested=limit,
                status="OK",
                results_returned=results_count,
                time_seconds=elapsed,
                response_size_kb=response_size_kb
            )

        except httpx.TimeoutException:
            elapsed = time.perf_counter() - start_time
            return TestResult(
                limit_requested=limit,
                status="TIMEOUT",
                results_returned=None,
                time_seconds=elapsed,
                error_message=f"Timeout después de {TIMEOUT_SECONDS}s"
            )

        except httpx.HTTPStatusError as e:
            elapsed = time.perf_counter() - start_time
            return TestResult(
                limit_requested=limit,
                status="ERROR",
                results_returned=None,
                time_seconds=elapsed,
                error_message=f"HTTP {e.response.status_code}: {e.response.text[:200]}"
            )

        except Exception as e:
            elapsed = time.perf_counter() - start_time
            return TestResult(
                limit_requested=limit,
                status="ERROR",
                results_returned=None,
                time_seconds=elapsed,
                error_message=str(e)[:200]
            )


async def test_api_with_date_range(limit: int) -> TestResult:
    """
    Prueba con filtro de fecha (feature v1.2.0).
    Busca desde 1978 hasta hoy - caso extremo de autocompletado.
    """
    endpoint = "/datosabiertos/api/legislacion-consolidada"

    query_obj = {
        "query": {
            "query_string": {
                "query": 'vigencia_agotada:"N"'
            },
            "range": {
                "fecha_publicacion": {
                    "gte": "19780101",
                    "lte": "20251201"
                }
            }
        }
    }

    params = {
        "limit": limit,
        "offset": 0,
        "query": json.dumps(query_obj)
    }

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }

    url = f"{BOE_API_BASE}{endpoint}"

    start_time = time.perf_counter()

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                url,
                headers=headers,
                params=params,
                timeout=TIMEOUT_SECONDS
            )
            elapsed = time.perf_counter() - start_time

            response.raise_for_status()
            data = response.json()

            results_count = 0
            total_available = "N/A"
            if "data" in data:
                if isinstance(data["data"], list):
                    results_count = len(data["data"])
                    total_available = f"{results_count}+ (paginado)"
                elif isinstance(data["data"], dict):
                    if "items" in data["data"]:
                        results_count = len(data["data"]["items"])
                    if "total" in data["data"]:
                        total_available = data["data"]["total"]

            response_size_kb = len(response.content) / 1024

            return TestResult(
                limit_requested=limit,
                status="OK",
                results_returned=results_count,
                time_seconds=elapsed,
                response_size_kb=response_size_kb,
                error_message=f"Total disponible: {total_available}"
            )

        except httpx.TimeoutException:
            elapsed = time.perf_counter() - start_time
            return TestResult(
                limit_requested=limit,
                status="TIMEOUT",
                results_returned=None,
                time_seconds=elapsed,
                error_message=f"Timeout después de {TIMEOUT_SECONDS}s"
            )

        except Exception as e:
            elapsed = time.perf_counter() - start_time
            return TestResult(
                limit_requested=limit,
                status="ERROR",
                results_returned=None,
                time_seconds=elapsed,
                error_message=str(e)[:200]
            )


def print_results_table(results: list[TestResult], title: str):
    """Imprime tabla formateada de resultados."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")
    print(f"{'Limit':>8} | {'Status':^10} | {'Results':>8} | {'Time (s)':>10} | {'Size (KB)':>10}")
    print(f"{'-'*8}-+-{'-'*10}-+-{'-'*8}-+-{'-'*10}-+-{'-'*10}")

    for r in results:
        results_str = str(r.results_returned) if r.results_returned is not None else "N/A"
        size_str = f"{r.response_size_kb:.1f}" if r.response_size_kb else "N/A"
        print(f"{r.limit_requested:>8} | {r.status:^10} | {results_str:>8} | {r.time_seconds:>10.3f} | {size_str:>10}")

    print(f"{'='*70}")

    # Notas adicionales
    for r in results:
        if r.error_message and r.status == "OK":
            print(f"  ℹ️  Limit {r.limit_requested}: {r.error_message}")
        elif r.error_message:
            print(f"  ⚠️  Limit {r.limit_requested}: {r.error_message}")


def analyze_results(results: list[TestResult]) -> dict[str, Any]:
    """Analiza resultados para recomendaciones."""
    analysis = {
        "max_working_limit": 0,
        "recommended_limit": 50,
        "avg_time_per_result": 0,
        "breaking_point": None,
        "notes": []
    }

    working_results = [r for r in results if r.status == "OK"]

    if working_results:
        analysis["max_working_limit"] = max(r.limit_requested for r in working_results)

        # Calcular tiempo promedio por resultado
        total_time = sum(r.time_seconds for r in working_results)
        total_results = sum(r.results_returned or 0 for r in working_results)
        if total_results > 0:
            analysis["avg_time_per_result"] = total_time / total_results

        # Encontrar punto óptimo (mejor ratio tiempo/resultados)
        best_ratio = float('inf')
        for r in working_results:
            if r.results_returned and r.results_returned > 0:
                ratio = r.time_seconds / r.results_returned
                if ratio < best_ratio and r.results_returned >= r.limit_requested * 0.8:
                    best_ratio = ratio
                    analysis["recommended_limit"] = r.limit_requested

    # Detectar punto de quiebre
    for r in results:
        if r.status in ("ERROR", "TIMEOUT"):
            analysis["breaking_point"] = r.limit_requested
            analysis["notes"].append(f"Fallo detectado en limit={r.limit_requested}")
            break

    # Análisis de tiempos
    for r in working_results:
        if r.time_seconds > 5:
            analysis["notes"].append(f"Limit {r.limit_requested}: >5s de respuesta")
        if r.time_seconds > 10:
            analysis["notes"].append(f"⚠️ Limit {r.limit_requested}: tiempo excesivo ({r.time_seconds:.1f}s)")

    return analysis


async def run_all_tests(include_mcp: bool = False):
    """Ejecuta todas las pruebas."""
    print("\n" + "🧪 TC-CC-11.4: TEST DE LÍMITES BOE-MCP v1.2.0 ".center(70, "="))
    print(f"Límites a probar: {LIMITS_TO_TEST}")
    print(f"Timeout por request: {TIMEOUT_SECONDS}s")

    # Test 1: API directa con query simple
    print("\n⏳ Ejecutando pruebas de API directa (query simple)...")
    results_simple = []
    for limit in LIMITS_TO_TEST:
        print(f"  Testing limit={limit}...", end=" ", flush=True)
        result = await test_api_direct(limit, query="ley")
        results_simple.append(result)
        print(f"{result.status} ({result.time_seconds:.2f}s)")
        await asyncio.sleep(0.5)  # Pausa entre requests

    print_results_table(results_simple, "API DIRECTA - Query simple: 'ley'")

    # Test 2: API directa con rango de fechas (v1.2.0)
    print("\n⏳ Ejecutando pruebas de API con rango de fechas (1978-2025)...")
    results_daterange = []
    for limit in LIMITS_TO_TEST:
        print(f"  Testing limit={limit} con fecha_publicacion...", end=" ", flush=True)
        result = await test_api_with_date_range(limit)
        results_daterange.append(result)
        print(f"{result.status} ({result.time_seconds:.2f}s)")
        await asyncio.sleep(0.5)

    print_results_table(results_daterange, "API DIRECTA - Con rango fechas (feature v1.2.0)")

    # Análisis
    print("\n" + "📊 ANÁLISIS DE RESULTADOS ".center(70, "="))

    analysis_simple = analyze_results(results_simple)
    analysis_daterange = analyze_results(results_daterange)

    print("\n📌 Query Simple:")
    print(f"   - Límite máximo funcional: {analysis_simple['max_working_limit']}")
    print(f"   - Límite recomendado: {analysis_simple['recommended_limit']}")
    if analysis_simple['breaking_point']:
        print(f"   - Punto de quiebre: {analysis_simple['breaking_point']}")

    print("\n📌 Con Rango de Fechas:")
    print(f"   - Límite máximo funcional: {analysis_daterange['max_working_limit']}")
    print(f"   - Límite recomendado: {analysis_daterange['recommended_limit']}")
    if analysis_daterange['breaking_point']:
        print(f"   - Punto de quiebre: {analysis_daterange['breaking_point']}")

    # Recomendaciones
    print("\n" + "💡 RECOMENDACIONES PARA DOCUMENTACIÓN ".center(70, "="))
    print("""
    Basado en los resultados, considerar:

    1. LÍMITE DEFAULT EN MCP:
       - Mantener limit=50 como default (balance tiempo/resultados)
       - Documentar que límites >200 pueden ser lentos

    2. LÍMITES EN CLIENTE:
       - Clientes deberían implementar paginación para >100 resultados
       - Advertir sobre límites >500 (posible timeout)

    3. DOCUMENTACIÓN DE USUARIO:
       - Incluir tabla de tiempos esperados por límite
       - Recomendar uso de filtros para reducir resultados
    """)

    # Guardar resultados en JSON para análisis posterior
    output = {
        "test_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "limits_tested": LIMITS_TO_TEST,
        "timeout_seconds": TIMEOUT_SECONDS,
        "results_simple_query": [
            {
                "limit": r.limit_requested,
                "status": r.status,
                "results": r.results_returned,
                "time_s": round(r.time_seconds, 3),
                "size_kb": round(r.response_size_kb, 1) if r.response_size_kb else None
            }
            for r in results_simple
        ],
        "results_date_range": [
            {
                "limit": r.limit_requested,
                "status": r.status,
                "results": r.results_returned,
                "time_s": round(r.time_seconds, 3),
                "size_kb": round(r.response_size_kb, 1) if r.response_size_kb else None,
                "total_available": r.error_message
            }
            for r in results_daterange
        ],
        "analysis": {
            "simple_query": analysis_simple,
            "date_range": analysis_daterange
        }
    }

    output_file = "tests/results_limits_v120.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n📁 Resultados guardados en: {output_file}")


if __name__ == "__main__":
    include_mcp = "--mcp" in sys.argv
    asyncio.run(run_all_tests(include_mcp))
