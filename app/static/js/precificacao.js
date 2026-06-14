document.addEventListener("DOMContentLoaded", function () {
    const formatter = new Intl.NumberFormat("pt-BR", {
        style: "currency",
        currency: "BRL"
    });

    const custoEl = document.getElementById("custo");
    const margemEl = document.getElementById("margem");
    const impostosEl = document.getElementById("impostos");
    const output = document.getElementById("preco-final");

    function calcularPreco() {
        // Força a conversão substituindo vírgula por ponto, caso o usuário digite com vírgula
        const custo = parseFloat(custoEl.value.replace(',', '.')) || 0;
        const margem = parseFloat(margemEl.value.replace(',', '.')) || 0;
        const impostos = parseFloat(impostosEl.value.replace(',', '.')) || 0;

        const somaPorcentagens = margem + impostos;

        // Validação da regra de negócio do Markup Divisor
        if (custo > 0 && somaPorcentagens < 100) {
            const precoFinal = custo / (1 - (somaPorcentagens / 100));
            output.textContent = formatter.format(precoFinal);
        } else if (somaPorcentagens >= 100) {
            output.textContent = "Inválido (>= 100%)";
        } else {
            output.textContent = "R$ 0,00";
        }
    }

    // Escuta tanto "input" quanto "change" para garantir que funcione em qualquer navegador
    [custoEl, margemEl, impostosEl].forEach(el => {
        if (el) {
            el.addEventListener("input", calcularPreco);
            el.addEventListener("change", calcularPreco);
        }
    });

    // Executa imediatamente para atualizar caso o navegador tenha guardado valores no cache
    calcularPreco();
});