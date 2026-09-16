// ==========================================
// ELEMENTOS
// ==========================================

const updateButton = document.querySelector(".update-button");
const menuItems = document.querySelectorAll(".menu-item");
const metricSelect = document.getElementById("metricSelect");

// ==========================================
// DIVISÃO DE TELAS
// ==========================================

const telas = [
    "tela-inicial",
    "tela-historico",
    "tela-previsoes",
    "tela-estacao",
    "tela-configuracoes"
];

const mapaMenus = {
    "menu-inicial": "tela-inicial",
    "menu-historico": "tela-historico",
    "menu-previsoes": "tela-previsoes",
    "menu-estacao": "tela-estacao",
    "menu-configuracoes": "tela-configuracoes"
};

// ==========================================
// MOSTRAR TELA
// ==========================================

function mostrarTela(telaId) {

    telas.forEach(function(id) {

        const tela = document.getElementById(id);

        if (!tela) return;

        tela.style.display = id === telaId ? "" : "none";

    });

    Object.keys(mapaMenus).forEach(function(menuId) {

        const menu = document.getElementById(menuId);

        if (menu) {
            menu.classList.remove("active");
        }

    });

    const menuAtivo = Object.keys(mapaMenus).find(function(menuId) {
        return mapaMenus[menuId] === telaId;
    });

    if (menuAtivo) {

        const menu = document.getElementById(menuAtivo);

        if (menu) {
            menu.classList.add("active");
        }

    }

    if (telaId === "tela-historico") {
        carregarHistorico();
    }

    if (telaId === "tela-previsoes") {
        carregarPrevisao();
        carregarHistoricoPrevisoes();
    }

    if (telaId === "tela-estacao") {
        carregarDados();
    }
}

// ==========================================
// CONFIGURAR NAVEGAÇÃO
// ==========================================

function configurarNavegacao() {

    Object.entries(mapaMenus).forEach(function([menuId, telaId]) {

        const menu = document.getElementById(menuId);

        if (!menu) return;

        menu.addEventListener("click", function(event) {

            event.preventDefault();
            mostrarTela(telaId);

        });

    });

}

// ==========================================
// CARREGAR DADOS METEOROLÓGICOS
// ==========================================

async function carregarDados() {

    try {

        const resposta = await fetch("/api/dados");

        if (!resposta.ok) {
            throw new Error("Erro ao obter dados.");
        }

        const dados = await resposta.json();

        const ultimaAtualizacao =
            document.getElementById("ultima-atualizacao");

        if (ultimaAtualizacao) {
            ultimaAtualizacao.textContent =
                dados.ultima_atualizacao || "--";
        }

        const temperatura =
            document.getElementById("temperatura");

        if (temperatura) {
            temperatura.textContent =
                formatarNumero(dados.temperatura);
        }

        const umidade =
            document.getElementById("umidade");

        if (umidade) {
            umidade.textContent =
                formatarNumero(dados.umidade);
        }

        const pressao =
            document.getElementById("pressao");

        if (pressao) {
            pressao.textContent =
                formatarNumero(dados.pressao);
        }

        const vento =
            document.getElementById("vento");

        if (vento) {
            vento.textContent =
                formatarNumero(dados.vento);
        }

        const pontoOrvalho =
            document.getElementById("pontoOrvalho");

        if (pontoOrvalho) {

            const valor =
                formatarNumero(dados.ponto_orvalho);

            pontoOrvalho.textContent =
                valor === "--"
                    ? "-- °C"
                    : `${valor} °C`;
        }

        const direcaoVento =
            document.getElementById("direcaoVento");

        if (direcaoVento) {

            const valor =
                formatarDirecao(dados.direcao_vento);

            direcaoVento.textContent =
                valor === "--"
                    ? "--°"
                    : `${valor}°`;
        }

        const velocidadeVento =
            document.getElementById("velocidadeVento");

        if (velocidadeVento) {

            const valor =
                formatarNumero(dados.vento);

            velocidadeVento.textContent =
                valor === "--"
                    ? "-- m/s"
                    : `${valor} m/s`;
        }

        const rajadaVento =
            document.getElementById("rajadaVento");

        if (rajadaVento) {

            const valor =
                formatarNumero(dados.rajada_vento);

            rajadaVento.textContent =
                valor === "--"
                    ? "-- m/s"
                    : `${valor} m/s`;
        }

        const estacaoTemperatura =
            document.getElementById("estacao-temperatura");

        if (estacaoTemperatura) {

            const valor =
                formatarNumero(dados.temperatura);

            estacaoTemperatura.textContent =
                valor === "--"
                    ? "-- °C"
                    : `${valor} °C`;
        }

        const estacaoUmidade =
            document.getElementById("estacao-umidade");

        if (estacaoUmidade) {

            const valor =
                formatarNumero(dados.umidade);

            estacaoUmidade.textContent =
                valor === "--"
                    ? "-- %"
                    : `${valor} %`;
        }

        const estacaoPressao =
            document.getElementById("estacao-pressao");

        if (estacaoPressao) {

            const valor =
                formatarNumero(dados.pressao);

            estacaoPressao.textContent =
                valor === "--"
                    ? "-- hPa"
                    : `${valor} hPa`;
        }

        const estacaoVento =
            document.getElementById("estacao-vento");

        if (estacaoVento) {

            const valor =
                formatarNumero(dados.vento);

            estacaoVento.textContent =
                valor === "--"
                    ? "-- m/s"
                    : `${valor} m/s`;
        }

    } catch (erro) {

        console.error("Erro ao carregar dados:", erro);

    }

}

// ==========================================
// UNIDADES DAS MÉTRICAS
// ==========================================

function obterUnidade(metrica) {

    const unidades = {
        temperatura: "°C",
        umidade: "%",
        pressao: "hPa",
        vento: "m/s"
    };

    return unidades[metrica] || "";
}

// ==========================================
// GRÁFICO
// ==========================================

let grafico = null;

async function carregarGrafico(metrica = "temperatura") {

    try {

        const resposta =
            await fetch(
                `/api/grafico?metrica=${encodeURIComponent(metrica)}`
            );

        if (!resposta.ok) {
            throw new Error(
                "Erro ao obter dados do gráfico."
            );
        }

        const dados = await resposta.json();

        const canvas =
            document.getElementById("graficoMeteorologico");

        if (!canvas) return;

        if (grafico) {
            grafico.destroy();
            grafico = null;
        }

        const unidade = obterUnidade(metrica);

        grafico = new Chart(canvas, {

            type: "line",

            data: {
                labels: dados.labels,

                datasets: [{
                    data: dados.valores,
                    borderWidth: 2.5,
                    pointRadius: 3,
                    pointHoverRadius: 5,
                    tension: 0.35,
                    fill: true,
                    backgroundColor: "rgba(38, 116, 74, 0.08)",
                    borderColor: "#26744a",
                    pointBackgroundColor: "#26744a",
                    pointBorderColor: "#ffffff"
                }]
            },

            options: {

                responsive: true,
                maintainAspectRatio: false,

                interaction: {
                    intersect: false,
                    mode: "index"
                },

                plugins: {

                    legend: {
                        display: false
                    },

                    tooltip: {

                        backgroundColor: "#17202a",
                        titleColor: "#ffffff",
                        bodyColor: "#ffffff",
                        padding: 10,
                        displayColors: false,

                        callbacks: {

                            label: function(context) {

                                return (
                                    formatarNumero(context.raw)
                                    + " "
                                    + unidade
                                );

                            }

                        }

                    }

                },

                scales: {

                    x: {

                        grid: {
                            display: false
                        },

                        ticks: {
                            color: "#929ca7",
                            font: {
                                size: 11
                            },
                            maxTicksLimit: 8
                        }

                    },

                    y: {

                        grid: {
                            color: "#edf0f2"
                        },

                        ticks: {

                            color: "#929ca7",

                            font: {
                                size: 11
                            },

                            callback: function(value) {

                                return (
                                    formatarNumero(value)
                                    + " "
                                    + unidade
                                );

                            }

                        }

                    }

                }

            }

        });

    } catch (erro) {

        console.error(
            "Erro ao carregar gráfico:",
            erro
        );

    }

}

// ==========================================
// FORMATAÇÃO DOS NÚMEROS
// ==========================================

function formatarNumero(valor) {

    if (
        valor === null ||
        valor === undefined ||
        valor === "" ||
        valor === "N/A" ||
        !Number.isFinite(Number(valor))
    ) {
        return "--";
    }

    return Number(valor)
        .toFixed(1)
        .replace(".", ",");

}

// ==========================================
// FORMATAÇÃO DA DIREÇÃO DO VENTO
// ==========================================

function formatarDirecao(valor) {

    if (
        valor === null ||
        valor === undefined ||
        valor === "" ||
        valor === "N/A" ||
        !Number.isFinite(Number(valor))
    ) {
        return "--";
    }

    return Math.round(Number(valor));

}

// ==========================================
// VALOR NUMÉRICO VÁLIDO
// ==========================================

function valorNumericoValido(valor) {

    if (
        valor === null ||
        valor === undefined ||
        valor === "" ||
        valor === "N/A"
    ) {
        return false;
    }

    return Number.isFinite(Number(valor));

}

// ==========================================
// DIFERENÇA DA PÁGINA INICIAL
// ==========================================

function atualizarDiferencasPaginaInicial(modelo, climatempo) {

    // As diferenças só podem existir quando:
    // 1. o modelo tiver retornado valores válidos;
    // 2. o Climatempo tiver retornado valores válidos.
    if (!modelo || !climatempo) {
        console.log("Diferença não calculada: dados ausentes.");
        return;
    }

    function converterNumero(valor) {

        if (
            valor === null ||
            valor === undefined ||
            valor === "" ||
            valor === "N/A"
        ) {
            return NaN;
        }

        // Aceita tanto 27.5 quanto "27,5"
        const numero = Number(
            String(valor).replace(",", ".")
        );

        return Number.isFinite(numero)
            ? numero
            : NaN;
    }

    const modeloMedia = converterNumero(modelo.media);
    const modeloMinima = converterNumero(modelo.minima);
    const modeloMaxima = converterNumero(modelo.maxima);

    const climatempoMedia = converterNumero(climatempo.media);
    const climatempoMinima = converterNumero(climatempo.minima);
    const climatempoMaxima = converterNumero(climatempo.maxima);

    console.log("===== COMPARAÇÃO MODELO x CLIMATEMPO =====");
    console.log("Modelo média:", modeloMedia);
    console.log("Climatempo média:", climatempoMedia);
    console.log("Modelo mínima:", modeloMinima);
    console.log("Climatempo mínima:", climatempoMinima);
    console.log("Modelo máxima:", modeloMaxima);
    console.log("Climatempo máxima:", climatempoMaxima);

    // ==========================================
    // MÉDIA
    // ID REAL DO HTML: comparacao-modelo
    // ==========================================

    const elementoMedia =
        document.getElementById("comparacao-modelo");

    if (elementoMedia) {

        if (
            Number.isFinite(modeloMedia) &&
            Number.isFinite(climatempoMedia)
        ) {

            const diferencaMedia =
                Math.abs(modeloMedia - climatempoMedia);

            elementoMedia.textContent =
                `${diferencaMedia
                    .toFixed(1)
                    .replace(".", ",")} °C`;

        } else {

            elementoMedia.textContent = "-";
        }

    } else {

        console.error(
            'Elemento "comparacao-modelo" não encontrado.'
        );
    }

    // ==========================================
    // MÍNIMA
    // ID REAL DO HTML: comparacao-diferenca-min
    // ==========================================

    const elementoMinima =
        document.getElementById(
            "comparacao-diferenca-min"
        );

    if (elementoMinima) {

        if (
            Number.isFinite(modeloMinima) &&
            Number.isFinite(climatempoMinima)
        ) {

            const diferencaMinima =
                Math.abs(modeloMinima - climatempoMinima);

            elementoMinima.textContent =
                `${diferencaMinima
                    .toFixed(1)
                    .replace(".", ",")} °C`;

        } else {

            elementoMinima.textContent = "-";
        }

    } else {

        console.error(
            'Elemento "comparacao-diferenca-min" não encontrado.'
        );
    }

    // ==========================================
    // MÁXIMA
    // ID REAL DO HTML: comparacao-diferenca-max
    // ==========================================

    const elementoMaxima =
        document.getElementById(
            "comparacao-diferenca-max"
        );

    if (elementoMaxima) {

        if (
            Number.isFinite(modeloMaxima) &&
            Number.isFinite(climatempoMaxima)
        ) {

            const diferencaMaxima =
                Math.abs(modeloMaxima - climatempoMaxima);

            elementoMaxima.textContent =
                `${diferencaMaxima
                    .toFixed(1)
                    .replace(".", ",")} °C`;

        } else {

            elementoMaxima.textContent = "-";
        }

    } else {

        console.error(
            'Elemento "comparacao-diferenca-max" não encontrado.'
        );
    }

    console.log("Diferenças atualizadas na página inicial.");
}

// ==========================================
// CARREGAR PREVISÃO
// ==========================================

async function carregarPrevisao() {

    try {

        const resposta =
            await fetch("/api/previsao");

        if (!resposta.ok) {

            throw new Error(
                "Não foi possível carregar a previsão."
            );

        }

        const dados =
            await resposta.json();

        const previsao =
            dados.previsao || {};

        const prevMed =
            document.getElementById("prev_med");

        if (prevMed) {
            prevMed.textContent =
                formatarNumero(
                    previsao.temperatura_media
                );
        }

        const prevMin =
            document.getElementById("prev_min");

        if (prevMin) {

            const valor =
                formatarNumero(
                    previsao.temperatura_minima
                );

            prevMin.textContent =
                valor === "--"
                    ? "-- °C"
                    : `${valor} °C`;

        }

        const prevMax =
            document.getElementById("prev_max");

        if (prevMax) {

            const valor =
                formatarNumero(
                    previsao.temperatura_maxima
                );

            prevMax.textContent =
                valor === "--"
                    ? "-- °C"
                    : `${valor} °C`;

        }

        const dataPrevisao =
            document.getElementById("data-previsao");

        if (dataPrevisao) {
            dataPrevisao.textContent =
                dados.data_prevista || "--";
        }

        const previsaoTelaMedia =
            document.getElementById("previsao-tela-media");

        if (previsaoTelaMedia) {
            previsaoTelaMedia.textContent =
                formatarNumero(
                    previsao.temperatura_media
                );
        }

        const previsaoTelaMin =
            document.getElementById("previsao-tela-min");

        if (previsaoTelaMin) {

            const valor =
                formatarNumero(
                    previsao.temperatura_minima
                );

            previsaoTelaMin.textContent =
                valor === "--"
                    ? "-- °C"
                    : `${valor} °C`;

        }

        const previsaoTelaMax =
            document.getElementById("previsao-tela-max");

        if (previsaoTelaMax) {

            const valor =
                formatarNumero(
                    previsao.temperatura_maxima
                );

            previsaoTelaMax.textContent =
                valor === "--"
                    ? "-- °C"
                    : `${valor} °C`;

        }

        console.log("Previsão do modelo:", previsao);

        return {
            media: previsao.temperatura_media,
            minima: previsao.temperatura_minima,
            maxima: previsao.temperatura_maxima
        };

    } catch (erro) {

        console.error(
            "Erro ao carregar previsão:",
            erro
        );

        return null;

    }

}

// ==========================================
// CARREGAR CLIMATEMPO
// ==========================================

async function carregarClimatempo(previsaoModelo = null) {

    try {

        if (!previsaoModelo) {
            previsaoModelo = await carregarPrevisao();
        }

        const respostaClimatempo =
            await fetch("/api/climatempo");

        if (!respostaClimatempo.ok) {

            throw new Error(
                "Não foi possível carregar os dados do Climatempo."
            );

        }

        const dadosClimatempo =
            await respostaClimatempo.json();

        const minimaClimatempo =
            Number(dadosClimatempo.minima);

        const maximaClimatempo =
            Number(dadosClimatempo.maxima);

        const mediaClimatempo =
            Number.isFinite(minimaClimatempo) &&
            Number.isFinite(maximaClimatempo)
                ? (minimaClimatempo + maximaClimatempo) / 2
                : NaN;

        const climatempoMedia =
            document.getElementById("climatempo-media");

        if (climatempoMedia) {

            climatempoMedia.textContent =
                Number.isFinite(mediaClimatempo)
                    ? mediaClimatempo
                        .toFixed(1)
                        .replace(".", ",")
                    : "--";

        }

        const climatempoMin =
            document.getElementById("climatempo-min");

        if (climatempoMin) {

            climatempoMin.textContent =
                Number.isFinite(minimaClimatempo)
                    ? `${minimaClimatempo
                        .toFixed(1)
                        .replace(".", ",")} °C`
                    : "-- °C";

        }

        const climatempoMax =
            document.getElementById("climatempo-max");

        if (climatempoMax) {

            climatempoMax.textContent =
                Number.isFinite(maximaClimatempo)
                    ? `${maximaClimatempo
                        .toFixed(1)
                        .replace(".", ",")} °C`
                    : "-- °C";

        }

        // ==========================================
        // CALCULAR DIFERENÇAS SOMENTE AGORA
        // ==========================================

        atualizarDiferencasPaginaInicial(

            previsaoModelo,

            {
                media: mediaClimatempo,
                minima: minimaClimatempo,
                maxima: maximaClimatempo
            }

        );

        console.log(
            "Climatempo:",
            dadosClimatempo
        );

        return {

            media: mediaClimatempo,
            minima: minimaClimatempo,
            maxima: maximaClimatempo

        };

    } catch (erro) {

        console.error(
            "Erro ao carregar Climatempo:",
            erro
        );

        return null;

    }

}

// ==========================================
// HISTÓRICO METEOROLÓGICO
// ==========================================

const historicoFonte =
    document.getElementById("historico-fonte");

const historicoPeriodo =
    document.getElementById("historico-periodo");

const historicoTabela =
    document.getElementById("historico-tabela-body");

// ==========================================
// UNIDADES DO HISTÓRICO
// ==========================================

function obterUnidadeHistorico(metrica) {

    const unidades = {

        temperatura_media: "°C",
        temperatura_maxima: "°C",
        temperatura_minima: "°C",
        umidade_media: "%",
        pressao_media: "hPa",
        vento: "m/s"

    };

    return unidades[metrica] || "";

}

// ==========================================
// FORMATAÇÃO DA DATA
// ==========================================

function formatarDataHistorico(data) {

    if (!data) return "--";

    const texto = String(data);

    if (/^\d{4}-\d{2}-\d{2}$/.test(texto)) {

        const partes = texto.split("-");

        return (
            partes[2] +
            "/" +
            partes[1] +
            "/" +
            partes[0]
        );

    }

    if (texto.includes("T")) {

        const somenteData =
            texto.split("T")[0];

        const partes =
            somenteData.split("-");

        if (partes.length === 3) {

            return (
                partes[2] +
                "/" +
                partes[1] +
                "/" +
                partes[0]
            );

        }

    }

    if (texto.includes(" ")) {

        const somenteData =
            texto.split(" ")[0];

        const partes =
            somenteData.split("-");

        if (partes.length === 3) {

            return (
                partes[2] +
                "/" +
                partes[1] +
                "/" +
                partes[0]
            );

        }

    }

    return texto;

}

// ==========================================
// FORMATAÇÃO DA DATA E HORA
// ==========================================

function formatarDataHoraHistorico(data) {

    if (!data) return "--";

    const texto = String(data);

    if (/^\d{2}\/\d{2}\/\d{4} /.test(texto)) {
        return texto;
    }

    if (texto.includes(" ")) {

        const partes = texto.split(" ");

        if (partes.length >= 2) {

            const partesData =
                partes[0].split("-");

            if (partesData.length === 3) {

                return (
                    partesData[2] +
                    "/" +
                    partesData[1] +
                    "/" +
                    partesData[0] +
                    " " +
                    partes[1].substring(0, 5)
                );

            }

        }

    }

    if (texto.includes("T")) {

        const partes = texto.split("T");
        const partesData = partes[0].split("-");

        if (partesData.length === 3) {

            return (
                partesData[2] +
                "/" +
                partesData[1] +
                "/" +
                partesData[0] +
                " " +
                (partes[1] || "").substring(0, 5)
            );

        }

    }

    return formatarDataHistorico(texto);

}

// ==========================================
// CARREGAR HISTÓRICO
// ==========================================

async function carregarHistorico() {

    if (!historicoTabela) return;

    const periodo =
        historicoPeriodo
            ? historicoPeriodo.value
            : "30";

    const tabela =
        historicoTabela.closest("table");

    const cabecalho =
        tabela
            ? tabela.querySelector("thead tr")
            : null;

    if (cabecalho) {

        cabecalho.innerHTML = `
            <th rowspan="2" class="col-data">
                Data
            </th>

            <th colspan="3" class="grupo-coleta">
                <span class="grupo-ponto"></span>
                Coleta
            </th>

            <th colspan="3" class="grupo-previsao">
                <span class="grupo-ponto"></span>
                Previsão
            </th>

            <th colspan="3" class="grupo-diferenca">
                <span class="grupo-ponto"></span>
                Diferença
            </th>
        `;

        const segundaLinha =
            tabela.querySelector(
                "thead tr:nth-child(2)"
            );

        if (segundaLinha) {

            segundaLinha.innerHTML = `
                <th>Mínima</th>
                <th>Média</th>
                <th>Máxima</th>

                <th>Mínima</th>
                <th>Média</th>
                <th>Máxima</th>

                <th>Mínima</th>
                <th>Média</th>
                <th>Máxima</th>
            `;

        }

    }

    historicoTabela.innerHTML = `
        <tr>
            <td colspan="10" class="historico-carregando">
                Carregando histórico...
            </td>
        </tr>
    `;

    try {

        const respostaColeta =
            await fetch(
                `/api/historico?metrica=temperatura_media&periodo=${encodeURIComponent(periodo)}`
            );

        if (!respostaColeta.ok) {

            throw new Error(
                "Erro ao carregar histórico de temperaturas."
            );

        }

        const dadosColeta =
            await respostaColeta.json();

        let registrosColeta = [];

        if (
            dadosColeta &&
            Array.isArray(dadosColeta.dados)
        ) {
            registrosColeta = dadosColeta.dados;
        }

        const respostaPrevisao =
            await fetch(
                `/api/historico-previsoes?periodo=${encodeURIComponent(periodo)}`
            );

        let registrosPrevisao = [];

        if (respostaPrevisao.ok) {

            const dadosPrevisao =
                await respostaPrevisao.json();

            if (
                dadosPrevisao &&
                Array.isArray(dadosPrevisao.dados)
            ) {

                registrosPrevisao =
                    dadosPrevisao.dados;

            } else if (Array.isArray(dadosPrevisao)) {

                registrosPrevisao =
                    dadosPrevisao;

            }

        }

        const historico = {};

        registrosColeta.forEach(function(item) {

            const data = item.data;

            if (!data) return;

            const partes = data.split("/");

            let chaveData = data;

            if (partes.length === 3) {

                chaveData =
                    `${partes[2]}-${partes[1]}-${partes[0]}`;

            }

            if (!historico[chaveData]) {

                historico[chaveData] = {

                    coleta: {
                        minima: null,
                        media: null,
                        maxima: null
                    },

                    previsao: {
                        minima: null,
                        media: null,
                        maxima: null
                    }

                };

            }

            historico[chaveData].coleta.minima =
                item.minima ?? null;

            historico[chaveData].coleta.media =
                item.media ?? null;

            historico[chaveData].coleta.maxima =
                item.maxima ?? null;

        });

        registrosPrevisao.forEach(function(item) {

            const data =
                item.Data_Prevista ??
                item.data_prevista;

            if (!data) return;

            const chaveData =
                String(data).substring(0, 10);

            if (!historico[chaveData]) {

                historico[chaveData] = {

                    coleta: {
                        minima: null,
                        media: null,
                        maxima: null
                    },

                    previsao: {
                        minima: null,
                        media: null,
                        maxima: null
                    }

                };

            }

            historico[chaveData].previsao.media =
                item.previsao?.media ?? null;

            historico[chaveData].previsao.minima =
                item.previsao?.minima ?? null;

            historico[chaveData].previsao.maxima =
                item.previsao?.maxima ?? null;

        });

        const datas =
            Object.keys(historico);

        historicoTabela.innerHTML = "";

        if (datas.length === 0) {

            historicoTabela.innerHTML = `
                <tr>
                    <td colspan="10" class="historico-sem-dados">
                        Nenhum dado histórico disponível.
                    </td>
                </tr>
            `;

            return;

        }

        datas.sort(function(a, b) {

            return new Date(b) - new Date(a);

        });

        function formatarTemperatura(valor) {

            if (!valorNumericoValido(valor)) {
                return "—";
            }

            return (
                `${Number(valor)
                    .toFixed(1)
                    .replace(".", ",")} °C`
            );

        }

        datas.forEach(function(data) {

            const registro =
                historico[data];

            const linha =
                document.createElement("tr");

            const colunaData =
                document.createElement("td");

            colunaData.className =
                "historico-data";

            colunaData.textContent =
                formatarDataHistorico(data);

            const coletaMin =
                document.createElement("td");

            coletaMin.className =
                "historico-valor historico-min";

            coletaMin.textContent =
                formatarTemperatura(
                    registro.coleta.minima
                );

            const coletaMedia =
                document.createElement("td");

            coletaMedia.className =
                "historico-valor historico-media";

            coletaMedia.textContent =
                formatarTemperatura(
                    registro.coleta.media
                );

            const coletaMax =
                document.createElement("td");

            coletaMax.className =
                "historico-valor historico-max";

            coletaMax.textContent =
                formatarTemperatura(
                    registro.coleta.maxima
                );

            const previsaoMin =
                document.createElement("td");

            previsaoMin.className =
                "historico-valor historico-min";

            previsaoMin.textContent =
                formatarTemperatura(
                    registro.previsao.minima
                );

            const previsaoMedia =
                document.createElement("td");

            previsaoMedia.className =
                "historico-valor historico-media";

            previsaoMedia.textContent =
                formatarTemperatura(
                    registro.previsao.media
                );

            const previsaoMax =
                document.createElement("td");

            previsaoMax.className =
                "historico-valor historico-max";

            previsaoMax.textContent =
                formatarTemperatura(
                    registro.previsao.maxima
                );

            // ==========================================
            // DIFERENÇA - MÍNIMA
            // ==========================================

            const diferencaMin =
                document.createElement("td");

            diferencaMin.className =
                "historico-valor historico-diferenca";

            if (
                valorNumericoValido(registro.coleta.minima) &&
                valorNumericoValido(registro.previsao.minima)
            ) {

                const diferenca =
                    Math.abs(
                        Number(registro.coleta.minima) -
                        Number(registro.previsao.minima)
                    );

                diferencaMin.textContent =
                    `${diferenca
                        .toFixed(1)
                        .replace(".", ",")} °C`;

            } else {

                diferencaMin.textContent = "-";

            }

            // ==========================================
            // DIFERENÇA - MÉDIA
            // ==========================================

            const diferencaMedia =
                document.createElement("td");

            diferencaMedia.className =
                "historico-valor historico-diferenca";

            if (
                valorNumericoValido(registro.coleta.media) &&
                valorNumericoValido(registro.previsao.media)
            ) {

                const diferenca =
                    Math.abs(
                        Number(registro.coleta.media) -
                        Number(registro.previsao.media)
                    );

                diferencaMedia.textContent =
                    `${diferenca
                        .toFixed(1)
                        .replace(".", ",")} °C`;

            } else {

                diferencaMedia.textContent = "-";

            }

            // ==========================================
            // DIFERENÇA - MÁXIMA
            // ==========================================

            const diferencaMax =
                document.createElement("td");

            diferencaMax.className =
                "historico-valor historico-diferenca";

            if (
                valorNumericoValido(registro.coleta.maxima) &&
                valorNumericoValido(registro.previsao.maxima)
            ) {

                const diferenca =
                    Math.abs(
                        Number(registro.coleta.maxima) -
                        Number(registro.previsao.maxima)
                    );

                diferencaMax.textContent =
                    `${diferenca
                        .toFixed(1)
                        .replace(".", ",")} °C`;

            } else {

                diferencaMax.textContent = "-";

            }

            linha.appendChild(colunaData);

            linha.appendChild(coletaMin);
            linha.appendChild(coletaMedia);
            linha.appendChild(coletaMax);

            linha.appendChild(previsaoMin);
            linha.appendChild(previsaoMedia);
            linha.appendChild(previsaoMax);

            linha.appendChild(diferencaMin);
            linha.appendChild(diferencaMedia);
            linha.appendChild(diferencaMax);

            historicoTabela.appendChild(linha);

        });

    } catch (erro) {

        console.error(
            "Erro ao carregar histórico:",
            erro
        );

        historicoTabela.innerHTML = `
            <tr>
                <td colspan="10" class="historico-sem-dados">
                    Erro ao carregar o histórico.
                </td>
            </tr>
        `;

    }

}

// ==========================================
// HISTÓRICO DE PREVISÕES
// ==========================================

const historicoPrevisoesTabela =
    document.getElementById(
        "historico-previsoes-body"
    );

function formatarDataHoraPrevisao(data) {

    if (!data) return "--";

    const texto = String(data);

    if (texto.includes(" ")) {

        const partes = texto.split(" ");

        if (partes.length >= 2) {

            const partesData =
                partes[0].split("-");

            if (partesData.length === 3) {

                return (
                    partesData[2] +
                    "/" +
                    partesData[1] +
                    "/" +
                    partesData[0] +
                    " " +
                    partes[1].substring(0, 5)
                );

            }

        }

    }

    return formatarDataHistorico(texto);

}

// ==========================================
// CARREGAR HISTÓRICO DE PREVISÕES
// ==========================================

async function carregarHistoricoPrevisoes() {

    if (!historicoPrevisoesTabela) {
        return;
    }

    historicoPrevisoesTabela.innerHTML = `
        <tr>
            <td colspan="8">
                Carregando histórico de previsões...
            </td>
        </tr>
    `;

    try {

        const resposta =
            await fetch(
                "/api/historico-previsoes"
            );

        if (!resposta.ok) {

            throw new Error(
                "Erro ao carregar histórico de previsões."
            );

        }

        const dados =
            await resposta.json();

        historicoPrevisoesTabela.innerHTML =
            "";

        let registros =
            dados;

        if (
            dados &&
            Array.isArray(dados.dados)
        ) {

            registros =
                dados.dados;

        }

        if (
            !Array.isArray(registros) ||
            registros.length === 0
        ) {

            historicoPrevisoesTabela.innerHTML = `
                <tr>
                    <td colspan="8">
                        Nenhuma previsão registrada.
                    </td>
                </tr>
            `;

            return;

        }

        registros =
            [...registros].reverse();

        registros.forEach(function(item) {

            const linha =
                document.createElement("tr");

            const colunaExecucao =
                document.createElement("td");

            colunaExecucao.textContent =
                formatarDataHoraPrevisao(
                    item.Data_Execucao ??
                    item.data_execucao
                );

            const colunaDataPrevista =
                document.createElement("td");

            colunaDataPrevista.textContent =
                formatarDataHistorico(
                    item.Data_Prevista ??
                    item.data_prevista
                );

            const colunaMediaPrevista =
                document.createElement("td");

            colunaMediaPrevista.textContent =
                formatarTemperaturaHistorico(
                    item.Temp_Media_Prevista_C ??
                    item.temp_media_prevista_c
                );

            const colunaMinPrevista =
                document.createElement("td");

            colunaMinPrevista.textContent =
                formatarTemperaturaHistorico(
                    item.Temp_Min_Prevista_C ??
                    item.temp_min_prevista_c
                );

            const colunaMaxPrevista =
                document.createElement("td");

            colunaMaxPrevista.textContent =
                formatarTemperaturaHistorico(
                    item.Temp_Max_Prevista_C ??
                    item.temp_max_prevista_c
                );

            const colunaMediaReal =
                document.createElement("td");

            colunaMediaReal.textContent =
                formatarTemperaturaHistorico(
                    item.Temp_Media_API_Externa_C ??
                    item.temp_media_api_externa_c
                );

            const colunaMinReal =
                document.createElement("td");

            colunaMinReal.textContent =
                formatarTemperaturaHistorico(
                    item.Temp_Min_API_Externa_C ??
                    item.temp_min_api_externa_c
                );

            const colunaMaxReal =
                document.createElement("td");

            colunaMaxReal.textContent =
                formatarTemperaturaHistorico(
                    item.Temp_Max_API_Externa_C ??
                    item.temp_max_api_externa_c
                );

            linha.appendChild(colunaExecucao);
            linha.appendChild(colunaDataPrevista);
            linha.appendChild(colunaMediaPrevista);
            linha.appendChild(colunaMinPrevista);
            linha.appendChild(colunaMaxPrevista);
            linha.appendChild(colunaMediaReal);
            linha.appendChild(colunaMinReal);
            linha.appendChild(colunaMaxReal);

            historicoPrevisoesTabela.appendChild(
                linha
            );

        });

    } catch (erro) {

        console.error(
            "Erro ao carregar histórico de previsões:",
            erro
        );

        historicoPrevisoesTabela.innerHTML = `
            <tr>
                <td colspan="8">
                    Erro ao carregar histórico de previsões.
                </td>
            </tr>
        `;

    }

}

// ==========================================
// FORMATAR TEMPERATURA DO HISTÓRICO
// ==========================================

function formatarTemperaturaHistorico(valor) {

    if (!valorNumericoValido(valor)) {
        return "--";
    }

    return (
        Number(valor)
            .toFixed(1)
            .replace(".", ",")
        + " °C"
    );

}

// ==========================================
// SELETOR DO GRÁFICO
// ==========================================

if (metricSelect) {

    metricSelect.addEventListener(
        "change",
        function() {

            carregarGrafico(
                this.value
            );

        }
    );

}

// ==========================================
// SELETOR DA FONTE DO HISTÓRICO
// ==========================================

if (historicoFonte) {

    historicoFonte.addEventListener(
        "change",
        function() {

            carregarHistorico();

        }
    );

}

// ==========================================
// SELETOR DO PERÍODO
// ==========================================

if (historicoPeriodo) {

    historicoPeriodo.addEventListener(
        "change",
        function() {

            carregarHistorico();

        }
    );

}

// ==========================================
// OVERLAY DE ATUALIZAÇÃO
// ==========================================

function mostrarLoadingAtualizacao() {

    let overlay =
        document.getElementById(
            "atualizacao-overlay"
        );

    if (!overlay) {

        overlay =
            document.createElement("div");

        overlay.id =
            "atualizacao-overlay";

        overlay.className =
            "atualizacao-overlay";

        overlay.innerHTML = `
            <div class="atualizacao-loading">

                <div class="atualizacao-spinner"></div>

                <div class="atualizacao-titulo">
                    Atualizando dados...
                </div>

                <div class="atualizacao-subtitulo">
                    Aguarde enquanto buscamos os dados mais recentes.
                </div>

            </div>
        `;

        document.body.appendChild(overlay);

    }

    requestAnimationFrame(function() {

        overlay.classList.add("ativo");

    });

}

function esconderLoadingAtualizacao() {

    const overlay =
        document.getElementById(
            "atualizacao-overlay"
        );

    if (overlay) {
        overlay.classList.remove("ativo");
    }

}

// ==========================================
// BOTÃO ATUALIZAR
// ==========================================

if (updateButton) {

    updateButton.addEventListener(
        "click",
        async function() {

            updateButton.disabled = true;

            mostrarLoadingAtualizacao();

            try {

                const resposta =
                    await fetch(
                        "/api/atualizar",
                        {
                            method: "POST"
                        }
                    );

                const resultado =
                    await resposta.json();

                if (
                    resposta.ok &&
                    resultado.sucesso
                ) {

                    window.location.reload();

                    return;

                }

                console.error(
                    "Erro na atualização:",
                    resultado.erro
                );

                esconderLoadingAtualizacao();

                updateButton.innerHTML =
                    "⚠ Erro";

                updateButton.disabled =
                    false;

            } catch (erro) {

                console.error(
                    "Erro ao atualizar:",
                    erro
                );

                esconderLoadingAtualizacao();

                updateButton.innerHTML =
                    "⚠ Erro";

                updateButton.disabled =
                    false;

            }

        }
    );

}

// ==========================================
// ATUALIZAÇÃO AUTOMÁTICA
// ==========================================

let intervaloAtualizacao = null;

async function atualizarDadosAutomaticamente() {

    try {

        await carregarDados();

        const metricaAtual =
            metricSelect
                ? metricSelect.value
                : "temperatura";

        await carregarGrafico(
            metricaAtual
        );

        // Previsão primeiro.
        // Depois Climatempo.
        // A diferença só é calculada após os dois.

        const previsaoModelo =
            await carregarPrevisao();

        await carregarClimatempo(
            previsaoModelo
        );

        const telaHistorico =
            document.getElementById(
                "tela-historico"
            );

        if (
            telaHistorico &&
            telaHistorico.style.display !== "none"
        ) {

            await carregarHistorico();

        }

        const telaPrevisoes =
            document.getElementById(
                "tela-previsoes"
            );

        if (
            telaPrevisoes &&
            telaPrevisoes.style.display !== "none"
        ) {

            await carregarHistoricoPrevisoes();

        }

    } catch (erro) {

        console.error(
            "Erro na atualização automática:",
            erro
        );

    }

}

// ==========================================
// INICIAR ATUALIZAÇÃO AUTOMÁTICA
// ==========================================

function iniciarAtualizacaoAutomatica() {

    if (intervaloAtualizacao) {

        clearInterval(
            intervaloAtualizacao
        );

    }

    intervaloAtualizacao =
        setInterval(
            atualizarDadosAutomaticamente,
            60000
        );

}

// ==========================================
// ATUALIZAR AO VOLTAR PARA A ABA
// ==========================================

document.addEventListener(
    "visibilitychange",
    function() {

        if (!document.hidden) {

            atualizarDadosAutomaticamente();

        }

    }
);

// ==========================================
// INICIALIZAÇÃO
// ==========================================

async function iniciar() {

    mostrarTela("tela-inicial");

    await carregarDados();

    await carregarGrafico(
        metricSelect
            ? metricSelect.value
            : "temperatura"
    );

    // ==========================================
    // PRIMEIRO: PREVISÃO
    // ==========================================

    const previsaoModelo =
        await carregarPrevisao();

    // ==========================================
    // SEGUNDO: CLIMATEMPO
    // ==========================================

    // carregarClimatempo espera a resposta
    // externa e só então calcula a diferença.

    await carregarClimatempo(
        previsaoModelo
    );

    iniciarAtualizacaoAutomatica();

}

// ==========================================
// INICIAR SITE
// ==========================================

document.addEventListener(
    "DOMContentLoaded",
    function() {

        configurarNavegacao();

        iniciar();

    }
);
