# LAB 02: Configure OSPF on Cisco Routers Using Python, Netmiko, and Pandas

**Practical Automation Use Case for Network Administration**

- **Author:** Alex Kam | alexkam-tech
- **Date:** July 2026
- **Repository:** [github.com/alexkam-tech/Portafolio](https://github.com/alexkam-tech/Portafolio)
- **YouTube:** [youtube.com/@Akam-Labs](https://youtube.com/@Akam-Labs)

> This document is part of my network automation project portfolio and is designed to generate value and community among the English-speaking audience.

---

## Table of Contents

1. [Use Case and Problem](#1-use-case-and-problem)
2. [Proposed Solution](#2-proposed-solution)
3. [Laboratory Topology](#3-laboratory-topology)
4. [Base SSH Configuration on Routers](#4-base-ssh-configuration-on-routers)
5. [Excel Inventory File (ip_planning.xlsx)](#5-excel-inventory-file-ip_planningxlsx)
6. [Python Script — Step-by-Step Explanation](#6-python-script--step-by-step-explanation)
7. [Threading — Parallel Execution](#7-threading--parallel-execution)
8. [Execution Results](#8-execution-results)
9. [COMPLETE SCRIPT (Original Code)](#9-complete-script-original-code)
10. [How to Use This Lab](#10-how-to-use-this-lab)
11. [Join the Community](#11-join-the-community)

---

## 1. Use Case and Problem

**Context:** As part of network engineering tasks, it is common to deploy complex configurations across dozens of devices. When managing 50 or more devices, the manual process becomes very slow and prone to human errors.

**Problem:** This manual approach is not only extremely slow but also error-prone. Additionally, if a change needs to be made later, it requires accessing the devices again, which is not scalable.

**Objective of this lab:** Create a Python script that automates SSH connections to multiple Cisco routers, executes the OSPF configuration, and saves the results organized in individual text files per device. Additionally, implement parallel execution using `threading` to significantly reduce total execution time.

---

## 2. Proposed Solution

A Python script is developed using the following tools:

- **Python**: Main scripting language.
- **Netmiko**: Specialized library for SSH connections to network devices (Cisco, Huawei, etc.). It facilitates prompt handling and multi-platform support.
- **Pandas**: To read the Excel inventory file in a clean and professional way.
- **Threading**: To execute connections in parallel and optimize execution time when managing many devices.

**Expected result:** A folder called `log/` containing one `.txt` file per processed router, with all the output from the executed commands.

---

## 3. Laboratory Topology

To simulate the scenario, the following topology is used in **GNS3** (or Eve-NG). From the "LAN Network" cloud, we connect via SSH to each of the routers.

> **Note:** The topology is for example purposes only. The script works with any number of devices as long as SSH connectivity is available and the Excel file is updated.

---

## 4. Base SSH Configuration on Cisco Routers

Apply the following base configuration on each router to enable SSH access:

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

### Management IP Addresses (Gi0/3)

| Hostname | IP Address          |
|----------|---------------------|
| R1       | 192.168.18.100/24   |
| R2       | 192.168.18.101/24   |
| R3       | 192.168.18.102/24   |
| R4       | 192.168.18.103/24   |
| R5       | 192.168.18.104/24   |

**Script Credentials:**  
- Username: `akam`  
- Password: `akam@123`

> **Important:** Make sure SSH access is working before running the script.

---

## 5. Excel Inventory File (ip_planning.xlsx)

The script uses an Excel file named `ip_planning.xlsx` (sheet: `devices`) that contains all the necessary device information.

### Excel Structure

| Column                        | Description                              |
|------------------------------|------------------------------------------|
| NE                           | Hostname (R1, R2, R3...)                 |
| IP                           | Management IP address                    |
| PORT                         | SSH Port (usually 22)                    |
| LOOPBACK_IP                  | Loopback IP address                      |
| LOOPBACK_MASK                | Loopback subnet mask                     |
| INTERFACE_DEVICE1            | First interconnection interface          |
| IP_INTERFACE_DEVICE1         | IP for first interface                   |
| MASK_INTERFACE_DEVICE1       | Mask for first interface                 |
| INTERFACE_DEVICE2            | Second interconnection interface (or `-`)|
| IP_INTERFACE_DEVICE2         | IP for second interface                  |
| MASK_INTERFACE_DEVICE2       | Mask for second interface                |

> The script reads this file row by row and uses the data to configure each device dynamically.

---

## 6. Python Script — Step-by-Step Explanation

Below is the explanation of the developed script, keeping the original code structure.

### 6.1 Importing Libraries

```python
import netmiko
import pandas
import threading
```

### 6.2 Defining the Connection Function with Netmiko

```python
def configure_ospf(row):
    try:
        connection_data = {
            "device_type": "cisco_ios",
            "ip": row['IP'],
            "port": row['PORT'],
            "username": "akam",
            "password": "akam@123",
            "timeout": 10
        }
        connector = netmiko.ConnectHandler(**connection_data)
        print(f"We are connected to the device {row['NE']}")
        ...
```

### 6.3 Command List and Execution Loop

The script dynamically builds the OSPF configuration using data from the Excel file and evaluates whether the device has a second interconnection interface.

### 6.4 Opening Log File per Device

Results are saved in individual `.txt` files inside the `log/` folder.

### 6.5 Loading Excel with Pandas and Execution

```python
df = pandas.read_excel("ip_planning.xlsx", sheet_name="devices")

for index, row in df.iterrows():
    configure_ospf(row)
```

---

## 7. Threading — Parallel Execution

When managing many devices (50+), sequential execution becomes slow. Using Python's `threading` module allows multiple devices to be configured simultaneously.

```python
list_of_threads = []

for index, row in df.iterrows():
    thread = threading.Thread(target=configure_ospf, args=(row,))
    list_of_threads.append(thread)
    thread.start()

for thread in list_of_threads:
    thread.join()
```

This significantly reduces total execution time.

---

## 8. Execution Results

As a final result, the script generates one log file per device inside the `log/` folder.

---

## 9. COMPLETE SCRIPT (Original Code)

```python
import netmiko
import pandas
import threading

def configure_ospf(row):
    try:
        connection_data = {
            "device_type": "cisco_ios",
            "ip": row['IP'],
            "port": row['PORT'],
            "username": "akam",
            "password": "akam@123",
            "timeout": 10
        }
        connector = netmiko.ConnectHandler(**connection_data)
        print(f"We are connected to the device {row['NE']}")

        list_for_results = []

        commands_for_ospf_part1 = f"""
        interface loopback 1
        ip address {row['LOOPBACK_IP']} {row['LOOPBACK_MASK']}
        #
        # OSPF CONFIGURATION
        #
        router ospf 1
        router-id {row['LOOPBACK_IP']}
        network {row['LOOPBACK_IP']} 0.0.0.0 area 0
        #
        # Interfaces to routers
        #
        interface {row['INTERFACE_DEVICE1']}
        ip address {row['IP_INTERFACE_DEVICE1']} {row['MASK_INTERFACE_DEVICE1']}
        ip ospf 1 area 0
        no shutdown
        #
        """
        if row['INTERFACE_DEVICE2'] != "-":
            commands_for_ospf_part2 = f"""
                interface {row['INTERFACE_DEVICE2']}
                ip address {row['IP_INTERFACE_DEVICE2']} {row['MASK_INTERFACE_DEVICE2']}
                ip ospf 1 area 0
                no shutdown
                #
            """
        else:
            commands_for_ospf_part2 = ""

        final_ospf_config = commands_for_ospf_part1 + '\n' + commands_for_ospf_part2

        output_ospf_config = connector.send_config_set(final_ospf_config.splitlines())
        output_save_config = connector.save_config()

        print(f"Configuration applied for router {row['NE']}")

        list_for_results.append(output_ospf_config)
        list_for_results.append(output_save_config)

        with open(f"/Users/akam/Documents/python_labs/portafolio/laboratorio_python/lab02/log/{row['NE']}.txt", "w") as file:
            file.write('\n'.join(list_for_results))

        print(f"Configuration log is generated for device {row['NE']}")

        connector.disconnect()

    except Exception as e:
        print(f"We have an error on the device {row['NE']} - {e}")


df = pandas.read_excel("/Users/akam/Documents/python_labs/portafolio/laboratorio_python/lab02/ip_planning.xlsx", sheet_name="devices")

# Sequential version (commented)
# for index, row in df.iterrows():
#     configure_ospf(row)

# Parallel version with Threading
list_of_threads = []

for index, row in df.iterrows():
    thread = threading.Thread(target=configure_ospf, args=(row,))
    list_of_threads.append(thread)
    thread.start()

for thread in list_of_threads:
    thread.join()
```

---

## 10. How to Use This Lab

### Requirements

- Python 3.10 or higher
- Libraries:
  ```bash
  pip install netmiko pandas openpyxl
  ```
- GNS3 or Eve-NG with the topology configured (or physical routers)
- SSH access enabled on the devices
- `ip_planning.xlsx` file in the same folder as the script

### Steps to Run

1. Prepare the `ip_planning.xlsx` file with your devices.
2. Ensure the routers have the base SSH configuration applied.
3. (Recommended) First run the script in sequential mode to test.
4. Once verified, use the threaded version for better performance.
5. Check the generated log files in the `log/` folder.

> **Security Recommendation:** For production environments, move credentials to environment variables or a `.env` file using `python-dotenv`.

---

## 11. Join the Community

This lab is part of my educational content on **network automation**. The goal is to share practical knowledge so more people can automate repetitive tasks and scale their work in networking.

Thank you for reading and for being part of this networking and automation community!

---

**Alex Kam**  
Networking | Python Automation | GNS3 Labs  
ft.alex.kam@gmail.com | San Isidro, Lima, Perú

### Connect with Me

- 🐙 **GitHub**: [github.com/alexkam-tech/Portafolio](https://github.com/alexkam-tech/Portafolio)
- ▶️ **YouTube**: [youtube.com/@Akam-Labs](https://youtube.com/@Akam-Labs)
- 🔗 **LinkedIn**: [linkedin.com/in/alexkamgoñe](https://linkedin.com/in/alexkamgoñe)

---

*If this lab helped you, please leave a ⭐ on the repository and subscribe to the channel!*


# LABORATORIO 02
## Configurar OSPF en routers Cisco mediante Python, Netmiko y Pandas

**Caso de uso práctico de automatización para administración de redes**

- **Autor:** Alex Kam | alexkam-tech
- **Fecha:** Julio 2026
- **Repositorio:** [github.com/alexkam-tech/Portafolio](https://github.com/alexkam-tech/Portafolio)
- **YouTube:** [youtube.com/@Akam-Labs](https://youtube.com/@Akam-Labs)

> Este documento forma parte de mi portafolio de proyectos de automatización de redes y está diseñado para generar valor y comunidad en la audiencia hispanohablante.

---

## Índice de Contenidos

1. [Caso de Uso y Problema](#1-caso-de-uso-y-problema)
2. [Solución Propuesta](#2-solución-propuesta)
3. [Topología de Laboratorio](#3-topología-de-laboratorio)
4. [Configuración Base SSH en los Routers](#4-configuración-base-ssh-en-los-routers)
5. [Archivo Excel de Inventario (ip_planning.xlsx)](#5-archivo-excel-de-inventario-ip_planningxlsx)
6. [Script en Python – Explicación Paso a Paso](#6-script-en-python--explicación-paso-a-paso)
7. [Threading – Ejecución en Paralelo](#7-threading--ejecución-en-paralelo)
8. [Resultados de la Ejecución](#8-resultados-de-la-ejecución)
9. [SCRIPT COMPLETO (Código Original)](#9-script-completo-código-original)
10. [Cómo usar este laboratorio](#10-cómo-usar-este-laboratorio)
11. [Únete a la comunidad](#11-únete-a-la-comunidad)

---

## 1. Caso de Uso y Problema

**Contexto:** Como parte de las tareas de administración de equipos de red, es común tener que desplegar configuraciones complejas en decenas de dispositivos. Cuando se gestionan 50 o más equipos, el proceso manual se vuelve muy lento y propenso a errores humanos.

**Problema:** Este enfoque manual no solo es extremadamente lento, sino que también es propenso a errores humanos y dificulta la escalabilidad. Además, si se requiere realizar un cambio posterior, implica tener que acceder nuevamente a los equipos, lo cual no es escalable.

**Objetivo de este laboratorio:** Crear un script en Python que automatice la conexión vía SSH a múltiples routers Cisco, ejecute la configuración y guarde los resultados organizados en archivos de texto individuales por dispositivo. Adicionalmente, se implementa ejecución en paralelo usando `threading` para reducir significativamente el tiempo total.

---

## 2. Solución Propuesta

Se desarrolla un script en Python que utiliza las siguientes herramientas:

- **Python**: Lenguaje principal del script.
- **Netmiko**: Librería especializada para conexiones SSH a dispositivos de red (Cisco, Huawei, etc.). Facilita el manejo de prompts y diferentes plataformas.
- **Pandas**: Para leer de forma sencilla y profesional el archivo Excel con el inventario de dispositivos.
- **Threading**: Para ejecutar las conexiones de forma paralela y optimizar el tiempo de ejecución cuando hay muchos dispositivos.

**Resultado esperado:** Una carpeta llamada `log/` que contiene un archivo `.txt` por cada router procesado, con toda la información recolectada de los comandos ejecutados.

---

## 3. Topología de Laboratorio

Para simular el escenario se utiliza la siguiente topología en **GNS3** (o Eve-NG). Desde la nube "RED LAN" nos conectamos vía SSH a cada uno de los routers.

> **Nota:** La topología es de ejemplo. El script funciona con cualquier cantidad de dispositivos siempre que se tenga conectividad SSH y el archivo Excel actualizado.

---

## 4. Configuración Base SSH en los Routers Cisco

Se debe aplicar la siguiente configuración base en cada router para permitir el acceso por SSH:

```bash
conf t
!
hostname RX
ip domain-name akam-labs
crypto key generate rsa general-keys 4096
ip ssh version 2
username akam privilege 15 secret akam@123
!
! Interfaz de gestión
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

### Direcciones IP utilizadas para la interfaz de gestión (Gi0/3)

| Hostname | IP Interfaz Gi0/3     |
|----------|-----------------------|
| R1       | 192.168.18.100/24     |
| R2       | 192.168.18.101/24     |
| R3       | 192.168.18.102/24     |
| R4       | 192.168.18.103/24     |
| R5       | 192.168.18.104/24     |

**Credenciales del script:**  
- Usuario: `akam`  
- Contraseña: `akam@123`

> **Importante:** Asegúrate de tener acceso SSH antes de ejecutar el script.

---

## 5. Archivo Excel de Inventario (ip_planning.xlsx)

El script utiliza un archivo Excel llamado `ip_planning.xlsx` (hoja: `devices`) que contiene la información de los dispositivos.

### Estructura del archivo Excel

| Columna                       | Descripción                                      |
|-------------------------------|--------------------------------------------------|
| NE                            | Hostname (R1, R2, R3...)                         |
| IP                            | Dirección IP de gestión                          |
| PORT                          | Puerto SSH (generalmente 22)                     |
| LOOPBACK_IP                   | Dirección IP del Loopback                        |
| LOOPBACK_MASK                 | Máscara del Loopback                             |
| INTERFACE_DEVICE1             | Primera interfaz de interconexión                |
| IP_INTERFACE_DEVICE1          | IP de la primera interfaz                        |
| MASK_INTERFACE_DEVICE1        | Máscara de la primera interfaz                   |
| INTERFACE_DEVICE2             | Segunda interfaz de interconexión (o `-`)        |
| IP_INTERFACE_DEVICE2          | IP de la segunda interfaz                        |
| MASK_INTERFACE_DEVICE2        | Máscara de la segunda interfaz                   |

> El script recorre cada fila del Excel y utiliza esos datos para conectarse y configurar dinámicamente cada dispositivo.

---

## 6. Script en Python – Explicación Paso a Paso

A continuación se explica el script desarrollado, manteniendo exactamente el código original.

### 6.1 Importar las librerías

```python
import netmiko
import pandas
import threading
```

### 6.2 Definir la función y realizar la conexión mediante Netmiko

```python
def configurar_ospf(fila):
    try:
        datos_conexion = {
            "device_type": "cisco_ios",
            "ip": fila['IP'],
            "port": fila['PORT'],
            "username": "akam",
            "password": "akam@123",
            "timeout": 10
        }
        conector = netmiko.ConnectHandler(**datos_conexion)
        print(f"Conectado al equipo {fila['NE']}")
        ...
```

### 6.3 Crear lista de comandos y recorrer con bucle for

Se definen los comandos OSPF dinámicamente usando los valores del Excel. Se evalúa si el dispositivo tiene segunda interfaz de interconexión.

### 6.4 Aperturar archivo de log por dispositivo

Se crea un archivo de texto por cada router dentro de la carpeta `log/`.

### 6.5 Cargar el Excel con Pandas y recorrer las filas

```python
df = pandas.read_excel("ip_planning.xlsx", sheet_name="devices")

for indice, fila in df.iterrows():
    configurar_ospf(fila)
```

---

## 7. Threading – Ejecución en Paralelo

**Consideración importante:** Cuando se tienen muchos dispositivos (50+), la ejecución secuencial puede tardar demasiado tiempo. Para mejorar el tiempo total de ejecución se utiliza la librería `threading` de Python, permitiendo ejecutar la función de forma paralela por cada fila del Excel.

```python
lista_de_hilos = []

for indice, fila in df.iterrows():
    hilo = threading.Thread(target=configurar_ospf, args=(fila,))
    lista_de_hilos.append(hilo)
    hilo.start()

for hilo in lista_de_hilos:
    hilo.join()
```

El resultado es una ejecución mucho más rápida porque varios dispositivos se procesan al mismo tiempo.

---

## 8. Resultados de la Ejecución

Como resultado final se generan varios archivos dentro de la carpeta `log/`, uno por cada dispositivo procesado.

---

## 9. SCRIPT COMPLETO (Código Original)

```python
import netmiko
import pandas
import threading

def configurar_ospf(fila):
    try:
        datos_conexion = {
            "device_type": "cisco_ios",
            "ip": fila['IP'],
            "port": fila['PORT'],
            "username": "akam",
            "password": "akam@123",
            "timeout": 10
        }
        conector = netmiko.ConnectHandler(**datos_conexion)
        print(f"Conectado al equipo {fila['NE']}")

        conector.enable()

        comandos_configuracion_ospf_parte1 = f"""
        interface loopback 1
        ip address {fila['LOOPBACK_IP']} {fila['LOOPBACK_MASK']}
        #
        # CONFIGURACION OSPF
        #
        router ospf 1
        router-id {fila['LOOPBACK_IP']}
        network {fila['LOOPBACK_IP']} 0.0.0.0 area 0
        #
        # INTERFACES DE INTERCONEXION
        #
        interface {fila['INTERFACE_DEVICE1']}
        ip address {fila['IP_INTERFACE_DEVICE1']} {fila['MASK_INTERFACE_DEVICE1']}
        ip ospf 1 area 0
        no shutdown
        #
        """
        if fila['INTERFACE_DEVICE2'] != "-":
            comandos_configuracion_ospf_parte2 = f"""
            interface {fila['INTERFACE_DEVICE2']}
            ip address {fila['IP_INTERFACE_DEVICE2']} {fila['MASK_INTERFACE_DEVICE2']}
            ip ospf 1 area 0
            no shutdown
        #
        """
        else:
            comandos_configuracion_ospf_parte2 = ""

        configuracion_final_ospf = comandos_configuracion_ospf_parte1 + '\n' + comandos_configuracion_ospf_parte2

        lista_de_resultados = []
        resultado_config = conector.send_config_set(configuracion_final_ospf.splitlines())
        resultado_guardado = conector.save_config()

        print(f"Se ha ejecutado la configuracion de ospf en el equipo {fila['NE']}")

        lista_de_resultados.append(resultado_config)
        lista_de_resultados.append(resultado_guardado)

        with open(f"/Users/akam/Documents/python_labs/portafolio/laboratorio_python/lab02/log/{fila['NE']}.txt", "w") as archivo:
            archivo.write('\n'.join(lista_de_resultados))

        print(f"Se ha generado el log de configuracion del equipo {fila['NE']}")

        conector.disconnect()

    except Exception as e:
        print(f"Se tiene problemas en el equipo {fila['NE']} - {e}")


df = pandas.read_excel("/Users/akam/Documents/python_labs/portafolio/laboratorio_python/lab02/ip_planning.xlsx", sheet_name="devices")

# Versión secuencial (comentada)
# for indice, fila in df.iterrows():
#     configurar_ospf(fila)

# Versión con Threading (paralela)
lista_de_hilos = []

for indice, fila in df.iterrows():
    hilo = threading.Thread(target=configurar_ospf, args=(fila,))
    lista_de_hilos.append(hilo)
    hilo.start()

for hilo in lista_de_hilos:
    hilo.join()
```

---

## 10. Cómo usar este laboratorio

### Requisitos

- Python 3.10 o superior instalado
- Librerías:
  ```bash
  pip install netmiko pandas openpyxl
  ```
- GNS3 o Eve-NG con la topología armada (o routers físicos)
- Acceso SSH habilitado en los dispositivos
- Archivo `ip_planning.xlsx` en la misma carpeta que el script

### Pasos para ejecutar

1. Prepara el archivo Excel `ip_planning.xlsx` con tus dispositivos (columnas mínimas: IP y PORT).
2. Asegúrate de que los routers tengan la configuración SSH aplicada.
3. Ejecuta el script de forma secuencial primero para probar.
4. Una vez verificado, usa la versión con `threading` para mayor velocidad.
5. Revisa los archivos generados en la carpeta `log/`.

> **Recomendación:** Para entornos reales, considera mover las credenciales a variables de entorno o un archivo `.env` por seguridad.

---

## 11. Únete a la comunidad

Este laboratorio forma parte de mi contenido educativo sobre **automatización de redes**. El objetivo es compartir conocimiento práctico para que más personas puedan automatizar tareas repetitivas y escalar su trabajo en redes.

¡Gracias por leer y por formar parte de esta comunidad de networking y automatización!

---

**Alex Kam**  
Networking | Python Automation | GNS3 Labs  
ft.alex.kam@gmail.com | San Isidro, Lima, Perú

### Conecta conmigo

- 🐙 **GitHub**: [github.com/alexkam-tech/Portafolio](https://github.com/alexkam-tech/Portafolio)
- ▶️ **YouTube**: [youtube.com/@Akam-Labs](https://youtube.com/@Akam-Labs)
- 🔗 **LinkedIn**: [linkedin.com/in/alexkamgoñe](https://linkedin.com/in/alexkamgoñe)

---

*Si este laboratorio te sirvió, déjame un ⭐ en el repositorio y suscríbete al canal.*
