import netmiko
import pandas
import threading

def configurar_ospf(fila):
    try:
        datos_conexion = {
            "device_type" : "cisco_ios",
            "ip" : fila['IP'],
            "port" : fila['PORT'],
            "username" : "akam",
            "password" : "akam@123",
            "timeout" : 10
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

        with open(f"/Users/akam/Documents/python_labs/portafolio/laboratorio_python/lab02/log/{fila['NE']}.txt","w") as archivo:
            archivo.write('\n'.join(lista_de_resultados))
        print(f"Se ha generado el log de configuracion del equipo {fila['NE']}")

        conector.disconnect()

    except Exception as e:
        print(f"Se tiene problemas en el equipo {fila['NE']} - {e}")

df = pandas.read_excel("/Users/akam/Documents/python_labs/portafolio/laboratorio_python/lab02/ip_planning.xlsx",sheet_name="devices")

# for indice,fila in df.iterrows():
#     configurar_ospf(fila)

lista_de_hilos = []

for indice,fila in df.iterrows():
    hilo = threading.Thread(target=configurar_ospf,args=(fila,))
    lista_de_hilos.append(hilo)
    hilo.start()

for hilo in lista_de_hilos:
    hilo.join()