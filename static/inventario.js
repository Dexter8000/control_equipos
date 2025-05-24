document.addEventListener("DOMContentLoaded", function() {
    // ======== VARIABLES GLOBALES ========
    let modalActivo = null;

    // ======== SELECTORES DE ELEMENTOS ========
    const modales = document.querySelectorAll('.modal');
    const btnAddEquipo = document.getElementById("btn-add-equipo");
    const btnAddPeriferico = document.getElementById("btn-add-periferico");
    const btnPrint = document.getElementById("btn-print");
    const btnImport = document.getElementById("btn-import");
    const inputImport = document.getElementById("file-import");
    const searchInput = document.getElementById("search-global");

    // ======== INICIALIZACIÓN ========
    modales.forEach(modal => {
        modal.classList.add("hidden");
    });

    // ======== EVENTOS PARA BOTONES PRINCIPALES ========
    if (btnAddEquipo) {
        btnAddEquipo.addEventListener("click", function() {
            mostrarModal("modal-equipo");
        });
    }

    if (btnAddPeriferico) {
        btnAddPeriferico.addEventListener("click", function() {
            mostrarModal("modal-periferico");
        });
    }

    if (btnPrint) {
        btnPrint.addEventListener("click", function() {
            window.print();
        });
    }

    // ======== IMPORTACIÓN DE ARCHIVOS ========
    if (btnImport && inputImport) {
        btnImport.addEventListener("click", function() {
            inputImport.click();
        });

        inputImport.addEventListener("change", function(e) {
            const file = e.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = function(event) {
                try {
                    const data = JSON.parse(event.target.result);
                    if (Array.isArray(data)) {
                        alert("Equipos importados (simulado). No guardado aún.");
                        location.reload();
                    } else {
                        alert("El archivo JSON no es válido.");
                    }
                } catch (error) {
                    alert("Error al leer el archivo JSON: " + error.message);
                }
            };
            reader.readAsText(file);
        });
    }

    // ======== BÚSQUEDA GLOBAL ========
    if (searchInput) {
        searchInput.addEventListener("input", function(e) {
            const value = e.target.value.toLowerCase();
            document.querySelectorAll("tbody tr").forEach(row => {
                row.style.display = row.textContent.toLowerCase().includes(value) ? "" : "none";
            });
        });
    }

    // ======== MANEJO DE FORMULARIOS ========
    const formEquipo = document.getElementById("form-agregar-equipo");
    if (formEquipo) {
        formEquipo.addEventListener("submit", function(e) {
            e.preventDefault();
            handleFormSubmit(e, '/equipos/agregar');
        });
    }

    const formPeriferico = document.getElementById("form-agregar-periferico");
    if (formPeriferico) {
        formPeriferico.addEventListener("submit", function(e) {
            e.preventDefault();
            handleFormSubmit(e, '/equipos/agregar_periferico');
        });
    }

    // ======== CERRAR MODALES ========
    document.querySelectorAll(".btn-cancelar, .modal-close-btn").forEach(btn => {
        btn.addEventListener("click", function() {
            const modal = this.closest('.modal');
            if (modal) {
                ocultarModal(modal.id);
            }
        });
    });

    modales.forEach(modal => {
        modal.addEventListener("click", function(e) {
            if (e.target === this) {
                ocultarModal(this.id);
            }
        });
    });

    // ======== ACCIONES DE TABLA (DELEGACIÓN DE EVENTOS) ========
    document.addEventListener("click", function(e) {
        if (e.target.classList.contains("btn-editar")) {
            const id = e.target.dataset.id || "0";
            alert(`Editando equipo ID: ${id} (simulado)`);
        }

        if (e.target.classList.contains("btn-eliminar")) {
            const id = e.target.dataset.id || "0";
            const confirmacion = confirm(`¿Deseas eliminar el equipo con ID: ${id}?`);
            if (confirmacion) {
                alert(`✅ Equipo con ID ${id} eliminado (simulado)`);
            }
        }
    });

    // ======== FUNCIONES DE MODALES GLOBALES ========
    window.mostrarModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove("hidden");
            modalActivo = modal;
            const tabla = document.querySelector("table");
            if (tabla) {
                tabla.style.display = "";
            }
        }
    };

    window.ocultarModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add("hidden");
            modalActivo = null;
        }
    };
});

// ======== PANEL FLOTANTE ========
function mostrarPanel() {
    document.getElementById("panel-acciones").classList.remove("hidden");
}

function cerrarPanel() {
    document.getElementById("panel-acciones").classList.add("hidden");
}

// ======== EVENTO CLICK PARA MOSTRAR PANEL FLOTANTE ========
document.addEventListener("DOMContentLoaded", () => {
    const panel = document.getElementById("panel-acciones");
    const checkboxes = document.querySelectorAll(".check-selector");

    checkboxes.forEach(chk => {
        chk.addEventListener("change", () => {
            const algunoMarcado = [...checkboxes].some(c => c.checked);
            panel.classList.toggle("hidden", !algunoMarcado);
        });
    });
});

// Funciones para editar, guardar y eliminar filas
function editarFilaSeleccionada() {
    const fila = document.querySelector('input.check-selector:checked')?.closest('tr');
    if (!fila) return alert("Debes seleccionar una fila primero.");

    fila.classList.add('modo-edicion');

    const celdas = fila.querySelectorAll('td');
    for (let i = 1; i < celdas.length; i++) {
        celdas[i].setAttribute('contenteditable', true);
        celdas[i].style.backgroundColor = "#fff8dc";
    }
}

function guardarCambiosFila() {
    const fila = document.querySelector('tr.modo-edicion');
    if (!fila) return alert("Primero debes entrar en modo edición.");

    const celdas = fila.querySelectorAll('td');
    const datos = {
        id: celdas[1].innerText.trim(),
        nombre: celdas[2].innerText.trim(),
        marca: celdas[3].innerText.trim(),
        modelo: celdas[4].innerText.trim(),
        serie: celdas[5].innerText.trim(),
        categoria: celdas[6].innerText.trim(),
        subcategoria: celdas[7].innerText.trim(),
        estado: celdas[8].innerText.trim(),
        condicion: celdas[9].innerText.trim(),
        tipo_adquisicion: celdas[10].innerText.trim(),
        id_departamento_asignado: celdas[11].innerText.trim(),
        ubicacion_especifica: celdas[12].innerText.trim(),
        responsable_actual: celdas[13].innerText.trim(),
        fecha_creacion: celdas[14].innerText.trim(),
        fecha_adquisicion: celdas[15].innerText.trim(),
        Detalles: celdas[16].innerText.trim(),
        periferico: celdas[17].innerText.trim()
    };

    for (let i = 1; i < celdas.length; i++) {
        celdas[i].removeAttribute('contenteditable');
        celdas[i].style.backgroundColor = "";
    }

    fila.classList.remove('modo-edicion');

    fetch("/equipos/actualizar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(datos)
    })
    .then(res => res.json())
    .then(data => {
        alert(data.mensaje || "✅ Cambios guardados correctamente.");
    })
    .catch(err => {
        console.error(err);
        alert("❌ Error al guardar los cambios.");
    });
}

function eliminarFilaSeleccionada() {
    const fila = document.querySelector('input.check-selector:checked')?.closest('tr');
    if (!fila) return alert("Debes seleccionar una fila para eliminar.");

    if (confirm("¿Estás seguro de eliminar este registro?")) {
        fila.remove();
    }
}

function cancelarEdicion() {
    const fila = document.querySelector('tr.modo-edicion');
    if (!fila) return alert("No hay ninguna fila en edición.");

    const celdas = fila.querySelectorAll('td');
    for (let i = 1; i < celdas.length; i++) {
        celdas[i].removeAttribute('contenteditable');
        celdas[i].style.backgroundColor = "";
    }

    fila.classList.remove('modo-edicion');
    alert("🚫 Edición cancelada.");
}

function handleFormSubmit(event, url) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);  // Correcto

    fetch(url, {
        method: 'POST',
        body: formData  // Sin headers, porque FormData lo maneja automáticamente
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('✅ Equipo guardado correctamente');
            form.reset();
            ocultarModal(form.id);
            location.reload();  // Refrescar para mostrar el nuevo equipo
        } else {
            alert('❌ Error: ' + (data.error || 'Error desconocido'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('🚨 Error de conexión con el servidor');
    });
}

