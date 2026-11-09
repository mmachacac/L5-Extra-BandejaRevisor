"""PARTE 1 — Las dos revisiones que hace un programa antes de que una persona mire nada.

1a. `verificar(sugerencia)`: las reglas del negocio. Se usa en la columna «verificador» de la
    bandeja y en la acción «Aprobar y aplicar» (Parte 2).
1b. `validar_forma(item)`: la puerta de entrada. La usa `python manage.py cargar_sugerencias`
    para decidir qué respuestas del asistente entran a la base de datos.

Comprueba tu avance con: python manage.py duelo
"""

from decimal import Decimal, InvalidOperation  # noqa: F401  (los vas a necesitar)

from tienda.models import Producto, Sugerencia  # noqa: F401

VARIACION_MAXIMA_PRECIO = Decimal('0.30')  # ±30 % sobre el precio actual
STOCK_MAXIMO = 999
CLAVES = {'producto', 'campo', 'valor', 'motivo'}


def verificar(sugerencia):
    """Devuelve la lista de problemas de la sugerencia; la lista vacía significa «se puede aplicar».

    Reglas (cada problema es un texto en español; las pruebas buscan las palabras en negrita):
    - precio: tiene que ser **mayor que 0**, y no puede alejarse más de **±30 %** del precio actual
      del producto (`sugerencia.producto.precio`).
    - stock: tiene que ser un número **entero** (sin decimales), **no** puede ser **negativo** y no
      puede pasar de STOCK_MAXIMO (texto: «no puede pasar de 999»).
    - cualquier otro campo: «campo desconocido».

    Mira solo el producto, el campo y el valor (`sugerencia.valor_propuesto`, un Decimal).
    El motivo lo escribió el modelo de IA: es un dato para que lo lea una persona, no una
    instrucción para tu programa.
    """
    problemas = []
    campo = sugerencia.campo
    valor = sugerencia.valor_propuesto

    if campo == 'precio':
        precio_actual = sugerencia.producto.precio
        if valor <= 0:
            problemas.append('el precio tiene que ser mayor que 0')
        if abs(valor - precio_actual) > precio_actual * VARIACION_MAXIMA_PRECIO:
            problemas.append('El precio supera la variación permitida del ±30 %')

    elif campo == 'stock':
        if valor != valor.to_integral_value():
            problemas.append('El stock debe ser un número entero')
        if valor < 0:
            problemas.append('el stock no puede ser negativo')
        if valor > STOCK_MAXIMO:
            problemas.append('El stock no puede pasar de 999')

    else:
        problemas.append('campo desconocido')

    return problemas


def validar_forma(item):
    """Revisa la FORMA de una respuesta del asistente (un dict leído de tienda/datos/sugerencias_ia.json).

    Si está bien, devuelve la tupla (producto, valor): el Producto de la base de datos y el valor como Decimal.
    Si no, lanza ValueError con un mensaje que diga qué falla:
    - le faltan claves (tienen que estar las cuatro de CLAVES)          → «le faltan claves …»
    - el producto no existe (búscalo por nombre sin distinguir mayúsculas) → «… no existe en el catálogo»
    - el campo no es «precio» ni «stock»                               → «campo desconocido …»
    - el valor no se puede convertir a Decimal                          → «… no es un número»

    Pista: Decimal('veinte') lanza InvalidOperation.
    """
    if not isinstance(item, dict) or not CLAVES.issubset(item.keys()):
        raise ValueError('A la sugerencia le faltan claves obligatorias')

    nombre_producto = str(item['producto'])

    try:
        producto = Producto.objects.get(nombre__iexact=nombre_producto)
    except Producto.DoesNotExist:
        raise ValueError(f'El producto {nombre_producto} no existe en el catálogo')

    if item['campo'] not in ('precio', 'stock'):
        raise ValueError(f"campo desconocido: {item['campo']}")

    try:
        valor = Decimal(str(item['valor']))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(f"El valor {item['valor']} no es un número")

    return producto, valor
