document.addEventListener('DOMContentLoaded', () => {
    // --- GENERAL ---
    const selectorEntrega = document.getElementById('quien-entrega');
    const placaInput = document.getElementById('placa-recibe');
    const rangoField = document.getElementById('rango-recibe');
    const nombreField = document.getElementById('nombre-recibe');
    const apellidoField = document.getElementById('apellido-recibe');
    const departamentoField = document.getElementById('departamento-recibe');
    const buscarBtn = document.getElementById('buscar-placa');

    const tipoSelect = document.getElementById('tipo-prestamo');
    const subtipoSelect = document.getElementById('subtipo-prestamo');
    const agregarTipoBtn = document.getElementById('agregar-tipo');
    const agregarSubtipoBtn = document.getElementById('agregar-subtipo');
    const serieInput = document.getElementById('serie-equipo');
    const agregarEquipoBtn = document.getElementById('agregar-equipo');
    const listaEquipos = document.getElementById('lista-equipos');

    // --- FUNCIONES AUXILIARES ---
    async function fetchData(url) {
        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Fetch error:', error);
            return null; // O manejar el error de otra manera
        }
    }

    function createOption(selectElement, value, text) {
        const option = document.createElement('option');
        option.value = value;
        option.textContent = text;
        selectElement.appendChild(option);
    }

    function createEquipmentItem(equipment, condition) {
        const li = document.createElement('li');
        li.innerHTML = `
            <span>${equipment.serie}</span>
            <span>${equipment.nombre}</span>
            <span>${equipment.marca}</span>
            <span>${equipment.modelo}</span>
            <span>${condition}</span>
        `;
        return li;
    }

    function createChipSelect(serie, chips) {
        const chipSelect = document.createElement('select');
        chipSelect.id = `chip-${serie}`;
        chips.forEach(chip => createOption(chipSelect, chip, chip));
        return chipSelect;
    }

    // --- CARGAR DATOS INICIALES ---
    async function loadInitialData() {
        const usuarios = await fetchData('/prestamos/usuarios');
        if (usuarios) usuarios.forEach(user => createOption(selectorEntrega, user.id, `${user.nombre} ${user.apellido}`)); // Ajuste para nombre completo

        const tipos = await fetchData('/prestamos/tipos_prestamo');
        if (tipos) tipos.forEach(tipo => createOption(tipoSelect, tipo.id, tipo.nombre)); // Ajuste para id/nombre

        // Inicializar subtipos (puede ser vacío al inicio)
        loadSubtipos(tipoSelect.value);
    }

    loadInitialData();

    // --- BUSCAR RECEPTOR ---
    buscarBtn.addEventListener('click', async () => {
        const placa = placaInput.value.trim();
        if (!placa) return;

        const persona = await fetchData(`/prestamos/buscar_persona/${placa}`);
        if (persona) {
            rangoField.textContent = persona.rango;
            nombreField.textContent = `${persona.nombre} ${persona.apellido}`;
            departamentoField.textContent = persona.nombre_departamento; // Ajuste
        } else {
            alert('Persona no encontrada');
            clearReceptorFields();
        }
    });

    function clearReceptorFields() {
        rangoField.textContent = '';
        nombreField.textContent = '';
        apellidoField.textContent = '';
        departamentoField.textContent = '';
    }

    // --- CARGAR SUBTIPOS ---
    async function loadSubtipos(tipoId) {
        subtipoSelect.innerHTML = ''; // Limpiar select
        if (!tipoId) return;

        const subtipos = await fetchData(`/prestamos/subtipos_prestamo/${tipoId}`);
        if (subtipos) subtipos.forEach(subtipo => createOption(subtipoSelect, subtipo.id, subtipo.nombre)); // Ajuste para id/nombre
    }

    tipoSelect.addEventListener('change', () => loadSubtipos(tipoSelect.value));

    // --- AGREGAR TIPO/SUBTIPO ---
    agregarTipoBtn.addEventListener('click', async () => {
        const nuevoTipo = prompt('Ingrese el nuevo tipo de préstamo:');
        if (!nuevoTipo) return;

        const result = await fetch('/prestamos/agregar_tipo_prestamo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nombre: nuevoTipo }) // Ajuste para el campo "nombre"
        });

        if (result.ok) {
            const tipos = await fetchData('/prestamos/tipos_prestamo'); // Recargar tipos
            tipoSelect.innerHTML = '';
            if (tipos) tipos.forEach(tipo => createOption(tipoSelect, tipo.id, tipo.nombre));
            loadSubtipos(tipoSelect.value); // Recargar subtipos
        } else {
            alert('Error al agregar tipo');
        }
    });

    agregarSubtipoBtn.addEventListener('click', async () => {
        const tipoId = tipoSelect.value;
        if (!tipoId) {
            alert('Seleccione un tipo de préstamo primero');
            return;
        }

        const nuevoSubtipo = prompt(`Ingrese el nuevo subtipo para ${tipoSelect.options[tipoSelect.selectedIndex].textContent}:`);
        if (!nuevoSubtipo) return;

        const result = await fetch('/prestamos/agregar_subtipo_prestamo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tipo_prestamo_id: tipoId, nombre: nuevoSubtipo }) // Ajuste para los campos
        });

        if (result.ok) {
            const subtipos = await fetchData(`/prestamos/subtipos_prestamo/${tipoId}`); // Recargar subtipos
            subtipoSelect.innerHTML = '';
            if (subtipos) subtipos.forEach(subtipo => createOption(subtipoSelect, subtipo.id, subtipo.nombre));
        } else {
            alert('Error al agregar subtipo');
        }
    });

    // --- AGREGAR EQUIPO ---
    agregarEquipoBtn.addEventListener('click', async () => {
        const serie = serieInput.value.trim();
        if (!serie) return;

        const equipo = await fetchData(`/prestamos/buscar_equipo/${serie}`);
        if (equipo) {
            const conditionSelect = `
                <select class="condition-select">
                    <option value="nuevo">Nuevo</option>
                    <option value="bueno">Bueno</option>
                    <option value="semi-bueno">Semi Bueno</option>
                </select>
            `;

            const li = createEquipmentItem(equipo, conditionSelect);
            listaEquipos.appendChild(li);

            if (equipo.categoria === 'Comunicación Satelital') { // Ajuste para la categoria
                const chipInputGroup = document.createElement('div');
                chipInputGroup.classList.add('chip-input-group');

                const chips = await fetchData('/prestamos/chips');
                if (chips) {
                    const chipSelect = createChipSelect(serie, chips);
                    chipInputGroup.appendChild(document.createTextNode('Chip: '));
                    chipInputGroup.appendChild(chipSelect);

                    const addChipButton = document.createElement('button');
                    addChipButton.textContent = '+ Chip';
                    addChipButton.classList.add('add-chip-btn');
                    addChipButton.type = 'button';
                    addChipButton.onclick = () => agregarChip(serie);
                    chipInputGroup.appendChild(addChipButton);

                    li.appendChild(chipInputGroup);
                }
            }
            serieInput.value = ''; // Limpiar el campo
        } else {
            alert('Equipo no encontrado');
        }
    });

    // --- AGREGAR CHIP ---
    async function agregarChip(serie) {
        const nuevoChip = prompt('Ingrese el número de chip:');
        if (!nuevoChip) return;

        const result = await fetch('/prestamos/agregar_chip', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ serie: nuevoChip }) // Ajuste para el campo "serie"
        });

        if (result.ok) {
            const chips = await fetchData('/prestamos/chips'); // Recargar chips
            const chipSelect = document.getElementById(`chip-${serie}`);
            if (chipSelect) {
                chipSelect.innerHTML = '';
                if (chips) chips.forEach(chip => createOption(chipSelect, chip, chip));
                chipSelect.value = nuevoChip; // Seleccionar el nuevo chip
            }
        } else {
            alert('Error al agregar chip');
        }
    }

    // --- FUNCIONALIDAD ADICIONAL (EDITAR TIPOS/SUBTIPOS) ---
    const editArea = document.getElementById('edit-area');
    const editList = document.querySelector('#edit-area .edit-list');

    function displayEditOptions() {
        editList.innerHTML = ''; // Limpiar la lista

        // Mostrar tipos
        const tipos = JSON.parse(localStorage.getItem('tipos')) || []; // Usar localStorage como ejemplo
        tipos.forEach(tipo => {
            const li = document.createElement('li');
            li.innerHTML = `
                <span>Tipo: ${tipo}</span>
                <button class="delete-btn" data-type="tipo" data-value="${tipo}">Eliminar</button>
            `;
            editList.appendChild(li);
        });

        // Mostrar subtipos (agrupados por tipo)
        const subtipos = JSON.parse(localStorage.getItem('subtipos')) || {}; // Usar localStorage como ejemplo
        Object.keys(subtipos).forEach(tipo => {
            const tipoHeader = document.createElement('li');
            tipoHeader.innerHTML = `<strong>${tipo}</strong>`;
            editList.appendChild(tipoHeader);

            subtipos[tipo].forEach(subtipo => {
                const li = document.createElement('li');
                li.innerHTML = `
                    <span>&nbsp;&nbsp;&nbsp;&nbsp;Subtipo: ${subtipo}</span>
                    <button class="delete-btn" data-type="subtipo" data-tipo-padre="${tipo}" data-value="${subtipo}">Eliminar</button>
                `;
                editList.appendChild(li);
            });
        });

        // Configurar los event listeners para los botones de eliminar
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', handleDelete);
        });
    }

    function handleDelete() {
        const type = this.dataset.type;
        const value = this.dataset.value;
        const tipoPadre = this.dataset.tipoPadre; // Solo para subtipos

        if (confirm(`¿Seguro que desea eliminar ${type}: ${value}?`)) {
            // Aquí iría la lógica para eliminar (ejemplo: localStorage)
            if (type === 'tipo') {
                let tipos = JSON.parse(localStorage.getItem('tipos')) || [];
                tipos = tipos.filter(t => t !== value);
                localStorage.setItem('tipos', JSON.stringify(tipos));
            } else if (type === 'subtipo') {
                let subtipos = JSON.parse(localStorage.getItem('subtipos')) || {};
                if (subtipos[tipoPadre]) {
                    subtipos[tipoPadre] = subtipos[tipoPadre].filter(s => s !== value);
                    localStorage.setItem('subtipos', JSON.stringify(subtipos));
                }
            }
            displayEditOptions(); // Actualizar la lista después de eliminar
        }
    }

    // Inicializar la funcionalidad de edición
    displayEditOptions();
});