# Resultados de los torneos de bots de ChompChamps

Este repositorio contiene los registros de las partidas y los resultados de los torneos de bots de ChompChamps.

Cada torneo evalúa los bots en tres modalidades de competencia:

- **Single Player:** Los bots compiten individualmente.
- **1 vs 1:** Dos bots compiten entre sí.
- **Free For All (FFA):** Varios bots compiten en una misma partida.

El repositorio contiene los registros de todas las partidas, permitiendo reproducirlas y observar cómo se desempeñaron los bots durante los torneos.

## Reproducción de partidas

Cada partida se almacena como una grabación de terminal generada mediante el comando `script`. Estas grabaciones capturan la salida de la vista del juego de ChompChamps durante el torneo original.

Para reproducir una partida, ejecutar el siguiente comando:

```bash
perl -pe 'BEGIN {$|=1} if (/\e\[H/) { select undef,undef,undef,0.003 }' <match-file>
```

Reemplazar `<match-file>` por la ruta del archivo de la partida que se desea reproducir.

El comando introduce una pequeña pausa entre las actualizaciones de pantalla, permitiendo seguir el desarrollo de la partida tal como ocurrió originalmente. El valor del retardo (`0.003`, expresado en segundos) se puede modificar para ajustar la velocidad de reproducción.

**Nota:** Estos registros permiten reproducir visualmente las partidas, pero no incluyen los binarios originales de los bots. Por lo tanto, no es posible volver a ejecutar los bots ni reproducir los torneos desde cero.

## Organización de los torneos

El repositorio también documenta los scripts y comandos utilizados para organizar los torneos, ejecutar las partidas, recopilar sus resultados, verificar errores de ejecución y calcular los rankings.

Se trata de notas de trabajo y fragmentos de comandos, no de un framework ejecutable de forma independiente. Algunas variables y parámetros se modifican manualmente a medida que avanza el torneo.

A continuación se detallan los scripts y comandos utilizados.

## Historial de torneos

En este repositorio se conservan los resultados y registros de las partidas de torneos anteriores. Se irán incorporando nuevas ediciones a medida que se realicen.

Cada edición incluye los registros de sus respectivas partidas, manteniendo un historial de las competencias.