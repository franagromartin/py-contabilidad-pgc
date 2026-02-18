class AsientoDescuadradoError(Exception):
    """Excepción lanzada cuando los importes del Debe y Haber no cuadran."""
    def __init__(self, diferencia: float):
        self.diferencia = diferencia
        super().__init__(f"El asiento está descuadrado por {diferencia}")

class CuentaNoEncontradaError(Exception):
    """Excepción lanzada cuando una cuenta contable no existe."""
    def __init__(self, cuenta_codigo: str):
        self.cuenta_codigo = cuenta_codigo
        super().__init__(f"La cuenta contable '{cuenta_codigo}' no existe")

class EjercicioCerradoError(Exception):
    """Excepción lanzada cuando se intenta operar en un ejercicio cerrado."""
    pass

class EjercicioNoEncontradoError(Exception):
    """Excepción lanzada cuando no se encuentra un ejercicio fiscal válido para la fecha."""
    pass
