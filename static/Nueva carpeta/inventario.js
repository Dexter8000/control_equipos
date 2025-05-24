class InventarioAvanzado {
    constructor() {
        this.peripheralCount = 0;
        this.init();
    }

    init() {
        this.initListeners();
        this.validarFechas();
        this.initBuscador();
        this.initOrdenamientoTabla();
        this.cargarInventarioInicial(); // Importante: carga al inicio
    }

    initListeners() {
        document.getElementById('add-peripheral-btn')?.addEventListener('click', () => this.agregarPeriferico());

        document.getElementById('add-equipment-form')?.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    cargarInventarioInicial() {
        if (!window.INVENTARIO_DATA || !Array.isArray(window.INVENTARIO_DATA)) return;

        window.INVENTARIO_DATA.forEach(equipo => {
            equipo.peripherals = equipo.peripherals || [];
            this.agregarFilaATabla(equipo);
        });
    }

    agregarPeriferico() {
        this.peripheralCount++;
        const wrapper = document.createElement('div');
        wrapper.classList.add('peripheral-entry');
        wrapper.innerHTML = `
            <h4>Periférico ${this.peripheralCount}</h4>
            <input type="text" name="peripherals[${this.peripheralCount}][id]" placeholder="ID" required>
            <input type="text" name="peripherals[${this.peripheralCount}][nombre]" placeholder="Nombre" required>
            <input type="text" name="peripherals[${this.peripheralCount}][marca]" placeholder="Marca" required>
            <input type="text" name="peripherals[${this.peripheralCount}][modelo]" placeholder="Modelo" required>
            <input type="text" name="peripherals[${this.peripheralCount}][serie]" placeholder="Serie" required>
            <textarea name="peripherals[${this.peripheralCount}][notas]" placeholder="Notas"></textarea>
        `;
        document.getElementById('peripherals-list')?.appendChild(wrapper);
    }

    handleSubmit(e) {
        e.preventDefault();
        const form = e.target;
        const data = new FormData(form);
        const equipo = {};
        const perifericos = [];

        for (let [key, value] of data.entries()) {
            if (key.startsWith('peripherals')) {
                const match = key.match(/peripherals\[(\d+)\]\[(\w+)\]/);
                if (match) {
                    const index = match[1];
                    const campo = match[2];
                    if (!perifericos[index]) perifericos[index] = {};
                    perifericos[index][campo] = value;
                }
            } else {
                equipo[key] = value;
            }
        }

        equipo.peripherals = perifericos.filter(p => p && p.id);
        this.agregarFilaATabla(equipo);

        form.reset();
        document.getElementById('peripherals-list').innerHTML = '';
        this.peripheralCount = 0;
    }

    agregarFilaATabla(equipo) {
        const tbody = document.querySelector('#inventory-table tbody');
        const row = document.createElement('tr');
        row.innerHTML = `
            <td class="fixed">${equipo.id}</td>
            <td class="fixed">${equipo.nombre}</td>
            <td>${equipo.marca}</td>
            <td>${equipo.modelo}</td>
            <td>${equipo.serie}</td>
            <td>${equipo.categoria}</td>
            <td>${equipo.subcategoria}</td>
            <td>${equipo.fecha_adquisicion}</td>
            <td>${equipo.garantia_hasta}</td>
            <td>${equipo.ubicacion}</td>
            <td>${equipo.ubicacion_especifica}</td>
            <td>${equipo.estado}</td>
            <td>${equipo.condicion}</td>
            <td>${equipo.responsable_actual}</td>
            <td>${equipo.tipo_adquisicion}</td>
            <td>${equipo.mantenimiento_programado}</td>
            <td>${equipo.id_departamento_asignado}</td>
            <td>${equipo.historial_mantenimientos || '[]'}</td>
            <td>${equipo.prestamo_actual_id || 'null'}</td>
            <td>${equipo.notas || ''}</td>
            <td>${equipo.fecha_creacion}</td>
            <td>${equipo.fecha_ultima_actualizacion}</td>
            <td>
                <button class="toggle-peripherals" data-target="peripherals-${equipo.id}">Mostrar Periféricos (${equipo.peripherals.length})</button>
                <div id="peripherals-${equipo.id}" class="collapsible-section">
                    <table class="peripherals-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Nombre</th>
                                <th>Marca</th>
                                <th>Modelo</th>
                                <th>Serie</th>
                                <th>Notas</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${equipo.peripherals.length > 0 ? equipo.peripherals.map(p => `
                                <tr class="periferico">
                                    <td>${p.id}</td>
                                    <td>${p.nombre}</td>
                                    <td>${p.marca}</td>
                                    <td>${p.modelo}</td>
                                    <td>${p.serie}</td>
                                    <td>${p.notas || ''}</td>
                                </tr>
                            `).join('') : '<tr><td colspan="6">No hay periféricos asociados.</td></tr>'}
                        </tbody>
                    </table>
                </div>
            </td>
        `;
        tbody.appendChild(row);

        row.querySelector('.toggle-peripherals').addEventListener('click', () => {
            const target = document.getElementById(`peripherals-${equipo.id}`);
            target.classList.toggle('active');
            const btn = row.querySelector('.toggle-peripherals');
            btn.textContent = target.classList.contains('active') 
                ? btn.textContent.replace('Mostrar', 'Ocultar') 
                : btn.textContent.replace('Ocultar', 'Mostrar');
        });
    }

    validarFechas() {
        const hoy = new Date().toISOString().split('T')[0];
        document.querySelectorAll('input[type="date"]').forEach(input => {
            input.min = hoy;
        });
    }

    initBuscador() {
        const input = document.querySelector('.search-input');
        input?.addEventListener('input', e => {
            const filtro = e.target.value.toLowerCase();
            document.querySelectorAll('#inventory-table tbody tr').forEach(row => {
                row.style.display = row.textContent.toLowerCase().includes(filtro) ? '' : 'none';
            });
        });
    }

    initOrdenamientoTabla() {
        document.querySelectorAll('#inventory-table th').forEach(header => {
            header.addEventListener('click', () => {
                const index = header.cellIndex;
                const tbody = document.querySelector('#inventory-table tbody');
                const filas = Array.from(tbody.rows);
                const asc = !header.classList.contains('asc');
                filas.sort((a, b) => {
                    const valA = a.cells[index].textContent.trim();
                    const valB = b.cells[index].textContent.trim();
                    return asc ? valA.localeCompare(valB) : valB.localeCompare(valA);
                });
                header.classList.toggle('asc', asc);
                header.classList.toggle('desc', !asc);
                filas.forEach(f => tbody.appendChild(f));
            });
        });
    }
}

document.addEventListener('DOMContentLoaded', () => new InventarioAvanzado());

