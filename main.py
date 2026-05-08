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
    """Servicio 1: Cálculo basado en horas de uso."""
    def calcular_costo(self, horas):
        if horas <= 0:
            raise DatosInvalidosError("La duración en horas debe ser positiva.")
        return self.costo_base * horas

class AlquilerEquipo(Servicio):
    """Servicio 2: Cálculo basado en cantidad de dispositivos."""
    def calcular_costo(self, cantidad):
        if cantidad <= 0:
            raise DatosInvalidosError("La cantidad de equipos debe ser mayor a cero.")
        return self.costo_base * cantidad

class AsesoriaEspecializada(Servicio):
    """Servicio 3: Cálculo con aplicación de impuestos (IVA)."""
    def calcular_costo(self, horas):
        if horas <= 0:
            raise DatosInvalidosError("Las horas de asesoría deben ser positivas.")
        iva = 1.19
        return (self.costo_base * horas) * iva

# =================================================================
# GESTIÓN DE RESERVAS Y MANEJO DE EXCEPCIONES
# Coordina objetos y gestiona errores con bloques try/except/finally.
# =================================================================
class Reserva:
    """Clase mediadora que integra Cliente y Servicio."""
    def __init__(self, cliente, servicio, magnitud):
        self.cliente = cliente
        self.servicio = servicio
        self.magnitud = magnitud # Puede ser horas o cantidad según el servicio
        self.estado = "Pendiente"

    def procesar_reserva(self):
        """Ejecuta la lógica de reserva con control de errores avanzado."""
        try:
            # Validación de integridad del objeto cliente
            if self.cliente is None:
                raise ReservaInvalidaError("No se puede procesar una reserva sin un cliente válido.")
            
            # Aplicación de Polimorfismo: el cálculo depende del tipo de servicio
            costo = self.servicio.calcular_costo(self.magnitud)
            self.estado = "Confirmada"
            print(f"ÉXITO: {self.servicio.nombre_servicio} para {self.cliente.nombre}. Costo: ${costo:,.0f}")
        
        except (ReservaInvalidaError, DatosInvalidosError) as e:
            # Captura de errores de lógica de negocio y registro en log
            self.estado = "Fallida"
            logging.error(f"Error en proceso de reserva: {e}")
            print(f"ERROR CONTROLADO: {e}")
        
        except Exception as e:
            # Captura de errores inesperados (estabilidad del sistema)
            logging.error(f"Error crítico inesperado: {e}")
            print("Ha ocurrido un error inesperado, el sistema permanece estable.")
        
        finally:
            # Bloque de cierre: se ejecuta siempre para limpieza o auditoría
            fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Resultado: {self.estado} | Registro: {fecha_actual}\n")

# =================================================================
# SIMULACIÓN DE OPERACIONES (10 Casos de Prueba)
# Demostración de robustez ante datos válidos e inválidos.
# =================================================================
def  iniciar_simulacion():
    print("=== PRUEBA DE SERVICIO (sin reservas aún) ===\n")
    # Solo probamos que la clase Servicio y sus hijas no se usan aún (este cambio será temporal)
    print("Esperando modificaciones de servicios concretos...")