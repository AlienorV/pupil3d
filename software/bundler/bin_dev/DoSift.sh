mogrify -format pgm $1
$2 --threshold 0.04 --verbose $3
rm $3
gzip $4

