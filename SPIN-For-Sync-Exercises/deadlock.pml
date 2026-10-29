/*
 * Classic deadlock caused by inconsistent lock ordering.
 *
 * P1 acquires A before B, while P2 acquires B before A.
 * Try running SPIN and inspecting the error trail.
 * What happens if both processes acquire the locks in the same order?
 */

#define sem_wait(s) atomic { s>0 -> s-- }
#define sem_post(s) s++

byte A = 1;
byte B = 1;

active proctype P1() {
  sem_wait(A);
  sem_wait(B);
  /* critical section */
  sem_post(B);
  sem_post(A);
}

active proctype P2() {
  sem_wait(B);
  sem_wait(A);
  /* critical section */
  sem_post(A);
  sem_post(B);
}
