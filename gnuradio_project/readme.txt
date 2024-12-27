启动方法是：
conda deactivate 先退出conda环境
然后运行这个.py脚本





#############################################################
因为每次运行.grc（GNUradio GUI）的话都会重新生成.py
所以运行我这个修改好的.py就行了，不去直接运行.grc
import datetime

        self.ant3 = ant3 = "/home/ssd2/gnss-sdr/fsc_data/data/" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f") + "_ant3" + ".dat" 
        self.ant2 = ant2 = "/home/ssd2/gnss-sdr/fsc_data/data/" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f") + "_ant2" + ".dat"
        self.ant1 = ant1 = "/home/ssd2/gnss-sdr/fsc_data/data/" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f") + "_ant1" + ".dat"
        self.ant0 = ant0 = "/home/ssd2/gnss-sdr/fsc_data/data/" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f") + "_ant0" + ".dat"
