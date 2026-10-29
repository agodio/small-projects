promela_model=$1

if [[ ! -f $promela_model ]]; then
  echo "$promela_model does not exist"
  exit
fi

rm -f pan pan.* *.trail

spin -a $promela_model || exit
gcc -DREACH -o pan pan.c || exit

echo "Running verification..."
./pan -i

if [[ -f $promela_model.trail ]]; then
  echo "Replaying trail..."
  spin -t -p -g -l $promela_model
fi
