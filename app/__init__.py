# app/__init__.py - VERSIÓN FINAL SÚPER COMENTADA

# --- 1. IMPORTACIONES ---
# Lo primero es traer las herramientas que necesito de las librerías que instalé.
# Flask es como el motor principal de mi servidor web.
# render_template es la herramienta mágica que me deja dibujar mis páginas HTML.
# SocketIO es para la comunicación en tiempo real, para que la página se actualice sola.
from flask import Flask, render_template
from flask_socketio import SocketIO

# --- 2. CONFIGURACIÓN INICIAL DE LA APP ---
# Aquí creo mi aplicación Flask. '__name__' es una variable especial de Python que ayuda a Flask a ubicarse.
app = Flask(__name__)
# Esta 'SECRET_KEY' es como una contraseña para mi aplicación, necesaria para la seguridad. Puede ser cualquier texto.
app.config['SECRET_KEY'] = 'mi-clave-super-secreta-123'
# Aquí conecto SocketIO con mi aplicación Flask para que puedan funcionar juntas.
socketio = SocketIO(app)


# --- 3. MI "BASE DE DATOS" DE MENTIRA ---
# Como todavía no uso una base de datos real (como PostgreSQL), simulo una con una lista de diccionarios.
# Cada diccionario dentro de la lista representa un producto con sus propiedades.
productos = [
    {'id': 1, 'nombre': 'Tornillos Phillips', 'sku': 'TOR-PH-001', 'cantidad': 100},
    {'id': 2, 'nombre': 'Martillos de Goma', 'sku': 'MAR-GO-002', 'cantidad': 50},
    {'id': 3, 'nombre': 'Cinta Aislante Negra', 'sku': 'CIN-NE-003', 'cantidad': 85}
]
# Necesito un contador para saber qué ID le toca al próximo producto que cree.
next_id = 4 


# --- 4. DEFINICIÓN DE LA RUTA PRINCIPAL ---

# '@app.route("/")' es un "decorador". Le dice a Flask: "Che, cuando alguien entre a la página principal de la web, ejecuta la función que está debajo".
@app.route('/')
def index():
    # 'render_template' busca en la carpeta 'templates' el archivo que le digo (en este caso, 'index.html').
    # Además, le paso mi lista de 'productos' al HTML para que pueda usarla y mostrar los datos en la tabla.
    return render_template('index.html', productos=productos)


# --- 5. MANEJO DE EVENTOS DE WEBSOCKET (LA MAGIA DEL TIEMPO REAL) ---

# Este evento especial se activa automáticamente cuando un navegador se conecta a mi servidor.
@socketio.on('connect')
def handle_connect():
    # Imprimo un mensaje en mi terminal de Python (la que tengo abierta) para saber que la conexión fue exitosa. Sirve para debuggear.
    print('✅ Un cliente se ha conectado!')

# Este evento lo llamo yo desde el JavaScript cuando el usuario guarda el formulario (ya sea para crear o editar).
@socketio.on('guardar_producto')
def handle_guardar_producto(data):
    # 'data' es el diccionario con la info del producto que me mandó el JavaScript.
    global next_id # Le aviso a Python que voy a usar y posiblemente modificar la variable 'next_id' que definí arriba.
    
    id_producto = data.get('id')
    
    # Chequeo si el producto que me mandaron tiene un ID.
    if id_producto and id_producto != '':
        # Si SÍ tiene un ID, significa que estamos EDITANDO un producto que ya existe.
        # Busco en mi lista el producto que coincida con ese ID para poder actualizarlo.
        producto_encontrado = next((p for p in productos if p['id'] == int(id_producto)), None)
        if producto_encontrado:
            # Si lo encontré, actualizo sus datos con los que me llegaron del formulario.
            producto_encontrado.update(data)
            producto_encontrado['cantidad'] = int(data['cantidad']) # Me aseguro que la cantidad sea un número.
            
            # Ahora, le aviso a TODOS los navegadores conectados que un producto se modificó.
            # El nombre del evento ('producto_modificado') es importante, porque el JavaScript estará escuchando este nombre específico.
            socketio.emit('producto_modificado', producto_encontrado)
            print(f"🔄 Producto modificado: {producto_encontrado}")
    else:
        # Si NO tiene un ID, significa que estamos CREANDO un producto nuevo.
        nuevo_producto = data
        nuevo_producto['id'] = next_id # Le asigno el siguiente ID disponible.
        nuevo_producto['cantidad'] = int(data['cantidad'])
        
        productos.append(nuevo_producto) # Agrego el nuevo producto a mi lista.
        next_id += 1 # Incremento el contador de ID para el próximo que se cree.
        
        # Le aviso a TODOS los navegadores conectados que se creó un producto nuevo.
        socketio.emit('producto_creado', nuevo_producto)
        print(f"✨ Producto creado: {nuevo_producto}")

# Este evento lo llamo desde el JavaScript cuando el usuario confirma que quiere eliminar un producto.
@socketio.on('eliminar_producto')
def handle_eliminar_producto(data):
    id_producto = data.get('id')
    if id_producto:
        # Busco en la lista el producto que tengo que eliminar.
        producto_a_eliminar = next((p for p in productos if p['id'] == int(id_producto)), None)
        if producto_a_eliminar:
            productos.remove(producto_a_eliminar) # Lo saco de mi lista de 'productos'.
            # Le aviso a todos los navegadores que tienen que borrar de su pantalla el producto con este ID.
            socketio.emit('producto_eliminado', {'id': id_producto})
            print(f"❌ Producto eliminado, ID: {id_producto}")