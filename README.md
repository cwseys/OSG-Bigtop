# OSG-Bigtop
The following are notes and tools gained in the process of migrating UW-Madison CMS-T2 from OpenScience Grid (3.5) packaged HDFS to Bigtop (1.5.0) packaging.  

## Supplemental RPM
The hdfs-bigtop-osg.rpm should be installed at the same time as Bigtop 1.5.0 RPMs. The hdfs-bigtop-osg.rpm (built from hdfs-bigtop-osg.spec file) satisfies the OSG RPM dependencies and installs a symlink from /usr/lib64/libhdfs.so.0.0.0 to /usr/lib64/libhdfs.so.0 .  This symlink allows xrootd and globus-gridftp packaged by OSG to run with Hadoop as packaged by Bigtop.

## Migration
In general follow the procedure given by Hadoop, but with the notes below.
We used **HA with downtime** https://hadoop.apache.org/docs/r2.10.1/hadoop-project-dist/hadoop-hdfs/HDFSHighAvailabilityWithQJM.html#HDFS_UpgradeFinalizationRollback_with_HA_Enabled
There is also an **HA without downtime** but the instructions for how to start the namenode daemon a) after starting the upgrade but b) before finishing the upgrade is not clear.  (Using HA with downtime in this scenario the namenode daemon should be started with no special command line switches.)
**notes**
- You may have to restart each (or some) datanodes to get them to connect to the namenodes after upgrade.  Create a list of datanodes before upgrade:
  hdfs dfsadmin -report -live 2>/dev/null | grep Hostname | sed -E 's/^.*\s+//g' > /tmp/datanodes
Be prepared to iterate over this list restarting datanodes.  (We used a script to ssh to each datanode and restart the datanode. If you don't have such a script, let us know.)
- After updating the NameNode to Bigtop, you may need to modify /usr/lib/hadoop-hdfs/bin/hdfs line 146 with environmental overrides normally sourced from /etc/default/hadoop-hdfs-namenode.  In our case, we increase the JVM heap size. You'll need to add whatever overrides which appear in /etc/default/hadoop-hdfs-namenode .  That file is sourced in the init script, but when upgrading HDFS the init scripts are not used when starting the namenode daemon. E.g. we changed HADOOP_OPTS="$HADOOP_OPTS $HADOOP_NAMENODE_OPTS" to HADOOP_OPTS="$HADOOP_OPTS $HADOOP_NAMENODE_OPTS -Xmx60000m".
- We encountered what appears to be the bug "DN may not send block report to NN after NN restart" https://issues.apache.org/jira/browse/HDFS-12749 . The symptom is that datanodes connect to the namenode, but the namenode "Datanodes" status page shows their block count to be 0 (if HDFS is in safemode). This can be worked around by triggering a block report from each datanode after it connects to the namenode.  The script triggerBlockReportAllDNs.sh automates this either by querying the namenodes for connected datanodes or reading in a list of datanodes.
