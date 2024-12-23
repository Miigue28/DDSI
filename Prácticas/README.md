# Seminario 2: Acceso a bases de datos

## Diseño y Desarrollo de Sistemas de Información

### Instalación

En primer lugar, será necesario crear un entorno virtual

```
python3 -m venv .env
```

Una vez creado, lo activamos mediante

```
source .env/bin/activate
```

Luego, instalamos todas las dependencias necesarias

```
pip install -r requirements.txt
```

> Si no tienes `venv`, instálalo:
>
> ```
> sudo apt-get install python3-venv
> ```

A continuación, construiremos el paquete de python mediante

```
python3 -m build --wheel
```

Para posteriormente ejecutar un contenedor de Docker con la aplicación 


```
docker compose up
```

### Roadmap

- [ ] Conexión a la base de datos
- [ ] Creación de tablas e inserción de tuplas
- [ ] Diseño de la interfaz de usuario
- [ ] Implementación de la interfaz de usuario
- [ ] Diseño de funcionalidades del backend
- [ ] Implementación del backend
- [ ] Tests
