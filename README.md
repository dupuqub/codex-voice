# Codex Voice

Cliente de terminal para pedir ao Codex que trabalhe em um projeto e ouvir
a resposta com a voz local do Chatterbox PT-BR.

## Instalar a voz local

O fluxo foi testado em Linux com uma NVIDIA RTX 3050 de 6 GB. Instale
`uv`, `git`, `curl` e `gst-play-1.0`, e confirme que o driver NVIDIA
funciona com `nvidia-smi`. O instalador prepara Python 3.11.18,
PyTorch 2.8 com CUDA 12.8, o código de inferência e a referência de voz.

```sh
bash setup-local.sh
python3 speak.py --sample
```

O primeiro comando usa internet e baixa cerca de 3 GB de pesos, além
das dependências do PyTorch. Os arquivos ficam em
`${XDG_DATA_HOME:-$HOME/.local/share}/codex-voice`. Para escolher outro
diretório, use a variável `CODEX_VOICE_HOME` na instalação e na execução.
A síntese roda localmente após a instalação.

O preset usa a referência feminina `pt_br_f2.wav`, intensidade 0,35,
temperatura 0,7, semente 31 e CFG 0,32. No teste que confirmou a voz,
o modelo carregou em 17,8 s e sintetizou a resposta em 13,9 s, com pico
de 3,36 GiB de VRAM alocada. Os tempos variam e cada nova execução carrega
o modelo novamente.

## Usar no terminal

Para ler um texto já pronto, envie-o pela entrada padrão:

```sh
printf '%s\n' 'Já conferi os arquivos. Podemos seguir.' | python3 speak.py
```

Para fazer um pedido novo, use o Codex CLI autenticado:

```sh
python3 codex_voice.py /caminho/do/projeto
```

Digite um pedido e pressione Enter. O Codex pode editar arquivos na pasta
indicada. O script exibe a resposta final e a encaminha ao Chatterbox.
A síntese usa a GPU e não faz uma chamada adicional ao Codex.

## Usar em outra conversa com Codex

Diga “Leia o AGENTS.md do codex-voice e use o speak.py quando eu pedir
uma resposta em voz alta.” O agente usa o texto que já escreveu para
acionar a leitura.
