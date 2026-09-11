// ==========================================
// ELEMENTOS
// ==========================================

const updateButton =
    document.querySelector(".update-button");

const menuItems =
    document.querySelectorAll(".menu-item");

const metricSelect =
    document.getElementById("metricSelect");


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

    "menu-inicial":
        "tela-inicial",

    "menu-historico":
        "tela-historico",

    "menu-previsoes":
        "tela-previsoes",

    "menu-estacao":
        "tela-estacao",

    "menu-configuracoes":
        "tela-configuracoes"

};


// ==========================================
// MOSTRAR TELA
// ==========================================

function mostrarTela(telaId) {

    telas.forEach(
        function(id) {

            const tela =
                document.getElementById(id);


            if (!tela) {
                return;
            }


            tela.style.display =
                id === telaId
                    ? ""
                    : "none";

        }
    );


    // ==========================================
    // ATUALIZAR MENU ATIVO
    // ==========================================

    Object.keys(mapaMenus).forEach(
        function(menuId) {

            const menu =
                document.getElementById(menuId);


            if (menu) {

                menu.classList.remove(
                    "active"
                );

            }

        }
    );


    const menuAtivo =
        Object.keys(mapaMenus).find(
            function(menuId) {

                return (
                    mapaMenus[menuId] ===
                    telaId
                );

            }
        );


    if (menuAtivo) {

        const menu =
            document.getElementById(
                menuAtivo
            );


        if (menu) {

            menu.classList.add(
                "active"
            );

        }

    }


    // ==========================================
    // AÇÕES AO ENTRAR NAS TELAS
    // ==========================================

    if (
        telaId ===
        "tela-historico"
    ) {

        carregarHistorico();

    }


    if (
        telaId ===
        "tela-previsoes"
    ) {

        carregarPrevisao();

        carregarHistoricoPrevisoes();

    }


    if (
        telaId ===
        "tela-estacao"
    ) {

        carregarDados();

    }

}


// ==========================================
// CONFIGURAR NAVEGAÇÃO
// ==========================================

function configurarNavegacao() {

    Object.entries(mapaMenus).forEach(
        function([menuId, telaId]) {

            const menu =
                document.getElementById(
                    menuId
                );


            if (!menu) {
                return;
            }


            menu.addEventListener(
                "click",
                function(event) {

                    event.preventDefault();


                    mostrarTela(
                        telaId
                    );

                }
            );

        }
    );

}


// ==========================================
// CARREGAR DADOS METEOROLÓGICOS
// ==========================================

async function carregarDados() {

    try {

        const resposta =
            await fetch(
                "/api/dados"
            );


        if (!resposta.ok) {

            throw new Error(
                "Erro ao obter dados."
            );

        }


        const dados =
            await resposta.json();


        // ==========================================
        // ÚLTIMA ATUALIZAÇÃO
        // ==========================================

        const ultimaAtualizacao =
            document.getElementById(
                "ultima-atualizacao"
            );


        if (ultimaAtualizacao) {

            ultimaAtualizacao.textContent =
                dados.ultima_atualizacao ||
                "--";

        }


        // ==========================================
        // TEMPERATURA
        // ==========================================

        const temperatura =
            document.getElementById(
                "temperatura"
            );


        if (temperatura) {

            temperatura.textContent =
                formatarNumero(
                    dados.temperatura
                );

        }


        // ==========================================
        // UMIDADE
        // ==========================================

        const umidade =
            document.getElementById(
                "umidade"
            );


        if (umidade) {

            umidade.textContent =
                formatarNumero(
                    dados.umidade
                );

        }


        // ==========================================
        // PRESSÃO
        // ==========================================

        const pressao =
            document.getElementById(
                "pressao"
            );


        if (pressao) {

            pressao.textContent =
                formatarNumero(
                    dados.pressao
                );

        }


        // ==========================================
        // VENTO
        // ==========================================

        const vento =
            document.getElementById(
                "vento"
            );


        if (vento) {

            vento.textContent =
                formatarNumero(
                    dados.vento
                );

        }


        // ==========================================
        // PONTO DE ORVALHO
        // ==========================================

        const pontoOrvalho =
            document.getElementById(
                "pontoOrvalho"
            );


        if (pontoOrvalho) {

            const valor =
                formatarNumero(
                    dados.ponto_orvalho
                );


            pontoOrvalho.textContent =
                valor === "--"
                    ? "-- °C"
                    : `${valor} °C`;

        }


        // ==========================================
        // DIREÇÃO DO VENTO
        // ==========================================

        const direcaoVento =
            document.getElementById(
                "direcaoVento"
            );


        if (direcaoVento) {

            const valor =
                formatarDirecao(
                    dados.direcao_vento
                );


            direcaoVento.textContent =
                valor === "--"
                    ? "--°"
                    : `${valor}°`;

        }


        // ==========================================
        // VELOCIDADE DO VENTO
        // ==========================================

        const velocidadeVento =
            document.getElementById(
                "velocidadeVento"
            );


        if (velocidadeVento) {

            const valor =
                formatarNumero(
                    dados.vento
                );


            velocidadeVento.textContent =
                valor === "--"
                    ? "-- m/s"
                    : `${valor} m/s`;

        }


        // ==========================================
        // RAJADA DO VENTO
        // ==========================================

        const rajadaVento =
            document.getElementById(
                "rajadaVento"
            );


        if (rajadaVento) {

            const valor =
                formatarNumero(
                    dados.rajada_vento
                );


            rajadaVento.textContent =
                valor === "--"
                    ? "-- m/s"
                    : `${valor} m/s`;

        }


        // ==========================================
        // DADOS DA TELA ESTAÇÃO
        // ==========================================

        const estacaoTemperatura =
            document.getElementById(
                "estacao-temperatura"
            );


        if (estacaoTemperatura) {

            const valor =
                formatarNumero(
                    dados.temperatura
                );


            estacaoTemperatura.textContent =
                valor === "--"
                    ? "-- °C"
                    : `${valor} °C`;

        }


        const estacaoUmidade =
            document.getElementById(
                "estacao-umidade"
            );


        if (estacaoUmidade) {

            const valor =
                formatarNumero(
                    dados.umidade
                );


            estacaoUmidade.textContent =
                valor === "--"
                    ? "-- %"
                    : `${valor} %`;

        }


        const estacaoPressao =
            document.getElementById(
                "estacao-pressao"
            );


        if (estacaoPressao) {

            const valor =
                formatarNumero(
                    dados.pressao
                );


            estacaoPressao.textContent =
                valor === "--"
                    ? "-- hPa"
                    : `${valor} hPa`;

        }


        const estacaoVento =
            document.getElementById(
                "estacao-vento"
            );


        if (estacaoVento) {

            const valor =
                formatarNumero(
                    dados.vento
                );


            estacaoVento.textContent =
                valor === "--"
                    ? "-- m/s"
                    : `${valor} m/s`;

        }

    }

    catch (erro) {

        console.error(
            "Erro ao carregar dados:",
            erro
        );

    }

}


// ==========================================
// UNIDADES DAS MÉTRICAS
// ==========================================

function obterUnidade(metrica) {

    const unidades = {

        temperatura:
            "°C",

        umidade:
            "%",

        pressao:
            "hPa",

        vento:
            "m/s"

    };


    return unidades[metrica] || "";

}


// ==========================================
// GRÁFICO
// ==========================================

let grafico = null;


async function carregarGrafico(
    metrica = "temperatura"
) {

    try {

        const resposta =
            await fetch(
                `/api/grafico?metrica=${encodeURIComponent(
                    metrica
                )}`
            );


        if (!resposta.ok) {

            throw new Error(
                "Erro ao obter dados do gráfico."
            );

        }


        const dados =
            await resposta.json();


        const canvas =
            document.getElementById(
                "graficoMeteorologico"
            );


        if (!canvas) {
            return;
        }


        // ==========================================
        // DESTRUIR GRÁFICO ANTERIOR
        // ==========================================

        if (grafico) {

            grafico.destroy();

            grafico = null;

        }


        const unidade =
            obterUnidade(
                metrica
            );


        // ==========================================
        // CRIAR GRÁFICO
        // ==========================================

        grafico =
            new Chart(
                canvas,
                {

                    type: "line",


                    data: {

                        labels:
                            dados.labels,


                        datasets: [

                            {

                                data:
                                    dados.valores,


                                borderWidth:
                                    2.5,


                                pointRadius:
                                    3,


                                pointHoverRadius:
                                    5,


                                tension:
                                    0.35,


                                fill:
                                    true,


                                backgroundColor:
                                    "rgba(38, 116, 74, 0.08)",


                                borderColor:
                                    "#26744a",


                                pointBackgroundColor:
                                    "#26744a",


                                pointBorderColor:
                                    "#ffffff"

                            }

                        ]

                    },


                    options: {

                        responsive:
                            true,


                        maintainAspectRatio:
                            false,


                        interaction: {

                            intersect:
                                false,


                            mode:
                                "index"

                        },


                        plugins: {

                            legend: {

                                display:
                                    false

                            },


                            tooltip: {

                                backgroundColor:
                                    "#17202a",


                                titleColor:
                                    "#ffffff",


                                bodyColor:
                                    "#ffffff",


                                padding:
                                    10,


                                displayColors:
                                    false,


                                callbacks: {

                                    label:
                                        function(
                                            context
                                        ) {

                                            return (
                                                formatarNumero(
                                                    context.raw
                                                )
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

                                    display:
                                        false

                                },


                                ticks: {

                                    color:
                                        "#929ca7",


                                    font: {

                                        size:
                                            11

                                    },


                                    maxTicksLimit:
                                        8

                                }

                            },


                            y: {

                                grid: {

                                    color:
                                        "#edf0f2"

                                },


                                ticks: {

                                    color:
                                        "#929ca7",


                                    font: {

                                        size:
                                            11

                                    },


                                    callback:
                                        function(
                                            value
                                        ) {

                                            return (
                                                formatarNumero(
                                                    value
                                                )
                                                + " "
                                                + unidade
                                            );

                                        }

                                }

                            }

                        }

                    }

                }
            );

    }

    catch (erro) {

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

        isNaN(valor)

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

        isNaN(valor)

    ) {

        return "--";

    }


    return Math.round(
        Number(valor)
    );

}


// ==========================================
// CARREGAR PREVISÃO
// ==========================================

async function carregarPrevisao() {

    try {

        const resposta =
            await fetch(
                "/api/previsao"
            );


        if (!resposta.ok) {

            throw new Error(
                "Não foi possível carregar a previsão."
            );

        }


        const dados =
            await resposta.json();


        const previsao =
            dados.previsao || {};


        const real =
            dados.real || {};


        const diferenca =
            dados.diferenca || {};


        // ==========================================
        // MÉDIA PREVISTA
        // ==========================================

        const prevMed =
            document.getElementById(
                "prev_med"
            );


        if (prevMed) {

            prevMed.textContent =
                formatarNumero(
                    previsao.temperatura_media
                );

        }


        // ==========================================
        // MÍNIMA PREVISTA
        // ==========================================

        const prevMin =
            document.getElementById(
                "prev_min"
            );


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


        // ==========================================
        // MÁXIMA PREVISTA
        // ==========================================

        const prevMax =
            document.getElementById(
                "prev_max"
            );


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


        // ==========================================
        // DATA DA PREVISÃO
        // ==========================================

        const dataPrevisao =
            document.getElementById(
                "data-previsao"
            );


        if (dataPrevisao) {

            dataPrevisao.textContent =
                dados.data_prevista ||
                "--";

        }


        // ==========================================
        // PREVISÃO NA TELA DE PREVISÕES
        // ==========================================

        const previsaoTelaMedia =
            document.getElementById(
                "previsao-tela-media"
            );


        if (previsaoTelaMedia) {

            previsaoTelaMedia.textContent =
                formatarNumero(
                    previsao.temperatura_media
                );

        }


        const previsaoTelaMin =
            document.getElementById(
                "previsao-tela-min"
            );


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
            document.getElementById(
                "previsao-tela-max"
            );


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


        // ==========================================
        // DIFERENÇA MÉDIA
        // ==========================================

        const diferencaMedia =
            document.getElementById(
                "previsao-diferenca-media"
            );


        if (diferencaMedia) {

            const valor =
                formatarNumero(
                    diferenca.media
                );


            diferencaMedia.textContent =
                valor === "--"
                    ? "-- °C"
                    : `${valor} °C`;

        }


        // ==========================================
        // DIFERENÇA MÍNIMA
        // ==========================================

        const diferencaMin =
            document.getElementById(
                "previsao-diferenca-min"
            );


        if (diferencaMin) {

            const valor =
                formatarNumero(
                    diferenca.minima
                );


            diferencaMin.textContent =
                valor === "--"
                    ? "-- °C"
                    : `${valor} °C`;

        }


        // ==========================================
        // DIFERENÇA MÁXIMA
        // ==========================================

        const diferencaMax =
            document.getElementById(
                "previsao-diferenca-max"
            );


        if (diferencaMax) {

            const valor =
                formatarNumero(
                    diferenca.maxima
                );


            diferencaMax.textContent =
                valor === "--"
                    ? "-- °C"
                    : `${valor} °C`;

        }


        // ==========================================
        // LOG PARA DEBUG
        // ==========================================

        console.log(
            "Previsão:",
            previsao
        );


        console.log(
            "Valores reais:",
            real
        );


        console.log(
            "Diferenças:",
            diferenca
        );

    }

    catch (erro) {

        console.error(
            "Erro ao carregar previsão:",
            erro
        );

    }

}


// ==========================================
// HISTÓRICO METEOROLÓGICO
// ==========================================

const historicoFonte =
    document.getElementById(
        "historico-fonte"
    );

const historicoPeriodo =
    document.getElementById(
        "historico-periodo"
    );

const historicoTabela =
    document.getElementById(
        "historico-tabela-body"
    );


// ==========================================
// UNIDADES DO HISTÓRICO
// ==========================================

function obterUnidadeHistorico(
    metrica
) {

    const unidades = {

        temperatura_media:
            "°C",

        temperatura_maxima:
            "°C",

        temperatura_minima:
            "°C",

        umidade_media:
            "%",

        pressao_media:
            "hPa",

        vento:
            "m/s"

    };

    return unidades[metrica] || "";
}


// ==========================================
// FORMATAÇÃO DA DATA DO HISTÓRICO
// ==========================================

function formatarDataHistorico(
    data
) {

    if (!data) {
        return "--";
    }

    const texto =
        String(data);


    // AAAA-MM-DD

    if (
        /^\d{4}-\d{2}-\d{2}$/.test(
            texto
        )
    ) {

        const partes =
            texto.split("-");

        return (
            partes[2] +
            "/" +
            partes[1] +
            "/" +
            partes[0]
        );
    }


    // AAAA-MM-DDTHH:MM:SS

    if (
        texto.includes("T")
    ) {

        const somenteData =
            texto.split("T")[0];

        const partes =
            somenteData.split("-");

        if (
            partes.length === 3
        ) {

            return (
                partes[2] +
                "/" +
                partes[1] +
                "/" +
                partes[0]
            );
        }
    }


    // AAAA-MM-DD HH:MM:SS

    if (
        texto.includes(" ")
    ) {

        const somenteData =
            texto.split(" ")[0];

        const partes =
            somenteData.split("-");

        if (
            partes.length === 3
        ) {

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

function formatarDataHoraHistorico(
    data
) {

    if (!data) {
        return "--";
    }

    const texto =
        String(data);


    // Já está em DD/MM/AAAA HH:MM

    if (
        /^\d{2}\/\d{2}\/\d{4} /.test(
            texto
        )
    ) {

        return texto;
    }


    // AAAA-MM-DD HH:MM:SS

    if (
        texto.includes(" ")
    ) {

        const partes =
            texto.split(" ");

        if (
            partes.length >= 2
        ) {

            const dataParte =
                partes[0];

            const horaParte =
                partes[1];

            const partesData =
                dataParte.split("-");

            if (
                partesData.length === 3
            ) {

                return (
                    partesData[2] +
                    "/" +
                    partesData[1] +
                    "/" +
                    partesData[0] +
                    " " +
                    horaParte.substring(
                        0,
                        5
                    )
                );
            }
        }
    }


    // AAAA-MM-DDTHH:MM:SS

    if (
        texto.includes("T")
    ) {

        const partes =
            texto.split("T");

        const partesData =
            partes[0].split("-");

        if (
            partesData.length === 3
        ) {

            return (
                partesData[2] +
                "/" +
                partesData[1] +
                "/" +
                partesData[0] +
                " " +
                (partes[1] || "")
                    .substring(0, 5)
            );
        }
    }

    return formatarDataHistorico(
        texto
    );
}

// ==========================================
// CARREGAR HISTÓRICO
// ==========================================

async function carregarHistorico() {

    if (!historicoTabela) {
        return;
    }

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

    // ==========================================
    // CABEÇALHO DA TABELA
    // ==========================================

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
        `;

        const segundaLinha =
            tabela.querySelector("thead tr:nth-child(2)");

        if (segundaLinha) {

            segundaLinha.innerHTML = `
                <th>Mínima</th>
                <th>Média</th>
                <th>Máxima</th>

                <th>Mínima</th>
                <th>Média</th>
                <th>Máxima</th>
            `;
        }
    }

    // ==========================================
    // MENSAGEM DE CARREGAMENTO
    // ==========================================

    historicoTabela.innerHTML = `
        <tr>
            <td colspan="7" class="historico-carregando">
                Carregando histórico...
            </td>
        </tr>
    `;

    try {

        // ==========================================
        // BUSCAR COLETA
        // ==========================================

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
            registrosColeta =
                dadosColeta.dados;
        }

        // ==========================================
        // BUSCAR PREVISÕES
        // ==========================================

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

            } else if (
                Array.isArray(dadosPrevisao)
            ) {

                registrosPrevisao =
                    dadosPrevisao;
            }
        }

        // ==========================================
        // ORGANIZAR POR DATA
        // ==========================================

        const historico = {};

        // ==========================================
        // COLETA
        // ==========================================

            registrosColeta.forEach(function(item) {

                const data = item.data;

                if (!data) {
                    return;
                }

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

        // ==========================================
        // PREVISÕES
        // ==========================================

        registrosPrevisao.forEach(function(item) {

            const data =
                item.Data_Prevista ??
                item.data_prevista;

            if (!data) {
                return;
            }

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

        // ==========================================
        // VERIFICAR SE EXISTEM DADOS
        // ==========================================

        const datas =
            Object.keys(historico);

        historicoTabela.innerHTML = "";

        if (datas.length === 0) {

            historicoTabela.innerHTML = `
                <tr>
                    <td colspan="7" class="historico-sem-dados">
                        Nenhum dado histórico disponível.
                    </td>
                </tr>
            `;

            return;
        }

        // ==========================================
        // MAIS RECENTE PRIMEIRO
        // ==========================================

        datas.sort(function(a, b) {

            return (
                new Date(b) -
                new Date(a)
            );

        });

        // ==========================================
        // FORMATAR VALOR
        // ==========================================

        function formatarTemperatura(valor) {

            if (
                valor === null ||
                valor === undefined ||
                valor === ""
            ) {
                return "—";
            }

            const numero =
                Number(valor);

            if (Number.isNaN(numero)) {
                return "—";
            }

            return `${numero.toFixed(1)} °C`;
        }

        // ==========================================
        // CRIAR LINHAS
        // ==========================================

        datas.forEach(function(data) {

            const registro =
                historico[data];

            const linha =
                document.createElement("tr");

            // DATA
            const colunaData =
                document.createElement("td");

            colunaData.className =
                "historico-data";

            colunaData.textContent =
                formatarDataHistorico(data);

            // COLETA - MÍNIMA
            const coletaMin =
                document.createElement("td");

            coletaMin.className =
                "historico-valor historico-min";

            coletaMin.textContent =
                formatarTemperatura(
                    registro.coleta.minima
                );

            // COLETA - MÉDIA
            const coletaMedia =
                document.createElement("td");

            coletaMedia.className =
                "historico-valor historico-media";

            coletaMedia.textContent =
                formatarTemperatura(
                    registro.coleta.media
                );

            // COLETA - MÁXIMA
            const coletaMax =
                document.createElement("td");

            coletaMax.className =
                "historico-valor historico-max";

            coletaMax.textContent =
                formatarTemperatura(
                    registro.coleta.maxima
                );

            // PREVISÃO - MÍNIMA
            const previsaoMin =
                document.createElement("td");

            previsaoMin.className =
                "historico-valor historico-min";

            previsaoMin.textContent =
                formatarTemperatura(
                    registro.previsao.minima
                );

            // PREVISÃO - MÉDIA
            const previsaoMedia =
                document.createElement("td");

            previsaoMedia.className =
                "historico-valor historico-media";

            previsaoMedia.textContent =
                formatarTemperatura(
                    registro.previsao.media
                );

            // PREVISÃO - MÁXIMA
            const previsaoMax =
                document.createElement("td");

            previsaoMax.className =
                "historico-valor historico-max";

            previsaoMax.textContent =
                formatarTemperatura(
                    registro.previsao.maxima
                );

            // ==========================================
            // ADICIONAR CÉLULAS
            // ==========================================

            linha.appendChild(colunaData);

            linha.appendChild(coletaMin);
            linha.appendChild(coletaMedia);
            linha.appendChild(coletaMax);

            linha.appendChild(previsaoMin);
            linha.appendChild(previsaoMedia);
            linha.appendChild(previsaoMax);

            historicoTabela.appendChild(linha);

        });

    }
    catch (erro) {

        console.error(
            "Erro ao carregar histórico:",
            erro
        );

        historicoTabela.innerHTML = `
            <tr>
                <td colspan="7" class="historico-sem-dados">
                    Erro ao carregar o histórico.
                </td>
            </tr>
        `;
    }
}


// ==========================================
// HISTÓRICO DE PREVISÕES DA TELA PREVISÕES
// ==========================================

const historicoPrevisoesTabela =
    document.getElementById(
        "historico-previsoes-body"
    );


// ==========================================
// FORMATAR DATA E HORA DA PREVISÃO
// ==========================================

function formatarDataHoraPrevisao(
    data
) {

    if (!data) {
        return "--";
    }

    const texto =
        String(data);


    if (
        texto.includes(" ")
    ) {

        const partes =
            texto.split(" ");

        if (
            partes.length >= 2
        ) {

            const dataParte =
                partes[0];

            const horaParte =
                partes[1];

            const partesData =
                dataParte.split("-");

            if (
                partesData.length === 3
            ) {

                return (
                    partesData[2] +
                    "/" +
                    partesData[1] +
                    "/" +
                    partesData[0] +
                    " " +
                    horaParte.substring(
                        0,
                        5
                    )
                );
            }
        }
    }


    return formatarDataHistorico(
        texto
    );
}


// ==========================================
// CARREGAR HISTÓRICO DE PREVISÕES DA TELA PREVISÕES
// ==========================================

async function carregarHistoricoPrevisoes() {

    if (
        !historicoPrevisoesTabela
    ) {
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
            Array.isArray(
                dados.dados
            )
        ) {

            registros =
                dados.dados;
        }


        if (
            !Array.isArray(
                registros
            ) ||
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


        registros.forEach(
            function(item) {

                const linha =
                    document.createElement(
                        "tr"
                    );


                const colunaExecucao =
                    document.createElement(
                        "td"
                    );

                colunaExecucao.textContent =
                    formatarDataHoraPrevisao(
                        item.Data_Execucao ??
                        item.data_execucao
                    );


                const colunaDataPrevista =
                    document.createElement(
                        "td"
                    );

                colunaDataPrevista.textContent =
                    formatarDataHistorico(
                        item.Data_Prevista ??
                        item.data_prevista
                    );


                const colunaMediaPrevista =
                    document.createElement(
                        "td"
                    );

                colunaMediaPrevista.textContent =
                    formatarTemperaturaHistorico(
                        item.Temp_Media_Prevista_C ??
                        item.temp_media_prevista_c
                    );


                const colunaMinPrevista =
                    document.createElement(
                        "td"
                    );

                colunaMinPrevista.textContent =
                    formatarTemperaturaHistorico(
                        item.Temp_Min_Prevista_C ??
                        item.temp_min_prevista_c
                    );


                const colunaMaxPrevista =
                    document.createElement(
                        "td"
                    );

                colunaMaxPrevista.textContent =
                    formatarTemperaturaHistorico(
                        item.Temp_Max_Prevista_C ??
                        item.temp_max_prevista_c
                    );


                const colunaMediaReal =
                    document.createElement(
                        "td"
                    );

                colunaMediaReal.textContent =
                    formatarTemperaturaHistorico(
                        item.Temp_Media_API_Externa_C ??
                        item.temp_media_api_externa_c
                    );


                const colunaMinReal =
                    document.createElement(
                        "td"
                    );

                colunaMinReal.textContent =
                    formatarTemperaturaHistorico(
                        item.Temp_Min_API_Externa_C ??
                        item.temp_min_api_externa_c
                    );


                const colunaMaxReal =
                    document.createElement(
                        "td"
                    );

                colunaMaxReal.textContent =
                    formatarTemperaturaHistorico(
                        item.Temp_Max_API_Externa_C ??
                        item.temp_max_api_externa_c
                    );


                linha.appendChild(
                    colunaExecucao
                );

                linha.appendChild(
                    colunaDataPrevista
                );

                linha.appendChild(
                    colunaMediaPrevista
                );

                linha.appendChild(
                    colunaMinPrevista
                );

                linha.appendChild(
                    colunaMaxPrevista
                );

                linha.appendChild(
                    colunaMediaReal
                );

                linha.appendChild(
                    colunaMinReal
                );

                linha.appendChild(
                    colunaMaxReal
                );


                historicoPrevisoesTabela.appendChild(
                    linha
                );

            }
        );

    }
    catch (erro) {

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

function formatarTemperaturaHistorico(
    valor
) {

    if (
        valor === null ||
        valor === undefined ||
        valor === "" ||
        valor === "N/A" ||
        isNaN(valor)
    ) {

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
// SELETOR DO HISTÓRICO
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

        document.body.appendChild(
            overlay
        );
    }

    requestAnimationFrame(
        function() {

            overlay.classList.add(
                "ativo"
            );

        }
    );
}


function esconderLoadingAtualizacao() {

    const overlay =
        document.getElementById(
            "atualizacao-overlay"
        );

    if (overlay) {

        overlay.classList.remove(
            "ativo"
        );

    }

}

// ==========================================
// BOTÃO ATUALIZAR
// ==========================================

if (updateButton) {

    updateButton.addEventListener(
        "click",
        async function() {

            // Impedir múltiplos cliques
            updateButton.disabled = true;

            // Mostrar loading
            mostrarLoadingAtualizacao();

            try {

                // ==========================================
                // ATUALIZAR DADOS NO SERVIDOR
                // ==========================================

                const resposta =
                    await fetch(
                        "/api/atualizar",
                        {
                            method: "POST"
                        }
                    );


                const resultado =
                    await resposta.json();


                // ==========================================
                // VERIFICAR RESULTADO
                // ==========================================

                if (
                    resposta.ok &&
                    resultado.sucesso
                ) {

                    // ==========================================
                    // RECARREGAR PÁGINA
                    // ==========================================

                    window.location.reload();

                    return;
                }


                // ==========================================
                // ERRO
                // ==========================================

                console.error(
                    "Erro na atualização:",
                    resultado.erro
                );

                esconderLoadingAtualizacao();

                updateButton.innerHTML =
                    "⚠ Erro";

                updateButton.disabled =
                    false;

            }

            catch (erro) {

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

let intervaloAtualizacao =
    null;


async function atualizarDadosAutomaticamente() {

    try {

        // ==========================================
        // DADOS DA ESTAÇÃO
        // ==========================================

        await carregarDados();


        // ==========================================
        // GRÁFICO
        // ==========================================

        const metricaAtual =
            metricSelect
                ? metricSelect.value
                : "temperatura";


        await carregarGrafico(
            metricaAtual
        );


        // ==========================================
        // PREVISÃO ATUAL
        // ==========================================

        await carregarPrevisao();


        // ==========================================
        // HISTÓRICO METEOROLÓGICO
        // ==========================================

        const telaHistorico =
            document.getElementById(
                "tela-historico"
            );


        if (

            telaHistorico &&

            telaHistorico.style.display !==
                "none"

        ) {

            await carregarHistorico();

        }


        // ==========================================
        // HISTÓRICO DE PREVISÕES
        // ==========================================

        const telaPrevisoes =
            document.getElementById(
                "tela-previsoes"
            );


        if (

            telaPrevisoes &&

            telaPrevisoes.style.display !==
                "none"

        ) {

            await carregarHistoricoPrevisoes();

        }

    }

    catch (erro) {

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

    // ==========================================
    // MOSTRAR TELA INICIAL
    // ==========================================

    mostrarTela(
        "tela-inicial"
    );


    // ==========================================
    // CARREGAR DADOS
    // ==========================================

    await carregarDados();


    // ==========================================
    // CARREGAR GRÁFICO
    // ==========================================

    await carregarGrafico(

        metricSelect
            ? metricSelect.value
            : "temperatura"

    );


    // ==========================================
    // CARREGAR PREVISÃO
    // ==========================================

    await carregarPrevisao();


    // ==========================================
    // INICIAR ATUALIZAÇÃO AUTOMÁTICA
    // ==========================================

}
// ==========================================
// CLIMATEMPO
// ==========================================

async function carregarClimatempo() {

    try {

        const resposta = await fetch("/api/climatempo");

        const dados = await resposta.json();

        console.log("CLIMATEMPO:", dados);

        if (!dados.sucesso) {
            throw new Error(
                dados.erro || "Erro na API Climatempo"
            );
        }

        const minima = Number(dados.minima);
        const maxima = Number(dados.maxima);

        // Calcula a média
        const media = (minima + maxima) / 2;

        // MÍNIMA
        const elementoMin =
            document.getElementById("climatempo-min");

        if (elementoMin) {
            elementoMin.textContent =
                `${minima} °C`;
        }

        // MÁXIMA
        const elementoMax =
            document.getElementById("climatempo-max");

        if (elementoMax) {
            elementoMax.textContent =
                `${maxima} °C`;
        }

        // MÉDIA
        const elementoMedia =
            document.getElementById("climatempo-media");

        if (elementoMedia) {
            elementoMedia.textContent =
                media.toFixed(1);
        }

    } catch (erro) {

        console.error(
            "Erro ao carregar Climatempo:",
            erro
        );

    }

}
// ==========================================
// INICIAR SITE
// ==========================================

document.addEventListener(
    "DOMContentLoaded",
    function() {

        configurarNavegacao();

        iniciar();

        carregarClimatempo();

    }
);