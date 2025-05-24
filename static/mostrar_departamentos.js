// static/mostrar_departamentos.js

document.addEventListener('DOMContentLoaded', function() {
    // Obtenemos referencias a los elementos HTML por sus IDs
    const mostrarDepartamentosBtn = document.getElementById('mostrarDepartamentosBtn'); // El botón
    // Cambiamos la referencia para apuntar al nuevo div contenedor
    const departamentosTableContainer = document.getElementById('departamentosTableContainer'); // El div donde irá la tabla
    const modalDepartamentos = document.getElementById('modal-departamentos'); // El div del modal

    // Verificamos que los elementos existen
    if (mostrarDepartamentosBtn && departamentosTableContainer && modalDepartamentos) {

        // Añadimos un evento click al botón
        mostrarDepartamentosBtn.addEventListener('click', function() {
            // Realizamos la petición GET al endpoint del backend
            fetch('/data/departamentos')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Error en la red o en el servidor: ' + response.statusText);
                    }
                    return response.json();
                })
                .then(data => {
                    // Limpiamos cualquier contenido previo en el contenedor
                    departamentosTableContainer.innerHTML = '';

                    if (data && Array.isArray(data) && data.length > 0) {
                        // Si hay datos, creamos la tabla
                        const table = document.createElement('table');
                        // Puedes añadir una clase CSS para estilizar la tabla
                        table.classList.add('departamentos-table');

                        // Creamos el encabezado de la tabla
                        const thead = document.createElement('thead');
                        const headerRow = document.createElement('tr');
                        const thId = document.createElement('th');
                        thId.textContent = 'ID'; // Texto de la columna ID
                        const thNombre = document.createElement('th');
                        thNombre.textContent = 'Nombre del Departamento'; // Texto de la columna Nombre
                        headerRow.appendChild(thId);
                        headerRow.appendChild(thNombre);
                        thead.appendChild(headerRow);
                        table.appendChild(thead);

                        // Creamos el cuerpo de la tabla e insertamos las filas de datos
                        const tbody = document.createElement('tbody');
                        data.forEach(departamento => {
                            const row = document.createElement('tr');
                            const tdId = document.createElement('td');
                            tdId.textContent = departamento.id; // Celda para el ID
                            const tdNombre = document.createElement('td');
                            tdNombre.textContent = departamento.nombre; // Celda para el Nombre
                            row.appendChild(tdId);
                            row.appendChild(tdNombre);
                            tbody.appendChild(row);
                        });
                        table.appendChild(tbody);

                        // Añadimos la tabla completa al div contenedor
                        departamentosTableContainer.appendChild(table);
                    } else {
                        // Si no hay datos o los datos no son un array válido
                        departamentosTableContainer.textContent = 'No se encontraron datos de departamentos o el formato es incorrecto.';
                    }

                    // Mostramos el modal
                    modalDepartamentos.style.display = 'block';

                })
                .catch(error => {
                    console.error('Hubo un problema con la operación fetch:', error);
                    // Mostramos un mensaje de error en el contenedor
                    departamentosTableContainer.innerHTML = '<p style="color: red;">Error al cargar los departamentos.</p>'; // Usamos innerHTML para permitir HTML simple
                    modalDepartamentos.style.display = 'block'; // Aseguramos que el modal se muestre
                });
        });

    } else {
        console.error('Alguno de los elementos HTML necesarios para mostrar los departamentos no fue encontrado.');
    }
});