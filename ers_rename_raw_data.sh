while read p; do
	j=`echo $p | cut -d'_' -f 5 | cut -d'T' -f 1`;echo $j
	datfile=`echo $p'/DAT_01.001'`
	echo $datfile
	datfiledest=`echo $j'.dat'`
	cp "$datfile" $datfiledest
	ldrfile=`echo $p'/LEA_01.001'`
	ldrfiledest=`echo $j'.ldr'`
	cp "$ldrfile" $ldrfiledest
done <rawdirs.txt