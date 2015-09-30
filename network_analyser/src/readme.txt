
1、使用方法：

	1、修改network_analyser.conf，将listen_ip修改为本机的ip，将target_ip修改为对方的ip，其它的采用默认值即可。
	2、在两部机器运行network_analyser.py:
	
		python network_analyser.py
		
	3、启动之后network_analyser会每隔5秒发送数据包给对方，以些分析网络情况。
	4、退出程序：
	
		ctrl + c
		