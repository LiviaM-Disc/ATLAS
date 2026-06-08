

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
        // Converte valores para float, tratando campos vazios como 0
        const custo = parseFloat(custoEl.value) || 0;
        const margem = parseFloat(margemEl.value) || 0;
        const impostos = parseFloat(impostosEl.value) || 0;

        if (custo > 0) {
            // Lógica de Markup (sobre o custo)
            const precoFinal = custo * (1 + (margem / 100) + (impostos / 100));
            output.textContent = formatter.format(precoFinal);
        } else {
            output.textContent = "R$ 0,00";
        }
    }

    // Adiciona o evento de escuta nos três campos
    [custoEl, margemEl, impostosEl].forEach(el => {
        if (el) {
            el.addEventListener("input", calcularPreco);
        }
    });

    // Roda uma vez ao carregar para garantir que o total esteja zerado ou atualizado
    calcularPreco();
});