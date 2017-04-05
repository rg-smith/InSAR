while read p; do
	cd $p
	snaphu_dec.csh 0.1 0
	cd ..
done <igram_dirs.txt
