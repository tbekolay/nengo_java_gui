import pylab
import numpy
import matplotlib
import random

class Theme:
    def __init__(self):
        self.bar_colors=['0.4','0.8','0.6','1.0']
    def bar_color(self,i):
        return self.bar_colors[i%len(self.bar_colors)]
    

class PlotData:
    def __init__(self,dpi=100,width=6,height=4):
        self.fig=pylab.figure(figsize=(width,height),dpi=dpi)
        self.theme=Theme()
        self.axes=self.fig.add_subplot(1,1,1)
        self.labels=[]
        self.legend_bars=None
    def fix_shape(self,value):
        if not hasattr(value,'shape'):
            value=numpy.array(value)
        count=reduce(lambda x,y: x*y,value.shape)
        if value.shape[-1]==3:
            value.shape=count/3,3    
        else:
            value.shape=count,1
        return value        
    def plot(self,label,value,width=0.8):
        value=self.fix_shape(value)
        x=len(self.labels)
        bars=len(value)
        barwidth=width/bars
        space=(1.0-width)/2
        bars=[]
        for i,val in enumerate(value):
            c=self.theme.bar_color(i)
            if len(val)==3:
                if val[1] is not None:
                    bar=self.axes.bar([x+i*barwidth+space],val[1],width=barwidth,color=c)
                    self.axes.errorbar(x+(i+0.5)*barwidth+space,val[1],yerr=[[val[1]-val[0]],[val[2]-val[1]]],ecolor='k',elinewidth=1)
            else:    
                if val[0] is not None:
                    bar=self.axes.bar([x+i*barwidth+space],val[0],width=barwidth,color=c)
            bars.append(bar)
        if self.legend_bars is None: self.legend_bars=bars    
        self.labels.append(label)
        self.axes.set_xticks([x+0.5 for x in range(len(self.labels))])        
        self.axes.set_xticklabels(self.labels)
        self.axes.set_xlim(0,len(self.labels))
    def legend(self,labels):
        self.axes.legend(self.legend_bars,labels,loc='best')    
    def show(self):
        pylab.show()        
        


