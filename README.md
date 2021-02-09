# OSG-Bigtop
The following are notes and tools gained in the process of migrating UW-Madison Wisconsin CMS-T2 from OpenScience Grid (3.5) packaged HDFS to [Apache Bigtop 1.5.0](https://bigtop.apache.org/download.html#releases) packaging.  

## Supplemental RPM
The hdfs-bigtop-osg.rpm should be installed at the same time as Bigtop 1.5.0 RPMs. The hdfs-bigtop-osg.rpm can be built from hdfs-bigtop-osg.spec file in this repo with `rpmbuild -bb hdfs-bigtop-osg.spec`). hdfs-bigtop-osg.rpm satisfies the OSG RPM dependencies and installs a symlink from /usr/lib64/libhdfs.so.0.0.0 to /usr/lib64/libhdfs.so.0 .  This symlink allows xrootd-hdfs and gridftp-hdfs as packaged by OSG to run with Hadoop as packaged by Bigtop.

## Migration Notes
In general follow the procedure given by Hadoop, but with the notes below.
We used [**HA with downtime**](https://hadoop.apache.org/docs/r2.10.1/hadoop-project-dist/hadoop-hdfs/HDFSHighAvailabilityWithQJM.html#HDFS_UpgradeFinalizationRollback_with_HA_Enabled) .
There is also an **HA without downtime** but the instructions for how to start the namenode daemon a) after starting the upgrade but b) before finishing the upgrade are not clear.  (Using HA with downtime in this scenario the namenode daemon should be started with no special command line switches.) 
Finally, for [**non-HA clusters**](https://hadoop.apache.org/docs/r2.10.1/hadoop-project-dist/hadoop-hdfs/HdfsRollingUpgrade.html#Upgrading_Non-HA_Clusters)
- NameNode JVM heap during upgrade:  The namenode daemon is not started with the initscript during upgrade.  This means that the JVM heap size and other changes set in /etc/default/hadoop-hdfs-namenode are not applied. There might be a more elegant way, but we hacking /usr/lib/hadoop-hdfs/bin/hdfs line 146.  E.g. we changed `HADOOP_OPTS="$HADOOP_OPTS $HADOOP_NAMENODE_OPTS"` to `HADOOP_OPTS="$HADOOP_OPTS $HADOOP_NAMENODE_OPTS -Xmx60000m"`.
- You may have to restart each (or some) datanodes to get them to connect to the namenodes after namenodes are upgraded and restarted.  One way to do this is to create a list of datanodes before upgrade: `hdfs dfsadmin -report -live 2>/dev/null | grep Hostname | sed -E 's/^.*\s+//g' > /tmp/datanodes` Be prepared to iterate over this list restarting datanodes.  (We used a script to ssh to each datanode and restart the datanode. If you don't have such a script, let us know.)
- Datanodes not reporting their blocks. We encountered what appears to be the bug ["DN may not send block report to NN after NN restart"](https://issues.apache.org/jira/browse/HDFS-12749) . The symptom is that datanodes connect to the namenode and appear on the namenode's "Datanodes" status page.  However, the block count reported is 0 (if HDFS is in safemode). This can be worked around by triggering a block report from each datanode after it connects to the namenode.  The script `triggerBlockReportAllDNs.sh` (in this repo) queries the namenode for connected datanodes and triggers blocks reports.
- Furthermore, we needed to trigger block reports frequently during the upgrade.  It seemed as though upgrading a datanode would often cause blocks not to be reported, resulting in underreplicated and missing blocks.
- Datanodes need more JVM heap during the upgrade than they do to run normally.
- Occassionally blocks would show up in the missing list, but could be recovered from the hdfs/current/BP-xxxxxxxxx-IPADDRESS-xxxxxxxxxxxx/previous.tmp directory. Most likely this was due to the datanode running out of Java Heap and terminating in the middle of the it first run.  Avoid this by increasing the DN heap size by 3G over normal before upgrading.  To recover these blocks, you'll need a way to find the last known location of a block file.  (We have a script for tracing block to node.) One way to rescue the block is to shutdown the datanode daemon, copy the block file and matching meta file out of the previous.tmp directory into the active blocks directory, then restart the datanode (with enough JVM heap!).  E.g. cp /data/04/hdfs/current/BP-xxxxxxxxx-IPADDRESS-xxxxxxxxxxxx/current/finalized/subdir24/subdir9/blk_-4848188265532479052 /data/04/hdfs/current/BP-xxxxxxxxx-IPADDRESS-xxxxxxxxxxxx/current/finalized/subdir24/subdir9/blk_-4848188265532479052
- xrootd, gridftp, and other daemons which use HDFS libraries need to be restarted to load the new libraries

