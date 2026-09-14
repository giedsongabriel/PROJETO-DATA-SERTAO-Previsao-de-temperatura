# IFWeather — Endereço fixo para Cloudflare Tunnel

Este projeto cria uma página fixa no GitHub Pages que lê a URL atual do Cloudflare Tunnel e redireciona o visitante automaticamente.

## Como funciona

```text
Cloudflare Tunnel
       ↓
PowerShell captura a URL
       ↓
endereço.txt
       ↓
GitHub API atualiza endereco.json
       ↓
GitHub Pages
       ↓
endereço fixo
       ↓
URL atual do Cloudflare
```

## 1. Antes de começar

Você precisa ter:

- Uma conta no GitHub
- Um repositório no GitHub para este projeto
- GitHub Pages habilitado
- PowerShell no computador que executa o Cloudflare Tunnel
- `cloudflared.exe`
- Seu servidor local funcionando em `http://localhost:5000`

## 2. Preencha as configurações

Abra:

`atualizar_cloudflare_github.ps1`

Procure este bloco:

```powershell
$githubUsuario = "INSIRA_AQUI_SEU_USUARIO_GITHUB"
$githubRepositorio = "INSIRA_AQUI_O_NOME_DO_REPOSITORIO"
$githubArquivo = "endereco.json"
$githubBranch = "main"
```

Exemplo:

```powershell
$githubUsuario = "andre-carvalho123"
$githubRepositorio = "ifweather-link"
```

Também confira estes caminhos:

```powershell
$cloudflared = "C:\cloudflared\cloudflared.exe"

$arquivoEndereco = "C:\Users\SEU_USUARIO\Documents\endereço.txt"

$logSaida = "C:\cloudflared\cloudflared.log"

$logErro = "C:\cloudflared\cloudflared_erro.log"
```

Altere `SEU_USUARIO` e os demais caminhos conforme o computador.

## 3. Crie o repositório

No GitHub, crie um repositório, por exemplo:

`ifweather-link`

Coloque nele:

- `index.html`
- `endereco.json`

Não coloque seu token do GitHub no repositório.

## 4. Crie o token do GitHub

Crie um Fine-grained Personal Access Token no GitHub.

Configure o token para ter acesso somente ao repositório escolhido e conceda:

`Repository permissions → Contents → Read and write`

Copie o token.

IMPORTANTE: nunca coloque o token dentro do `index.html`, dentro do `endereco.json`, ou em um arquivo que será enviado ao GitHub.

## 5. Salve o token como variável de ambiente

Abra o PowerShell e execute:

```powershell
[Environment]::SetEnvironmentVariable(
    "GITHUB_TOKEN",
    "COLE_SEU_TOKEN_AQUI",
    "User"
)
```

Depois feche e abra o PowerShell novamente.

Teste:

```powershell
if ($env:GITHUB_TOKEN) {
    Write-Host "GITHUB_TOKEN configurado."
} else {
    Write-Host "GITHUB_TOKEN NÃO configurado."
}
```

Não publique o valor do token em prints, mensagens ou arquivos.

## 6. Ative o GitHub Pages

No repositório:

`Settings → Pages`

Em "Build and deployment":

- Source: `Deploy from a branch`
- Branch: `main`
- Folder: `/ (root)`

Salve.

O endereço ficará parecido com:

`https://SEU_USUARIO.github.io/NOME_DO_REPOSITORIO/`

## 7. Teste

Primeiro garanta que seu servidor local está funcionando em:

`http://localhost:5000`

Depois execute:

```powershell
.\atualizar_cloudflare_github.ps1
```

O script:

1. inicia o Cloudflare Tunnel;
2. espera a URL `trycloudflare.com`;
3. salva a URL em `endereço.txt`;
4. atualiza `endereco.json` no GitHub.

Depois de alguns segundos, abra seu endereço do GitHub Pages.

## 8. Se o GitHub disser que o arquivo mudou

O script busca o `sha` atual de `endereco.json` antes de atualizar. Isso permite substituir o arquivo existente sem precisar editar manualmente.

## 9. Segurança

O token fica somente no computador que executa o PowerShell.

O repositório público contém apenas a URL pública do Cloudflare Tunnel.

Como o endereço `trycloudflare.com` é temporário, qualquer pessoa que tiver essa URL poderá acessar o serviço enquanto o túnel estiver ativo. O GitHub Pages não protege o seu servidor.

## 10. Observação sobre o atraso

Quando o Cloudflare gerar uma nova URL, o PowerShell atualiza o GitHub. O GitHub Pages pode levar alguns segundos para disponibilizar a nova versão do arquivo.

Se quiser evitar problemas de cache, o `index.html` já consulta:

```javascript
endereco.json?t=TIMESTAMP
```

para solicitar uma versão nova do arquivo.

## 11. Personalização

Você pode editar `index.html` para colocar:

- logo do IFWeather;
- nome do projeto;
- botão de acesso;
- informações do projeto;
- aparência personalizada.

