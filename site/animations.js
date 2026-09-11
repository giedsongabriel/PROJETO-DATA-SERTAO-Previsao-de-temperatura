// ==========================================
// ANIMATIONS.JS
// Micro-interações que combinam com as animações
// já definidas no style.css (fadeIn, slideInLeft,
// statusPulse, ripple, valueFlash, badgeGlow,
// reveal-on-scroll). Sem tilt/3D — removido por
// deixar o card do gráfico estranho.
// Não mexe na lógica de dados do script.js.
// ==========================================

document.addEventListener("DOMContentLoaded", () => {

    // --------------------------------------
    // 1) SCROLL REVEAL
    // --------------------------------------
    // Usa a classe .reveal-on-scroll / .is-visible
    // que já existe no style.css.

    const alvosScroll = document.querySelectorAll(
        ".chart-card, .bottom-grid .card"
    );

    alvosScroll.forEach((el) => {
        el.classList.add("reveal-on-scroll");
    });

    const observer = new IntersectionObserver(
        (entradas) => {
            entradas.forEach((entrada) => {
                if (entrada.isIntersecting) {
                    entrada.target.classList.add("is-visible");
                    observer.unobserve(entrada.target);
                }
            });
        },
        {
            threshold: 0.15,
            rootMargin: "0px 0px -40px 0px"
        }
    );

    alvosScroll.forEach((el) => observer.observe(el));


    // --------------------------------------
    // 2) CONTAGEM ANIMADA DOS NÚMEROS
    // --------------------------------------
    // Sempre que o script.js atualizar o texto de um
    // valor, anima a contagem até o número novo em vez
    // de trocar seco. Preserva prefixo/sufixo (°C, m/s,
    // °, etc.) que estejam junto do número no mesmo elemento.

    const idsAnimados = [
        "temperatura",
        "umidade",
        "pressao",
        "vento",
        "previsao",
        "prev_min",
        "prev_max",
        "pontoOrvalho",
        "direcaoVento",
        "velocidadeVento",
        "rajadaVento"
    ];

    const estadoAnterior = {};

    function extrairNumero(texto) {

        const match = texto.match(/-?\d+(?:[.,]\d+)?/);

        if (!match) {
            return null;
        }

        return {
            numero: parseFloat(match[0].replace(",", ".")),
            prefixo: texto.slice(0, match.index),
            sufixo: texto.slice(match.index + match[0].length),
            temDecimal: match[0].includes(",") || match[0].includes(".")
        };
    }

    function animarNumero(elemento, partesNovas) {

        const anterior = estadoAnterior[elemento.id];

        const partida = (anterior && !isNaN(anterior.numero))
            ? anterior.numero
            : partesNovas.numero;

        const destino = partesNovas.numero;

        const duracao = 600;
        const inicioTempo = performance.now();

        function passo(agora) {

            const progresso = Math.min(
                (agora - inicioTempo) / duracao,
                1
            );

            const suavizado = 1 - Math.pow(1 - progresso, 3);

            const valorAtual = partida + (destino - partida) * suavizado;

            const valorFormatado = partesNovas.temDecimal
                ? valorAtual.toFixed(1).replace(".", ",")
                : Math.round(valorAtual);

            elemento.textContent =
                partesNovas.prefixo + valorFormatado + partesNovas.sufixo;

            if (progresso < 1) {
                requestAnimationFrame(passo);
            } else {

                elemento.textContent =
                    partesNovas.prefixo
                    + (partesNovas.temDecimal
                        ? destino.toFixed(1).replace(".", ",")
                        : destino)
                    + partesNovas.sufixo;

                elemento.classList.add("value-updated");

                setTimeout(() => {
                    elemento.classList.remove("value-updated");
                }, 700);
            }
        }

        requestAnimationFrame(passo);
    }

    idsAnimados.forEach((id) => {

        const elemento = document.getElementById(id);

        if (!elemento) {
            return;
        }

        estadoAnterior[id] = extrairNumero(elemento.textContent.trim());

        const monitor = new MutationObserver(() => {

            const textoNovo = elemento.textContent.trim();
            const partesNovas = extrairNumero(textoNovo);

            if (!partesNovas) {
                return;
            }

            const eraIgual =
                estadoAnterior[id]
                &&
                estadoAnterior[id].numero === partesNovas.numero
                &&
                estadoAnterior[id].prefixo === partesNovas.prefixo
                &&
                estadoAnterior[id].sufixo === partesNovas.sufixo;

            if (eraIgual) {
                return;
            }

            monitor.disconnect();

            // Se não havia número antes (placeholder "--"),
            // apenas define o valor sem animar a contagem.
            if (!estadoAnterior[id]) {
                elemento.textContent = textoNovo;
            } else {
                animarNumero(elemento, partesNovas);
            }

            estadoAnterior[id] = partesNovas;

            monitor.observe(elemento, {
                childList: true,
                characterData: true,
                subtree: true
            });
        });

        monitor.observe(elemento, {
            childList: true,
            characterData: true,
            subtree: true
        });
    });


    // --------------------------------------
    // 3) RIPPLE NO BOTÃO ATUALIZAR
    // --------------------------------------
    // Usa a classe .ripple e a keyframe rippleEffect
    // que já existem no style.css.

    const botaoAtualizar = document.querySelector(".update-button");

    if (botaoAtualizar) {

        botaoAtualizar.addEventListener("click", (evento) => {

            const ripple = document.createElement("span");

            const tamanho = Math.max(
                botaoAtualizar.clientWidth,
                botaoAtualizar.clientHeight
            );

            const retangulo = botaoAtualizar.getBoundingClientRect();

            ripple.className = "ripple";

            ripple.style.width = ripple.style.height = `${tamanho}px`;

            ripple.style.left = `${evento.clientX - retangulo.left - tamanho / 2}px`;
            ripple.style.top = `${evento.clientY - retangulo.top - tamanho / 2}px`;

            botaoAtualizar.appendChild(ripple);

            setTimeout(() => ripple.remove(), 600);

            botaoAtualizar.classList.add("is-loading");

            setTimeout(() => {
                botaoAtualizar.classList.remove("is-loading");
            }, 1200);
        });
    }

});
