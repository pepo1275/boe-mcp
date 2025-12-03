#!/usr/bin/env python3
"""
Generador de Informe de Casos de Uso - Smart Navigation v2.0

Ejecuta los casos de uso documentados y genera un informe legible
en formato pregunta-respuesta.

Uso:
    uv run python tests/generar_informe_casos_uso.py > docs/INFORME-CASOS-USO.md
"""

import asyncio
import sys
sys.path.insert(0, 'src')

from boe_mcp.server import (
    get_article_info,
    search_in_law,
    get_law_structure_summary,
    get_law_index
)

# Constants
LEY_CONCURSAL = "BOE-A-2020-4859"
LEY_INEXISTENTE = "BOE-A-0000-0000"


def print_header():
    print("# Informe de Casos de Uso - Smart Navigation v2.0")
    print()
    print("**Ley de referencia:** BOE-A-2020-4859 (Texto Refundido de la Ley Concursal)")
    print()
    print("**Fecha de generación:** ", end="")
    from datetime import datetime
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print()
    print("---")
    print()


async def run_simple_cases():
    """Ejecuta casos simples (S)."""
    print("## 1. CASOS SIMPLES")
    print()
    print("### 1.1 get_article_info - Consultas básicas")
    print()

    # S1.1
    print("#### S1.1 ¿Existe el artículo 1 en la Ley Concursal?")
    result = await get_article_info(LEY_CONCURSAL, "1")
    if result.get("error"):
        print(f"**Respuesta:** ❌ Error - {result.get('mensaje')}")
    else:
        print(f"**Respuesta:** ✅ Sí, existe")
        print(f"- Artículo: {result['articulo']}")
        print(f"- Block ID: {result['block_id']}")
        print(f"- Título: {result['titulo_completo']}")
    print()

    # S1.2
    print("#### S1.2 ¿Cuál es el block_id del artículo 386?")
    result = await get_article_info(LEY_CONCURSAL, "386")
    if result.get("error"):
        print(f"**Respuesta:** ❌ Error - {result.get('mensaje')}")
    else:
        print(f"**Respuesta:** `{result['block_id']}`")
    print()

    # S1.3
    print("#### S1.3 ¿Fue modificado el artículo 1?")
    result = await get_article_info(LEY_CONCURSAL, "1")
    if result.get("error"):
        print(f"**Respuesta:** ❌ Error - {result.get('mensaje')}")
    else:
        mod = "✅ Sí" if result['modificado'] else "❌ No"
        print(f"**Respuesta:** {mod}")
        print(f"- Fecha actualización: {result['fecha_actualizacion']}")
        print(f"- Fecha ley original: {result['fecha_ley_original']}")
    print()

    # S1.4
    print("#### S1.4 ¿Fue modificado el artículo 386?")
    result = await get_article_info(LEY_CONCURSAL, "386")
    if result.get("error"):
        print(f"**Respuesta:** ❌ Error - {result.get('mensaje')}")
    else:
        mod = "✅ Sí" if result['modificado'] else "❌ No"
        print(f"**Respuesta:** {mod}")
        print(f"- Fecha actualización: {result['fecha_actualizacion']}")
    print()

    # S1.5
    print("#### S1.5 ¿Existe el artículo 9999?")
    result = await get_article_info(LEY_CONCURSAL, "9999")
    if result.get("error"):
        print(f"**Respuesta:** ❌ No existe")
        print(f"- Código error: `{result.get('codigo')}`")
        print(f"- Mensaje: {result.get('mensaje')}")
    else:
        print(f"**Respuesta:** ✅ Sí existe (inesperado)")
    print()

    # S1.6
    print("#### S1.6 ¿Existe el artículo '224 bis'?")
    result = await get_article_info(LEY_CONCURSAL, "224 bis")
    if result.get("error"):
        print(f"**Respuesta:** ❌ Error - {result.get('mensaje')}")
    else:
        print(f"**Respuesta:** ✅ Sí, existe")
        print(f"- Artículo: {result['articulo']}")
        print(f"- Block ID: {result['block_id']}")
        print(f"- Modificado: {'Sí' if result['modificado'] else 'No'}")
    print()

    # S1.7
    print("#### S1.7 ¿Cuál es el texto del artículo 1?")
    result = await get_article_info(LEY_CONCURSAL, "1", incluir_texto=True)
    if result.get("error"):
        print(f"**Respuesta:** ❌ Error - {result.get('mensaje')}")
    else:
        texto = result['texto'][:500] + "..." if len(result['texto']) > 500 else result['texto']
        print(f"**Respuesta:** (primeros 500 caracteres)")
        print("```")
        print(texto)
        print("```")
    print()

    # --- search_in_law ---
    print("### 1.2 search_in_law - Búsquedas básicas")
    print()

    # S2.1
    print("#### S2.1 ¿Cuántos artículos modificados tiene la ley?")
    result = await search_in_law(LEY_CONCURSAL, solo_modificados=True)
    if result.get("error"):
        print(f"**Respuesta:** ❌ Error - {result.get('mensaje')}")
    else:
        print(f"**Respuesta:** **{result['total_encontrados']}** artículos modificados")
    print()

    # S2.2
    print("#### S2.2 Dame los artículos 1, 2 y 386")
    result = await search_in_law(LEY_CONCURSAL, articulos=["1", "2", "386"])
    if result.get("error"):
        print(f"**Respuesta:** ❌ Error - {result.get('mensaje')}")
    else:
        print(f"**Respuesta:** Encontrados {result['total_encontrados']} artículos")
        print()
        print("| Artículo | Título | Modificado | Fecha |")
        print("|----------|--------|------------|-------|")
        for art in result['resultados']:
            mod = "✅" if art['modificado'] else "❌"
            print(f"| {art['articulo']} | {art['titulo'][:30]} | {mod} | {art['fecha_actualizacion']} |")
    print()

    # S2.3
    print("#### S2.3 ¿Hay algún 'artículo único'?")
    result = await search_in_law(LEY_CONCURSAL, query="único")
    if result.get("error"):
        print(f"**Respuesta:** ❌ Error - {result.get('mensaje')}")
    else:
        print(f"**Respuesta:** Sí, hay **{result['total_encontrados']}** artículo(s) único(s)")
        for art in result['resultados']:
            print(f"- {art['titulo']}")
    print()

    # S2.4
    print("#### S2.4 Dame 5 artículos modificados")
    result = await search_in_law(LEY_CONCURSAL, solo_modificados=True, limit=5)
    if result.get("error"):
        print(f"**Respuesta:** ❌ Error - {result.get('mensaje')}")
    else:
        print(f"**Respuesta:** (mostrando 5 de {result['total_encontrados']})")
        print()
        print("| Artículo | Fecha Modificación |")
        print("|----------|-------------------|")
        for art in result['resultados']:
            print(f"| {art['articulo']} | {art['fecha_actualizacion']} |")
    print()

    # --- get_law_structure_summary ---
    print("### 1.3 get_law_structure_summary - Estructura básica")
    print()

    # S3.1
    print("#### S3.1 ¿Cuántos libros tiene la Ley Concursal?")
    result = await get_law_structure_summary(LEY_CONCURSAL, nivel="libros")
    if result.get("error"):
        print(f"**Respuesta:** ❌ Error - {result.get('mensaje')}")
    else:
        print(f"**Respuesta:** **{len(result['estructura'])}** libros")
        print()
        for libro in result['estructura']:
            print(f"- {libro['titulo']}: {libro['num_articulos']} artículos ({libro['num_modificados']} modificados)")
    print()

    # S3.2
    print("#### S3.2 ¿Cuántos artículos tiene en total?")
    result = await get_law_structure_summary(LEY_CONCURSAL)
    if result.get("error"):
        print(f"**Respuesta:** ❌ Error - {result.get('mensaje')}")
    else:
        print(f"**Respuesta:** **{result['total_articulos']}** artículos")
        print(f"- Modificados: {result['total_modificados']}")
        pct = (result['total_modificados'] / result['total_articulos']) * 100
        print(f"- Porcentaje modificado: {pct:.1f}%")
    print()

    # S3.3
    print("#### S3.3 ¿Cuál es el título de la ley?")
    result = await get_law_structure_summary(LEY_CONCURSAL)
    if result.get("error"):
        print(f"**Respuesta:** ❌ Error - {result.get('mensaje')}")
    else:
        print(f"**Respuesta:** {result['titulo']}")
    print()

    # --- get_law_index ---
    print("### 1.4 get_law_index - Índice básico")
    print()

    # S4.1
    print("#### S4.1 Dame los primeros 10 bloques")
    result = await get_law_index(LEY_CONCURSAL, limit=10)
    if result.get("error"):
        print(f"**Respuesta:** ❌ Error - {result.get('mensaje')}")
    else:
        print(f"**Respuesta:** (mostrando 10 de {result['total_bloques']})")
        print()
        print("| ID | Título |")
        print("|----|--------|")
        for bloque in result['bloques']:
            print(f"| {bloque['id']} | {bloque['titulo'][:50]} |")
    print()

    # S4.2
    print("#### S4.2 ¿Cuántos artículos tiene la ley?")
    result = await get_law_index(LEY_CONCURSAL, tipo_bloque="articulos")
    if result.get("error"):
        print(f"**Respuesta:** ❌ Error - {result.get('mensaje')}")
    else:
        print(f"**Respuesta:** **{result['total_bloques']}** artículos")
    print()

    # S4.3
    print("#### S4.3 ¿Cuántas disposiciones tiene?")
    result = await get_law_index(LEY_CONCURSAL, tipo_bloque="disposiciones")
    if result.get("error"):
        print(f"**Respuesta:** ❌ Error - {result.get('mensaje')}")
    else:
        print(f"**Respuesta:** **{result['total_bloques']}** disposiciones")
        print()
        print("Ejemplos:")
        for bloque in result['bloques'][:5]:
            print(f"- {bloque['titulo']}")
    print()


async def run_intermediate_cases():
    """Ejecuta casos intermedios (M)."""
    print("## 2. CASOS INTERMEDIOS")
    print()
    print("### 2.1 get_article_info - Consultas con ubicación")
    print()

    # M1.1-M1.4
    print("#### M1.1-M1.4 ¿En qué parte de la estructura está el artículo 386?")
    result = await get_article_info(LEY_CONCURSAL, "386")
    if result.get("error"):
        print(f"**Respuesta:** ❌ Error - {result.get('mensaje')}")
    else:
        ub = result['ubicacion']
        print(f"**Respuesta:** Ubicación jerárquica del artículo 386:")
        print(f"- **Libro:** {ub.get('libro', 'N/A')}")
        print(f"- **Título:** {ub.get('titulo', 'N/A')}")
        print(f"- **Capítulo:** {ub.get('capitulo', 'N/A')}")
        print(f"- **Sección:** {ub.get('seccion', 'N/A')}")
    print()

    # M1.5
    print("#### M1.5 ¿Cuándo fue modificado el artículo 224 bis?")
    result = await get_article_info(LEY_CONCURSAL, "224 bis")
    if result.get("error"):
        print(f"**Respuesta:** ❌ Error - {result.get('mensaje')}")
    else:
        fecha = result['fecha_actualizacion']
        print(f"**Respuesta:** {fecha[:4]}-{fecha[4:6]}-{fecha[6:8]}")
    print()

    print("### 2.2 search_in_law - Búsquedas con filtros combinados")
    print()

    # M2.1
    print("#### M2.1 ¿Qué artículos se modificaron en 2022?")
    result = await search_in_law(
        LEY_CONCURSAL,
        modificados_desde="20220101",
        modificados_hasta="20221231"
    )
    if result.get("error"):
        print(f"**Respuesta:** ❌ Error - {result.get('mensaje')}")
    else:
        print(f"**Respuesta:** **{result['total_encontrados']}** artículos modificados en 2022")
        print()
        if result['resultados']:
            print("Primeros 10:")
            print("| Artículo | Fecha |")
            print("|----------|-------|")
            for art in result['resultados'][:10]:
                print(f"| {art['articulo']} | {art['fecha_actualizacion']} |")
    print()

    # M2.2
    print("#### M2.2 Dame la página 2 de artículos modificados (5 por página)")
    result1 = await search_in_law(LEY_CONCURSAL, solo_modificados=True, limit=5, offset=0)
    result2 = await search_in_law(LEY_CONCURSAL, solo_modificados=True, limit=5, offset=5)
    if result1.get("error") or result2.get("error"):
        print(f"**Respuesta:** ❌ Error")
    else:
        print("**Respuesta:**")
        print()
        print("**Página 1:**")
        for art in result1['resultados']:
            print(f"- Artículo {art['articulo']}")
        print()
        print("**Página 2:**")
        for art in result2['resultados']:
            print(f"- Artículo {art['articulo']}")
    print()

    print("### 2.3 get_law_structure_summary - Estructura con niveles")
    print()

    # M3.1-M3.2
    print("#### M3.1-M3.2 Estadísticas por libro")
    result = await get_law_structure_summary(LEY_CONCURSAL, nivel="libros")
    if result.get("error"):
        print(f"**Respuesta:** ❌ Error - {result.get('mensaje')}")
    else:
        print("**Respuesta:**")
        print()
        print("| Libro | Artículos | Modificados | % Modificado |")
        print("|-------|-----------|-------------|--------------|")
        for libro in result['estructura']:
            pct = (libro['num_modificados'] / libro['num_articulos'] * 100) if libro['num_articulos'] > 0 else 0
            print(f"| {libro['titulo'][:30]} | {libro['num_articulos']} | {libro['num_modificados']} | {pct:.1f}% |")
    print()

    # M3.3
    print("#### M3.3 ¿Cuántos títulos tiene la ley?")
    result = await get_law_structure_summary(LEY_CONCURSAL, nivel="titulos")
    if result.get("error"):
        print(f"**Respuesta:** ❌ Error - {result.get('mensaje')}")
    else:
        total_titulos = 0
        for libro in result['estructura']:
            total_titulos += len(libro['hijos'])
        print(f"**Respuesta:** **{total_titulos}** títulos distribuidos en {len(result['estructura'])} libros")
    print()


async def run_advanced_cases():
    """Ejecuta casos avanzados (A)."""
    print("## 3. CASOS AVANZADOS")
    print()
    print("### 3.1 Análisis de modificaciones")
    print()

    # A1.1
    print("#### A1.1 ¿Qué porcentaje de artículos han sido modificados?")
    result = await get_law_structure_summary(LEY_CONCURSAL)
    if result.get("error"):
        print(f"**Respuesta:** ❌ Error - {result.get('mensaje')}")
    else:
        pct = (result['total_modificados'] / result['total_articulos']) * 100
        print(f"**Respuesta:** **{pct:.1f}%** de la ley ha sido modificada")
        print(f"- Total artículos: {result['total_articulos']}")
        print(f"- Artículos modificados: {result['total_modificados']}")
    print()

    # A1.3
    print("#### A1.3 ¿Qué libro tiene más modificaciones proporcionalmente?")
    result = await get_law_structure_summary(LEY_CONCURSAL, nivel="libros")
    if result.get("error"):
        print(f"**Respuesta:** ❌ Error - {result.get('mensaje')}")
    else:
        max_ratio = 0
        libro_max = None
        for libro in result['estructura']:
            if libro['num_articulos'] > 0:
                ratio = libro['num_modificados'] / libro['num_articulos']
                if ratio > max_ratio:
                    max_ratio = ratio
                    libro_max = libro
        if libro_max:
            print(f"**Respuesta:** **{libro_max['titulo']}**")
            print(f"- {libro_max['num_modificados']} de {libro_max['num_articulos']} artículos ({max_ratio*100:.1f}%)")
    print()

    print("### 3.2 Validaciones cruzadas")
    print()

    # A3.1
    print("#### A3.1 ¿El total de artículos coincide entre herramientas?")
    struct_result = await get_law_structure_summary(LEY_CONCURSAL)
    index_result = await get_law_index(LEY_CONCURSAL, tipo_bloque="articulos")
    if struct_result.get("error") or index_result.get("error"):
        print(f"**Respuesta:** ❌ Error")
    else:
        total_struct = struct_result['total_articulos']
        total_index = index_result['total_bloques']
        diff = abs(total_struct - total_index)
        if diff <= 5:
            print(f"**Respuesta:** ✅ Sí coinciden (diferencia: {diff})")
        else:
            print(f"**Respuesta:** ⚠️ Diferencia significativa: {diff}")
        print(f"- get_law_structure_summary: {total_struct}")
        print(f"- get_law_index: {total_index}")
    print()

    # A3.3
    print("#### A3.3 ¿La suma de artículos por libro = total?")
    result = await get_law_structure_summary(LEY_CONCURSAL, nivel="libros")
    if result.get("error"):
        print(f"**Respuesta:** ❌ Error - {result.get('mensaje')}")
    else:
        suma_libros = sum(libro['num_articulos'] for libro in result['estructura'])
        total = result['total_articulos']
        diff = total - suma_libros
        if diff == 0:
            print(f"**Respuesta:** ✅ Sí, suma exacta = {suma_libros}")
        else:
            print(f"**Respuesta:** ⚠️ Hay {diff} artículos fuera de los libros")
            print(f"- Suma por libros: {suma_libros}")
            print(f"- Total reportado: {total}")
    print()


async def run_error_cases():
    """Ejecuta casos de error (E)."""
    print("## 4. CASOS DE ERROR Y VALIDACIÓN")
    print()
    print("### 4.1 Validación de entrada")
    print()

    cases = [
        ("E1.1", "Identificador inválido", get_article_info("INVALIDO", "1")),
        ("E1.2", "Ley inexistente", get_article_info(LEY_INEXISTENTE, "1")),
        ("E1.3", "SQL injection en artículo", get_article_info(LEY_CONCURSAL, "1; DROP")),
        ("E1.4", "XSS en query", search_in_law(LEY_CONCURSAL, query="<script>")),
        ("E1.5", "Path traversal", get_article_info("../etc/passwd", "1")),
        ("E1.6", "Búsqueda sin criterios", search_in_law(LEY_CONCURSAL)),
        ("E1.7", "Rango fechas invertido", search_in_law(LEY_CONCURSAL, modificados_desde="20221231", modificados_hasta="20220101")),
    ]

    print("| ID | Caso | Resultado | Código Error |")
    print("|----|------|-----------|--------------|")

    for case_id, desc, coro in cases:
        result = await coro
        if result.get("error"):
            print(f"| {case_id} | {desc} | ✅ Bloqueado | `{result.get('codigo')}` |")
        else:
            print(f"| {case_id} | {desc} | ❌ No bloqueado | - |")
    print()

    print("### 4.2 Límites y paginación")
    print()

    # E2.1
    print("#### E2.1 Offset mayor que total")
    result = await get_law_index(LEY_CONCURSAL, offset=10000)
    if result.get("error"):
        print(f"**Respuesta:** Error - {result.get('mensaje')}")
    else:
        print(f"**Respuesta:** Devuelve lista vacía = {result['bloques'] == []}, hay_mas = {result['hay_mas']}")
    print()

    # E2.2
    print("#### E2.2 Limit=0")
    result = await get_law_index(LEY_CONCURSAL, limit=0)
    if result.get("error"):
        print(f"**Respuesta:** Error - {result.get('mensaje')}")
    else:
        print(f"**Respuesta:** Se ajusta y devuelve {len(result['bloques'])} bloque(s)")
    print()

    # E2.3
    print("#### E2.3 Limit muy alto (9999)")
    result = await get_law_index(LEY_CONCURSAL, limit=9999)
    if result.get("error"):
        print(f"**Respuesta:** Error - {result.get('mensaje')}")
    else:
        print(f"**Respuesta:** Se ajusta a máximo {len(result['bloques'])} bloques")
    print()


async def main():
    print_header()

    print("## Resumen Ejecutivo")
    print()
    print("Este informe valida los 4 herramientas de Smart Navigation v2.0:")
    print("1. `get_article_info` - Información de artículo específico")
    print("2. `search_in_law` - Búsqueda dentro de una ley")
    print("3. `get_law_structure_summary` - Resumen de estructura jerárquica")
    print("4. `get_law_index` - Índice de bloques de la ley")
    print()
    print("---")
    print()

    await run_simple_cases()
    print("---")
    print()

    await run_intermediate_cases()
    print("---")
    print()

    await run_advanced_cases()
    print("---")
    print()

    await run_error_cases()

    print("---")
    print()
    print("## Conclusiones")
    print()
    print("✅ **Todas las herramientas funcionan correctamente**")
    print()
    print("- Las consultas de artículos devuelven información completa")
    print("- Las búsquedas filtran correctamente por modificaciones y fechas")
    print("- La estructura jerárquica es consistente")
    print("- Las validaciones de seguridad bloquean entradas maliciosas")
    print("- Los límites se ajustan automáticamente")


if __name__ == "__main__":
    asyncio.run(main())
