#define sem_wait(s) atomic { s > 0 -> s-- }
#define sem_post(s) s++

#define N 4

byte gate      = 1;
byte equipo_ok = 1;
byte vacia     = 1;
byte mutex     = 1;

byte n         = 0;
bit inside     = 0;

proctype paciente() {
  do
  :: sem_wait(gate);
     sem_post(gate);

     /* entra() */

     sem_wait(mutex);
     if
     :: (n == 0 && inside == 0) ->
        sem_wait(equipo_ok);
        sem_wait(vacia)
     :: n == N ->
       n++;
       sem_post(equipo_ok)
     :: else ->
       n++;
       skip
     fi;
     sem_post(mutex);

     /* recibeAten() */

     sem_wait(mutex);
     if
     :: (n == (N + 1) && inside == 0) ->
        sem_wait(equipo_ok)
     :: (n == 1) ->
        n--
        if
        :: inside == 0 ->
           sem_post(equipo_ok)
        :: else ->
           skip
        fi;
        sem_post(vacia)
     :: else ->
        n--
     fi;
     sem_post(mutex);

     /* sale() */
  od
}

proctype equipo() {
  int aux;

  do
  :: sem_wait(equipo_ok);
     sem_wait(gate);

     /* entra() */

     sem_wait(mutex);
     inside = 1;
     aux = n;
     sem_post(mutex);

     if
     :: (aux > 0) ->
          sem_wait(vacia);
          /* limpProf() */
     :: else ->
          /* limpSup() */
          skip
     fi;

     sem_wait(mutex);
     inside = 0;
     sem_post(mutex);

     sem_post(gate);
     sem_post(equipo_ok);

     /* sale() */
  od
}

init {
    run paciente();
    run equipo();
}
