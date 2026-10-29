# Checklist de Revisão Técnica e Editorial

Use a cada troca do runtime adotado ou, no mínimo, a cada semestre. Registre os achados em `06_revisao-evolucao/revisao-editorial-AAAA-MM.md`.

## Antes de começar

- [ ] Runtime-alvo definido (versão do Databricks Runtime / DBSQL e do Spark).
- [ ] Release notes desde a última revisão lidas (Databricks SQL, Databricks Runtime, Delta Lake, Spark).

## Por arquivo

1. **Correção**
   - [ ] Sintaxe e funções existem no runtime-alvo.
   - [ ] Blocos Python são válidos (sem `\` de continuação seguido de comentário; prefira encadeamento entre parênteses).
   - [ ] A semântica descrita confere com a documentação oficial.
2. **Defasagem**
   - [ ] Recomendação não foi superada por recurso mais novo (layout de tabela, tipos, governança, APIs).
   - [ ] Caminhos e práticas legadas (`/mnt`, DBFS root, global temp views) estão sinalizados ou substituídos.
3. **Didática**
   - [ ] Explica o porquê, o limite e o trade-off, não só o comando.
   - [ ] Exemplo mínimo, executável e com nomes realistas.
   - [ ] Nenhuma afirmação absoluta ou número sem fonte.
4. **Tom**
   - [ ] Neutro e técnico; sem exageros, gírias ou caixa alta para ênfase.
   - [ ] Português com acentuação; termos técnicos em inglês só quando são o nome do recurso.
5. **Portabilidade e versão**
   - [ ] Recursos específicos do Databricks estão identificados.
   - [ ] Versão mínima indicada quando relevante.
   - [ ] Link para a documentação oficial nos temas dependentes de versão.
6. **Lacunas**
   - [ ] O que se espera do tema e não está no arquivo foi listado (não escrito direto: vai para o backlog para decisão).

## Depois

- [ ] Blocos Python verificados com `ast.parse` e funções testadas em Spark local quando possível.
- [ ] `python build_docs.py` sem erros.
- [ ] Banco de desafios ajustado se seções `##` foram criadas, renomeadas ou removidas.
- [ ] Backlog e avaliações de cobertura atualizados.
