# SPIN for Synchronization Exercises

A Bash script that verifies synchronization exercises modeled in Promela using [SPIN](https://spinroot.com/). It runs the verification, searches for the shortest error trail, and replays the trail to help identify problems such as deadlocks.

## Dependencies

- [SPIN](https://spinroot.com/)
- GCC

## Usage

Place your Promela model in a `.pml` file, for example `hospital.pml`, and run:

```bash
./verify.sh hospital.pml
```

The script generates the verifier using `spin -a`, compiles it with GCC, and runs the verification. If an error trail is found, it replays it with global and local variable values and statement-by-statement execution output.
