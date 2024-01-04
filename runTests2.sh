function ProgressBar {
# Process data
    let _progress=(${1}*100/${2}*100)/100
    let _done=(${_progress}*4)/10
    let _left=40-$_done
# Build progressbar string lengths
    _fill=$(printf "%${_done}s")
    _empty=$(printf "%${_left}s")

# 1.2 Build progressbar strings and print the ProgressBar line
# 1.2.1 Output example:                           
# 1.2.1.1 Progress : [########################################] 100%
printf "\rProgress : [${_fill// /#}${_empty// /-}] ${_progress}%%"

}

doalarm () { perl -e 'alarm shift; exec @ARGV' "$@"; }

_start=1
_end=200
for i in $(seq ${_start} ${_end})
do
    ProgressBar ${i} ${_end}
    echo -n "$i: " >> ./stats2.txt
    timeout 30 python ./test_folder/testAct2.py
done