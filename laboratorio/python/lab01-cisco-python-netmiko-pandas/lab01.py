import netmiko
import pandas
import threading

def obtener_informacion(fila):
    try:
        usuario = "akam"
        contra = "akam@123"

        datos_de_conexion = {
            "device_type" : "cisco_ios",
            "username" : usuario,
            "password" : contra,
            "host" : fila['IP'],
            "port" : fila['PUERTO']
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
            resultado = conector.send_command(comando,strip_command=False,strip_prompt=False)
            lista_de_resultados.append("\n")
            lista_de_resultados.append("="*70)
            lista_de_resultados.append(resultado)
            lista_de_resultados.append("\n")
            lista_de_resultados.append("="*70)

        print(f"Se ha ejecutado los comandos en el equipo {fila['HOSTNAME']}")

        with open(f"/Users/akam/Documents/python_labs/portafolio/laboratorio_python/lab01/logs/{fila['HOSTNAME']}.txt","w") as archivo:
            cli = "\n".join(lista_de_resultados)
            archivo.write(cli)

        print(f"Se ha generado el archivo con la informacion de  {fila['HOSTNAME']}")

        conector.disconnect()
        print(f"Desconectado del equipo -  {fila['HOSTNAME']}")


    except Exception as e:
        print(f"Se tiene un error en el equipo {fila['HOSTNAME']} - error: {e}")

df = pandas.read_excel("/Users/akam/Documents/python_labs/portafolio/laboratorio_python/lab01/ip_planning.xlsx",sheet_name="Hoja1")


# for _,fila in df.iterrows():
#     obtener_informacion(fila)

lista_de_hilos = []

for _,fila in df.iterrows():
    hilo = threading.Thread(target=obtener_informacion,args=(fila,))
    lista_de_hilos.append(hilo)
    hilo.start()

for hilo in lista_de_hilos:
    hilo.join()
