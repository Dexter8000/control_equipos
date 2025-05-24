// Variables globales
let equiposSeleccionados = [];
let empleadoActual = null;
let equipoActual = null;
let numPrestamo = '';
let trabajadores = [];
let departamentos = [];
let equipos;

// Cargar datos desde archivos JSON
async function cargarDatos() {
    try {
        const [trabajadoresRes, departamentosRes, equiposRes] = await Promise.all([
            fetch('/data/Trabajadores.json'),
            fetch('/data/departamentos.json'),
            fetch('/data/inventario.json')
        ]);

        if (!trabajadoresRes.ok || !departamentosRes.ok || !equiposRes.ok) {
            throw new Error('Error al cargar los datos');
        }

        trabajadores = await trabajadoresRes.json();
        departamentos = await departamentosRes.json();
        equipos = await equiposRes.json();

        console.log('Datos cargados correctamente');
    } catch (error) {
        console.error('Error al cargar los datos:', error);
    }
}

// Módulo para manejar las búsquedas
const Busqueda = {
    buscarEmpleado: function() {
        const placa = document.getElementById('placa-empleado').value.trim();
        if (!placa) {
            this.mostrarError('placa-empleado', 'Por favor, ingrese un número de placa.');
            return;
        }

        const empleado = trabajadores.find(t => t.placa === placa);

        if (empleado) {
            // Encontrado, mostrar datos
            document.getElementById('error-empleado').classList.add('hidden');
            document.getElementById('datos-empleado').classList.remove('hidden');

            document.getElementById('rango-empleado').textContent = empleado.rango;
            document.getElementById('nombre-empleado').textContent = `${empleado.nombre} ${empleado.apellido}`;
            document.getElementById('id-empleado').textContent = empleado.id;

            // Buscar departamento
            const departamento = departamentos.find(d => d.id === empleado.departamento_id);
            document.getElementById('departamento-empleado').textContent = departamento ? departamento.nombre : 'No asignado';

            // Guardar empleado actual
            empleadoActual = empleado;
        } else {
            // No encontrado, mostrar error
            document.getElementById('datos-empleado').classList.add('hidden');
            document.getElementById('error-empleado').classList.remove('hidden');
            empleadoActual = null;
        }
    },

    buscarEquipo: function() {
        const serie = document.getElementById('serie-equipo').value.trim();
        if (!serie) {
            this.mostrarError('serie-equipo', 'Por favor, ingrese un número de serie.');
            return;
        }

        const equipo = equipos.find(t => t.serie === serie);

        if (equipo) {
            // Encontrado, mostrar datos
            document.getElementById('error-equipo').classList.add('hidden');
            document.getElementById('datos-equipo').classList.remove('hidden');

            document.getElementById('nombre-equipo').textContent = equipo.nombre;
            document.getElementById('marca-equipo').textContent = equipo.marca;
            document.getElementById('modelo-equipo').textContent = equipo.modelo;
            document.getElementById('categoria-equipo').textContent = equipo.categoria;
            document.getElementById('subcategoria-equipo').textContent = equipo.subcategoria;
            document.getElementById('estado-equipo').textContent = equipo.estado;

            // Mostrar campo SIM si es teléfono satelital
            const simContainer = document.getElementById('sim-container');
            if (equipo.categoria === "Comunicación Satelital" && equipo.subcategoria === "Teléfonos satelitales") {
                simContainer.classList.remove('hidden');
                document.getElementById('numero-sim').value = '';
            } else {
                simContainer.classList.add('hidden');
            }

            // Guardar equipo actual
            equipoActual = equipo;
        } else {
            // No encontrado, mostrar error
            document.getElementById('datos-equipo').classList.add('hidden');
            document.getElementById('error-equipo').classList.remove('hidden');
            equipoActual = null;
        }
    },

    mostrarError: function(elementId, mensaje) {
        const errorElement = document.getElementById(`error-${elementId}`);
        errorElement.textContent = mensaje;
        errorElement.classList.remove('hidden');
        errorElement.classList.add('fade-in');
    }
};

// Módulo para manejar la adición de equipos
const Equipos = {
    agregarEquipo: function() {
        if (!equipoActual) {
            alert('Por favor, busque un equipo primero.');
            return;
        }

        // Verificar si ya está en la lista
        if (equiposSeleccionados.find(e => e.id === equipoActual.id)) {
            alert('Este equipo ya está en la lista de préstamos.');
            return;
        }

        // Obtener número SIM si es teléfono satelital
        let numeroSim = '';
        if (equipoActual.categoria === "Comunicación Satelital" && equipoActual.subcategoria === "Teléfonos satelitales") {
            numeroSim = document.getElementById('numero-sim').value.trim();
            if (!numeroSim) {
                alert('Por favor, ingrese el número SIM del teléfono satelital.');
                return;
            }
        }

        // Crear copia del equipo con el número SIM
        const equipoConSim = {
            ...equipoActual,
            numeroSim: numeroSim
        };

        // Agregar a la lista de equipos seleccionados
        equiposSeleccionados.push(equipoConSim);

        // Agregar a la tabla de visualización
        const tbody = document.getElementById('lista-equipos');
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-gray-50';
        tr.innerHTML = `
            <td class="py-3 px-4">${equipoActual.serie}</td>
            <td class="py-3 px-4">${equipoActual.nombre}</td>
            <td class="py-3 px-4">${equipoActual.marca}</td>
            <td class="py-3 px-4">${equipoActual.modelo}</td>
            <td class="py-3 px-4">
                <button type="button" class="eliminar-equipo text-red-600 hover:text-red-800 font-medium"
                        data-id="${equipoActual.id}">
                    <i class="fas fa-trash mr-1"></i> Eliminar
                </button>
            </td>
        `;

        tbody.appendChild(tr);

        // Actualizar contador de equipos
        actualizarContadorEquipos();

        // Agregar el evento de eliminación
        tr.querySelector('.eliminar-equipo').addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            Equipos.eliminarEquipo(id, tr);
        });

        // Limpiar selección actual
        document.getElementById('serie-equipo').value = '';
        document.getElementById('datos-equipo').classList.add('hidden');
        document.getElementById('sim-container').classList.add('hidden');
        equipoActual = null;
    },

    eliminarEquipo: function(id, elemento) {
        // Eliminar del array
        equiposSeleccionados = equiposSeleccionados.filter(e => e.id !== id);

        // Eliminar del DOM
        elemento.remove();

        // Actualizar contador
        actualizarContadorEquipos();
    }
};

// Módulo para manejar las pestañas
const Tabs = {
    cambiarTab: function(tabId) {
        // Ocultar todos los contenidos de pestañas
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.add('hidden');
            content.classList.remove('active');
        });

        // Mostrar el contenido de la pestaña seleccionada
        document.getElementById(`content-${tabId}`).classList.remove('hidden');
        document.getElementById(`content-${tabId}`).classList.add('active');

        // Actualizar estado de los botones de pestaña
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active', 'text-blue-800', 'border-blue-800');
            btn.classList.add('text-gray-500');
        });

        // Activar el botón de la pestaña seleccionada
        document.getElementById(`tab-${tabId}`).classList.add('active', 'text-blue-800', 'border-blue-800');
        document.getElementById(`tab-${tabId}`).classList.remove('text-gray-500');
    },

    validarAntesDeCambiar: function(tabActual, tabSiguiente) {
        // Validaciones específicas antes de cambiar de pestaña
        if (tabActual === 'empleado' && tabSiguiente === 'entrega') {
            if (!empleadoActual) {
                alert('Debe buscar y seleccionar un empleado válido antes de continuar.');
                return false;
            }
        }

        if (tabActual === 'entrega' && tabSiguiente === 'equipos') {
            const responsable = document.getElementById('responsable-entrega').value;
            if (!responsable) {
                alert('Debe seleccionar un responsable de entrega.');
                return false;
            }

            const tipoPrestamo = document.querySelector('input[name="tipo-prestamo"]:checked');
            if (!tipoPrestamo) {
                alert('Debe seleccionar un tipo de préstamo.');
                return false;
            }

            const detalle = document.getElementById('detalle-prestamo').value;
            if (!detalle) {
                alert('Debe ingresar el detalle del tipo de préstamo.');
                return false;
            }
        }

        if (tabActual === 'equipos' && tabSiguiente === 'resumen') {
            if (equiposSeleccionados.length === 0) {
                alert('Debe agregar al menos un equipo al préstamo.');
                return false;
            }
        }

        return true;
    }
};

// Módulo para manejar el resumen
const Resumen = {
    actualizarResumen: function() {
        if (!empleadoActual) return;

        // Actualizar datos del empleado
        const departamento = departamentos.find(d => d.id === empleadoActual.departamento_id);
        document.getElementById('resumen-empleado').innerHTML = `
            <p class="text-sm text-gray-600">Nombre:</p>
            <p class="font-semibold text-blue-800 mb-2">${empleadoActual.nombre} ${empleadoActual.apellido}</p>

            <p class="text-sm text-gray-600">Placa:</p>
            <p class="font-semibold text-blue-800 mb-2">${empleadoActual.placa}</p>

            <p class="text-sm text-gray-600">Departamento:</p>
            <p class="font-semibold text-blue-800">${departamento ? departamento.nombre : 'No asignado'}</p>
        `;

        // Actualizar datos de entrega
        const responsable = document.getElementById('responsable-entrega').value;
        const tipoPrestamo = document.querySelector('input[name="tipo-prestamo"]:checked').value;
        const detallePrestamo = document.getElementById('detalle-prestamo').value;

        document.getElementById('resumen-entrega').innerHTML = `
            <p class="text-sm text-gray-600">Responsable:</p>
            <p class="font-semibold text-blue-800 mb-2">${responsable}</p>

            <p class="text-sm text-gray-600">Tipo de préstamo:</p>
            <p class="font-semibold text-blue-800 mb-2">${tipoPrestamo}</p>

            <p class="text-sm text-gray-600">Detalle:</p>
            <p class="font-semibold text-blue-800">${detallePrestamo}</p>
        `;

        // Actualizar lista de equipos
        const tbody = document.getElementById('resumen-lista-equipos');
        tbody.innerHTML = '';

        equiposSeleccionados.forEach(equipo => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="py-2 px-4">${equipo.serie}</td>
                <td class="py-2 px-4">${equipo.nombre}</td>
                <td class="py-2 px-4">${equipo.marca}</td>
                <td class="py-2 px-4">${equipo.modelo}</td>
                <td class="py-2 px-4">${equipo.numeroSim || 'N/A'}</td>
            `;
            tbody.appendChild(tr);
        });

        document.getElementById('resumen-total-equipos').textContent = equiposSeleccionados.length;
    }
};

// Inicializar fecha y número de préstamo
function inicializarFechaYNumero() {
    // Mostrar fecha actual
    const fechaActual = new Date();
    const options = { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' };
    document.getElementById('fecha-actual').textContent = fechaActual.toLocaleDateString('es-ES', options);

    // Generar número de préstamo (fecha + hora + random)
    const hora = fechaActual.getHours().toString().padStart(2, '0');
    const minutos = fechaActual.getMinutes().toString().padStart(2, '0');
    const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
    numPrestamo = `PREST-${fechaActual.getFullYear()}${(fechaActual.getMonth() + 1).toString().padStart(2, '0')}${fechaActual.getDate().toString().padStart(2, '0')}-${hora}${minutos}-${random}`;

    document.getElementById('num-prestamo').textContent = numPrestamo;
}

// Actualizar el contador de equipos
function actualizarContadorEquipos() {
    document.getElementById('total-equipos').textContent = equiposSeleccionados.length;
    document.getElementById('resumen-total-equipos').textContent = equiposSeleccionados.length;
}

// Finalizar préstamo
function finalizarPrestamo(e) {
    e.preventDefault();

    // Validaciones finales
    if (!empleadoActual) {
        alert('Debe seleccionar un empleado válido.');
        return;
    }

    const responsableEntrega = document.getElementById('responsable-entrega').value;
    if (!responsableEntrega) {
        alert('Debe seleccionar un responsable de entrega.');
        return;
    }

    const tipoPrestamo = document.querySelector('input[name="tipo-prestamo"]:checked');
    if (!tipoPrestamo) {
        alert('Debe seleccionar un tipo de préstamo.');
        return;
    }

    const detallePrestamo = document.getElementById('detalle-prestamo').value;
    if (!detallePrestamo) {
        alert('Debe ingresar el detalle del tipo de préstamo.');
        return;
    }

    if (equiposSeleccionados.length === 0) {
        alert('Debe agregar al menos un equipo al préstamo.');
        return;
    }

    // Crear objeto con los datos del préstamo
    const prestamoData = {
        fecha: document.getElementById('fecha-actual').textContent,
        numero_prestamo: numPrestamo,
        empleado: {
            nombre: `${empleadoActual.nombre} ${empleadoActual.apellido}`,
            placa: empleadoActual.placa,
            departamento: departamentos.find(d => d.id === empleadoActual.departamento_id)?.nombre || 'No asignado'
        },
        entrega: {
            responsable: responsableEntrega,
            tipo_prestamo: tipoPrestamo.value,
            detalle_prestamo: detallePrestamo
        },
        equipos: equiposSeleccionados.map(e => ({
            serie: e.serie,
            nombre: e.nombre,
            marca: e.marca,
            modelo: e.modelo,
            numero_sim: e.numeroSim || 'N/A'
        }))
    };

    // Imprimir los datos que se enviarán al servidor
    console.log('Datos a enviar:', prestamoData);

    // Enviar los datos al backend FastAPI
    fetch('/prestamos/finalizar-prestamo', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(prestamoData)
    })
    .then(res => {
        if (!res.ok) {
            return res.json().then(err => { throw new Error(err.detail || 'Error desconocido'); });
        }
        return res.json();
    })
    .then(res => {
        console.log('Respuesta del backend:', res);
        // Mostrar modal de confirmación
        document.getElementById('modal-num-prestamo').textContent = numPrestamo;
        document.getElementById('confirm-modal').classList.remove('hidden');
    })
    .catch(err => {
        console.error('Error al guardar el préstamo:', err.message);
        alert('Error al guardar el préstamo: ' + err.message);
    });
}


// Inicialización del formulario
document.addEventListener('DOMContentLoaded', async function() {
    // Cargar datos desde archivos JSON
    await cargarDatos();

    // Inicializar fecha y número de préstamo
    inicializarFechaYNumero();

    // Configurar radios personalizados
    document.querySelectorAll('.tipo-prestamo-radio').forEach(radio => {
        radio.addEventListener('change', function() {
            // Actualizar visualización del radio
            document.querySelectorAll('.radio-dot').forEach(dot => {
                dot.classList.add('hidden');
            });

            const label = document.querySelector(`label[for="${this.id}"]`);
            label.querySelector('.radio-dot').classList.remove('hidden');

            // Mostrar/ocultar detalle según tipo
            const detalleTipoPrestamo = document.getElementById('detalle-tipo-prestamo');
            if (this.checked) {
                detalleTipoPrestamo.classList.remove('hidden');
                document.getElementById('detalle-prestamo').value = this.value !== 'otro' ? this.value + ' ' : '';
            }
        });
    });

    // Seleccionar PAT por defecto
    document.getElementById('tipo-pat').checked = true;
    document.querySelector('label[for="tipo-pat"] .radio-dot').classList.remove('hidden');
    document.getElementById('detalle-tipo-prestamo').classList.remove('hidden');
    document.getElementById('detalle-prestamo').value = 'PAT ';

    // Event listeners para búsqueda de empleado
    document.getElementById('buscar-empleado').addEventListener('click', Busqueda.buscarEmpleado);
    document.getElementById('placa-empleado').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            Busqueda.buscarEmpleado();
        }
    });

    // Event listeners para búsqueda de equipo
    document.getElementById('buscar-equipo').addEventListener('click', Busqueda.buscarEquipo);
    document.getElementById('serie-equipo').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            Busqueda.buscarEquipo();
        }
    });

    // Event listener para agregar equipo
    document.getElementById('agregar-equipo').addEventListener('click', Equipos.agregarEquipo);

    // Event listeners para navegación entre pestañas
    document.getElementById('next-to-entrega').addEventListener('click', function() {
        if (Tabs.validarAntesDeCambiar('empleado', 'entrega')) {
            Tabs.cambiarTab('entrega');
        }
    });

    document.getElementById('next-to-equipos').addEventListener('click', function() {
        if (Tabs.validarAntesDeCambiar('entrega', 'equipos')) {
            Tabs.cambiarTab('equipos');
        }
    });

    document.getElementById('next-to-resumen').addEventListener('click', function() {
        if (Tabs.validarAntesDeCambiar('equipos', 'resumen')) {
            Resumen.actualizarResumen();
            Tabs.cambiarTab('resumen');
        }
    });

    document.getElementById('skip-to-resumen').addEventListener('click', function() {
        if (equiposSeleccionados.length > 0) {
            Resumen.actualizarResumen();
            Tabs.cambiarTab('resumen');
        } else {
            alert('Debe agregar al menos un equipo para ver el resumen.');
        }
    });

    // Botones para volver atrás
    document.getElementById('back-to-empleado').addEventListener('click', function() {
        Tabs.cambiarTab('empleado');
    });

    document.getElementById('back-to-entrega').addEventListener('click', function() {
        Tabs.cambiarTab('entrega');
    });

    document.getElementById('back-to-equipos').addEventListener('click', function() {
        Tabs.cambiarTab('equipos');
    });

    // Event listener para el formulario
    document.getElementById('prestamo-form').addEventListener('submit', finalizarPrestamo);

    // Event listener para cerrar modal
    document.getElementById('close-modal').addEventListener('click', function() {
        document.getElementById('confirm-modal').classList.add('hidden');

        // Reiniciar formulario
        document.getElementById('prestamo-form').reset();
        document.getElementById('placa-empleado').value = '';
        document.getElementById('datos-empleado').classList.add('hidden');
        document.getElementById('serie-equipo').value = '';
        document.getElementById('datos-equipo').classList.add('hidden');
        document.getElementById('sim-container').classList.add('hidden');
        document.getElementById('lista-equipos').innerHTML = '';
        equiposSeleccionados = [];
        empleadoActual = null;
        equipoActual = null;
        actualizarContadorEquipos();

        // Generar nuevo número de préstamo
        inicializarFechaYNumero();

        // Volver a la primera pestaña
        Tabs.cambiarTab('empleado');

        // Seleccionar PAT por defecto
        document.getElementById('tipo-pat').checked = true;
        document.querySelector('label[for="tipo-pat"] .radio-dot').classList.remove('hidden');
        document.getElementById('detalle-tipo-prestamo').classList.remove('hidden');
        document.getElementById('detalle-prestamo').value = 'PAT ';
    });

    // Event listeners para las pestañas
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const tabId = this.id.replace('tab-', '');

            // Validar si se puede cambiar a esa pestaña
            let puedeCambiar = true;

            if (tabId === 'entrega' && !empleadoActual) {
                puedeCambiar = false;
                alert('Debe completar la información del empleado primero.');
            }

            if (tabId === 'equipos') {
                const responsable = document.getElementById('responsable-entrega').value;
                const tipoPrestamo = document.querySelector('input[name="tipo-prestamo"]:checked');
                const detalle = document.getElementById('detalle-prestamo').value;

                if (!responsable || !tipoPrestamo || !detalle) {
                    puedeCambiar = false;
                    alert('Debe completar la información de entrega primero.');
                }
            }

            if (tabId === 'resumen' && equiposSeleccionados.length === 0) {
                puedeCambiar = false;
                alert('Debe agregar al menos un equipo para ver el resumen.');
            }

            if (puedeCambiar) {
                if (tabId === 'resumen') {
                    Resumen.actualizarResumen();
                }
                Tabs.cambiarTab(tabId);
            }
        });
    });
});
