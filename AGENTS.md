# Codex Voice

- Fale com o usuário em PT-BR. Quando ele pedir áudio, envie o texto da resposta já escrita para `python3 speak.py` pela entrada padrão. Execute a partir deste repositório ou use o caminho absoluto do script. O script usa o leitor da GPU que já estiver aberto. Para manter a voz pronta durante uma sessão, use `python3 speak.py --serve`. Para liberar a GPU, use `python3 speak.py --stop`.
- Para repetir o poema de teste, use `python3 speak.py --sample`. Preserve a referência feminina `pt_br_f2.wav` e o preset aprovado. O usuário prefere uma leitura contida, sem gírias, com timbre feminino mais grave e levemente rouco. Um leve sotaque do interior paulista é uma preferência de voz, ainda sem teste específico.
- A síntese é local. Reutilize o texto pronto sem outra chamada ao Codex e sem demos externas. Se o ambiente local não estiver instalado, siga o README. Mantenha as mudanças pequenas e os comentários em inglês por bloco de intenção.
