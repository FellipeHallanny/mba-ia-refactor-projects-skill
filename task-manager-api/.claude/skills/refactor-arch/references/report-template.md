# Template Padronizado de Relatório de Auditoria (Phase 2)

Este documento define o formato oficial e obrigatório para a saída da **Fase 2: Architecture Audit**. Todo relatório gerado pela skill deve obedecer rigorosamente a esta estrutura para garantir padronização entre diferentes ferramentas e projetos.

---

## Formato do Relatório

```markdown
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome-do-projeto>
Stack:   <Linguagem + Framework>
Files:   <quantidade> analyzed | ~<linhas> lines of code

## Summary
CRITICAL: <count> | HIGH: <count> | MEDIUM: <count> | LOW: <count>

## Findings

### [<SEVERITY>] <Título do Anti-pattern / Vulnerabilidade>
File: <caminho/do/arquivo>:<linhas-exatas>
Description: <Explicação detalhada do problema observado no código>
Impact: <Impacto arquitetural, de segurança, de performance ou de manutenção>
Recommendation: <Ação corretiva prescrita baseada no playbook de refatoração>

[... repetir para cada finding identificado, ordenado de CRITICAL para LOW ...]

================================
Total: <total_findings> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

---

## Regras de Preenchimento:
1. **Identificação Exata**: Todo finding deve conter obrigatoriamente o caminho do arquivo e o intervalo ou número da linha onde o problema ocorre (ex: `models.py:28-35` ou `src/utils.js:3`).
2. **Ordenação Obrigatória**: Findings devem ser ordenados estritamente por severidade:
   - Primeiro todos os `[CRITICAL]`
   - Em seguida todos os `[HIGH]`
   - Depois todos os `[MEDIUM]`
   - Por fim todos os `[LOW]`
3. **Mínimo de Findings**: O relatório deve listar no mínimo 5 problemas e conter pelo menos 1 de severidade `CRITICAL` ou `HIGH`.
4. **Pausa Interativa**: O encerramento do relatório deve conter a pergunta `Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]`.
