const ctx = document.getElementById('meuGraficoFinanceiro').getContext('2d');

const meuGrafico = new Chart(ctx, {
    type: 'line', // Tipo: Linha (pode ser 'bar' para barras)
    data: {
        labels: ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun'], // Eixo X
        datasets: [{
            label: 'Receitas',
            data: [12000, 19000, 15000, 25000, 22000, 30000], // Dados fictícios
            borderColor: '#00d1b2', // Verde neon
            backgroundColor: 'rgba(0, 209, 178, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4 // Deixa a linha curvada/suave
        }, {
            label: 'Despesas',
            data: [10000, 15000, 12000, 18000, 16000, 21000],
            borderColor: '#ff4d4d', // Vermelho suave
            backgroundColor: 'rgba(255, 77, 77, 0.1)',
            borderWidth: 3,
            fill: true,
            tension: 0.4
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                labels: { color: '#ffffff' } // Cor da legenda
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                grid: { color: '#333' }, // Cor das linhas de grade
                ticks: { color: '#ffffff' } // Cor dos números
            },
            x: {
                grid: { color: '#333' },
                ticks: { color: '#ffffff' }
            }
        }
    }
});