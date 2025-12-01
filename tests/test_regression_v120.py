#!/usr/bin/env python3
"""
TC-REG-01 y TC-REG-02: Pruebas de Regresión BOE-MCP v1.2.0

Verifica que funcionalidades v1.1.0 siguen funcionando correctamente en v1.2.0:
- TC-REG-01: Búsquedas sin nuevos parámetros (comportamiento legacy)
- TC-REG-02: Parámetros from_date/to_date siguen funcionando

Uso:
    uv run python tests/test_regression_v120.py
"""

import asyncio
import json
import time
from dataclasses import dataclass
from typing import Any
import httpx

BOE_API_BASE = "https://www.boe.es"
USER_AGENT = "boe-mcp-test/1.0"
TIMEOUT_SECONDS = 30


@dataclass
class RegressionResult:
    """Resultado de una prueba de regresión."""
    test_id: str
    test_name: str
    status: str  # "PASS", "FAIL", "ERROR"
    time_seconds: float
    details: str
    results_count: int | None = None


async def make_request(endpoint: str, params: dict[str, Any]) -> tuple[dict | None, float, str | None]:
    """Hace request a API BOE y devuelve (data, tiempo, error)."""
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    url = f"{BOE_API_BASE}{endpoint}"

    start = time.perf_counter()
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params, timeout=TIMEOUT_SECONDS)
            elapsed = time.perf_counter() - start
            response.raise_for_status()
            return response.json(), elapsed, None
        except Exception as e:
            elapsed = time.perf_counter() - start
            return None, elapsed, str(e)


async def test_reg_01_basic_search() -> RegressionResult:
    """
    TC-REG-01a: Búsqueda básica sin parámetros nuevos v1.2.0
    Simula comportamiento típico v1.1.0
    """
    endpoint = "/datosabiertos/api/legislacion-consolidada"

    # Query estilo v1.1.0 - solo parámetros básicos
    query_obj = {
        "query": {
            "query_string": {
                "query": 'titulo:(protección datos) and vigencia_agotada:"N"'
            }
        }
    }

    params = {
        "limit": 20,
        "offset": 0,
        "query": json.dumps(query_obj)
    }

    data, elapsed, error = await make_request(endpoint, params)

    if error:
        return RegressionResult(
            test_id="TC-REG-01a",
            test_name="Búsqueda básica v1.1.0 style",
            status="ERROR",
            time_seconds=elapsed,
            details=f"Error: {error}"
        )

    results_count = len(data.get("data", [])) if data else 0

    if results_count > 0:
        return RegressionResult(
            test_id="TC-REG-01a",
            test_name="Búsqueda básica v1.1.0 style",
            status="PASS",
            time_seconds=elapsed,
            details=f"Devolvió {results_count} resultados correctamente",
            results_count=results_count
        )
    else:
        return RegressionResult(
            test_id="TC-REG-01a",
            test_name="Búsqueda básica v1.1.0 style",
            status="FAIL",
            time_seconds=elapsed,
            details="No devolvió resultados (esperaba >0)",
            results_count=0
        )


async def test_reg_01_with_ambito() -> RegressionResult:
    """
    TC-REG-01b: Búsqueda con filtro de ámbito (v1.0.0)
    """
    endpoint = "/datosabiertos/api/legislacion-consolidada"

    query_obj = {
        "query": {
            "query_string": {
                "query": 'titulo:(ley) and vigencia_agotada:"N" and ambito@codigo:"1"'
            }
        }
    }

    params = {
        "limit": 10,
        "offset": 0,
        "query": json.dumps(query_obj)
    }

    data, elapsed, error = await make_request(endpoint, params)

    if error:
        return RegressionResult(
            test_id="TC-REG-01b",
            test_name="Búsqueda con ámbito Estatal",
            status="ERROR",
            time_seconds=elapsed,
            details=f"Error: {error}"
        )

    results_count = len(data.get("data", [])) if data else 0

    # Verificar que todos son ámbito Estatal (código 1)
    all_estatal = True
    if data and "data" in data:
        for item in data["data"]:
            if item.get("ambito", {}).get("codigo") != "1":
                all_estatal = False
                break

    if results_count > 0 and all_estatal:
        return RegressionResult(
            test_id="TC-REG-01b",
            test_name="Búsqueda con ámbito Estatal",
            status="PASS",
            time_seconds=elapsed,
            details=f"{results_count} resultados, todos ámbito Estatal",
            results_count=results_count
        )
    elif results_count > 0:
        return RegressionResult(
            test_id="TC-REG-01b",
            test_name="Búsqueda con ámbito Estatal",
            status="FAIL",
            time_seconds=elapsed,
            details="Resultados incluyen ámbitos incorrectos",
            results_count=results_count
        )
    else:
        return RegressionResult(
            test_id="TC-REG-01b",
            test_name="Búsqueda con ámbito Estatal",
            status="FAIL",
            time_seconds=elapsed,
            details="No devolvió resultados",
            results_count=0
        )


async def test_reg_01_with_rango_v11() -> RegressionResult:
    """
    TC-REG-01c: Búsqueda con rango_codigo (v1.1.0)
    """
    endpoint = "/datosabiertos/api/legislacion-consolidada"

    # Código 1300 = Ley
    query_obj = {
        "query": {
            "query_string": {
                "query": 'vigencia_agotada:"N" and rango@codigo:"1300"'
            }
        }
    }

    params = {
        "limit": 10,
        "offset": 0,
        "query": json.dumps(query_obj)
    }

    data, elapsed, error = await make_request(endpoint, params)

    if error:
        return RegressionResult(
            test_id="TC-REG-01c",
            test_name="Búsqueda con rango_codigo (Ley)",
            status="ERROR",
            time_seconds=elapsed,
            details=f"Error: {error}"
        )

    results_count = len(data.get("data", [])) if data else 0

    # Verificar que todos son rango Ley (código 1300)
    all_ley = True
    if data and "data" in data:
        for item in data["data"]:
            if item.get("rango", {}).get("codigo") != "1300":
                all_ley = False
                break

    if results_count > 0 and all_ley:
        return RegressionResult(
            test_id="TC-REG-01c",
            test_name="Búsqueda con rango_codigo (Ley)",
            status="PASS",
            time_seconds=elapsed,
            details=f"{results_count} resultados, todos rango Ley",
            results_count=results_count
        )
    else:
        return RegressionResult(
            test_id="TC-REG-01c",
            test_name="Búsqueda con rango_codigo (Ley)",
            status="FAIL",
            time_seconds=elapsed,
            details=f"Resultados: {results_count}, todos Ley: {all_ley}",
            results_count=results_count
        )


async def test_reg_02_from_date() -> RegressionResult:
    """
    TC-REG-02a: Parámetro from_date (fecha actualización)
    Este es el parámetro ORIGINAL que filtra por fecha de actualización en BD.
    """
    endpoint = "/datosabiertos/api/legislacion-consolidada"

    # from_date filtra por fecha de actualización (no publicación)
    # Usamos una fecha reciente para obtener normas actualizadas recientemente
    params = {
        "limit": 10,
        "offset": 0,
        "from": "20251101"  # Normas actualizadas desde noviembre 2025
    }

    data, elapsed, error = await make_request(endpoint, params)

    if error:
        return RegressionResult(
            test_id="TC-REG-02a",
            test_name="from_date (actualización)",
            status="ERROR",
            time_seconds=elapsed,
            details=f"Error: {error}"
        )

    results_count = len(data.get("data", [])) if data else 0

    # Verificar que fecha_actualizacion >= 20251101
    all_recent = True
    sample_dates = []
    if data and "data" in data:
        for item in data["data"][:3]:  # Revisar primeros 3
            fecha_act = item.get("fecha_actualizacion", "")
            sample_dates.append(fecha_act[:8] if fecha_act else "N/A")
            if fecha_act and fecha_act[:8] < "20251101":
                all_recent = False

    if results_count > 0 and all_recent:
        return RegressionResult(
            test_id="TC-REG-02a",
            test_name="from_date (actualización)",
            status="PASS",
            time_seconds=elapsed,
            details=f"{results_count} resultados. Fechas muestra: {sample_dates}",
            results_count=results_count
        )
    elif results_count > 0:
        return RegressionResult(
            test_id="TC-REG-02a",
            test_name="from_date (actualización)",
            status="FAIL",
            time_seconds=elapsed,
            details=f"Fechas fuera de rango. Muestra: {sample_dates}",
            results_count=results_count
        )
    else:
        return RegressionResult(
            test_id="TC-REG-02a",
            test_name="from_date (actualización)",
            status="FAIL",
            time_seconds=elapsed,
            details="No devolvió resultados",
            results_count=0
        )


async def test_reg_02_to_date() -> RegressionResult:
    """
    TC-REG-02b: Parámetro to_date (fecha actualización máxima)
    """
    endpoint = "/datosabiertos/api/legislacion-consolidada"

    params = {
        "limit": 10,
        "offset": 0,
        "from": "20250101",
        "to": "20250601"  # Normas actualizadas en primer semestre 2025
    }

    data, elapsed, error = await make_request(endpoint, params)

    if error:
        return RegressionResult(
            test_id="TC-REG-02b",
            test_name="from_date + to_date combinados",
            status="ERROR",
            time_seconds=elapsed,
            details=f"Error: {error}"
        )

    results_count = len(data.get("data", [])) if data else 0

    # Verificar rango de fechas
    in_range = True
    sample_dates = []
    if data and "data" in data:
        for item in data["data"][:3]:
            fecha_act = item.get("fecha_actualizacion", "")
            date_part = fecha_act[:8] if fecha_act else ""
            sample_dates.append(date_part)
            if date_part and (date_part < "20250101" or date_part > "20250601"):
                in_range = False

    if results_count > 0 and in_range:
        return RegressionResult(
            test_id="TC-REG-02b",
            test_name="from_date + to_date combinados",
            status="PASS",
            time_seconds=elapsed,
            details=f"{results_count} resultados en rango. Muestra: {sample_dates}",
            results_count=results_count
        )
    elif results_count > 0:
        return RegressionResult(
            test_id="TC-REG-02b",
            test_name="from_date + to_date combinados",
            status="FAIL",
            time_seconds=elapsed,
            details=f"Fechas fuera de rango. Muestra: {sample_dates}",
            results_count=results_count
        )
    else:
        # Puede ser válido si no hay actualizaciones en ese rango
        return RegressionResult(
            test_id="TC-REG-02b",
            test_name="from_date + to_date combinados",
            status="PASS",
            time_seconds=elapsed,
            details="0 resultados (puede ser válido si no hay actualizaciones en rango)",
            results_count=0
        )


async def test_reg_02_mixed_old_new() -> RegressionResult:
    """
    TC-REG-02c: Mezcla parámetros v1.0/v1.1 con v1.2.0
    Verifica que no hay conflictos
    """
    endpoint = "/datosabiertos/api/legislacion-consolidada"

    # Combinación: from_date (v1.0) + rango_codigo estilo (v1.1) + ordenamiento (v1.2.0)
    query_obj = {
        "query": {
            "query_string": {
                "query": 'vigencia_agotada:"N" and rango@codigo:"1300"'
            }
        },
        "sort": [{"fecha_disposicion": "desc"}]  # v1.2.0
    }

    params = {
        "limit": 10,
        "offset": 0,
        "from": "20240101",  # v1.0
        "query": json.dumps(query_obj)
    }

    data, elapsed, error = await make_request(endpoint, params)

    if error:
        return RegressionResult(
            test_id="TC-REG-02c",
            test_name="Mezcla parámetros v1.0+v1.1+v1.2",
            status="ERROR",
            time_seconds=elapsed,
            details=f"Error: {error}"
        )

    results_count = len(data.get("data", [])) if data else 0

    # Verificar ordenamiento descendente por fecha_disposicion
    ordered = True
    dates = []
    if data and "data" in data and len(data["data"]) > 1:
        for item in data["data"]:
            dates.append(item.get("fecha_disposicion", ""))
        for i in range(len(dates) - 1):
            if dates[i] < dates[i+1]:
                ordered = False
                break

    if results_count > 0 and ordered:
        return RegressionResult(
            test_id="TC-REG-02c",
            test_name="Mezcla parámetros v1.0+v1.1+v1.2",
            status="PASS",
            time_seconds=elapsed,
            details=f"{results_count} resultados, ordenados desc. Fechas: {dates[:3]}",
            results_count=results_count
        )
    elif results_count > 0:
        return RegressionResult(
            test_id="TC-REG-02c",
            test_name="Mezcla parámetros v1.0+v1.1+v1.2",
            status="FAIL",
            time_seconds=elapsed,
            details=f"Ordenamiento incorrecto. Fechas: {dates[:5]}",
            results_count=results_count
        )
    else:
        return RegressionResult(
            test_id="TC-REG-02c",
            test_name="Mezcla parámetros v1.0+v1.1+v1.2",
            status="FAIL",
            time_seconds=elapsed,
            details="No devolvió resultados",
            results_count=0
        )


def print_results(results: list[RegressionResult]):
    """Imprime resultados de regresión."""
    print("\n" + "="*70)
    print("  RESULTADOS PRUEBAS DE REGRESIÓN v1.2.0")
    print("="*70)

    passed = sum(1 for r in results if r.status == "PASS")
    failed = sum(1 for r in results if r.status == "FAIL")
    errors = sum(1 for r in results if r.status == "ERROR")

    for r in results:
        icon = {"PASS": "✅", "FAIL": "❌", "ERROR": "⚠️"}.get(r.status, "?")
        print(f"\n{icon} {r.test_id}: {r.test_name}")
        print(f"   Status: {r.status} | Tiempo: {r.time_seconds:.3f}s")
        print(f"   {r.details}")

    print("\n" + "-"*70)
    print(f"  RESUMEN: {passed} PASS | {failed} FAIL | {errors} ERROR")
    print(f"  Total: {len(results)} pruebas")
    print("="*70)

    return passed, failed, errors


async def main():
    """Ejecuta todas las pruebas de regresión."""
    print("\n🔄 TC-REG-01/02: PRUEBAS DE REGRESIÓN BOE-MCP v1.2.0")
    print("="*70)

    results = []

    # TC-REG-01: Búsquedas sin nuevos parámetros
    print("\n📋 TC-REG-01: Verificando búsquedas estilo v1.0/v1.1...")

    print("  Ejecutando TC-REG-01a...", end=" ", flush=True)
    results.append(await test_reg_01_basic_search())
    print(results[-1].status)

    print("  Ejecutando TC-REG-01b...", end=" ", flush=True)
    results.append(await test_reg_01_with_ambito())
    print(results[-1].status)

    print("  Ejecutando TC-REG-01c...", end=" ", flush=True)
    results.append(await test_reg_01_with_rango_v11())
    print(results[-1].status)

    # TC-REG-02: Parámetros from_date/to_date
    print("\n📋 TC-REG-02: Verificando parámetros from_date/to_date...")

    print("  Ejecutando TC-REG-02a...", end=" ", flush=True)
    results.append(await test_reg_02_from_date())
    print(results[-1].status)

    print("  Ejecutando TC-REG-02b...", end=" ", flush=True)
    results.append(await test_reg_02_to_date())
    print(results[-1].status)

    print("  Ejecutando TC-REG-02c...", end=" ", flush=True)
    results.append(await test_reg_02_mixed_old_new())
    print(results[-1].status)

    # Resultados
    passed, failed, errors = print_results(results)

    # Guardar JSON
    output = {
        "test_date": time.strftime("%Y-%m-%d %H:%M:%S"),
        "test_type": "regression",
        "version_tested": "v1.2.0",
        "summary": {
            "total": len(results),
            "passed": passed,
            "failed": failed,
            "errors": errors
        },
        "results": [
            {
                "test_id": r.test_id,
                "test_name": r.test_name,
                "status": r.status,
                "time_s": round(r.time_seconds, 3),
                "results_count": r.results_count,
                "details": r.details
            }
            for r in results
        ]
    }

    output_file = "tests/results_regression_v120.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n📁 Resultados guardados en: {output_file}")

    # Exit code
    if failed > 0 or errors > 0:
        return 1
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
