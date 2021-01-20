#!/bin/bash
# trigger full block reports from all datanodes

# ATM I don't see a way to trigger based on a number of block threshhold:
# I don't see how to get the number of blocks on a DN as reported by the NN
if [ "$1" != '' ]; then
	# read a list of DNs from file
	cat "$1" \
		| xargs -I{} \
 		sudo -u hdfs /usr/bin/hdfs dfsadmin -triggerBlockReport {}:50020
else 
	sudo -u hdfs /usr/bin/hdfs dfsadmin -report -live 2>/dev/null \
		| grep Hostname | cut -d: -f2 | xargs -I{} \
 		sudo -u hdfs /usr/bin/hdfs dfsadmin -triggerBlockReport {}:50020
fi
