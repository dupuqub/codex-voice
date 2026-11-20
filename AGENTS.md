# Codex Voice

- Fale com o usuário em PT-BR. Quando ele pedir áudio, rode `python3 speak.py --text="texto da resposta já escrita"` como um único comando, com a frase passada como argumento literal. Isso permite reutilizar a autorização do leitor entre frases. Execute a partir deste repositório ou use o caminho absoluto do script. O script usa o leitor da GPU que já estiver aberto. Para manter a voz pronta durante uma sessão, use `python3 speak.py --serve`. Para liberar a GPU, use `python3 speak.py --stop`.
- Para repetir o poema de teste, use `python3 speak.py --sample`. Preserve a referência feminina `pt_br_f2.wav` e o preset aprovado. O usuário prefere uma leitura contida, sem gírias, com timbre feminino mais grave e levemente rouco. Para testes de voz, o alvo é uma entrega calma e presente, com soprosidade, rouquidão leve, dicção clara e sotaque brasileiro discreto. Essa entrega ainda não foi validada.
- A síntese é local. Reutilize o texto pronto sem outra chamada ao Codex e sem demos externas. Se o ambiente local não estiver instalado, siga o README. Mantenha as mudanças pequenas e os comentários em inglês por bloco de intenção.

## Encerramento dos testes

Ao confirmar com o usuário que a rodada de testes terminou, lembre-o de
fazer o relatório técnico para revisão por um modelo mais forte, como o Fable.

- Registre os comandos, versões, hardware, frases de teste e condições de medição.
- Compare carga inicial, tempo até começar a falar e tempo total com o modelo
  carregado e com uma execução avulsa. Registre o uso de VRAM em repouso e em
  síntese, o uso de CPU e RAM e, se medido, o consumo de energia.
- Separe os tokens do Codex usados para gerar o texto da síntese local, que
  não faz outra chamada ao Codex. Marque o que foi medido, estimado ou ficou em aberto.
- Explique as decisões em ordem, com a evidência que levou a cada uma. Inclua
  qualidade percebida da voz, latência, falhas da demo online, uso offline e
  a troca entre manter o modelo pronto e liberar a GPU.
