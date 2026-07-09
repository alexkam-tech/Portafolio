# 🚀 LABORATORIO 01

## Obtener información de routers Cisco mediante Python, Netmiko y Pandas

**Caso de uso práctico de automatización para administración de redes**

<p align="center">
  <a href="https://github.com/alexkam-tech/Portafolio"><img src="https://img.shields.io/badge/GitHub-Repository-blue?logo=github" alt="GitHub"></a>
  <a href="https://youtube.com/@Akam-Labs"><img src="https://img.shields.io/badge/YouTube-Akam_Labs-red?logo=youtube" alt="YouTube"></a>
  <a href="#"><img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python" alt="Python"></a>
  <a href="#"><img src="https://img.shields.io/badge/Netmiko-Library-orange" alt="Netmiko"></a>
</p>

**Autor:** Alex Kam | [alexkam-tech](https://github.com/alexkam-tech)  
**Fecha:** Julio 2026  
**YouTube:** [Akam Labs](https://youtube.com/@Akam-Labs)

> Este documento forma parte de mi portafolio de proyectos de automatización de redes y está diseñado para generar valor práctico en la comunidad hispanohablante.

---

## 📋 Índice de Contenidos

- [1. Caso de Uso y Problema](#1-caso-de-uso-y-problema)
- [2. Solución Propuesta](#2-solución-propuesta)
- [3. Topología de Laboratorio](#3-topología-de-laboratorio)
- [4. Configuración Base SSH](#4-configuración-base-ssh-en-los-routers-cisco)
- [5. Archivo Excel de Inventario](#5-archivo-excel-de-inventario-ip_planningxlsx)
- [6. Script en Python – Paso a Paso](#6-script-en-python--explicación-paso-a-paso)
- [7. Threading – Ejecución Paralela](#7-threading--ejecución-en-paralelo)
- [8. Resultados de la Ejecución](#8-resultados-de-la-ejecución)
- [9. Script Completo](#9-script-completo-código-original)
- [10. Cómo Usar este Laboratorio](#10-cómo-usar-este-laboratorio)
- [11. Únete a la Comunidad](#11-únete-a-la-comunidad)

---

## 1. Caso de Uso y Problema

**Contexto**  
Como parte de las tareas diarias de un ingeniero de red, es muy común tener que obtener el estado de los dispositivos de forma periódica (diaria o varias veces al día). Cuando se gestionan **50 o más equipos** y se deben ejecutar alrededor de **10 comandos** por dispositivo, el proceso manual se vuelve extremadamente lento y propenso a errores.

**Problema**  
- El trabajo manual consume mucho tiempo.
- Existe alto riesgo de inconsistencias en los datos recolectados.
- Revisar manualmente la salida de cada comando en cada dispositivo es ineficiente cuando se escala.

**Objetivo del laboratorio**  
Crear un script en **Python** que:
- Automatice la conexión SSH a múltiples routers Cisco.
- Ejecute una lista de comandos de diagnóstico (`show` commands).
- Guarde los resultados organizados en archivos de texto individuales por dispositivo.
- Utilice **threading** para ejecutar las tareas en paralelo y reducir significativamente el tiempo total.

---

## 2. Solución Propuesta

Se desarrolla un script en Python utilizando las siguientes herramientas:

| Herramienta   | Propósito                                           |
|---------------|-----------------------------------------------------|
| **Python**    | Lenguaje principal del script                       |
| **Netmiko**   | Manejo de conexiones SSH a dispositivos de red      |
| **Pandas**    | Lectura del archivo Excel de inventario             |
| **Threading** | Ejecución en paralelo para mejorar el rendimiento   |

**Resultado esperado**  
Una carpeta `logs/` que contiene un archivo `.txt` por cada router procesado, con toda la salida de los comandos ejecutados.

---

## 3. Topología de Laboratorio

Se utiliza la siguiente topología en **GNS3** (o Eve-NG):

> **Nota:** La topología es solo de ejemplo. El script funciona con cualquier cantidad de dispositivos mientras tengan conectividad SSH y el archivo Excel esté actualizado.

---

## 4. Configuración Base SSH en los Routers Cisco

Aplica esta configuración base en cada router:

```bash
conf t
!
hostname RX
ip domain-name akam-labs
crypto key generate rsa general-keys 4096
ip ssh version 2
username akam privilege 15 secret akam@123
!
interface gigabitEthernet 0/3
 ip address x.x.x.x y.y.y.y
 no shutdown
!
line vty 0 15
 login local
 transport input ssh
!
end
write
```

### Direcciones IP de Gestión (Gi0/3)

| Hostname | IP de Gestión         |
|----------|-----------------------|
| R1       | 192.168.18.100/24     |
| R2       | 192.168.18.101/24     |
| R3       | 192.168.18.102/24     |
| R4       | 192.168.18.103/24     |
| R5       | 192.168.18.104/24     |

**Credenciales del script:**  
- Usuario: `akam`  
- Contraseña: `akam@123`

---

## 5. Archivo Excel de Inventario (ip_planning.xlsx)

El script utiliza un archivo Excel llamado `ip_planning.xlsx` (hoja: `Hoja1`).

### Estructura mínima recomendada

| Columna     | Descripción                    |
|-------------|--------------------------------|
| HOSTNAME    | Nombre del equipo              |
| IP          | Dirección IP de gestión        |
| PUERTO      | Puerto SSH (normalmente 22)    |

> El script recorre cada fila del Excel y utiliza los datos para conectarse automáticamente a cada dispositivo.

---

## 6. Script en Python – Explicación Paso a Paso

### 6.1 Importar librerías

```python
import netmiko
import pandas
import threading
```

### 6.2 Función de conexión con Netmiko

```python
def obtener_informacion(fila):
    try:
        datos_de_conexion = {
            "device_type": "cisco_ios",
            "username": "akam",
            "password": "akam@123",
            "host": fila['IP'],
            "port": fila['PUERTO']
        }

        conector = netmiko.ConnectHandler(**datos_de_conexion)
        print(f"Conexion establecida al equipo {fila['HOSTNAME']}")
        ...
```

### 6.3 Lista de comandos y ejecución

Se define una lista de comandos `show` que se ejecutarán en cada dispositivo:

```python
lista_de_comandos = [
    "show run",
    "show ip int brief",
    "show logg"
]
```

### 6.4 Guardado de logs por dispositivo

Los resultados se guardan en archivos individuales dentro de la carpeta `logs/`.

### 6.5 Ejecución con Pandas

```python
df = pandas.read_excel("ip_planning.xlsx", sheet_name="Hoja1")

for _, fila in df.iterrows():
    obtener_informacion(fila)
```

---

## 7. Threading – Ejecución en Paralelo

Cuando se gestionan muchos dispositivos, la ejecución secuencial es muy lenta. Usamos `threading` para procesar varios routers al mismo tiempo.

```python
lista_de_hilos = []

for _, fila in df.iterrows():
    hilo = threading.Thread(target=obtener_informacion, args=(fila,))
    lista_de_hilos.append(hilo)
    hilo.start()

for hilo in lista_de_hilos:
    hilo.join()
```

Esto reduce significativamente el tiempo total de ejecución.

---

## 8. Resultados de la Ejecución

Al finalizar, se genera una carpeta `logs/` con un archivo de texto por cada router procesado.

---

## 9. Script Completo (Código Original)

```python
import netmiko
import pandas
import threading

def obtener_informacion(fila):
    try:
        usuario = "akam"
        contra = "akam@123"

        datos_de_conexion = {
            "device_type": "cisco_ios",
            "username": usuario,
            "password": contra,
            "host": fila['IP'],
            "port": fila['PUERTO']
        }

        conector = netmiko.ConnectHandler(**datos_de_conexion)
        print(f"Conexion establecida al equipo {fila['HOSTNAME']}")

        lista_de_comandos = [
            "show run",
            "show ip int brief",
            "show logg"
        ]

        lista_de_resultados = []

        for comando in lista_de_comandos:
            resultado = conector.send_command(comando, strip_command=False, strip_prompt=False)
            lista_de_resultados.append("\n")
            lista_de_resultados.append("="*70)
            lista_de_resultados.append(resultado)
            lista_de_resultados.append("\n")
            lista_de_resultados.append("="*70)

        print(f"Se ha ejecutado los comandos en el equipo {fila['HOSTNAME']}")

        with open(f"/Users/akam/Documents/python_labs/portafolio/laboratorio_python/lab01/logs/{fila['HOSTNAME']}.txt", "w") as archivo:
            cli = "\n".join(lista_de_resultados)
            archivo.write(cli)

        print(f"Se ha generado el archivo con la informacion de {fila['HOSTNAME']}")

        conector.disconnect()
        print(f"Desconectado del equipo - {fila['HOSTNAME']}")

    except Exception as e:
        print(f"Se tiene un error en el equipo {fila['HOSTNAME']} - error: {e}")


df = pandas.read_excel("/Users/akam/Documents/python_labs/portafolio/laboratorio_python/lab01/ip_planning.xlsx", sheet_name="Hoja1")

# === Versión Secuencial (comentada) ===
# for _, fila in df.iterrows():
#     obtener_informacion(fila)

# === Versión Paralela con Threading ===
lista_de_hilos = []

for _, fila in df.iterrows():
    hilo = threading.Thread(target=obtener_informacion, args=(fila,))
    lista_de_hilos.append(hilo)
    hilo.start()

for hilo in lista_de_hilos:
    hilo.join()
```

---

## 10. Cómo usar este laboratorio

### Requisitos

- Python 3.10 o superior
- Instalar librerías:
  ```bash
  pip install netmiko pandas openpyxl
  ```
- GNS3 / Eve-NG o routers físicos con SSH habilitado
- Archivo `ip_planning.xlsx` en la misma carpeta del script

### Pasos recomendados

1. Prepara tu archivo Excel con los dispositivos (mínimo: `HOSTNAME`, `IP`, `PUERTO`).
2. Verifica que los routers tengan SSH habilitado.
3. Ejecuta primero en modo secuencial (descomenta el bucle `for`).
4. Una vez validado, usa la versión con `threading`.
5. Revisa los archivos generados en la carpeta `logs/`.

> **Recomendación de seguridad:** En entornos reales, usa variables de entorno (`.env`) en lugar de credenciales hardcodeadas.

---

## 11. Únete a la comunidad

Este laboratorio forma parte de una serie de contenido educativo sobre **automatización de redes**. Mi objetivo es compartir conocimiento práctico y aplicable para que más personas puedan escalar su trabajo como ingenieros de red.

¡Gracias por leer y por ser parte de esta comunidad!

---

**Alex Kam**  
Networking | Python Automation | GNS3 Labs  
📧 ft.alex.kam@gmail.com | 📍 Lima, Perú

### Conecta conmigo

- 🐙 **GitHub**: [alexkam-tech/Portafolio](https://github.com/alexkam-tech/Portafolio)
- ▶️ **YouTube**: [@Akam-Labs](https://youtube.com/@Akam-Labs)
- 🔗 **LinkedIn**: [Alex Kam Goñe](https://linkedin.com/in/alexkamgoñe)

---

⭐ **Si este laboratorio te fue útil, déjame una estrella en el repositorio y suscríbete al canal.**  
¡Nos vemos en el próximo laboratorio!
```
