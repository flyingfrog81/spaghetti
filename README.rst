=========
SPAGHETTI
=========
----------------------------
Numpy arrays over websockets
----------------------------

L'idea è quella di avere un server HTTP che consenta ad un utente di avere una
rappresentazione grafica di un particolare dato tramite una pagina WEB.
L'utilizzo più semplice e immediato è quello di un plot bidimensionale, ad
esempio di una serie temporale. 

Il flusso dei dati è una roba del genere: 

1. Un software produce dei dati. Immaginiamo che i dati possano essere degli
   array numpy.
2. Tramite un semplice decoratore si aggiunge alla funzione che produce dati
   la capacità di spedire i dati ad un server.
3. Il server raccoglie i dati e li serve tramite un' interfaccia web.


DIPENDENZE 
==========

* tornado
* numpy
* zmq
* pyzmq
* zmqnumpy

UTILIZZO
========

Per far partire il server::

$ spaghetti --logging=debug

A questo punto dobbiamo creare le "stanze" per i dati che vogliamo spedire,
possiamo farlo visitando questi url con il browser: 

* http://127.0.0.1:8765/create/randomproducer/
* http://127.0.0.1:8765/create/gaussproducer/
* http://127.0.0.1:8765/create/windowproducer/

Per produrre i dati da inviare al server::

$ cd test 
$ python producer.py

A questo punto accedendo alla [root](http://127.0.0.1:8765/rooms/) dovresti
avere disponibili i plot generati.

HTML5
-----
Tutto funziona solo grazie ad html5 ed in particoalre a WebSocket e TypedArray
che ho messo assieme per creare una classe TypedWebSocket che trovi in
static/js/ 
