# 🚀 Software FJ - Sistema de Gestión de Clientes, Servicios y Reservas
##  Acerca de este repositorio

Este proyecto es un **fork** del repositorio original de [YeysonUnd/Programacion_Fase4_SoftwareFJ](https://github.com/YeysonUnd/Programacion_Fase4_SoftwareFJ), el cual sirvió como base funcional. A partir de ese código, se implementaron las siguientes **extensiones para cumplir completamente con los requerimientos de la tarea**:

- **Manejo avanzado de excepciones**: se agregaron bloques `try/except/else/finally`, excepciones personalizadas (`ServicioNoDisponibleError`) y encadenamiento (`raise ... from e`).
- **Sobrecarga de métodos**: el método `calcular_costo` ahora acepta parámetros opcionales `descuento` e `impuesto` mediante `**kwargs`.
- **Confirmación y cancelación de reservas**: se añadieron métodos `confirmar()` y `cancelar()` a la clase `Reserva`.
- **Registro de eventos**: se configuró `logging` en nivel `INFO` para registrar también operaciones exitosas, no solo errores.
- **Validaciones robustas**: se reescribió la clase `Cliente` con propiedades (`@property`) y validaciones más estrictas (nombre no vacío, formato de email).
- **Adaptación a moneda colombiana**: se incorporó la función `formato_cop()` y se ajustaron los precios a valores realistas en COP.
- **Simulación completa**: se rediseñó la función de simulación para ejecutar exactamente 10 operaciones, mezclando casos válidos e inválidos.

Estas mejoras permiten que el sistema demuestre todos los pilares de la POO (abstracción, herencia, polimorfismo, encapsulación) y cumpla con los requisitos de robustez y manejo de errores exigidos en el enunciado.


"Agradezco a YEYSON JAVIER MARTINEZ MARTINEZ por proporcionar el punto de partida de este trabajo. Su código demostró una comprensión sólida de los fundamentos de POO (clases abstractas, herencia, polimorfismo básico), lo que me permitió enfocarme en añadir los elementos de manejo avanzado de excepciones, sobrecarga de métodos, confirmación/cancelación de reservas y registro detallado de eventos que se solicitaban en la fase final de la tarea."

**Nota:** Las diferencias no implican que el código base sea incorrecto; simplemente el enunciado original de la tarea requería un nivel de detalle y robustez adicional que ha sido implementado en esta versión.
