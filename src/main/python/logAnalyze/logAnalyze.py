import csv
import re
'''
41.901: [GC [PSYoungGen: 16777216K->128327K(18874368K)] 16777216K->128327K(39845888K), 0.1245200 secs] [Times: user=0.79 sys=0.08, real=0.12 secs]
'''
report_file = open('report.csv','w')
report_writer = csv.writer(report_file,delimiter=",",quotechar='"')
report_writer.writerow(['Time since VM started(s)','pre-collection young gen usage(K)','post-collection young gen usage(K)','Total young gen size(K)','pre-collection heap size(K)','post-collection heap size(K)','total heap size(K)','total collection time(s)'])
log_file = open('analyze.log','rU')
p = re.compile('[0-9.]+')
try:
	for line in log_file:
		report_writer.writerow(p.findall(line)[0:8])
finally:
	log_file.close()
	report_file.close()
