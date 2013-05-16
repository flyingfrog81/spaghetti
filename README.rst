SPAGHETTI
=========
L'idea è quella di avere un server HTTP che consenta ad un utente di avere una
rappresentazione grafica di un particolare dato tramite una pagina WEB.
L'utilizzo più semplice e immediato è quello di un plot bidimensionale, ad
esempio di una serie temporale. 

Il flusso dei dati è una roba del genere: 
    1. Un software produce dei dati. Immaginiamo che i dati possano essere degli
    array numpy.
    2. Tramite un semplice decoratore si aggiunge alla funzione che produce dati
    la capacità di spedire i dati ad un server.
    3. Il server raccoglie i dati e li serve tramite un interfaccia web.

DIPENDENZE 
==========
    * tornado
    * numpy
    * zmq
    * pyzmq
    * zmqnumpy

PYTHON 
------

Tutti installabili via pypi, zmqnumpy è un pacchetto che ho fatto io spero non
dia problemi, ma nel caso puoi chiedere a me. 
La scelta di "tornado" come server è un po' arbitraria ma è dettata dai seguenti
motivi: 
    1. il codice è comprensibile ed è facile metterci mano
    2. Per questo progetto servivano essenzialmente HTTP e WEBSOCKET, e tornado
    le serve out-of-the-box , tra l'altro con una documentazione decente.
Ciò non significa che sia la scelta migliore.

ZMQ invece è una manna dal cielo, qui sono più convinto della bontà della
soluzione.

JAVASCRIPT
----------

AL momento ho fatto il plot utilizzando la libreria [flot](http://www.flotcharts.org/) 
è già nel tar. Forse ora come ora è un po' datata, dovessi ripartire guarderei
bene [d3](http://d3js.org/)

UTILIZZO
========

Per far partire il server:
$ python server.py --logging=debug

A questo punto dobbiamo creare le "stanze" per i dati che vogliamo spedire,
possiamo farlo visitando questi url con il browser: 
    * http://127.0.0.1:8765/create/randomproducer/
    * http://127.0.0.1:8765/create/gaussproducer/
    * http://127.0.0.1:8765/create/windowproducer/

Per produrre i dati da inviare al server: 
$ python producer.py

A questo punto accedendo alla [root](http://127.0.0.1:8765/rooms/) dovresti
avere disponibili i plot generati.
Guarda bene nei template html, mi sa che ci siano hardcoded degli indirizzi IP
che vanno cambiati perchè tutto funzioni, colpa mia ;) 

HTML5
-----
Tutto funziona solo grazie ad html5 ed in particoalre a WebSocket e TypedArray
che ho messo assieme per creare una classe TypedWebSocket che trovi in
static/js/ . 
Anche flot credo utilizzi canvas e metodi di disegno provenienti da html5.
Uno dei limiti grossi è proprio questo, anche perchè molti proxy e firewall
ancora non gestiscono websocket. 
