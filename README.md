# GTFS
Herramientas para procesar GTFS

#GTFS_frequenciesToScheduled

Comando que permite cambiar un GTFS definido mediante frecuencias (existencia de frequencies.txt) a un GTFS definido por itinerario. Aquellos trips definidos por frecuencia son multiplicados en el stop_times.txt y en el trips.txt. En caso de que el GTFS definido por frecuencia contenga viajes definidos por itinerario son conservados sin cambios, solo se adicional viajes por aquellos definidos por frecuencia.



