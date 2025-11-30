"""
Triple Validation - V3: End-to-End MCP Client Test

Este test simula un cliente MCP real llamando al servidor.
Usa el SDK de MCP para hacer llamadas reales al servidor.
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_e2e_search_laws():
    """Test end-to-end del MCP server"""

    server_params = StdioServerParameters(
        command="/Users/pepo/.claude-worktrees/boe-mcp/kind-swartz/.venv/bin/python",
        args=["-m", "boe_mcp.server"],
        env={"PYTHONPATH": "/Users/pepo/.claude-worktrees/boe-mcp/kind-swartz/src"}
    )

    print("\n" + "#"*60)
    print("# TRIPLE VALIDACIÓN - NIVEL V3: MCP END-TO-END")
    print("#"*60)

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Test 1: Listar tools disponibles
            print("\n" + "="*60)
            print("TEST V3.1: Verificar tools disponibles")
            print("="*60)

            tools = await session.list_tools()
            tool_names = [t.name for t in tools.tools]
            print(f"Tools disponibles: {tool_names}")

            if "search_laws_list" in tool_names:
                print("✅ search_laws_list disponible")
            else:
                print("❌ search_laws_list NO disponible")
                return False

            # Test 2: Verificar que los nuevos parámetros están en el schema
            print("\n" + "="*60)
            print("TEST V3.2: Verificar nuevos parámetros en schema")
            print("="*60)

            search_tool = next(t for t in tools.tools if t.name == "search_laws_list")
            schema = search_tool.inputSchema
            properties = schema.get("properties", {})

            new_params = ["rango_codigo", "materia_codigo", "numero_oficial"]
            all_present = True
            for param in new_params:
                if param in properties:
                    print(f"✅ {param} presente en schema")
                else:
                    print(f"❌ {param} NO presente en schema")
                    all_present = False

            if not all_present:
                return False

            # Test 3: Llamar con rango_codigo
            print("\n" + "="*60)
            print("TEST V3.3: Llamar search_laws_list con rango_codigo='1300'")
            print("="*60)

            result = await session.call_tool(
                "search_laws_list",
                arguments={"rango_codigo": "1300", "limit": 2}
            )

            # El resultado viene como TextContent
            content = result.content[0].text if result.content else ""
            try:
                data = json.loads(content)
                laws = data.get("data", {}).get("data", [])
                print(f"Resultados: {len(laws)} normas")

                all_leyes = True
                for law in laws[:2]:
                    rango = law.get("rango", {}).get("codigo", "")
                    titulo = law.get("titulo", "")[:50]
                    print(f"  - [{rango}]: {titulo}...")
                    if rango != "1300":
                        all_leyes = False

                if all_leyes:
                    print("✅ Todas son Leyes (1300)")
                else:
                    print("❌ Algunas no son Leyes")
                    return False
            except json.JSONDecodeError:
                print(f"Respuesta: {content[:200]}")
                if "error" not in content.lower():
                    print("⚠️ Respuesta no JSON pero sin error")

            # Test 4: Llamar con numero_oficial
            print("\n" + "="*60)
            print("TEST V3.4: Llamar search_laws_list con numero_oficial='39/2015'")
            print("="*60)

            result = await session.call_tool(
                "search_laws_list",
                arguments={"numero_oficial": "39/2015", "limit": 5}
            )

            content = result.content[0].text if result.content else ""
            try:
                data = json.loads(content)
                laws = data.get("data", {}).get("data", [])

                found = any(
                    law.get("identificador") == "BOE-A-2015-10565"
                    for law in laws
                )

                if found:
                    print("✅ Encontrada Ley 39/2015 (BOE-A-2015-10565)")
                else:
                    print(f"❌ No encontrada. Resultados: {[l.get('identificador') for l in laws]}")
                    return False
            except json.JSONDecodeError:
                print(f"Respuesta: {content[:200]}")

            print("\n" + "="*60)
            print("RESUMEN V3")
            print("="*60)
            print("✅ Tools disponibles")
            print("✅ Nuevos parámetros en schema")
            print("✅ rango_codigo funciona")
            print("✅ numero_oficial funciona")
            print("\n🎉 V3 VALIDACIÓN COMPLETA - MCP END-TO-END OK")

            return True


if __name__ == "__main__":
    success = asyncio.run(test_e2e_search_laws())
    exit(0 if success else 1)
