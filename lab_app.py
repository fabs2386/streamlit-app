import streamlit as st
from dataclasses import dataclass
from typing import List

# --- Data models ---
@dataclass
class Patient:
    id: int
    name: str
    document: str

@dataclass
class Doctor:
    id: int
    name: str

@dataclass
class Institution:
    id: int
    name: str

@dataclass
class Test:
    id: int
    name: str
    price: float

@dataclass
class Order:
    id: int
    patient_id: int
    doctor_id: int
    test_id: int
    status: str = "pendiente"

@dataclass
class Result:
    order_id: int
    value: str

# --- Initialize session storage ---
def get_state_list(key: str) -> List:
    if key not in st.session_state:
        st.session_state[key] = []
    return st.session_state[key]

# Utility functions

def next_id(items: List) -> int:
    return (items[-1].id + 1) if items else 1

# --- UI functions ---

def pacientes_page():
    st.header("Pacientes")
    pacientes = get_state_list("pacientes")
    with st.form("nuevo_paciente"):
        nombre = st.text_input("Nombre")
        documento = st.text_input("Documento")
        submitted = st.form_submit_button("Agregar")
        if submitted and nombre and documento:
            pacientes.append(Patient(next_id(pacientes), nombre, documento))
            st.success("Paciente agregado")
    if pacientes:
        st.subheader("Listado")
        st.table([p.__dict__ for p in pacientes])


def doctores_page():
    st.header("Doctores")
    doctores = get_state_list("doctores")
    with st.form("nuevo_doctor"):
        nombre = st.text_input("Nombre")
        submitted = st.form_submit_button("Agregar")
        if submitted and nombre:
            doctores.append(Doctor(next_id(doctores), nombre))
            st.success("Doctor agregado")
    if doctores:
        st.subheader("Listado")
        st.table([d.__dict__ for d in doctores])


def instituciones_page():
    st.header("Instituciones/Seguros")
    instituciones = get_state_list("instituciones")
    with st.form("nueva_institucion"):
        nombre = st.text_input("Nombre")
        submitted = st.form_submit_button("Agregar")
        if submitted and nombre:
            instituciones.append(Institution(next_id(instituciones), nombre))
            st.success("Institución agregada")
    if instituciones:
        st.subheader("Listado")
        st.table([i.__dict__ for i in instituciones])


def pruebas_page():
    st.header("Pruebas")
    pruebas = get_state_list("pruebas")
    with st.form("nueva_prueba"):
        nombre = st.text_input("Nombre")
        precio = st.number_input("Precio", min_value=0.0, step=0.1)
        submitted = st.form_submit_button("Agregar")
        if submitted and nombre:
            pruebas.append(Test(next_id(pruebas), nombre, precio))
            st.success("Prueba agregada")
    if pruebas:
        st.subheader("Listado")
        st.table([p.__dict__ for p in pruebas])


def ordenes_page():
    st.header("Órdenes")
    pacientes = get_state_list("pacientes")
    doctores = get_state_list("doctores")
    pruebas = get_state_list("pruebas")
    ordenes = get_state_list("ordenes")
    if not pacientes or not doctores or not pruebas:
        st.info("Debe registrar pacientes, doctores y pruebas antes de crear órdenes")
        return
    with st.form("nueva_orden"):
        paciente = st.selectbox("Paciente", pacientes, format_func=lambda p: p.name)
        doctor = st.selectbox("Doctor", doctores, format_func=lambda d: d.name)
        prueba = st.selectbox("Prueba", pruebas, format_func=lambda t: t.name)
        submitted = st.form_submit_button("Crear")
        if submitted:
            ordenes.append(Order(next_id(ordenes), paciente.id, doctor.id, prueba.id))
            st.success("Orden creada")
    if ordenes:
        st.subheader("Listado")
        st.table([o.__dict__ for o in ordenes])


def resultados_page():
    st.header("Resultados")
    ordenes = get_state_list("ordenes")
    resultados = get_state_list("resultados")
    if not ordenes:
        st.info("No hay órdenes registradas")
        return
    with st.form("nuevo_resultado"):
        orden = st.selectbox("Orden", ordenes, format_func=lambda o: f"Orden {o.id}")
        valor = st.text_input("Resultado")
        submitted = st.form_submit_button("Guardar")
        if submitted and valor:
            resultados.append(Result(orden.id, valor))
            orden.status = "finalizada"
            st.success("Resultado guardado")
    if resultados:
        st.subheader("Listado")
        st.table([r.__dict__ for r in resultados])


def finanzas_page():
    st.header("Finanzas")
    ordenes = {o.id: o for o in get_state_list("ordenes")}
    pruebas = {p.id: p for p in get_state_list("pruebas")}
    resultados = get_state_list("resultados")
    total = 0.0
    for res in resultados:
        orden = ordenes.get(res.order_id)
        if orden:
            prueba = pruebas.get(orden.test_id)
            if prueba:
                total += prueba.price
    st.metric("Total facturado", f"${total:.2f}")


def estadisticas_page():
    st.header("Estadísticas")
    st.write("- Pacientes registrados:", len(get_state_list("pacientes")))
    st.write("- Órdenes generadas:", len(get_state_list("ordenes")))
    st.write("- Resultados registrados:", len(get_state_list("resultados")))


def reportes_page():
    st.header("Reportes")
    pacientes = {p.id: p for p in get_state_list("pacientes")}
    doctores = {d.id: d for d in get_state_list("doctores")}
    pruebas = {t.id: t for t in get_state_list("pruebas")}
    ordenes = get_state_list("ordenes")
    resultados = {r.order_id: r for r in get_state_list("resultados")}
    if not ordenes:
        st.info("No hay órdenes")
        return
    data = []
    for o in ordenes:
        data.append({
            "Orden": o.id,
            "Paciente": pacientes[o.patient_id].name,
            "Doctor": doctores[o.doctor_id].name,
            "Prueba": pruebas[o.test_id].name,
            "Estado": o.status,
            "Resultado": resultados.get(o.id).value if o.id in resultados else ""
        })
    st.table(data)

# --- Main ---
PAGES = {
    "Pacientes": pacientes_page,
    "Doctores": doctores_page,
    "Instituciones": instituciones_page,
    "Pruebas": pruebas_page,
    "Órdenes": ordenes_page,
    "Resultados": resultados_page,
    "Finanzas": finanzas_page,
    "Estadísticas": estadisticas_page,
    "Reportes": reportes_page,
}

st.sidebar.title("Menú")
selection = st.sidebar.radio("Ir a", list(PAGES.keys()))
PAGES[selection]()

