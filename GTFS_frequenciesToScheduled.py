from collections import defaultdict
import pandas as pd
import datetime
import zipfile

import argparse
import glob
import os
import sys
import errno

# add path so we can use function through command line
new_path = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.append(new_path)

#funcion auxiliar para el escritor del codigo, no implica nada al proceso
def extraercolumnas(df,var,namedf):
        
    print("for {} in range(len({})):".format(var,namedf))
    for i in df.columns:
        print("    {}={}.iloc[{}]['{}']".format(i,namedf,var,i))
        
#sumar segundos a hora en tring
def sumarsegundostostring(stringtime,segundos,formato):
    return datetime.datetime.strptime(stringtime, formato)+datetime.timedelta(seconds=segundos)

#sumar segundos a hora en tring
def sumarsegundostodatetime(dtime,segundos):
    return dtime+datetime.timedelta(seconds=segundos)


def main(argv):
    # Arguments and description
    
    parser = argparse.ArgumentParser(description='Cambiar GTFS definido como frecuencia a uno definido por itinerario')
    
    parser.add_argument('GTFS_INPUT', action="store",help='Ruta de GTFS INPUT definido como frecuencia. e.g. \path\to\GTFS_INPUT.zip')
    #parser.add_argument('GTFS_OUTPUT', action="store",help='Ruta de GTFS OUTPUT definido como frecuencia. e.g. \path\to\GTFS_INPUT.zip')
 
    args = parser.parse_args(argv[1:])
    
    # Give names to arguments
    INPUT = args.GTFS_INPUT
    route=INPUT[:INPUT.rfind("\\")]
    
    OUTPUT=route+'\OUTPUT_SCHEDULED'
    new_route=OUTPUT
    
    try:
        os.mkdir(OUTPUT)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
        
    #extraemos archivos de gtfs.zip input
    z = zipfile.ZipFile(INPUT)
    z.extractall(route)
    z.close()
    
    #procesamos archivos INPUT
    agency=pd.read_csv(route+"\\agency.txt",sep=",")
    calendar=pd.read_csv(route+"\\calendar.txt",sep=",") 
    calendar_dates=pd.read_csv(route+"\\calendar_dates.txt",sep=",") 
    feed_info=pd.read_csv(route+"\\feed_info.txt",sep=",") 
    frequencies=pd.read_csv(route+"\\frequencies.txt",sep=",") 
    routes=pd.read_csv(route+"\\routes.txt",sep=",") 
    shapes=pd.read_csv(route+"\\shapes.txt",sep=",") 
    stop_times=pd.read_csv(route+"\\stop_times.txt",sep=",") 
    stops=pd.read_csv(route+"\\stops.txt",sep=",") 
    trips=pd.read_csv(route+"\\trips.txt",sep=",")
     
    #generar diccionario de frequencies
    print("Generando diccionarios")
     
    dfrequencies=defaultdict(list)
     
    for j in range(len(frequencies)):
        #print(j)
        trip_id=frequencies.iloc[j]['trip_id']
        start_time=frequencies.iloc[j]['start_time']
        end_time=frequencies.iloc[j]['end_time']
        headway_secs=frequencies.iloc[j]['headway_secs']
        exact_times=frequencies.iloc[j]['exact_times']
        
        dfrequencies[trip_id].append((start_time,end_time,headway_secs,exact_times))
    
    dstop_times=defaultdict(list)
    
    for i in range(len(stop_times)):
        
        #print(i)
        trip_id=stop_times.iloc[i]['trip_id']
        arrival_time=stop_times.iloc[i]['arrival_time']
        departure_time=stop_times.iloc[i]['departure_time']
        stop_id=stop_times.iloc[i]['stop_id']
        stop_sequence=stop_times.iloc[i]['stop_sequence']
        
        dstop_times[trip_id].append((arrival_time,departure_time,stop_id,stop_sequence))
        
    newtrips_route_id=[]
    newtrips_service_id=[]
    newtrips_trip_id=[]
    newtrips_trip_headsign=[]
    newtrips_direction_id=[]
    newtrips_shape_id=[]
    
    newstop_times_trip_id=[]
    newstop_times_arrival_time=[]
    newstop_times_departure_time=[]
    newstop_times_stop_id=[]
    newstop_times_stop_sequence=[]
    
    print("Cambiando frecuencia a itinerario ")
    #recorremos todos los viajes, si estan definidos por frecuencias hay que duplicra todos los viajes 
    #nuevo trip id, si no esta definido por frecuencia se mantiene 
    #control simultaneo de stop_times, que no pase la hora definida por frequencies y fin del dia 
    for i in range(len(trips)):
        #print(i)
        route_id=trips.iloc[i]["route_id"]
        service_id=trips.iloc[i]["service_id"]
        trip_id=trips.iloc[i]["trip_id"]
        trip_headsign=trips.iloc[i]["trip_headsign"]
        direction_id=trips.iloc[i]["direction_id"]
        shape_id=trips.iloc[i]["shape_id"]
        
        #si esta definido por frecuencia el viaje
        if(dfrequencies.get(trip_id)):
            #recorremos los horarios que esta definido por frecuenia
            nhorarios=0
            for start_time,end_time,headway_secs,exact_times in dfrequencies[(trip_id)]:
                nhorarios=nhorarios+1
                start=datetime.datetime.strptime(start_time, '%H:%M:%S')
                
                if(end_time=='24:00:00'):
                    end_time='23:59:59'
                
                end=datetime.datetime.strptime(end_time, '%H:%M:%S')
                
            
                #vemos cuantas veces se puede repetir el stoptimes y duplicamos trips
                nveces=0
                s=start
                while(True):
                    if(s<end):
                        nveces=nveces+1
                        s=sumarsegundostodatetime(s,int(headway_secs))
                        
                        newtrips_route_id.append(route_id)
                        newtrips_service_id.append(service_id)
                        newtrips_trip_id.append("{}_{}_{}".format(trip_id,nhorarios,nveces))
                        newtrips_trip_headsign.append(trip_headsign)
                        newtrips_direction_id.append(direction_id)
                        newtrips_shape_id.append(shape_id)
                        
                        
                        #cadatiempo del stop times hay que repetirlo y cambiar el id
                        st=dstop_times[trip_id]
                        for k in range(len(st)):
                            arrival_time=st[k][0]
                            departure_time=st[k][1]
                            stop_id=st[k][2]
                            stop_sequence=st[k][3]
    
                            timearrival=datetime.datetime.strptime(arrival_time, '%H:%M:%S')   
                            timedeparture=datetime.datetime.strptime(departure_time, '%H:%M:%S')
                            inicio=datetime.datetime.strptime("00:00:00", '%H:%M:%S')  
    
                            arrivalsegundos=(timearrival-inicio).seconds
                            departuresegundos=(timedeparture-inicio).seconds
    
    
                            newstop_times_trip_id.append("{}_{}_{}".format(trip_id,nhorarios,nveces))
                            newstop_times_arrival_time.append(sumarsegundostodatetime(start,arrivalsegundos+int(headway_secs)*(nveces-1)).strftime('%H:%M:%S'))
                            newstop_times_departure_time.append(sumarsegundostodatetime(start,departuresegundos+int(headway_secs)*(nveces-1)).strftime('%H:%M:%S'))
                            newstop_times_stop_id.append(stop_id)
                            newstop_times_stop_sequence.append(stop_sequence)
                                
                    else:
                        break;
                                
                #while(True):
                    #no cambiamos de dia ni llegamos al end
                    #if(dia==sumarsegundostodatetime(horaultimaparada,headway_secs).day):
     
        #si no esta definido por frecuencia se mantiene trip y stoptimes asociado
        else:
            
            #agregamos trip no definido por frecuencia
            newtrips_route_id.append(route_id)
            newtrips_service_id.append(service_id)
            newtrips_trip_id.append(trip_id)
            newtrips_trip_headsign.append(trip_headsign)
            newtrips_direction_id.append(direction_id)
            newtrips_shape_id.append(shape_id)
            
            #agregamos stop_times no definidos por frecuencia asociado al trip_id
            if(dstop_times.get(trip_id)):
                for arrival_time,departure_time,stop_id,stop_sequence in dstop_times[trip_id]:
                    newstop_times_trip_id.append(trip_id)
                    newstop_times_arrival_time.append(arrival_time)
                    newstop_times_departure_time.append(departure_time)
                    newstop_times_stop_id.append(stop_id)
                    newstop_times_stop_sequence.append(stop_sequence)
    
    print("Generando archivos")
    
    new_trips=pd.DataFrame({"route_id":newtrips_route_id,"service_id":newtrips_service_id,"trip_id":newtrips_trip_id,"trip_headsign":newtrips_trip_headsign,"direction_id":newtrips_direction_id,"shape_id":newtrips_shape_id})
    new_stop_times=pd.DataFrame({"trip_id":newstop_times_trip_id,"arrival_time":newstop_times_arrival_time,"departure_time":newstop_times_departure_time,"stop_id":newstop_times_stop_id,"stop_sequence":newstop_times_stop_sequence})
    
    new_stop_times = new_stop_times.sort_values(['trip_id','stop_sequence'],ascending=[True,True])
    
    #stop_times 
    d=defaultdict(list)
    for i in stop_times.columns:
        #print(i)
        d[i]=new_stop_times[i]
    end_stop_times =pd.DataFrame()
    for i in stop_times.columns:
        end_stop_times [i]=d[i]
    end_stop_times.to_csv(new_route+"\\stop_times.txt", header=True, index=None, sep=',')
    
    #trips
    d=defaultdict(list)
    for i in trips.columns:
        #print(i)
        d[i]=new_trips[i]
    end_trips =pd.DataFrame()
    for i in trips.columns:
        end_trips[i]=d[i]
    end_trips.to_csv(new_route+"\\trips.txt", header=True, index=None, sep=',')
    
    
    agency.to_csv(new_route+"\\agency.txt", header=True, index=None, sep=',')
    calendar.to_csv(new_route+"\\calendar.txt", header=True, index=None, sep=',') 
    calendar_dates.to_csv(new_route+"\\calendar_dates.txt", header=True, index=None, sep=',') 
    feed_info.to_csv(new_route+"\\feed_info.txt", header=True, index=None, sep=',') 
    routes.to_csv(new_route+"\\routes.txt", header=True, index=None, sep=',') 
    shapes.to_csv(new_route+"\\shapes.txt", header=True, index=None, sep=',') 
    stops.to_csv(new_route+"\\stops.txt", header=True, index=None, sep=',')
    

    
    #comprimimos archivos en zip
    ze = zipfile.ZipFile(OUTPUT+'\\GTFS_scheduled.zip', 'w')
 
    for folder, subfolders, files in os.walk(OUTPUT):
        for file in files:
            ze.write(os.path.join(folder, file), os.path.relpath(os.path.join(folder,file), OUTPUT), compress_type = zipfile.ZIP_DEFLATED)
     
    ze.close()
    
    
    print("Fin, puede encontrar su nuevo GTFS en {}".format(OUTPUT))
    

if __name__ == "__main__":
    #print(sys.argv)
    sys.exit(main(sys.argv))

