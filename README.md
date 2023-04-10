# INFORME REDES LAB2 

## Preguntas 

### ¿Qué estrategias existen para poder implementar este mismo servidor pero con capacidad de atender múltiples clientes simultáneamente?

Encontramos que para implementar este tipo de funcionalidad tenemos 2 opciones

#### 1. Utilizar la libreria 'threading' de python
- Cada vez que se acepte un cliente, se abre un nuevo hilo el cual se encarga de las instrucciones y el hilo principal vuelve, para aceptar nuevos clientes.
  
#### 2. Utilizar la libreria 'multiprocessing' de python  
- La idea es la misma que con los hilos, pero con otra libreria


### ¿Qué diferencia hay si se corre el servidor desde la IP “localhost”, “127.0.0.1” o la ip “0.0.0.0”?

Las direcciones IP 127.0.0.1 y 0.0.0.0 son similares en el sentido de que estan reservadas. No identifican a un dispositivo en particular en una red como otras direcciones IP, en cambio, se definen para uso especial.

127.0.0.1 se define como la direccion IP de loopback. El mecanismo del loopback puede ser utilizado para correr una red de servicio en un host local sin necesidad de una interfaz de red fisica. Esto lo hace no accesible para otros dispositivos en la misma red. 

localhost es simplemente el nombre de host de 127.0.0.1, en IPv4.

0.0.0.0 puede tener distintos significados segun el contexto. En este caso, puede representar cualquier direccion IP en una misma red, esto significa que setear un servidor a escuchar en la IP 0.0.0.0 hace que acepte pedidos de cualquier dispositivo en esa red.

Al ejecutar el servidor en una computadora del laboratorio, conectarse como cliente desde otra solo es posible si el servidor se ejecuta desde 0.0.0.0, pues esta direccion es capaz de escuchar conexiones entrantes desde cualquier dispositivo en la red, al contrario de 127.0.0.1/localhost, que solo es accesible para el dispositivo desde el cual se ejecuta el servidor.


## Decisiones de diseño tomadas

### Estructura del servidor

El servidor esta armado sobre una clase, en la cual se debe llamar al metodo 'serve' para iniciarlo. Una vez iniciado, el este mismo espera a que algun cliente establezca una conexion, al hacerlo, se crea un hilo el cual se encarga de manejar los pedidos de su respectivo cliente. Por ultimo, el servidor vuelve al estado de espera, libre para aceptar algun otro cliente.
Por ahora decidimos limitar la cantidad de conexiones a 5 a la vez.


### Manejo de pedidos

Dentro del metodo serve(), se crea un objeto del tipo 'connection' y se lo llama dentro de un nuevo hilo con el metodo handle(), el cual se encarga del manejo de pedidos.

Para el manejo de pedidos, el metodo handle() recibe un comando, y luego de revisar posibles errores ya sean accidentales o malintecionados, llama a parse_command() con una lista la cual contiene el comando como primer elemento y los argumentos del comando (en caso de tenerlos) en los siguientes elementos. Por ultimo, el parser se encarga llamar al respectivo comando y ejecutarlo.


## Dificultades con las que nos encontramos


### server-test.py

La mayoria de las dificultades que tuvimos, fueron principalmente con los tests, como que al probar casos similares a los tests utilizando telnet, nos funcinaba bien, pero los tests seguian tirando errores.