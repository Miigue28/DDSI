# Práctica 3
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

Ejecutamos la siguiente orden para inicializar nuestra base de datos:

```
flask init-db
```

Ejecutamos la aplicación:

```
python3 app.py
```