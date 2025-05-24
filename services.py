from config import trabajadores, departamentos, inventario, usuarios, prestamos, devoluciones

equipos_seleccionados = []
empleado_actual = None
equipo_actual = None

def buscar_empleado(placa: str):
    global empleado_actual
    empleado = next((t for t in trabajadores if t["placa"] == placa), None)
    if empleado:
        empleado_actual = empleado
        departamento = next((d for d in departamentos if d["id"] == empleado["departamento_id"]), None)
        return {
            "rango": empleado["rango"],
            "nombre": f"{empleado['nombre']} {empleado['apellido']}",
            "id": empleado["id"],
            "departamento": departamento["nombre"] if departamento else "No asignado"
        }
    return {"error": "No se encontró ningún empleado con esa placa."}

def buscar_equipo(serie: str):
    global equipo_actual
    equipo = next((e for e in inventario if e["serie"] == serie), None)
    if equipo:
        equipo_actual = equipo
        return {
            "nombre": equipo["nombre"],
            "marca": equipo["marca"],
            "modelo": equipo["modelo"],
            "categoria": equipo["categoria"],
            "estado": equipo["estado"]
        }
    return {"error": "No se encontró ningún equipo con esa serie."}

def agregar_equipo(serie: str):
    global equipos_seleccionados, equipo_actual
    if not equipo_actual:
        return {"error": "No se ha buscado ningún equipo."}

    if any(e["id"] == equipo_actual["id"] for e in equipos_seleccionados):
        return {"error": "Este equipo ya está en la lista de préstamos."}

    equipos_seleccionados.append(equipo_actual)
    return {"message": "Equipo agregado correctamente."}

def eliminar_equipo(id: str):
    global equipos_seleccionados
    equipos_seleccionados = [e for e in equipos_seleccionados if e["id"] != id]
    return {"message": "Equipo eliminado correctamente."}

def finalizar_prestamo():
    global empleado_actual, equipos_seleccionados
    if not empleado_actual:
        return {"error": "Debe seleccionar un empleado válido."}

    if not equipos_seleccionados:
        return {"error": "Debe agregar al menos un equipo al préstamo."}

    # Aquí se procesaría el envío del formulario a un backend
    return {"message": "Préstamo finalizado correctamente."}
