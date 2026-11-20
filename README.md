# Codex Voice

Cliente de terminal para pedir ao Codex que trabalhe em um projeto e ouvir
a resposta com a voz local do Chatterbox PT-BR.

## Instalar a voz local

O fluxo foi testado em Linux com uma NVIDIA RTX 3050 de 6 GB. Instale
`uv`, `git`, `curl`, os plugins base e good do GStreamer e os bindings
PyGObject do GStreamer para o Python do sistema. No Ubuntu, os pacotes de
áudio são `python3-gi`, `gir1.2-gstreamer-1.0`, `gstreamer1.0-plugins-base`
e `gstreamer1.0-plugins-good`. Confirme o driver NVIDIA com `nvidia-smi`. O instalador prepara Python 3.11.18,
PyTorch 2.8 com CUDA 12.8, o código de inferência e a referência de voz.

```sh
bash setup-local.sh
python3 speak.py --sample
```

O primeiro comando usa internet e baixa cerca de 3 GB de pesos, além
das dependências do PyTorch. Os arquivos ficam em
`${XDG_DATA_HOME:-$HOME/.local/share}/codex-voice`. Para escolher outro
diretório, use a variável `CODEX_VOICE_HOME` na instalação e na execução.
A síntese roda localmente após a instalação. O áudio toca a 1,5× com
preservação da altura da voz. A velocidade de geração depende do modelo
e da GPU.

O preset usa a referência feminina `pt_br_f2.wav`, intensidade 0,35,
temperatura 0,7, semente 31 e CFG 0,32. No teste que confirmou a voz,
o modelo carregou em 17,8 s e sintetizou a resposta em 13,9 s, com pico
de 3,36 GiB de VRAM alocada. Os tempos variam.

## Manter a voz pronta na GPU

Em um terminal, rode `python3 speak.py --serve` e espere aparecer
“Voz pronta”. Deixe esse terminal aberto enquanto usar a voz. Em outro
terminal, use os mesmos comandos de leitura abaixo. O leitor reutiliza
o modelo e a referência já carregados. A memória de vídeo fica ocupada
enquanto o leitor está aberto.

Para liberar a GPU, pressione Ctrl+C no terminal do leitor ou rode
`python3 speak.py --stop`. Se o leitor estiver parado, o comando de
leitura carrega o modelo somente para aquela resposta.

## Usar no terminal

Para ler um texto já pronto:

```sh
python3 speak.py --text='Já conferi os arquivos. Podemos seguir.'
```

A entrada padrão continua disponível para integração com outros scripts.

Para fazer um pedido novo, use o Codex CLI autenticado:

```sh
python3 codex_voice.py /caminho/do/projeto
```

Digite um pedido e pressione Enter. O Codex pode editar arquivos na pasta
indicada. O script exibe a resposta final e a encaminha ao Chatterbox.
A síntese usa a GPU e não faz uma chamada adicional ao Codex.

## Usar com outros modelos no Codex do VS Code

Abra o repositório no VS Code ou mantenha uma cópia local dele ao trabalhar
em outro projeto. Se o terminal estiver em WSL ou numa sessão remota,
o leitor e o Codex precisam executar no ambiente Linux que tem acesso ao
mesmo processo local, à GPU e à saída de áudio. Inicie o leitor conforme
a seção acima e espere “Voz pronta”.

Envie esta instrução na outra conversa:

> Leia o AGENTS.md do Codex Voice no caminho local que vou indicar.
> Quando eu pedir uma resposta em voz alta, passe o texto que você já
> escreveu ao speak.py com --text e o caminho absoluto do script.
> Use o leitor local já carregado.

Para confirmar o leitor fora do chat:

```sh
python3 /caminho/para/codex-voice/speak.py --text='Oi, a voz local está funcionando.'
```

No aviso de aprovação do Codex, a opção de autorizar comandos similares
pode salvar o prefixo formado por `python3` e pelo caminho absoluto de
`speak.py`. Use uma chamada direta ao script e passe a frase como argumento.
O modelo selecionado no Codex escreve o texto. O Chatterbox local usa
o mesmo preset para ler o texto que receber.

## Estado dos testes de voz

A configuração publicada usa a referência padrão `pt_br_f2.wav`. O leitor
residente carregou em 20,9 s e preparou duas falas curtas em 5,5 s e 4,7 s,
usando cerca de 3,5 GiB de VRAM no processo. A síntese usa a GPU local e
não faz uma nova chamada ao Codex.

Os testes com outros áudios de referência e reprodução a 1,25× foram avulsos. A altura reduzida artificialmente soou distorcida. A conversão
RVC comunitária trocou o timbre, mas manteve a entonação animada da fala de
origem e levou 42,5 s na CPU. A entrega mais calma ainda está em aberto.
As amostras pessoais e os pesos dos modelos ficam fora deste repositório.

## Licença

O código do Codex Voice está disponível sob a [GNU AGPL 3.0](LICENSE).
O instalador obtém o Chatterbox e os arquivos de voz nas fontes indicadas
em [setup-local.sh](setup-local.sh). Esses arquivos seguem os termos de
seus respectivos projetos.
