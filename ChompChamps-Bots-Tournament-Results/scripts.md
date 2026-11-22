# Preparación

## Crear links symbólicos

```bash
# Crear links a cada vista y player indicada por cada grupo con el formato V_G# y P_G# donde # es el numero de grupo.
# V_G# es el link a la vista y P_G# es el link al player.
# Estos links se crean dentro de la carpeta de cada grupo
```

## Instalar dependencias

```bash
apt update && apt-get install libncurses-dev bc dos2unix
```

## Chequear md5sum del master

```bash
md5sum ChompChamps
```

## Función auxiliar

```bash
cleanup() {
  killall -9 -qr '^(V_|R_|P_|view)'
  rm -f /dev/shm/*
  tput reset
}
```

## Mostrar grupos en ejecución y errores en otras terminales

```bash
rm -f currentGroup err
tail -F currentGroup 2>/dev/null
tail -F err 2>/dev/null
```

# Torneo de vistas

## Listar vistas consideradas para cada grupo

```bash
ls -l */V_G* | cut -d ' ' -f 9- | sort -V

# Salida de ejemplo
# 1/V_G1 -> tp1-so/bin/view
# 2/V_G2 -> TP1-SO-2026-2C/view
# 3/V_G3 -> TP1_SISTEMAS_OPERATIVOS/bin/view
# ...
```

## Definir grupos

```bash
numberOfGroups=24
seq 1 $numberOfGroups | sort -R | xargs -n 4 | tee FaseGrupos

# Salida de ejemplo
# 24 12 16 23
# 13 8 20 19
# 17 14 18 9
# 3 5 6 10
# 1 15 4 11
# 2 7 22 21
```

## Presentar vistas

```bash
groups="$(sed -n '1p' FaseGrupos)"
echo $groups

defaultParams="-w 10 -h 10 -d 40 -t 3 -p R_*"
echo > currentGroup;
echo > err
while true; do
  for g in $groups; do
    cleanup;
    echo "########## GRUPO $g ##########" | tee -a currentGroup err;
    sleep 2; 
    ./ChompChamps $defaultParams -v $g/V_G${g} 2>>err; sleep 2;
#    ./ChompChamps ${defaultParams//-w 10/-w 15} -v $g/V_G${g} 2>>err; sleep 2;
#    ./ChompChamps ${defaultParams//-h 10/-h 15} -v $g/V_G${g} 2>>err; sleep 2;
  done;
done
```

## Formato de competencia por grupos

```
2 ganadores por grupo

Grupo A -> 1A 2A 
Grupo B -> 1B 2B
Grupo C -> 1C 2B
Grupo D -> 1D 2D
Grupo E -> 1E 2E
Grupo F -> 1F 2F
```

## Formato de eliminación directa

```
1A 2F -> AF 
1B 2A -> BA
1C 2B -> CB
1D 2C -> DC
1E 2D -> ED
1F 2E -> FE 

AF DC -> AFDC
BA ED -> BAED
CB FE -> CBFE

AFDC BAED CBFE -> Top 3
```

# Torneo de bots

## Listar bots considerados

```bash
ls -l */P_G* | cut -d ' ' -f 9- | sort -V

# Salida de ejemplo
# 1/P_G1 -> tp1-so/bin/player
# 2/P_G2 -> TP1-SO-2026-2C/player
# 3/P_G3 -> TP1_SISTEMAS_OPERATIVOS/bin/player
# ...
```

## Preparar torneo

```bash
# Mostrar errores en otra terminal
rm -f err
tail -F err 2>/dev/null

# Seed
seed=$(echo $RANDOM); echo $seed

# Single player
defaultParams="-v view -w 20 -h 30 -d 5 -t 3 -s $seed"
for g in $(seq 1 $numberOfGroups); do
  echo "echo \"Single Player $g\" >> err"
  echo "script -q -c \"./ChompChamps $defaultParams -p $g/P_G${g} 2>>err\" logs/log-SP-G${g}-$(date +"%T.%3N")";
  echo "read -p \"Presiona una tecla para continuar...\";"
  sleep 0.1;
done > matches-SP.sh

# 1 VS 1
defaultParams="-v view -w 15 -h 20 -d 5 -t 3"
for r in {1..4}; do
  seq 1 $numberOfGroups | sort -R | xargs -n 2 | while read g1 g2; do
    echo "echo \"1vs1 $g1 $g2\" >> err"
    echo "script -q -c \"./ChompChamps $defaultParams -p $g1/P_G${g1} $g2/P_G${g2} 2>>err\" logs/log-1VS1-G${g1}-G${g2}-$(date +"%T.%3N")";
    echo "read -p \"Presiona una tecla para continuar...\";"
    sleep 0.1;
  done;
done > matches-1vs1.sh

# FFA
defaultParams="-v view -w 20 -h 30 -d 5 -t 3"
for r in {1..4}; do
  seq 1 $numberOfGroups | sort -R | xargs -n 4 | while read g1 g2 g3 g4; do
    echo "echo \"1vs1 $g1 $g2 $g3 $g4\" >> err"
    echo "script -q -c \"./ChompChamps $defaultParams -p $g1/P_G${g1} $g2/P_G${g2} $g3/P_G${g3} $g4/P_G${g4} 2>>err\" logs/log-FFA-G${g1}-G${g2}-G${g3}-G${g4}-$(date +"%T.%3N")";
    echo "read -p \"Presiona una tecla para continuar...\";"
    sleep 0.1;
  done;
done > matches-FFA.sh

chmod +x *.sh

# Resultados
mkdir -p logs
rm -f logs/*

# Iniciar torneo
./matches-SP.sh
./matches-1vs1.sh
./matches-FFA.sh

# Revisar errores y repetir la que haga falta
vim err
grep "EXIT_CODE" logs/* | grep -v "=\"0\""
```

## Armar rankings

```bash
dos2unix -f logs/*

for modo in -SP -1VS1 -FFA -; do
  case $modo in
    "-SP")
      header="Single Player";
      lines=1;;
    "-1VS1")
      header="1 vs 1";
      lines=4;;
    "-FFA")
      header="FFA";
      lines=4;;
    "-")
      header="Global";
      lines=9;;
  esac
  
  echo
  echo " #### Ranking $header #### ";

  for g in $(seq 1 $numberOfGroups); do
    if [[ $g = "1" ]]; then echo "Score/Valid/Invalid/Grupo"; fi
    echo "$(grep "Player P_G$g " logs/log$modo* | sed 's:.*of ::g;s: / :,:g' | tr ',' '\n' | pr -${lines}ts+ | bc | xargs | sed 's: :/:g')/P_G$g"
  done | sort -Vr | awk -F/ 'NR==1 { printf "%6s %6s %8s %s\n", $1, $2, $3, $4; next } { printf "%6d %6d %8d %s\n", $1, $2, $3, $4 }'
done
```

```bash
 # Salida de ejemplo
 #### Ranking Single Player ####
 Score  Valid  Invalid Grupo
  2952    594        0 P_G6
  2426    439        0 P_G13
  2360    398        0 P_G23
 ...

 #### Ranking 1 vs 1 ####
 Score  Valid  Invalid Grupo
  3730    700        8 P_G11
  3096    599        1 P_G13
  2750    567       11 P_G6
 ...

 #### Ranking FFA ####
 Score  Valid  Invalid Grupo
  4274    719        2 P_G4
  4121    859        4 P_G6
  3910    616        3 P_G15
 ...

 #### Ranking Global ####
 Score  Valid  Invalid Grupo
  9823   2020       15 P_G6
  9149   1670       11 P_G11
  8509   1416       14 P_G4
 ...
```

