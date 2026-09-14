# ============================================================
# IFWeather - Cloudflare Tunnel + GitHub Pages
# ============================================================
# Este script:
# 1. Inicia o Cloudflare Tunnel
# 2. Captura a URL trycloudflare.com
# 3. Atualiza o endereço.txt
# 4. Atualiza endereco.json no GitHub via API
#
# IMPORTANTE:
# O token NÃO fica neste arquivo.
# Ele deve estar na variável de ambiente GITHUB_TOKEN.
# ============================================================


# ============================================================
# CONFIGURAÇÕES DO COMPUTADOR
# ============================================================

$cloudflared = "C:\cloudflared\cloudflared.exe"

$arquivoEndereco = "C:\Users\SEU_USUARIO\Documents\endereço.txt"

$logSaida = "C:\cloudflared\cloudflared.log"

$logErro = "C:\cloudflared\cloudflared_erro.log"


# ============================================================
# CONFIGURAÇÕES DO GITHUB
# ============================================================

# >>> PREENCHA AQUI <<<

$githubUsuario = "INSIRA_AQUI_SEU_USUARIO_GITHUB"

$githubRepositorio = "INSIRA_AQUI_O_NOME_DO_REPOSITORIO"

$githubArquivo = "endereco.json"

$githubBranch = "main"


# ============================================================
# TOKEN DO GITHUB
# ============================================================

$githubToken = $env:GITHUB_TOKEN

if (-not $githubToken) {
    Write-Host ""
    Write-Host "ERRO: GITHUB_TOKEN nao configurado."
    Write-Host ""
    Write-Host "Configure com:"
    Write-Host '[Environment]::SetEnvironmentVariable("GITHUB_TOKEN", "SEU_TOKEN", "User")'
    Write-Host ""
    exit 1
}


# ============================================================
# VERIFICA CONFIGURAÇÕES
# ============================================================

if ($githubUsuario -like "INSIRA_AQUI*") {
    Write-Host "ERRO: preencha `$githubUsuario no script."
    exit 1
}

if ($githubRepositorio -like "INSIRA_AQUI*") {
    Write-Host "ERRO: preencha `$githubRepositorio no script."
    exit 1
}

if (-not (Test-Path $cloudflared)) {
    Write-Host "ERRO: cloudflared.exe nao encontrado:"
    Write-Host $cloudflared
    exit 1
}


# ============================================================
# LIMPA LOGS
# ============================================================

Remove-Item $logSaida -Force -ErrorAction SilentlyContinue
Remove-Item $logErro -Force -ErrorAction SilentlyContinue


# ============================================================
# AGUARDA O SERVIDOR LOCAL
# ============================================================

Write-Host ""
Write-Host "Aguardando servidor local..."
Start-Sleep -Seconds 30


# ============================================================
# INICIA CLOUDFLARE
# ============================================================

Start-Process `
    -FilePath $cloudflared `
    -ArgumentList "tunnel --url http://localhost:5000" `
    -NoNewWindow `
    -RedirectStandardOutput $logSaida `
    -RedirectStandardError $logErro

Write-Host "Iniciando Cloudflare Tunnel..."
Write-Host ""


# ============================================================
# AGUARDA A URL
# ============================================================

$endereco = $null

for ($i = 0; $i -lt 30; $i++) {

    Start-Sleep -Seconds 1

    if (Test-Path $logSaida) {

        $conteudo = Get-Content `
            $logSaida `
            -Raw `
            -ErrorAction SilentlyContinue

        if ($conteudo -match "https://[a-zA-Z0-9-]+\.trycloudflare\.com") {
            $endereco = $matches[0]
            break
        }
    }

    if (Test-Path $logErro) {

        $conteudo = Get-Content `
            $logErro `
            -Raw `
            -ErrorAction SilentlyContinue

        if ($conteudo -match "https://[a-zA-Z0-9-]+\.trycloudflare\.com") {
            $endereco = $matches[0]
            break
        }
    }

    Write-Host "Aguardando URL... $($i + 1)/30"
}


# ============================================================
# URL ENCONTRADA
# ============================================================

if ($endereco) {

    # --------------------------------------------------------
    # SALVA endereço.txt
    # --------------------------------------------------------

    $texto = @"
Endereco publico do IFWeather:

$endereco

Atualizado em: $(Get-Date -Format "dd/MM/yyyy HH:mm:ss")
"@

    [System.IO.File]::WriteAllText(
        $arquivoEndereco,
        $texto,
        [System.Text.Encoding]::UTF8
    )

    Write-Host ""
    Write-Host "======================================"
    Write-Host "Cloudflare Tunnel iniciado!"
    Write-Host "Endereco publico:"
    Write-Host $endereco
    Write-Host "======================================"
    Write-Host ""


    # --------------------------------------------------------
    # CRIA JSON
    # --------------------------------------------------------

    $json = @{
        url = $endereco
    } | ConvertTo-Json


    # --------------------------------------------------------
    # GITHUB API
    # --------------------------------------------------------

    $apiUrl = "https://api.github.com/repos/$githubUsuario/$githubRepositorio/contents/$githubArquivo"

    $headers = @{
        Authorization = "Bearer $githubToken"
        Accept = "application/vnd.github+json"
        "X-GitHub-Api-Version" = "2022-11-28"
        "User-Agent" = "IFWeather-Tunnel"
    }


    try {

        Write-Host "Consultando endereco.json atual no GitHub..."

        $sha = $null

        try {

            $arquivoGitHub = Invoke-RestMethod `
                -Uri $apiUrl `
                -Headers $headers `
                -Method Get `
                -ErrorAction Stop

            $sha = $arquivoGitHub.sha

        }
        catch {

            Write-Host "Arquivo ainda nao encontrado. Sera criado."
        }


        # ----------------------------------------------------
        # CONVERTE O JSON PARA BASE64
        # ----------------------------------------------------

        $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)

        $base64 = [System.Convert]::ToBase64String($bytes)


        # ----------------------------------------------------
        # MONTA REQUISICAO
        # ----------------------------------------------------

        $body = @{
            message = "Atualiza URL do Cloudflare Tunnel"
            content = $base64
            branch  = $githubBranch
        }

        if ($sha) {
            $body.sha = $sha
        }


        $bodyJson = $body | ConvertTo-Json


        # ----------------------------------------------------
        # ENVIA PARA O GITHUB
        # ----------------------------------------------------

        Write-Host "Atualizando endereco.json no GitHub..."

        Invoke-RestMethod `
            -Uri $apiUrl `
            -Headers $headers `
            -Method Put `
            -Body $bodyJson `
            -ContentType "application/json" `
            -ErrorAction Stop | Out-Null


        Write-Host ""
        Write-Host "======================================"
        Write-Host "GITHUB ATUALIZADO COM SUCESSO!"
        Write-Host "======================================"
        Write-Host ""
        Write-Host "URL fixa do GitHub Pages:"
        Write-Host "https://$githubUsuario.github.io/$githubRepositorio/"
        Write-Host ""

    }
    catch {

        Write-Host ""
        Write-Host "ERRO AO ATUALIZAR GITHUB:"
        Write-Host $_.Exception.Message
        Write-Host ""
    }

}
else {

    # ========================================================
    # NAO ENCONTROU URL
    # ========================================================

    $texto = @"
Endereco publico do IFWeather:

Nao foi possivel obter o endereco.

Consulte:

$logSaida
$logErro
"@

    [System.IO.File]::WriteAllText(
        $arquivoEndereco,
        $texto,
        [System.Text.Encoding]::UTF8
    )

    Write-Host ""
    Write-Host "ERRO: nao foi possivel obter o endereco do Cloudflare Tunnel."
    Write-Host ""
    Write-Host "Verifique:"
    Write-Host $logSaida
    Write-Host $logErro
}
