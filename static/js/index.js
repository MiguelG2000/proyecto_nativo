document.addEventListener("DOMContentLoaded", function () {
    let btnNotificaciones = document.getElementById("btnNotificaciones");
    let notificacionesContainer = document.getElementById("notificacionesContainer");
    let notificacionesList = document.getElementById("notificacionesList");
    let notificacionesCount = document.getElementById("notificacionesCount");

    // Función para actualizar el contador de notificaciones
    function actualizarContador() {
        let count = document.querySelectorAll(".notification-item").length;
        if (count > 0) {
            notificacionesCount.textContent = count;
            notificacionesCount.classList.remove("hidden");
        } else {
            notificacionesCount.textContent = "0"; // Mostrar 0 si no hay notificaciones
            notificacionesCount.classList.add("hidden");
        }
    }

    // Mostrar/Ocultar notificaciones al hacer clic en el botón
    btnNotificaciones.addEventListener("click", function (event) {
        notificacionesContainer.classList.toggle("hidden");
        event.stopPropagation(); // Evita que se cierre inmediatamente
    });

    // Cerrar el contenedor si se hace clic fuera
    document.addEventListener("click", function (event) {
        if (!notificacionesContainer.contains(event.target) && !btnNotificaciones.contains(event.target)) {
            notificacionesContainer.classList.add("hidden");
        }
    });

    // Marcar como visto una notificación individual
    notificacionesList.addEventListener("click", function (event) {
        if (event.target.classList.contains("mark-as-read")) {
            let notificationItem = event.target.closest(".notification-item");
            notificationItem.style.opacity = "0.5"; // Indica que está vista
            setTimeout(() => {
                notificationItem.remove(); // Elimina la notificación después de un tiempo
                actualizarContador(); // Actualiza el contador
            }, 300);
        }
    });

    // Inicializar el contador al cargar la página
    actualizarContador();
});