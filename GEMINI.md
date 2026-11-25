# Antigravity Workspace Guidelines

## Custom Skill: refactor-arch

Este repositório contém a skill **`refactor-arch`**, localizada em `.agents/skills/refactor-arch/SKILL.md` (e compatível com Claude Code em `.claude/skills/refactor-arch/SKILL.md`).

### Invocação da Skill
Sempre que o usuário solicitar `/refactor-arch` ou pedir para analisar, auditar ou refatorar a arquitetura de um projeto para o padrão MVC:
1. Ative a skill **`refactor-arch`** lendo suas instruções em `.agents/skills/refactor-arch/SKILL.md`.
2. Execute rigorosamente as 3 fases sequenciais:
   - **Fase 1 (Project Analysis)**: Detecte linguagem (Python, Node.js, C#/.NET), framework, dependências, tabelas e arquitetura atual, exibindo o banner padrão.
   - **Fase 2 (Architecture Audit)**: Analise o código cruzando contra o catálogo de anti-patterns (`references/anti-patterns.md`), ordene por severidade (CRITICAL -> LOW) e **faça a pausa obrigatória** solicitando confirmação do usuário (`Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]`).
   - **Fase 3 (Refactoring Complete)**: Reestruture a aplicação no padrão MVC conforme `references/mvc-guidelines.md` e `references/refactoring-playbook.md`, garantindo que a aplicação suba e todos os endpoints continuem funcionando.
