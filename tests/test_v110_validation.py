"""
Triple Validation Tests for v1.1.0 - New Search Parameters

RPVEA 2.0 Methodology:
- V1: API directa (curl) - Ya validado manualmente
- V2: MCP local - Este archivo
- V3: MCP integrado - Requiere cliente MCP
"""

import asyncio
import json
import sys
sys.path.insert(0, "src")

from boe_mcp.server import search_laws_list


async def test_v1_rango_codigo():
    """
    V2 Test: rango_codigo parameter

    Expected: Solo devuelve Leyes (rango.codigo = 1300)
    """
    print("\n" + "="*60)
    print("TEST V2.1: rango_codigo='1300' (Solo Leyes)")
    print("="*60)

    result = await search_laws_list(
        rango_codigo="1300",
        limit=3
    )

    if isinstance(result, str):
        print(f"ERROR: {result}")
        return False

    # Verificar que la query se construyó correctamente
    params = result.get("params", {})
    query_str = params.get("query", "")

    print(f"\nQuery generada: {query_str[:200]}...")

    # Verificar resultados
    data = result.get("data", {}).get("data", [])
    print(f"\nResultados: {len(data)} normas")

    all_leyes = True
    for item in data[:3]:
        rango = item.get("rango", {})
        codigo = rango.get("codigo")
        texto = rango.get("texto")
        titulo = item.get("titulo", "")[:60]
        print(f"  - [{codigo}] {texto}: {titulo}...")
        if codigo != "1300":
            all_leyes = False

    if all_leyes:
        print("\n✅ PASS: Todos los resultados son Leyes (1300)")
        return True
    else:
        print("\n❌ FAIL: Algunos resultados no son Leyes")
        return False


async def test_v2_materia_codigo():
    """
    V2 Test: materia_codigo parameter

    Expected: Filtra por materia temática
    """
    print("\n" + "="*60)
    print("TEST V2.2: materia_codigo='2557' (Protección de datos)")
    print("="*60)

    result = await search_laws_list(
        materia_codigo="2557",
        limit=3
    )

    if isinstance(result, str):
        print(f"ERROR: {result}")
        return False

    params = result.get("params", {})
    query_str = params.get("query", "")

    print(f"\nQuery generada: {query_str[:200]}...")

    # Verificar que contiene el filtro de materia
    if 'materia@codigo:\\"2557\\"' in query_str or 'materia@codigo:"2557"' in query_str:
        print("\n✅ PASS: Query contiene filtro de materia correcto")
    else:
        print(f"\n❌ FAIL: Query no contiene filtro de materia esperado")
        print(f"   Query: {query_str}")
        return False

    data = result.get("data", {}).get("data", [])
    print(f"\nResultados: {len(data)} normas")

    for item in data[:3]:
        titulo = item.get("titulo", "")[:80]
        print(f"  - {titulo}...")

    return len(data) > 0


async def test_v3_numero_oficial():
    """
    V2 Test: numero_oficial parameter

    Expected: Devuelve la Ley 39/2015 exacta
    """
    print("\n" + "="*60)
    print("TEST V2.3: numero_oficial='39/2015' (Ley Procedimiento)")
    print("="*60)

    result = await search_laws_list(
        numero_oficial="39/2015",
        limit=5
    )

    if isinstance(result, str):
        print(f"ERROR: {result}")
        return False

    params = result.get("params", {})
    query_str = params.get("query", "")

    print(f"\nQuery generada: {query_str[:200]}...")

    data = result.get("data", {}).get("data", [])
    print(f"\nResultados: {len(data)} normas")

    found_39_2015 = False
    for item in data:
        num = item.get("numero_oficial", "")
        identificador = item.get("identificador", "")
        titulo = item.get("titulo", "")[:60]
        print(f"  - [{num}] {identificador}: {titulo}...")
        if num == "39/2015" and "BOE-A-2015-10565" in identificador:
            found_39_2015 = True

    if found_39_2015:
        print("\n✅ PASS: Encontrada Ley 39/2015 (BOE-A-2015-10565)")
        return True
    else:
        print("\n❌ FAIL: No se encontró la Ley 39/2015 exacta")
        return False


async def test_v4_combinacion():
    """
    V2 Test: Combinación de parámetros nuevos + existentes

    Expected: rango_codigo + ambito funcionan juntos
    """
    print("\n" + "="*60)
    print("TEST V2.4: rango_codigo='1290' + ambito='Estatal' (LO Estatales)")
    print("="*60)

    result = await search_laws_list(
        rango_codigo="1290",  # Ley Orgánica (código correcto)
        ambito="Estatal",
        limit=3
    )

    if isinstance(result, str):
        print(f"ERROR: {result}")
        return False

    params = result.get("params", {})
    query_str = params.get("query", "")

    print(f"\nQuery generada:")
    # Pretty print la query
    try:
        query_obj = json.loads(query_str)
        print(json.dumps(query_obj, indent=2, ensure_ascii=False)[:500])
    except:
        print(query_str[:300])

    data = result.get("data", {}).get("data", [])
    print(f"\nResultados: {len(data)} normas")

    all_correct = True
    for item in data[:3]:
        rango_txt = item.get("rango", {}).get("texto", "")
        rango_cod = item.get("rango", {}).get("codigo", "")
        ambito_txt = item.get("ambito", {}).get("texto", "")
        titulo = item.get("titulo", "")[:50]
        print(f"  - [{rango_cod}:{rango_txt}] [{ambito_txt}]: {titulo}...")
        if rango_cod != "1290" or ambito_txt != "Estatal":
            all_correct = False

    if all_correct and len(data) > 0:
        print("\n✅ PASS: Combinación de filtros funciona")
        return True
    else:
        print("\n❌ FAIL: Combinación de filtros no funciona correctamente")
        return False


async def main():
    """Ejecuta todos los tests de validación V2"""
    print("\n" + "#"*60)
    print("# TRIPLE VALIDACIÓN - NIVEL V2: MCP LOCAL")
    print("# v1.1.0 - Nuevos parámetros de búsqueda")
    print("#"*60)

    results = []

    results.append(("rango_codigo", await test_v1_rango_codigo()))
    results.append(("materia_codigo", await test_v2_materia_codigo()))
    results.append(("numero_oficial", await test_v3_numero_oficial()))
    results.append(("combinacion", await test_v4_combinacion()))

    print("\n" + "="*60)
    print("RESUMEN V2")
    print("="*60)

    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name}: {status}")
        if result:
            passed += 1

    print(f"\nTotal: {passed}/{len(results)} tests passed")

    if passed == len(results):
        print("\n🎉 V2 VALIDACIÓN COMPLETA - MCP LOCAL OK")
        return 0
    else:
        print("\n⚠️ V2 VALIDACIÓN INCOMPLETA - Revisar fallos")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
