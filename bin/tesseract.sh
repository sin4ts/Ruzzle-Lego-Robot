#! /usr/bin/env bash

echo "Tesseract detection"
outputFile="../Software/output_sv.txt"
outputBonus="../Software/bonus.txt"
temp="tesseract"
color="color.txt"
imgTemp="imageTemp.png"
cd /cygdrive/c/Users/stan/Desktop/Lund/LegoRobotRuzzle/Opencv_WebCa/Software
pwd
cd ../temp
rm $outputBonus
rm $outputFile

for img in `ls *.png`
do
	#Bonus
	name=$(identify  $img | awk '{print $1}')
	bonus=${name:3:2}
	if [ $bonus = "NN" ]
		then echo 'n' | tr -d '\n' >> $outputBonus
	elif [ $bonus = "TW" ]
		then echo 'T' | tr -d '\n' >> $outputBonus
	elif [ $bonus = "DW" ]
		then echo 'D' | tr -d '\n' >> $outputBonus
	elif [ $bonus = "TL" ]
		then echo 't' | tr -d '\n' >> $outputBonus
	elif [ $bonus = "DL" ]
		then echo 'd' | tr -d '\n' >> $outputBonus
	fi
done
		

letterImage="letters.png"
#we detect letter
tesseract $img $temp -l swe -psm 7 ../SoftWare/tesseract.conf
cat $temp.txt | tr -d " \t\n\r"
value=`cat $temp.txt`
value=value | tr 'Ö' '2'
value=value | tr 'A' '1'
value=value | tr 'Å' '0'
echo $value | tr -d '\n' >> $outputFile
rm $temp.txt

cd ..
echo "End of tesseract" >> "Software/end.txt"
