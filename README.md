# Codex Voice

A local Python client for talking to Codex while it works in a project folder.

The first milestone is to send one typed request to Codex, display its final reply, and read it aloud. Microphone input and a chat window can come later.

## Primeiro teste no terminal

No Linux, use Python 3, o Codex CLI autenticado e o Speech Dispatcher
(`spd-say`) com um sintetizador de português do Brasil e áudio configurado.

```sh
python3 codex_voice.py /caminho/do/projeto
```

Digite o pedido e pressione Enter. O Codex executa na pasta indicada com
permissão de escrita no projeto. O script exibe a resposta final e solicita
a leitura em PT-BR ao sintetizador local. Cada execução recebe um pedido.
A qualidade da voz depende do sintetizador instalado.

## Ouvir com a voz aprovada

Em Linux com Python 3.9 ou mais recente e `gst-play-1.0`, reproduza
a segunda leitura aprovada do trecho de Fernando Pessoa:

```sh
python3 speak.py --sample
```

Para ouvir outro trecho:

```sh
printf '%s\n' 'Já conferi os arquivos. Podemos seguir.' | python3 speak.py
```

O script envia até 300 caracteres à demo pública do Chatterbox PT-BR
no Hugging Face. Envie somente texto que possa compartilhar com a demo.
A síntese usa o serviço da demo e não faz uma chamada ao Codex. A fila
pública pode afetar a espera. O script de terminal acima usa o sintetizador
local do sistema.

## Usar em outra conversa com Codex

Diga ao Codex: “Leia o AGENTS.md do repositório codex-voice e use o
speak.py quando eu pedir para me responder em voz alta.” A leitura é
acionada pelo agente quando pedida na conversa.
