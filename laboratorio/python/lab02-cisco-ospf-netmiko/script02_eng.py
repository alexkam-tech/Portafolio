import netmiko
import pandas
import threading

def configure_ospf(row):
    try:
        connection_data = {
            "device_type" : "cisco_ios",
            "ip" : row['IP'],
            "port" : row['PORT'],
            "username" : "akam",
            "password" : "akam@123",
            "timeout" : 10
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

        with open(f"/Users/akam/Documents/python_labs/portafolio/laboratorio_python/lab02/log/{row['NE']}.txt","w") as file:
            file.write('\n'.join(list_for_results))
        
        print(f"Configuration log is generated for device {row['NE']}")

        connector.disconnect()

    except Exception as e:
        print(f"We have an error on the device {row['NE']} - {e}")


df = pandas.read_excel("/Users/akam/Documents/python_labs/portafolio/laboratorio_python/lab02/ip_planning.xlsx",sheet_name="devices")

# for index,row in df.iterrows():
#     configure_ospf(row)

list_of_threads = []

for index, row in df.iterrows():
    thread = threading.Thread(target=configure_ospf,args=(row,))
    list_of_threads.append(thread)
    thread.start()

for thread in list_of_threads:
    thread.join()
    