/*
 * Experiment with detecting potential race conditions.
 *
 * In Promela, each increment is atomic, so a race on x++ cannot
 * be detected by modeling the increment alone.
 *
 * threads_in_critical_section tracks how many processes are executing the region.
 * The assertion fails if more than one process can be there
 * simultaneously.
 *
 * Try adding sem_wait(mutex) before threads_in_critical_section++ and sem_post(mutex)
 * after threads_in_critical_section--. The assertion should no longer fail because
 * mutual exclusion is now guaranteed.
 */

byte shared_variable = 0;
byte threads_in_critical_section = 0;

active [2] proctype P() {
  do
  :: 
    threads_in_critical_section++;
    assert(threads_in_critical_section == 1);
    
    /* critical section */
    shared_variable++;

    threads_in_critical_section--;
  od
}
