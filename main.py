import logging
from abc import ABC, abstractmethod
from datetime import datetime

# =================================================================
# CONFIGURACIÓN DE LOGS (Requerimiento de la Fase 4)
# Se encarga de registrar errores en un archivo externo para 
# garantizar la estabilidad y trazabilidad del sistema.
# =================================================================
logging.basicConfig(
    filename='sistema.log',          # Cambiamos el nombre del archivo
    level=logging.INFO,              # Cambiamos de ERROR a INFO
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'      # Añadimos el formato de fecha
)


def formato_cop(valor):
    """Formatea un número como pesos colombianos (COP) con separador de miles."""
    return f"${valor:,.0f} COP"

# =================================================================
# EXCEPCIONES PERSONALIZADAS
# Implementación de jerarquía de errores para un manejo 
# robusto y específico según la lógica del negocio.
# =================================================================
class SoftwareFJError(Exception):
    """Clase base para todas las excepciones del sistema FJ."""
    pass

class DatosInvalidosError(SoftwareFJError):
    """Se lanza cuando los datos de entrada (nombres, correos) son erróneos."""
    pass

class ReservaInvalidaError(SoftwareFJError):
    """Se lanza ante fallos específicos en el proceso de reserva."""
    pass

class ServicioNoDisponibleError(SoftwareFJError):
    """Se lanza cuando un servicio tiene parámetros inválidos o no está disponible."""
    pass

# =================================================================
# CLASES BASE Y ABSTRACCIÓN (Pilar POO: Abstracción)
# Uso de clases abstractas para definir contratos obligatorios.
# =================================================================
class Entidad(ABC):
    """Representa una entidad general. Define el contrato base."""
    def __init__(self, id_entidad):
        # Corrección: Uso de __init__ (doble guion bajo) para el constructor
        self.id_entidad = id_entidad

    @abstractmethod
    def mostrar_detalle(self):
        """Método obligatorio que deben implementar las subclases."""
        pass

class Cliente(Entidad):
    _contador_id = 1  # Atributo de clase para generar IDs automáticos
    
    def __init__(self, nombre, email):
        # Ya no recibimos id_cliente, lo generamos automáticamente
        self._id = Cliente._contador_id
        Cliente._contador_id += 1
        # Llamamos al constructor de Entidad con el ID generado
        super().__init__(self._id)
        self.nombre = nombre
        self.email = email
        logging.info(f"Cliente creado: {self.mostrar_detalle()}")
    
    @property
    def nombre(self):
        return self._nombre
    
    @nombre.setter
    def nombre(self, valor):
        if not valor or not valor.strip():
            raise DatosInvalidosError("El nombre no puede estar vacío.")
        self._nombre = valor.strip()
    
    @property
    def email(self):
        return self._email
    
    @email.setter
    def email(self, valor):
        if not valor or "@" not in valor or "." not in valor:
            raise DatosInvalidosError(f"Email inválido: {valor}. Debe contener '@' y un punto.")
        self._email = valor.strip()
    
    def mostrar_detalle(self):
        """Implementación del método abstracto de Entidad."""
        return f"Cliente: {self.nombre} (ID: {self.id_entidad})"

# =================================================================
# SERVICIOS Y POLIMORFISMO (Pilares POO: Herencia y Polimorfismo)
# Implementación de métodos sobrescritos para cálculos específicos.
# =================================================================
class Servicio(ABC):
    _contador_codigo = 1000  # Atributo de clase para códigos únicos
    
    def __init__(self, nombre, precio_base):
        self._codigo = Servicio._contador_codigo
        Servicio._contador_codigo += 1
        self.nombre = nombre
        self.precio_base = precio_base
        logging.info(f"Servicio creado: {self.mostrar_resumen()}")
    
    @property
    def nombre(self):
        return self._nombre
    
    @nombre.setter
    def nombre(self, valor):
        if not valor or not valor.strip():
            raise ServicioNoDisponibleError("El nombre del servicio no puede estar vacío.")
        self._nombre = valor.strip()
    
    @property
    def precio_base(self):
        return self._precio_base
    
    @precio_base.setter
    def precio_base(self, valor):
        if not isinstance(valor, (int, float)) or valor < 0:
            raise ServicioNoDisponibleError(f"El precio base debe ser un número positivo. Dado: {valor}")
        self._precio_base = float(valor)
    
    @abstractmethod
    def calcular_costo(self, duracion, **kwargs):
        """Calcula el costo con duración y parámetros opcionales (descuento, impuesto)"""
        pass
    
    @abstractmethod
    def descripcion(self):
        """Retorna una breve descripción del servicio"""
        pass
    
    def mostrar_resumen(self):
        """Muestra información básica del servicio"""
        return f"Código: {self._codigo} | {self.nombre} | {formato_cop(self.precio_base)}"

class ReservaSala(Servicio):
    def __init__(self, nombre, precio_base, capacidad):
        super().__init__(nombre, precio_base)
        self.capacidad = capacidad
    
    def calcular_costo(self, duracion, **kwargs):
        if duracion <= 0:
            raise ReservaInvalidaError("La duración debe ser positiva.")
        costo_base = self.precio_base * duracion
        descuento = kwargs.get('descuento', 0.0)
        impuesto = kwargs.get('impuesto', 0.0)
        if not (0 <= descuento <= 1) or not (0 <= impuesto <= 1):
            raise DatosInvalidosError("Descuento o impuesto fuera de rango [0,1]")
        return round(costo_base * (1 - descuento) * (1 + impuesto), 2)
    
    def descripcion(self):
        return f"Sala con capacidad para {self.capacidad} personas. {formato_cop(self.precio_base)}/hora"

class AlquilerEquipo(Servicio):
    def __init__(self, nombre, precio_base, tipo_equipo):
        super().__init__(nombre, precio_base)
        self.tipo_equipo = tipo_equipo
    
    def calcular_costo(self, duracion, **kwargs):
        if duracion <= 0:
            raise ReservaInvalidaError("La duración debe ser positiva.")
        costo_base = self.precio_base * duracion
        descuento = kwargs.get('descuento', 0.0)
        impuesto = kwargs.get('impuesto', 0.0)
        if not (0 <= descuento <= 1) or not (0 <= impuesto <= 1):
            raise DatosInvalidosError("Descuento o impuesto inválido.")
        return round(costo_base * (1 - descuento) * (1 + impuesto), 2)
    
    def descripcion(self):
        return f"Equipo: {self.tipo_equipo}. {formato_cop(self.precio_base)}/día"

class AsesoriaEspecializada(Servicio):
    def __init__(self, nombre, precio_base, especialidad):
        super().__init__(nombre, precio_base)
        self.especialidad = especialidad
    
    def calcular_costo(self, duracion, **kwargs):
        if duracion <= 0:
            raise ReservaInvalidaError("La duración debe ser positiva.")
        costo_base = self.precio_base * duracion
        descuento = kwargs.get('descuento', 0.0)
        impuesto = kwargs.get('impuesto', 0.0)
        if not (0 <= descuento <= 1) or not (0 <= impuesto <= 1):
            raise DatosInvalidosError("Descuento o impuesto inválido.")
        return round(costo_base * (1 - descuento) * (1 + impuesto), 2)
    
    def descripcion(self):
        return f"Asesoría en {self.especialidad}. {formato_cop(self.precio_base)}/hora"

# =================================================================
# GESTIÓN DE RESERVAS (VERSIÓN ACTUALIZADA CON CONFIRMAR, CANCELAR, PROCESAR)
# =================================================================
class Reserva:
    _contador_reserva = 1
    
    def __init__(self, cliente, servicio, duracion):
        self._id = Reserva._contador_reserva
        Reserva._contador_reserva += 1
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "PENDIENTE"
        
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("Cliente inválido.")
        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("Servicio inválido.")
        if duracion <= 0:
            raise ReservaInvalidaError("Duración positiva requerida.")
        logging.info(f"Reserva creada (ID: {self._id})")
    
    def confirmar(self):
        if self.estado == "CANCELADA":
            raise ReservaInvalidaError("No se puede confirmar una reserva cancelada.")
        self.estado = "CONFIRMADA"
        logging.info(f"Reserva {self._id} confirmada.")
    
    def cancelar(self):
        if self.estado == "CANCELADA":
            raise ReservaInvalidaError("La reserva ya está cancelada.")
        self.estado = "CANCELADA"
        logging.info(f"Reserva {self._id} cancelada.")
    
    def procesar(self, **kwargs):
        try:
            costo = self.servicio.calcular_costo(self.duracion, **kwargs)
            logging.info(f"Reserva {self._id} procesada. Costo: {formato_cop(costo)}")
            return costo
        except Exception as e:
            raise ReservaInvalidaError(f"Error al procesar reserva {self._id}: {e}") from e
    
    def mostrar_resumen(self):
        return f"Reserva #{self._id} | Cliente: {self.cliente.nombre} | Servicio: {self.servicio.nombre} | Estado: {self.estado}"

# =================================================================
# SIMULACIÓN DE 10 OPERACIONES (VÁLIDAS E INVÁLIDAS)
# =================================================================
def iniciar_simulacion():
    print("\n=== SOFTWARE FJ - SISTEMA DE GESTIÓN (Pesos Colombianos) ===\n")
    
    clientes = []
    servicios = []
    reservas = []
    
    # 1. Cliente válido
    try:
        c1 = Cliente("Yeyson Martínez", "yeyson@correo.com")
        clientes.append(c1)
        print("✅ Cliente válido creado.")
    except DatosInvalidosError as e:
        logging.error(f"Error cliente: {e}")
        print(f"❌ {e}")
    
    # 2. Cliente con email inválido (falla)
    try:
        c2 = Cliente("Ana Luz", "ana@correo")
        clientes.append(c2)
        print("✅ Cliente válido creado.")
    except DatosInvalidosError as e:
        logging.error(f"Error cliente: {e}")
        print(f"❌ Error esperado (email inválido): {e}")
    
    # 3. Servicio Sala válido
    try:
        s1 = ReservaSala("Sala Ejecutiva", 100000, 10)
        servicios.append(s1)
        print("✅ Servicio Sala creado.")
    except ServicioNoDisponibleError as e:
        logging.error(e)
        print(f"❌ {e}")
    
    # 4. Servicio Alquiler con precio negativo (falla)
    try:
        s2 = AlquilerEquipo("Laptop", -50000, "Dell")
        servicios.append(s2)
        print("✅ Servicio Alquiler creado.")
    except ServicioNoDisponibleError as e:
        logging.error(e)
        print(f"❌ Error esperado (precio negativo): {e}")
    
    # 5. Servicio Alquiler válido
    try:
        s3 = AlquilerEquipo("Laptop Dell", 70000, "Portátil")
        servicios.append(s3)
        print("✅ Servicio Alquiler válido creado.")
    except ServicioNoDisponibleError as e:
        logging.error(e)
        print(f"❌ {e}")
    
    # 6. Servicio Asesoría válido (ahora sí existe la clase)
    try:
        s4 = AsesoriaEspecializada("Asesoría Python", 200000, "Programación")
        servicios.append(s4)
        print("✅ Servicio Asesoría creado.")
    except ServicioNoDisponibleError as e:
        logging.error(e)
        print(f"❌ {e}")
    
    # 7. Reserva exitosa con confirmación, cancelación y sobrecarga
    try:
        if len(clientes) > 0 and len(servicios) > 0:
            r1 = Reserva(clientes[0], servicios[0], 3)
            r1.confirmar()
            costo = r1.procesar(descuento=0.1, impuesto=0.19)
            reservas.append(r1)
            print(f"✅ Reserva exitosa. Costo final: {formato_cop(costo)}")
            r1.cancelar()
            print("   Reserva cancelada correctamente.")
        else:
            print("⚠️ No hay clientes o servicios para reserva.")
    except (DatosInvalidosError, ReservaInvalidaError) as e:
        logging.error(f"Error en reserva: {e}")
        print(f"❌ {e}")
    
    # 8. Reserva con cliente inválido (falla)
    try:
        r2 = Reserva("Cliente falso", servicios[0] if servicios else None, 2)
        reservas.append(r2)
        print("✅ Reserva creada (no debería).")
    except ReservaInvalidaError as e:
        logging.error(f"Error esperado: {e}")
        print(f"❌ Error esperado (cliente inválido): {e}")
    
    # 9. Reserva con duración negativa (falla)
    try:
        if clientes and servicios:
            r3 = Reserva(clientes[0], servicios[0], -5)
            reservas.append(r3)
            print("✅ Reserva con duración negativa creada (no debería).")
    except ReservaInvalidaError as e:
        logging.error(f"Error esperado: {e}")
        print(f"❌ Error esperado (duración negativa): {e}")
    
    # 10. Intentar cancelar reserva ya cancelada (demonstración excepción + finally)
    try:
        if reservas:
            reservas[0].cancelar()  # ya estaba cancelada, debe lanzar error
        else:
            print("⚠️ No hay reserva para probar doble cancelación.")
    except ReservaInvalidaError as e:
        logging.error(f"Error esperado (doble cancelación): {e}")
        print(f"❌ Error esperado (reserva ya cancelada): {e}")
    finally:
        print("🧹 Bloque finally: operación de doble cancelación finalizada.\n")
    
    # Demostración de try/except/else
    print("--- Demostración de try/except/else ---")
    try:
        if servicios:
            costo_demo = servicios[0].calcular_costo(2, descuento=0.05)
            print(f"Cálculo válido (2 horas con 5% desc): {formato_cop(costo_demo)}")
    except DatosInvalidosError as e:
        print(f"Error: {e}")
    else:
        print("El bloque else se ejecuta porque no hubo excepción.")
    finally:
        print("Bloque finally: siempre se ejecuta.\n")
    
    print("=== FIN DE LA SIMULACIÓN ===")
    print("Revise el archivo 'sistema.log' para detalles de eventos y errores.")

if __name__ == "__main__":
    iniciar_simulacion()