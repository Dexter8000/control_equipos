function setupSelects(subcategorias) {
    function filtrarSubcategorias(selectCategoriaId, selectSubcategoriaId) {
        const categoriaId = document.getElementById(selectCategoriaId).value;
        const subcatSelect = document.getElementById(selectSubcategoriaId);
        subcatSelect.innerHTML = '<option value="">Seleccionar Subcategoría</option>';

        subcategorias
            .filter(sub => sub.id_categoria === categoriaId)
            .forEach(sub => {
                const option = document.createElement('option');
                option.value = sub.id;
                option.textContent = sub.nombre;
                subcatSelect.appendChild(option);
            });
    }

    document.getElementById("categoria-equipo")?.addEventListener("change", () =>
        filtrarSubcategorias("categoria-equipo", "subcategoria-equipo")
    );
    document.getElementById("categoria-periferico")?.addEventListener("change", () =>
        filtrarSubcategorias("categoria-periferico", "subcategoria-periferico")
    );
}


