# GTFS
Herramientas para procesar GTFS

# GTFS_frequenciesToScheduled

Comando que permite cambiar un GTFS definido mediante frecuencias (existencia de frequencies.txt) a un GTFS definido por itinerario. Aquellos trips definidos por frecuencia son repetidos en el stop_times.txt y en el trips.txt con un trip_id creado. En caso de que el GTFS definido por frecuencia contenga viajes definidos por itinerario son conservados sin cambios, solo se adicionan trips para aquellos definidos por frecuencia.

## Ejecución

La ejecución es mediante consola de comando siguiendo la siguiente estructura:

```
python3 GTFS_frequenciesToScheduled.py \path\to\GTFS_INPUT.zip
```


