<script>
    // *******************************************************************
    // TODO: Asegúrate de que tus variables 'empleadoActual' y
    // 'equiposSeleccionados' estén definidas globalmente (o accesibles)
    // y se llenen correctamente con tu lógica existente.
    // Aquí se inicializan como ejemplo si no lo están ya.
    // *******************************************************************
    let empleadoActual = null; // Asumiendo que esta variable se llena en alguna parte de tu JS
    let equiposSeleccionados = []; // Asumiendo que esta variable se llena en alguna parte de tu JS

    // (TUS FUNCIONES EXISTENTES COMO Tabs, Resumen, y lógica de búsqueda de persona, equipos, chips, etc. DEBEN IR AQUÍ)
    // Por ejemplo:
    const Tabs = {
        cambiarTab: function(tabId) {
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.add('hidden');
            });
            document.getElementById(tabId).classList.remove('hidden');

            document.querySelectorAll('.tab-button').forEach(button => {
                button.classList.remove('bg-blue-500', 'text-white');
                button.classList.add('text-blue-700', 'hover:bg-blue-100');
            });
            document.querySelector(`.tab-button[data-tab="${tabId}"]`).classList.add('bg-blue-500', 'text-white');
            document.querySelector(`.tab-button[data-tab="${tabId}"]`).classList.remove('text-blue-700', 'hover:bg-blue-100');
        }
    };

    const Resumen = {
        actualizarResumen: function() {
            const responsableEntrega = document.getElementById('responsable-entrega').value;
            const responsableDevolucion = document.getElementById('responsable-devolucion').value;
            const tipoPrestamoElement = document.querySelector('input[name="tipo-prestamo"]:checked');
            const tipoPrestamo = tipoPrestamoElement ? tipoPrestamoElement.nextElementSibling.textContent.trim() : 'No seleccionado';
            const detallePrestamo = document.getElementById('detalle-prestamo').value;

            document.getElementById('resumen-responsable-entrega').textContent = responsableEntrega || 'N/A';
            document.getElementById('resumen-responsable-devolucion').textContent = responsableDevolucion || 'N/A';
            document.getElementById('resumen-tipo-prestamo').textContent = tipoPrestamo || 'N/A';
            document.getElementById('resumen-detalle-prestamo').textContent = detallePrestamo || 'N/A';

            const resumenEquiposList = document.getElementById('resumen-equipos-list');
            resumenEquiposList.innerHTML = ''; // Limpiar lista
            if (equiposSeleccionados.length > 0) {
                equiposSeleccionados.forEach(equipo => {
                    const li = document.createElement('li');
                    li.textContent = `Serie: ${equipo.serie}, Modelo: ${equipo.modelo}, Categoría: ${equipo.categoria}`;
                    resumenEquiposList.appendChild(li);
                });
            } else {
                const li = document.createElement('li');
                li.textContent = 'No se han seleccionado equipos.';
                resumenEquiposList.appendChild(li);
            }
        }
    };

    // Función para cargar tipos de préstamo (ejemplo, debes tener la tuya)
    async function cargarTiposPrestamo() {
        try {
            const response = await fetch('/prestamos/tipos_prestamo');
            if (response.ok) {
                const tipos = await response.json();
                const contenedorTipos = document.getElementById('tipo-prestamo-container');
                contenedorTipos.innerHTML = ''; // Limpiar opciones existentes
                tipos.forEach(tipo => {
                    const div = document.createElement('div');
                    div.className = 'flex items-center';
                    div.innerHTML = `
                        <input type="radio" id="tipo-${tipo.id}" name="tipo-prestamo" value="${tipo.id}" class="form-radio h-4 w-4 text-blue-600">
                        <label for="tipo-${tipo.id}" class="ml-2 text-gray-700">${tipo.nombre}</label>
                    `;
                    contenedorTipos.appendChild(div);
                });
            } else {
                console.error('Error al cargar tipos de préstamo:', await response.text());
            }
        } catch (error) {
            console.error('Error de red al cargar tipos de préstamo:', error);
        }
    }
    // Llama a cargarTiposPrestamo() en DOMContentLoaded si es necesario

    // *******************************************************************
    // LÓGICA PRINCIPAL - EVENT LISTENER PARA EL BOTÓN "FINALIZAR PRÉSTAMO"
    // ESTE ES EL BLOQUE QUE DEBES AÑADIR/VERIFICAR
    // *******************************************************************
    document.addEventListener('DOMContentLoaded', () => {
        // Asegúrate de que el botón tiene el ID 'confirmar-prestamo' en tu HTML
        const btnFinalizarPrestamo = document.getElementById('confirmar-prestamo');

        if (btnFinalizarPrestamo) {
            btnFinalizarPrestamo.addEventListener('click', async () => {
                console.log('DEBUG (Frontend): Botón "Finalizar Préstamo" clicado.');

                // Confirmación opcional antes de enviar
                if (!confirm('¿Está seguro de finalizar el préstamo?')) {
                    console.log('DEBUG (Frontend): Envío cancelado por el usuario.');
                    return;
                }

                // === Recopilar todos los datos ===
                // Datos de la pestaña "Entrega"
                const responsableEntrega = document.getElementById('responsable-entrega').value;
                const responsableDevolucion = document.getElementById('responsable-devolucion').value;
                const tipoPrestamoElement = document.querySelector('input[name="tipo-prestamo"]:checked');
                const tipoPrestamo = tipoPrestamoElement ? tipoPrestamoElement.value : null;
                const detallePrestamo = document.getElementById('detalle-prestamo').value;

                // Datos de la pestaña "Equipos" (asegúrate de que 'equiposSeleccionados' esté poblado)
                if (typeof equiposSeleccionados === 'undefined' || equiposSeleccionados.length === 0) {
                    alert('Debe seleccionar al menos un equipo para finalizar el préstamo.');
                    console.error('ERROR (Frontend): No hay equipos seleccionados.');
                    return;
                }

                const datosPrestamo = {
                    responsable_entrega: responsableEntrega,
                    responsable_devolucion: responsableDevolucion,
                    tipo_prestamo: tipoPrestamo,
                    detalle_prestamo: detallePrestamo,
                    equipos_seleccionados: equiposSeleccionados
                };

                console.log('DEBUG (Frontend): Datos a enviar al backend:', datosPrestamo);

                try {
                    console.log('DEBUG (Frontend): Iniciando fetch POST a /prestamos/finalizar-prestamo');
                    // ¡¡¡ESTA ES LA LÍNEA MÁS IMPORTANTE PARA EL ENVÍO!!!
                    const response = await fetch('/prestamos/finalizar-prestamo', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(datosPrestamo),
                    });
                    console.log('DEBUG (Frontend): Respuesta del servidor recibida.');

                    const result = await response.json();
                    console.log('DEBUG (Frontend): Resultado del servidor:', result);

                    if (response.ok) {
                        alert(result.mensaje + ` ID: ${result.prestamo_id}`);
                        console.log('DEBUG (Frontend): Préstamo registrado con éxito. Redirigiendo...');
                        window.location.href = '/dashboard';
                    } else {
                        alert('Error al finalizar el préstamo: ' + result.detail);
                        console.error('ERROR (Frontend): Error del servidor:', result);
                    }
                } catch (error) {
                    console.error('ERROR (Frontend): Error de red o JavaScript al enviar el préstamo:', error);
                    alert('Ocurrió un error al intentar registrar el préstamo. Por favor, inténtelo de nuevo.');
                }
            });
        } else {
            console.warn('ADVERTENCIA (Frontend): Botón #confirmar-prestamo no encontrado. La lógica de envío no se adjuntará.');
        }

        // Lógica para el cambio de pestañas (ya la tienes)
        document.querySelectorAll('.tab-button').forEach(button => {
            button.addEventListener('click', () => {
                const tabId = button.dataset.tab;
                let puedeCambiar = true;

                // ... (tus validaciones de cambio de pestaña existentes) ...

                if (puedeCambiar) {
                    if (tabId === 'resumen') {
                        Resumen.actualizarResumen();
                    }
                    Tabs.cambiarTab(tabId);
                }
            });
        });

        // Llama a las funciones de carga de datos al inicio
        cargarTiposPrestamo(); // Asegúrate de que esta función exista y funcione

        // Aquí irían otras inicializaciones que necesites, como la carga de equipos, etc.
        // ...
    });
</script>