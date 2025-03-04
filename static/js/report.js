document.addEventListener("DOMContentLoaded", function() {
    var ctx = document.getElementById('graficaProductos').getContext('2d');

    // Colores dinámicos para cada línea
    var dynamicColors = function() {
        var r = Math.floor(Math.random() * 255);
        var g = Math.floor(Math.random() * 255);
        var b = Math.floor(Math.random() * 255);
        return "rgba(" + r + "," + g + "," + b + ", 0.6)";
    };

    var backgroundColors = [];
    for (var i = 0; i < data.length; i++) {
        backgroundColors.push(dynamicColors());
    }

    var graficaProductos = new Chart(ctx, {
        type: 'line', // Tipo de gráfica: línea
        data: {
            labels: labels, // Etiquetas del eje X (aunque no se mostrarán)
            datasets: [{
                label: 'Cantidad Vendida', // Etiqueta del dataset
                data: data, // Datos del eje Y
                backgroundColor: backgroundColors, // Colores de fondo
                borderColor: backgroundColors.map(color => color.replace('0.6', '1')), // Colores del borde
                borderWidth: 2, // Grosor de la línea
                fill: false, // No rellenar el área bajo la línea
                tension: 0.4 // Suavizado de la línea
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true // El eje Y comienza en 0
                },
                x: {
                    display: false // Oculta el eje X y sus etiquetas
                }
            },
            plugins: {
                legend: {
                    display: true, // Mostrar la leyenda
                    position: 'top' // Posición de la leyenda
                }
            }
        }
    });
});