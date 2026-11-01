import re
import os
import sys
import random
import chardet

def read_unknown_encoding(filepath):
    try:
        with open(filepath, 'rb') as f:
            rawdata = f.read()
        result = chardet.detect(rawdata)
        encoding = result['encoding']
        if not encoding or encoding == 'ascii':
            # 如果无法确定编码或者编码为ASCII，则默认使用UTF-8编码
            encoding = 'utf-8'
        text = rawdata.decode(encoding)
        textline = text.splitlines(keepends=True)
        textline = [item.replace("\r", "") for item in textline]
    except:
        with open(filepath, 'r') as f:
            textline = f.readlines()
    return textline

def cut(line):
    p=re.compile(r';.*')
    subs=p.sub('',line)
    if subs.lstrip():subs=subs.lstrip()
    return subs

def findstateno(state):
    s=0
    stateno=-1
    p=re.compile(r'value\s*=\s*(\d+)',re.I)
    p1=re.compile(r'value\s*=\s*ifelse\(.*,\s*(\d+)\s*,\s*(\d+)\s*\)',re.I)
    for line in state:
        m=p.search(line)
        m1=p1.search(line)
        if m:            
            stateno=int(m.group(1))
            break
        if m1 and stateno == -1:
            stateno=int(m1.group(1))
    return stateno

def findstatedef(stateno):
    p=re.compile(r'\[Statedef\s*'+str(stateno)+'(\s*|\D+.*)\]',re.I)
    p1=re.compile(r'\[Statedef',re.I)
    s=0
    statedef=[]
    if newstfiles != None:
        for cnsfile in newstfiles:
            if os.path.isfile(cnsfile):
                ST=open(cnsfile,'r',encoding='utf-8')        
                try:
                    if statedef ==[]:
                        temp=ST.readlines()
                        for line in temp:
                            m=p.search(line)
                            m1=p1.search(line)
                            if s==1:
                                if m1==None:statedef.append(line)
                                if m1:break
                            if m and s==0:
                                s=1
                                statedef.append(line)
                finally:ST.close()
    return statedef

def findaction(animno):
    p=re.compile(r'\[Begin action\s*'+str(animno)+'\s*\]',re.I)
    p1=re.compile(r'\[Begin action',re.I)
    s=0
    anim=0
    clsn1=0
    action=[]
    if actionlist != None:
        for line in actionlist:
            m=p.search(line)
            if s==1:
                m1=p1.search(line)
                if m1==None and cut(line):
                    if line != None and line != '' and 'clsn1' in line.lower():clsn1=1
                    action.append(line)
                if m1:break
            if m and s==0:
                action.append(line)
                s=1
    return action,clsn1

def findreach(action,pausetime=0,statetype='A'):
    t=re.compile(r'\s*-?\d+\s*,\s*-?\d+\s*,\s*-?\d+\s*,\s*-?\d+\s*,\s*(-?\d+)\s*')
    c=re.compile(r'clsn(\d+)\s*\:\s*\d+\s*',re.I)
    c0=re.compile(r'clsn\[\d+\]\s*=\s*(-?\d+\s*),(\s*-?\d+\s*),(\s*-?\d+\s*),(\s*-?\d+\s*)',re.I)
    c1=re.compile(r'clsn1\[\d+\]\s*=\s*(-?\d+\s*),(\s*-?\d+\s*),(\s*-?\d+\s*),(\s*-?\d+\s*)',re.I)
    c2=re.compile(r'clsn2\[\d+\]\s*=\s*(-?\d+\s*),(\s*-?\d+\s*),(\s*-?\d+\s*),(\s*-?\d+\s*)',re.I)
    s,s0,s1,s2,s3,s4=0,0,0,0,0,0
    time=0
    atkendtime=0
    totaltime=0
    pattern=0
    clsn=0
    c1x1=None
    c1x2=None
    c1y1=None
    c1y2=None    
    c2y1=None
    c2y2=None    
    for line in action:        
        m=t.search(line)
        mc=c.search(line)
        m0=c0.search(line)
        m1=c1.search(line)
        m2=c2.search(line)        
        if m:
            t1=abs(int(m.group(1)))
            time=time+t1*(1-s1)*(1-s3)
            totaltime=totaltime+t1
            if s1==1:s0=1
            if s2==1:s4=1
            if s==1:
                atkendtime=atkendtime+t1*s
                s=0
        if m1:s=1
        if m1 and s0==0:                        
            if c1x1 is not None:
                c1x1=min(c1x1,int(m1.group(1)),int(m1.group(3)))
            else:c1x1=min(int(m1.group(1)),int(m1.group(3)))
            if c1x2 is not None:
                c1x2=max(c1x2,int(m1.group(1)),int(m1.group(3)))
            else:c1x2=max(int(m1.group(1)),int(m1.group(3)))
            if c1y1 is not None:
                c1y1=min(c1y1,int(m1.group(2)),int(m1.group(4)))
            else:c1y1=min(int(m1.group(2)),int(m1.group(4)))
            if c1y2 is not None:                
                c1y2=max(c1y2,int(m1.group(2)),int(m1.group(4)))
            else:c1y2=max(int(m1.group(2)),int(m1.group(4)))
            s1=1
            if s2==0:s3=1
        if m2 and s4==0:            
            if statetype == 'A' and s1==1:
                if c2y1 is not None:
                    c2y1=min(int(m2.group(2)),int(m2.group(4)),c2y1)
                else:c2y1=min(int(m2.group(2)),int(m2.group(4)))
                if c2y2 is not None:
                    c2y2=max(int(m2.group(2)),int(m2.group(4)),c2y2)
                else:c2y2=max(int(m2.group(2)),int(m2.group(4)))
                s2=1
        if mc:
            pattern=1
            clsn=int(mc.group(1))
        if clsn==1 and m0:s=1
        if clsn==1 and m0 and s0==0:
            if c1x1 is not None:
                c1x1=min(c1x1,int(m0.group(1)),int(m0.group(3)))
            else:c1x1=min(int(m0.group(1)),int(m0.group(3)))
            if c1x2 is not None:
                c1x2=max(c1x2,int(m0.group(1)),int(m0.group(3)))
            else:c1x2=max(int(m0.group(1)),int(m0.group(3)))
            if c1y1 is not None:
                c1y1=min(c1y1,int(m0.group(2)),int(m0.group(4)))
            else:c1y1=min(int(m0.group(2)),int(m0.group(4)))
            if c1y2 is not None:                
                c1y2=max(c1y2,int(m0.group(2)),int(m0.group(4)))
            else:c1y2=max(int(m0.group(2)),int(m0.group(4)))
            s1=1
            if s2==0:s3=1
        if clsn==2 and m0 and s4==0:            
            if statetype == 'A' and s1==1:
                if c2y1 is not None:
                    c2y1=min(int(m0.group(2)),int(m0.group(4)),c2y1)
                else:c2y1=min(int(m0.group(2)),int(m0.group(4)))
                if c2y2 is not None:
                    c2y2=max(int(m0.group(2)),int(m0.group(4)),c2y2)
                else:c2y2=max(int(m0.group(2)),int(m0.group(4)))
                s2=1
    if c1x1 == None:time = None
    if time != None and time!=0:time=time+1    
    if pausetime != None and time != None and time >= pausetime:time=time-pausetime
    return time,totaltime,c1x1,c1x2,c1y1,c1y2,c2y1,c2y2,atkendtime

def read_animelem(animno,elemno,oper=''):
    t=re.compile(r'\s*-?\d+\s*,\s*-?\d+\s*,\s*-?\d+\s*,\s*-?\d+\s*,\s*(-?\d+)\s*')
    action=findaction(animno)[0]
    i=1
    time=0
    s=0
    opertime=0
    totaltime=None
    if oper != None and oper != '':opertime=int(re.findall(r'\d+',oper)[0])
    for line in action:
        m=t.search(line)
        if m and s==0:
            t1=abs(int(m.group(1)))
            time=time+t1*(1-s)
            i=i+1
            if i>=elemno:s=1
    if oper != None and oper !='':
        if '<' in oper:
            opertime=0
            totaltime=time
        else:
            if '=' not in oper:
                totaltime=time+opertime+1
            else:
                totaltime=time+opertime
    else:totaltime=time
    if elemno>1:totaltime=totaltime+1
    return totaltime

def findattr(statedef):
    animno=None
    temp_animno=None
    temp_clsn1=0
    temp_reach=None
    s1=0
    s2=0
    s3=0
    power=0
    oper=None
    sctrl=None
    statetype=None
    hitdef=None
    guardflag=None
    pausetime=0
    pause_start=None
    pause_end=None
    nothitby_start=None
    nothitbytime=1
    nothitby_end=None
    nothitby_attr=None
    nothitby_flag=0
    nextstate=None
    changestatetime=None
    helper_statenolist=[]
    reversal=None
    helper_flag=0
    proj_flag=0
    velx=0
    vely=0
    velmulx=1
    velmuly=1
    veladdx=0
    veladdy=0
    velmulstart=None
    veladdstart=None
    velstart=None
    timeend=None
    velxattr=[]
    velyattr=[]
    p0=re.compile(r'^guardflag\s*=\s*(\S+)',re.I)
    p1=re.compile(r'^anim\s*=\s*(\d+)',re.I)
    p1_1=re.compile(r'^anim\s*=\s*(\w+)',re.I)
    p1_2=re.compile(r'^anim\s*=\s*ifelse\(.*,\s*(\d+)\s*,\s*(\d+)\s*\)',re.I)
    p2=re.compile(r'^type\s*=\s*(\w)\s*$',re.I)
    p3=re.compile(r'^type\s*=\s*poweradd\s*$',re.I)
    p4=re.compile(r'^poweradd\s*=\s*-(\d+)',re.I)
    p5=re.compile(r'^value\s*=\s*-(\d+)',re.I)
    p5_1=re.compile(r'value\s*=\s*(\d+)',re.I)
    p6=re.compile(r'^type\s*=\s*hitdef\s*$',re.I)
    p7=re.compile(r'^type\s*=\s*(super)?pause\s*$',re.I)
    p8=re.compile(r'^(?:move)?time\s*=\s*(\d+)\s*',re.I)
    p9=re.compile(r'^hitflag\s*=\s*(\S+)',re.I)
    p10=re.compile(r'^type\s*=\s*(\w+)\s*$',re.I)
    p11=re.compile(r'^reversal\.attr\s*=\s*(\S+.*)\s*$',re.I)
    p12=re.compile(r'trigger(all|\d+)\s*=\s*time\s*([><=]+)\s*(\d+)\s*$',re.I)
    p13=re.compile(r'trigger(all|\d+)\s*=\s*animelem\s*=\s*(\d+)(,?.*)$',re.I)
    p14=re.compile(r'trigger(all|\d+)\s*=\s*AnimElemTime\s*(\(\d+\))\s*([><=]+\s*\d+)\s*',re.I)
    p15=re.compile(r'^Value\s*=(\D*,\D*)',re.I)
    p15_1=re.compile(r'^Value\s*=\s*([SCA]+)',re.I)
    p16=re.compile(r'trigger(all|\d+)\s*=\s*!time\s*',re.I)
    p17=re.compile(r'^value\s*=\s*(\d+)',re.I)
    p18=re.compile(r'trigger(all|\d+)\s*=\s*time\s*=\s*\[\s*(\d+)\s*,\s*(\d+)\s*\]\s*$',re.I)
    p19=re.compile(r"trigger(all|\d+)\s*=[^!]*ishelper(?!\s*=\s*0)",re.I)
    p20=re.compile(r'^velset\s*=\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)',re.I)
    p21=re.compile(r'^x\s*=\s*(-?\d+\.?\d*)\s*',re.I)
    p22=re.compile(r'^y\s*=\s*(-?\d+\.?\d*)\s*',re.I)
    p23=re.compile(r'trigger(all|\d+)\s*=\s*animtime\s*=\s*-?(\d+)',re.I)
    for line in statedef:
        line=cut(line)
        m1=p1.search(line)
        m1_1=p1_1.search(line)
        m1_2=p1_2.search(line)
        m2=p2.search(line)
        m3=p3.search(line)
        m4=p4.search(line)
        m5=p5.search(line)
        m5_1=p5_1.search(line)
        m6=p6.search(line)
        m7=p7.search(line)
        m8=p8.search(line)
        m9=p9.search(line)
        m0=p0.search(line)
        m10=p10.search(line)
        m11=p11.search(line)
        m12=p12.search(line)
        m13=p13.search(line)
        m14=p14.search(line)
        m15=p15.search(line)
        m15_1=p15_1.search(line)
        m16=p16.search(line)
        m17=p17.search(line)
        m18=p18.search(line)
        m19=p19.search(line)
        m20=p20.search(line)
        m21=p21.search(line)
        m22=p22.search(line)
        m23=p23.search(line)
        if m10:
            sctrl=m10.group(1).lower().strip()
        if m1 and animno==None:
            animno=m1.group(1)
            temp_clsn1=findaction(animno)[1]
        if m1_1 and animno==None:
            if m1_1.group(1).lower()=="stateno":animno=stateno
        if m1_2 and animno==None:
            animno=int(m1_2.group(1))
        if m2 and statetype==None:            
            statetype=m2.group(1)            
        if m3 and s1==0 and power == 0:
            s1=1
        if m5 and s1==1 and power == 0:
            power = int(m5.group(1))
            s1=0
        if m4:power = int(m4.group(1))
        if m6 and s2==1:
            hitdef=''.join(m6.group(2).split())
        if m6 and s2==0:
            s2=1
            p6=re.compile(r'^attr\s*=\s*([SCA]*),\s*(\w\w)',re.I)        
        #if m7:
        #    s3=1
        #if (sctrl != "superpause" and sctrl != "pause") and s3 == 1:s3=0
        if sctrl=="superpause" or sctrl == "pause":
            if m8:pausetime = int(m8.group(1))
            if m12 and pause_start==None:
                if '<' not in m12.group(2):
                    pause_start=int(m12.group(3))
                else:
                    pause_start=0
                    if '<' in m12.group(2):pause_end=int(m12.group(3))-('=' not in m12.group(2))
            if m13 and animno != None and pause_start==None:
                elemno=int(m13.group(2))
                if m13.group(3) != None:
                    if ',' in m13.group(3):oper=m13.group(3).replace(',','').strip()
                pause_start=read_animelem(animno,elemno,oper)
            if m14 and animno != None and pause_start==None:
                elemno=int(m14.group(2).replace('(', '').replace(')', ''))
                if m14.group(3) != None:oper=m14.group(3)
                pause_start=read_animelem(animno,elemno,oper)
            if m18:
                pause_start=int(m18.group(2))
                pause_end=int(m18.group(3))
        if m9 and hitdef != None:
            if 'A' not in m9.group(1):hitdef=hitdef+'-A'
            if '-' in m9.group(1):hitdef=hitdef+'-B'
        if m0 and hitdef != None:
            guardflag=m0.group(1)
            if 'A' not in m0.group(1):hitdef=hitdef+'-G'
            if 'L' in m0.group(1) and statetype != 'C':hitdef=hitdef+'-L'
            if 'H' in m0.group(1) and statetype != 'A':hitdef=hitdef+'-C'
        if sctrl=="changeanim":
            if m17:
                if animno==None:
                    animno=int(m17.group(1))
                    temp_clsn1=findaction(animno)[1]
                if animno!=None and temp_clsn1==0:
                    temp_animno=int(m17.group(1))
                    temp_clsn1=findaction(temp_animno)[1]
                    if temp_clsn1==1:animno=temp_animno
        if sctrl=="helper":
            helper_flag=1
        if sctrl=="reversaldef":
            if m11 and reversal == None:
                reversal=m11.group(1).upper().strip()
        if sctrl=="nothitby":
            if m15:
                nothitby_attr=m15.group(1).strip()
            if m15_1:
                nothitby_attr=m15_1.group(1).strip()
            if m16:nothitby_start=0
            if m12:
                if '<' not in m12.group(2):
                    nothitby_start=int(m12.group(3))+('=' not in m12.group(2))
                else:
                    nothitby_start=0
                    if '<' in m12.group(2):nothitby_end=int(m12.group(3))-('=' not in m12.group(2))
            if m18:
                nothitby_start=int(m18.group(2))
                nothitby_end=int(m18.group(3))
            if m13 and animno != None:
                elemno=int(m13.group(2))
                if m13.group(3) != None:
                    if ',' in m13.group(3):oper=m13.group(3).replace(',','').strip()
                nothitby_start=read_animelem(animno,elemno,oper)
            if m14 and animno != None:
                elemno=int(m14.group(2).replace('(', '').replace(')', ''))
                if m14.group(3) != None:oper=m14.group(3)
                nothitby_start=read_animelem(animno,elemno,oper)
        if m8:nothitbytime=int(m8.group(1))
        if m19:nothitby_flag=-1
        if m20 and (velx == 0 or vely==0):
            velx,vely=float(m20.group(1)),float(m20.group(2))
        if sctrl=="velset":
            if m21 and velx == 0:velx=float(m21.group(1))
            if m22 and velx == 0:vely=float(m22.group(1))
            if m16:velstart=0
            if m12:
                if '<' not in m12.group(2):
                    veladdstart=int(m12.group(3))+('=' not in m12.group(2))
            else:
                velstart=0
            if m13 and animno != None:
                elemno=int(m13.group(2))
                if m13.group(3) != None:
                    if ',' in m13.group(3):oper=m13.group(3).replace(',','').strip()
                velstart=read_animelem(animno,elemno,oper)
            if m14 and animno != None:
                elemno=int(m14.group(2).replace('(', '').replace(')', ''))
                if m14.group(3) != None:oper=m14.group(3)
                velstart=read_animelem(animno,elemno,oper)
        if sctrl=="velmul" and velx !=0 or vely !=0:
            if m21:velmulx=float(m21.group(1))
            if m22:velmuly=float(m22.group(1))
            if m16:velmulstart=0
            if m12:
                if '<' not in m12.group(2):
                    velmulstart=int(m12.group(3))+('=' not in m12.group(2))
                else:
                    velmulstart=0
            if m13 and animno != None:
                elemno=int(m13.group(2))
                if m13.group(3) != None:
                    if ',' in m13.group(3):oper=m13.group(3).replace(',','').strip()
                velmulstart=read_animelem(animno,elemno,oper)
            if m14 and animno != None:
                elemno=int(m14.group(2).replace('(', '').replace(')', ''))
                if m14.group(3) != None:oper=m14.group(3)
                velmulstart=read_animelem(animno,elemno,oper)
        if sctrl=="veladd":
            if m21:veladdx=float(m21.group(1))
            if m22:veladdy=float(m22.group(1))
            if m16:veladdstart=0
            if m12:
                if '<' not in m12.group(2):
                    veladdstart=int(m12.group(3))+('=' not in m12.group(2))
                else:
                    veladdstart=0
                if m13 and animno != None:
                    elemno=int(m13.group(2))
                    if m13.group(3) != None:
                        if ',' in m13.group(3):oper=m13.group(3).replace(',','').strip()
                    veladdstart=read_animelem(animno,elemno,oper)
                if m14 and animno != None:
                    elemno=int(m14.group(2).replace('(', '').replace(')', ''))
                    if m14.group(3) != None:oper=m14.group(3)
                    veladdstart=read_animelem(animno,elemno,oper)
        velxattr=[velmulx,velmulstart,veladdx,veladdstart,velstart]
        velyattr=[velmuly,velmulstart,veladdy,veladdstart,velstart]
        if sctrl=="projectile":
            proj_flag=1
        if sctrl=="destroyself":
            if m16:timeend=0
            if m12:
                if '<' not in m12.group(2):
                    timeend=int(m12.group(3))+('=' not in m12.group(2))
                else:
                    timeend=0
                if m13 and animno != None:
                    elemno=int(m13.group(2))
                    if m13.group(3) != None:                    
                        if ',' in m13.group(3):oper=m13.group(3).replace(',','').strip()
                    timeend=read_animelem(animno,elemno,oper)
                if m14 and animno != None:
                    elemno=int(m14.group(2).replace('(', '').replace(')', ''))
                    if m14.group(3) != None:oper=m14.group(3)
                    timeend=read_animelem(animno,elemno,oper)
        if sctrl=="changestate":
            if m16:changestatetime=0
            if m12:
                if '<' not in m12.group(2):
                    changestatetime=int(m12.group(3))+('=' not in m12.group(2))
                else:
                    changestatetime=0
                if m13 and animno != None:
                    elemno=int(m13.group(2))
                    if m13.group(3) != None:                    
                        if ',' in m13.group(3):oper=m13.group(3).replace(',','').strip()
                    changestatetime=read_animelem(animno,elemno,oper)
                if m14 and animno != None:
                    elemno=int(m14.group(2).replace('(', '').replace(')', ''))
                    if m14.group(3) != None:oper=m14.group(3)
                    changestatetime=read_animelem(animno,elemno,oper)
            if m23:changestatetime=-1*(int(m23.group(2))+1)
            if m5_1:
                if int(m5_1.group(1))>=200:nextstate=int(m5_1.group(1))
    if guardflag == None and hitdef != None:hitdef=hitdef+'-U'
    if pause_start != None:
        if pause_end == None:
            pause_end=pause_start+pausetime
        else:
            pause_end=pause_end+pausetime
    if nothitby_start!=None:
        if nothitby_end == None:
            nothitby_end=nothitby_start+nothitbytime
        else:
            nothitby_end=nothitby_end+nothitbytime
    if nothitby_start!=None and pause_start!=None:
        if nothitby_end > pause_end:
            nothitby_start=min(nothitby_start,pause_start)      
    if nothitby_start!=None and pause_start!=None and nothitby_end != None and pause_end!=None:
        if nothitby_end > pause_start:
            nothitby_end=nothitby_end-pause_end
        if nothitby_end <= nothitby_start:
            if nothitby_start<pause_start and nothitby_end > pause_start:nothitby_end=pause_start
    if nothitby_start!=None and nothitby_end != None and nothitby_end > nothitby_start and nothitby_attr != None and nothitby_flag==0:
        nothitby_flag=1
    if changestatetime != None and pausetime != None:
        if pause_start != None and pause_start <= changestatetime and changestatetime > pausetime:changestatetime=changestatetime-pausetime
    return animno,statetype,power,hitdef,pausetime,reversal,nothitby_attr,nothitby_start,nothitby_end,nothitby_flag,helper_flag,velx,velxattr,vely,velyattr,timeend,proj_flag,nextstate,changestatetime
    
def clearcmd(state):
    p = re.compile(r'(\s*)statetype\s*=\s*[SC]',re.I)
    p0 = re.compile(fr'{ai_var_re}\s*<?=\s*0|!\s*{ai_var}',re.I)
    p1 = re.compile(r'command\s*!?=\s*".*?"',re.I)
    p2 = re.compile(r'(&&|\(|=|(?:\|\|))\s*&&')
    p3 = re.compile(r'&&\s*(&&|(?:\|\|)|\s*$|\))')
    p4 = re.compile(r'(&&|\(|=|(?:\|\|))\s*\|\|')
    p5 = re.compile(r'\|\|\s*(&&|(?:\|\|)|\s*$|\))')
    p6 = re.compile(r'\(\s*\)',re.I)
    p7 = re.compile(r'trigger\S+\s*=\s*$',re.I)    
    temp = []
    for line in state:        
        m = p.search(line)        
        if m:line=re.sub(p,r'\1Statetype != A',line)
        m0=p0.search(line)
        if m0:line=re.sub(p0,'1',line)
        m1=p1.search(line)
        if m1:
            if 'value' in line.lower():line=re.sub(p1,'random%2',line)
            else:line=re.sub(p1,'1',line)
        m2=p2.search(line)
        m3=p3.search(line)
        m4=p4.search(line)
        m5=p5.search(line)
        while(m2 or m3 or m4 or m5):
            m2=p2.search(line)
            if m2:line=re.sub(p2,r'\1',line)
            m3=p3.search(line)
            if m3:line=re.sub(p3,r'\1',line)
            m4=p4.search(line)
            if m4:line=re.sub(p4,r'\1',line)
            m5=p5.search(line)
            if m5:line=re.sub(p5,r'\1',line)        
        m6=p6.search(line)
        if m6:line=re.sub(p6,'',line)
        m7=p7.search(line)
        if m7:line=re.sub(p7,'',line)
        temp.append(line)
    if temp != []:
        for lineno in range(len(temp)):
            if lineno < len(temp)-1 and temp[lineno]=='\n':
                temp.pop(lineno)
    return temp

def velsum(vel,velattr,reach,time=60):
    dist=0
    dist_reach=0
    t=0
    velmul=velattr[0]
    velmulstart=velattr[1]
    veladd=velattr[2]
    veladdstart=velattr[3]
    velstart=velattr[4]
    while abs(dist)<=255 and t<=time:
        if vel != None and velstart != None:dist=dist+vel*(t>=velstart)
        if vel != None and velstart != None and reach != None and t <= reach and reach <= time:dist_reach=dist_reach+vel*(t>=velstart)
        if vel != None and velmul !=None and velmulstart != None:vel=vel*velmul*(t>=velmulstart)
        if vel != None and veladd !=None and veladdstart != None:vel=vel+veladd*(t>=veladdstart)
        t=t+1
    return int(dist),int(dist_reach)

def proj(stateno):
    sctrl=None
    proj_animno=None
    proj_start=None
    proj_action=None
    proj_clsn1=0
    proj_pos=[0,0]  
    proj_start=None
    proj_start_list=[]
    proj_hitdef=None
    proj_guardflag=None
    proj_reach=None
    proj_remove=1
    oper=None
    proj_removetime=-1
    proj_endtime=60
    proj_ID=None
    proj_IDlist=[]
    proj_postype=None
    velx=0
    vely=0
    velmulx=0
    velmuly=0
    veladdx=0
    veladdy=0
    distx_reach=None
    distx=None
    disty_reach=None
    disty=None
    velxattr=[]
    velyattr=[]
    time,c1x1,c1x2=[],[],[]
    c1y1,c1y2,c2y1,c2y2=[],[],[],[]
    p=re.compile(r'\[State',re.I)
    p0=re.compile(r'^type\s*=\s*(\w+)\s*$',re.I)
    p1=re.compile(r'trigger(all|\d+)\s*=\s*!time\s*',re.I)
    p2=re.compile(r'trigger(all|\d+)\s*=\s*(?:state)?time\s*([><=]+)\s*(\d+)\s*',re.I)
    p3=re.compile(r'trigger(all|\d+)\s*=\s*animelem\s*=\s*(\d+)(,?.*)$',re.I)
    p4=re.compile(r'trigger(all|\d+)\s*=\s*AnimElemTime\s*(\(\d+\))\s*([><=]+\s*\d+)\s*',re.I)
    p5=re.compile(r'ProjAnim\s*=\s*(\d+)',re.I)
    p6=re.compile(r'postype\s*=\s*(\S+)',re.I)
    p7=re.compile(r'offset\s*=\s*(-?\d+).*,\s*(-?\d+).*',re.I)
    p8=re.compile(r'^guardflag\s*=\s*(\S+)',re.I)
    p9=re.compile(r'^hitflag\s*=\s*(\S+)',re.I)
    p10=re.compile(r'^attr\s*=\s*([SCA]*),\s*(\w\w)',re.I)  
    p11=re.compile(r'^\s*ID\s*=\s*(\d+)',re.I)
    p12=re.compile(r'Velocity\s*=\s*(-?\d+\.?\d*),(-?\d+\.?\d*)\s*',re.I)
    p13=re.compile(r'ProjReMove(Time)?\s*=\s*(-?\d+)\s*',re.I)
    p14=re.compile(r'accel\s*=\s*(-?\d+\.?\d*),(-?\d+\.?\d*)\s*',re.I)
    p15=re.compile(r'velmul\s*=\s*(-?\d+\.?\d*),(-?\d+\.?\d*)\s*',re.I)
    p16=re.compile(r'projscale\s*=\s*(\d+\.?\d*),(\d+\.?\d*)\s*',re.I)
    statedef=findstatedef(stateno)
    attr=findattr(statedef)
    animno=attr[0]
    statetype=attr[1]
    pausetime=attr[4]
    action=findaction(animno)[0]
    reach=findreach(action,pausetime,statetype)
    totaltime=reach[1]
    for line in statedef:
        line=cut(line)
        m=p.search(line)
        m0=p0.search(line)
        m1=p1.search(line)
        m2=p2.search(line)
        m3=p3.search(line)
        m4=p4.search(line)
        m5=p5.search(line)
        m6=p6.search(line)
        m7=p7.search(line)
        m8=p8.search(line)
        m9=p9.search(line)
        m10=p10.search(line)
        m11=p11.search(line)
        m12=p12.search(line)
        m13=p13.search(line)
        m14=p14.search(line)
        m15=p15.search(line)
        m16=p16.search(line)
        if m:
            proj_start=None
        if m0:sctrl=m0.group(1).lower().strip()
        if sctrl=="projectile":
            if m5:proj_animno=int(m5.group(1))
            if m1 and proj_start==None:proj_start=0
            if m2 and proj_start==None:
                if '<' not in m2.group(2):
                    proj_start=int(m2.group(3))+('=' not in m2.group(2))
                else:
                    proj_start=0
            if m3 and animno != None and proj_start==None:
                elemno=int(m3.group(2))
                if m3.group(3) != None:
                    if ',' in m3.group(3):oper=m3.group(3).replace(',','').strip()
                proj_start=read_animelem(animno,elemno,oper)
            if m4 and animno != None and proj_start==None:
                elemno=int(m4.group(2).replace('(', '').replace(')', ''))
                if m4.group(3) != None:oper=m4.group(3)
                proj_start=read_animelem(animno,elemno,oper)
            if m6:proj_postype=m6.group(1)
            if m7:
                proj_pos=[int(m7.group(1)),int(m7.group(2))]
            if m11:
                proj_ID=m11.group(1)
                if proj_ID not in proj_IDlist:proj_IDlist.append(proj_ID)
            if m10:proj_hitdef=m10.group(1)
            if m9 and proj_hitdef != None:
                if 'A' not in m9.group(1):proj_hitdef=proj_hitdef+'-A'
                if '-' in m9.group(1):proj_hitdef=proj_hitdef+'-B'
            if m8 and proj_hitdef != None:
                proj_guardflag=m8.group(1)
                if 'A' not in m8.group(1):proj_hitdef=proj_hitdef+'-G'
                if 'L' in m8.group(1) and statetype != 'C':proj_hitdef=proj_hitdef+'-L'
                if 'H' in m8.group(1) and statetype != 'A':proj_hitdef=proj_hitdef+'-C'
            if m16:xscale,yscale=float(m16.group(1)),float(m16.group(2))
            if m12:velx,vely=float(m12.group(1)),float(m12.group(2))
            if m14:veladdx,veladdy=float(m14.group(1)),float(m14.group(2))
            if m15:velmulx,velmuly=float(m15.group(1)),float(m15.group(2))
            if m13:
                if m13.group(1) != None:proj_removetime = int(m13.group(2))
                else:proj_remove=(int(m13.group(2))!=0)
            if proj_animno !=None:proj_action,proj_clsn1=findaction(proj_animno)
            if proj_action !=None and proj_clsn1==1:proj_reach=findreach(proj_action,pausetime)
            if proj_reach != None:proj_reach=list(proj_reach)
            if proj_reach != None and proj_reach[0] != None and proj_start != None and proj_reach[2] != None and proj_pos != None:
                proj_reach[0]=proj_reach[0]+proj_start
                proj_reach[2]=proj_reach[2]+proj_pos[0]
                proj_reach[3]=proj_reach[3]+proj_pos[0]
                proj_reach[4]=proj_reach[4]+proj_pos[1]
                proj_reach[5]=proj_reach[5]+proj_pos[1]
                if proj_postype != None and proj_postype.lower()=="p2":proj_reach[2],proj_reach[3],proj_reach[4],proj_reach[5]=-512,512,-255,255
                time.append(proj_reach[0])
                c1x1.append(proj_reach[2])
                c1x2.append(proj_reach[3])
                c1y1.append(proj_reach[4])
                c1y2.append(proj_reach[5])
                if proj_reach[6] != None:c2y1.append(proj_reach[6])
                if proj_reach[7] != None:c2y2.append(proj_reach[7])
    if proj_guardflag==None and proj_hitdef != None:proj_hitdef=proj_hitdef+'-U'
    if time != [] and c1x1 != [] and c1x2 !=[] and c1y1!=[] and c1y2!=[]:
        proj_reach = [min(time),totaltime,min(c1x1),max(c1x2),min(c1y1),max(c1y2)]
        if pausetime != None:
            if proj_reach[0]>pausetime:proj_reach[0]=proj_reach[0]-pausetime
            if proj_reach[1]>pausetime:proj_reach[1]=proj_reach[1]-pausetime
        if c2y1 !=[]:
            proj_reach.append(min(c2y1))
        else:
            proj_reach.append(None)
        if c2y2 !=[]:
            proj_reach.append(max(c2y2))
        else:
            proj_reach.append(None)
    if proj_start != None and proj_remove==1 and proj_removetime > 0:proj_endtime=proj_start+proj_removetime
    velxattr=[velmulx,0,veladdx,0,0]
    velyattr=[velmuly,0,veladdy,0,0]
    if velx != None and proj_reach != None and proj_reach[0] != None and velxattr != None:
        distx=velsum(velx,velxattr,proj_reach[0],proj_endtime)[0]
        #distx_reach=velsum(velx,velxattr,proj_reach[0],proj_endtime)[1]
    if vely != None and proj_reach != None and proj_reach[0] != None and velyattr != None:
        disty=velsum(vely,velyattr,proj_reach[0],proj_endtime)[0]
        #disty_reach=velsum(vely,velyattr,proj_reach[0],proj_endtime)[1]
    if proj_reach != None and proj_reach[3] != None and distx != None:
        proj_reach[3]=proj_reach[3]+distx
        if proj_reach[3]<proj_reach[2]:proj_reach[2],proj_reach[3]=proj_reach[3],proj_reach[2]
    if proj_reach != None and proj_reach[5] != None and disty != None:
        proj_reach[5]=proj_reach[5]+disty
        if proj_reach[5]<proj_reach[4]:proj_reach[4],proj_reach[5]=proj_reach[5],proj_reach[4]
    return proj_reach,proj_hitdef


def helper(stateno):
    s=0
    animno=None
    helper_animno=None
    helper_statedef=None
    helper_action=None
    helper_reach=None
    helper_hitdef=None
    helper_clsn1=0
    start=None
    postype=None
    helper_pos=None
    helper_postype=None
    sctrl=None
    oper=None
    helper_stateno=None
    helper_statenolist=[]
    helper_ID=None
    helper_IDlist=[]
    helper_start=None
    helper_endtime=None
    subhelper_stateno=None
    subhelper_flag=0
    velx=0
    vely=0
    distx_reach=None
    distx=None
    disty_reach=None
    disty=None
    velxattr=[]
    velyattr=[]
    time,c1x1,c1x2=[],[],[]
    c1y1,c1y2,c2y1,c2y2=[],[],[],[]
    atkendtime=[]
    p0=re.compile(r'^type\s*=\s*(\w+)\s*$',re.I)
    p1=re.compile(r'^velset\s*=\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)',re.I)
    p2=re.compile(r'^x\s*=\s*(-?\d+\.?\d*)\s*',re.I)
    p3=re.compile(r'^y\s*=\s*(-?\d+\.?\d*)\s*',re.I)
    p4=re.compile(r'^type\s*=\s*velmul\s*$',re.I)
    p5=re.compile(r'trigger(all|\d+)\s*=\s*!time\s*',re.I)
    p6=re.compile(r'trigger(all|\d+)\s*=\s*(?:state)?time\s*([><=]+)\s*(\d+)\s*',re.I)
    p7=re.compile(r'trigger(all|\d+)\s*=\s*animelem\s*=\s*(\d+)(,?.*)$',re.I)
    p8=re.compile(r'trigger(all|\d+)\s*=\s*AnimElemTime\s*(\(\d+\))\s*([><=]+\s*\d+)\s*',re.I)
    p9=re.compile(r'^\s*stateno\s*=\s*(\d+)',re.I)
    p10=re.compile(r'postype\s*=\s*(\S+)',re.I)
    p11=re.compile(r'pos\s*=\s*(-?\d+).*,\s*(-?\d+).*',re.I)
    p12=re.compile(r'^\s*ID\s*=\s*(\d+)',re.I)
    p13=re.compile(r'\[State',re.I)
    statedef=findstatedef(stateno)
    attr=findattr(statedef)
    animno=attr[0]
    statetype=attr[1]
    pausetime=attr[4]
    action=findaction(animno)[0]
    reach=findreach(action,pausetime,statetype)
    totaltime=reach[1]
    for line in statedef:
        line=cut(line)
        m0=p0.search(line)
        m1=p1.search(line)
        m2=p2.search(line)
        m3=p3.search(line)
        m4=p4.search(line)
        m5=p5.search(line)
        m6=p6.search(line)
        m7=p7.search(line)
        m8=p8.search(line)
        m9=p9.search(line)
        m10=p10.search(line)
        m11=p11.search(line)
        m12=p12.search(line)
        m13=p13.search(line)
        if m0:sctrl=m0.group(1).lower().strip()
        if m13:
            helper_start=None
            helper_statedef=None
            helper_stateno=None
            helper_start==None
            helper_reach==None
            #helper_hitdef=None
            helper_pos=None
            helper_postype=None
            helper_action=None
        if sctrl=="helper":
            if m5 and helper_start==None:helper_start=0
            if m6 and helper_start==None:
                if '<' not in m6.group(2):
                    helper_start=int(m6.group(3))+('=' not in m6.group(2))
                else:
                    helper_start=0
            if m7 and animno != None and helper_start==None:
                elemno=int(m7.group(2))
                if m7.group(3) != None:
                    if ',' in m7.group(3):oper=m7.group(3).replace(',','').strip()
                helper_start=read_animelem(animno,elemno,oper)
            if m8 and animno != None and helper_start==None:
                elemno=int(m8.group(2).replace('(', '').replace(')', ''))
                if m8.group(3) != None:oper=m8.group(3)
                helper_start=read_animelem(animno,elemno,oper)
            #if helper_start != None and pausetime != None and helper_start > pausetime:helper_start = helper_start-pausetime
            if m10:helper_postype=m10.group(1)
            if m11:
                helper_pos=[int(m11.group(1)),int(m11.group(2))]
            if m9:helper_stateno=int(m9.group(1))
            if m12:helper_ID=m12.group(1)
            if helper_statedef==None and helper_stateno != None and helper_pos != None and helper_postype != None and helper_ID != None and ((helper_ID not in helper_IDlist) or (helper_stateno not in helper_statenolist)):
                helper_statenolist.append(helper_stateno)
                helper_IDlist.append(helper_ID)
                helper_statedef=findstatedef(helper_stateno)
                helper_attr=findattr(helper_statedef)
                helper_hitdef= helper_attr[3]
                helper_animno=helper_attr[0]
                helper_pausetime=helper_attr[4]
                helper_statetype=helper_attr[1]
                subhelper_flag=helper_attr[10]
                helper_endtime=helper_attr[15]
                velx=helper_attr[11]
                velxattr=helper_attr[12]
                vely=helper_attr[13]
                velyattr=helper_attr[14]
                if helper_animno != None:
                    helper_action,helper_clsn1=findaction(helper_animno)
                if helper_action!=None and helper_clsn1==1:
                    helper_reach=findreach(helper_action,helper_pausetime,helper_statetype)
                    if helper_reach != None:helper_reach=list(helper_reach)
                    if velx != None and velxattr !=None and helper_reach != None and helper_reach[0] != None:
                        if helper_reach[8] != None and helper_endtime != None and helper_endtime<helper_reach[8]:
                            distx=velsum(velx,velxattr,helper_reach[0],helper_endtime)[0]
                            #distx_reach=velsum(velx,velxattr,helper_reach[0],helper_endtime)[1]
                        else:
                            distx=velsum(velx,velxattr,helper_reach[0],helper_reach[8])[0]
                            #distx_reach=velsum(velx,velxattr,helper_reach[0],helper_reach[8])[1]
                    if vely != None and velyattr !=None and helper_reach != None and helper_reach[0] != None:
                        if helper_reach[8] != None and helper_endtime != None and helper_endtime<helper_reach[8]:
                            disty=velsum(vely,velyattr,helper_reach[0],helper_endtime)[0]
                            #disty_reach=velsum(vely,velyattr,helper_reach[0],helper_endtime)[1]
                        else:
                            disty=velsum(vely,velyattr,helper_reach[0],helper_reach[8])[0]
                            #disty_reach=velsum(vely,velyattr,helper_reach[0],helper_reach[8])[1]
                    if helper_reach != None and helper_reach[0] != None and helper_start != None:
                        helper_reach[0]=helper_reach[0]+helper_start
                    if helper_reach != None and helper_reach[2] != None and helper_pos != None:
                        helper_reach[2]=helper_reach[2]+helper_pos[0]
                        helper_reach[3]=helper_reach[3]+helper_pos[0]
                        helper_reach[4]=helper_reach[4]+helper_pos[1]
                        helper_reach[5]=helper_reach[5]+helper_pos[1]
                    if helper_reach != None and helper_reach[3] != None and distx != None:
                        helper_reach[3]=helper_reach[3]+distx
                    if helper_reach != None and helper_reach[5] != None and disty != None:
                        helper_reach[5]=helper_reach[5]+disty
                        if helper_postype != None and helper_postype.lower()=="p2":
                            helper_reach[2],helper_reach[3],helper_reach[4],helper_reach[5]=-512,512,-255,255
                        if helper_reach[6] != None:helper_reach[6]=helper_reach[6]+helper_pos[1]
                        if helper_reach[7] != None:helper_reach[7]=helper_reach[7]+helper_pos[1]
                        if helper_reach[3]<helper_reach[2]:helper_reach[2],helper_reach[3]=helper_reach[3],helper_reach[2]
                        if helper_reach[5]<helper_reach[4]:helper_reach[4],helper_reach[5]=helper_reach[5],helper_reach[4]
                        time.append(helper_reach[0])
                        c1x1.append(helper_reach[2])
                        c1x2.append(helper_reach[3])
                        c1y1.append(helper_reach[4])
                        c1y2.append(helper_reach[5])
                        if helper_reach[6] != None:c2y1.append(helper_reach[6])
                        if helper_reach[7] != None:c2y2.append(helper_reach[7])
                        if helper_reach[8] != None:atkendtime.append(helper_reach[8])
    if time != [] and c1x1 != [] and c1x2 !=[] and c1y1!=[] and c1y2!=[]:
        helper_reach = [min(time),totaltime,min(c1x1),max(c1x2),min(c1y1),max(c1y2)]
        if pausetime != None:
            if helper_reach[0]>pausetime:helper_reach[0]=helper_reach[0]-pausetime
            if helper_reach[1]>pausetime:helper_reach[1]=helper_reach[1]-pausetime
        if c2y1 !=[]:
            helper_reach.append(min(c2y1))
        else:
            helper_reach.append(None)
        if c2y2 !=[]:
            helper_reach.append(max(c2y2))
        else:
            helper_reach.append(None)
    #if helper_reach != None and helper_reach[2] != None and helper_hitdef !=None:
    #    helper_reach=list(helper_reach)
    #    helper_reach.append(helper_hitdef)
    return helper_reach,helper_hitdef

def state_read(stateno):
    attacktype = "unknown"
    statedef = findstatedef(stateno)       
    stateattr = findattr(statedef)        
    action = findaction(stateattr[0])[0]
    reach = findreach(action,stateattr[4],stateattr[1])
    attr=None
    if stateattr[3] != None:
        attacktype="hitdef"
        attr=stateattr[3]
    if stateattr[3] == None and stateattr[5] != None:
        attacktype="reversal"
        attr=stateattr[5]
    if helper_key==1 and stateattr[3] == None and stateattr[5] == None and reach[2]==None and stateattr[10] == 1:
        temp_reach=helper(stateno)
        if temp_reach != None and temp_reach[0] != None:
            reach=temp_reach[0]
            attr=temp_reach[1]
            attacktype="helper"
    if helper_key==1 and stateattr[3] == None and stateattr[5] == None and reach[2]==None and attacktype!="helper" and stateattr[16] == 1:
        proj_reach=proj(stateno)
        if proj_reach != None and proj_reach[0] != None:
            reach=proj_reach[0]
            attr=proj_reach[1]
            attacktype="proj"
    print("stateno:",stateno,"animno:",stateattr[0],"attacktype:",attacktype,"time:",reach[0])
    return attacktype,stateattr,reach,attr

def writecounter(py,reachtime,hitdef):
    tempstate=state[:]            
    if reachtime > 1:
        tempstate.insert(trigger,py)
        tempstate.insert(trigger+1,"triggerall = p2movetype = A && p2stateno=helper({aihelperID}),var(2) && enemynear,time < helper({aihelperID}),var(3)-{reachtime}\n".format(aihelperID=aihelperID,reachtime=reachtime))
        tempstate.insert(trigger+2,"triggerall = enemynear,time >= 60-8*{ai_var} && random <= 75*{ai_var}\n".format(ai_var=ai_var))        
    else:
        tempstate.insert(trigger,py)
        tempstate.insert(trigger+1,"triggerall = p2movetype = A && !enemynear,hitdefattr = sca,aa,ap,at\n")
        tempstate.insert(trigger+2,"triggerall = p2stateno < 2000 || p2stateno = helper({aihelperID}),var(2)\n".format(aihelperID=aihelperID))
        tempstate.insert(trigger+3,"triggerall = enemynear,time >= 60-8*{ai_var} && random <= 75*{ai_var}\n".format(ai_var=ai_var))
    if 'T' in hitdef:tempstate.insert(trigger+3,"triggerall = helper({aihelperID}),var(18) <= 0\n".format(aihelperID=aihelperID))
    return tempstate

def writecounter2(py,reversal):
    tempstate=state[:]
    tempstate.insert(trigger,py)
    tempstate.insert(trigger+1,"triggerall = p2movetype = A && helper({aihelperID}),var(1) <= 1 && enemynear,hitdefattr={reversal}\n".format(aihelperID=aihelperID,reversal=reversal))
    tempstate.insert(trigger+2,"triggerall = enemynear,time >= 70-9*{ai_var} && random <= 75*{ai_var}\n".format(ai_var=ai_var)) 
    return tempstate

def writecounter3(py,reachtime,nothitby_attr,nothitby_end):
    tempstate=state[:]
    invincible=0
    attr=nothitby_attr.split(',')
    attr=list(map(str.upper,attr))
    if len(attr)== 1 and ('S' in attr[0].strip() and 'C' in attr[0].strip() and 'A' in attr[0].strip()) :
        invincible = 1
    if (attr[0]=="" or ('S' in attr[0].strip() and 'C' in attr[0].strip() and 'A' in attr[0].strip()))  and "AP" in attr and "AA" in attr and "AT" in attr:
        invincible = 1
    if (attr[0]=="" or ('S' in attr[0].strip() and 'C' in attr[0].strip() and 'A' in attr[0].strip())) and "NP" in attr and "NA" in attr and "NT" in attr and "SP" in attr and "SA" in attr and "ST" in attr and "HP" in attr and "HA" in attr and "HT" in attr:
        invincible = 1
    tempstate.insert(trigger,py)
    if nothitby_end>=reachtime and invincible == 1:
        tempstate.insert(trigger+1,"triggerall = p2movetype = A && enemynear,animtime < -%d\n"%reachtime)
        tempstate.insert(trigger+2,"triggerall = enemynear,time >= 70-9*{ai_var} && random <= 75*{ai_var} || {ai_var} >= 8 && (!ctrl || enemynear,hitdefattr=sca,at)\n".format(ai_var=ai_var))
    if nothitby_end<reachtime or invincible != 1:
        tempstate.insert(trigger+1,"triggerall = p2movetype = A && enemynear,hitdefattr={nothitby_attr} && enemynear,animtime < -{reachtime}\n".format(nothitby_attr=nothitby_attr,reachtime=reachtime))
        tempstate.insert(trigger+2,"triggerall = enemynear,time >= 70-9*{ai_var} && random <= 75*{ai_var} || {ai_var} >= 8 && (!ctrl || enemynear,hitdefattr=sca,at)\n".format(ai_var=ai_var))
    return tempstate

def writechance(py,reachtime,hitdef,totaltime):    
    tempstate=state[:]
    tempstate.insert(trigger,py)
    if reachtime+totaltime <= 25:        
        tempstate.insert(trigger+1,"triggerall = p2movetype = A || p2movetype = I\n")
    else:
        tempstate.insert(trigger+1,"triggerall = p2movetype = A || p2movetype = I && p2stateno > 160\n")
    tempstate.insert(trigger+2,"triggerall = p2statetype != L && !enemynear,ctrl && enemynear,animtime < -%d\n"%reachtime)
    tempstate.insert(trigger+3,"triggerall = !inguarddist || helper({aihelperID}),var(1) > 1 && (p2statetype != A || prevstateno = [120,159]) && random%3 < 2\n".format(aihelperID=aihelperID))
    tempstate.insert(trigger+4,"triggerall = random <= 113*{ai_var}\n".format(ai_var=ai_var))
    tempstate.insert(trigger+5,"triggerall = random%%2=0 || enemynear,time+enemynear,animtime >= 0 || enemynear,animtime = -%d\n"%(reachtime+1))
    if hitdef != None and 'T' in hitdef:tempstate.insert(trigger+4,"triggerall = helper({aihelperID}),var(18) <= 0\n".format(aihelperID=aihelperID))
    return tempstate

def writefight(py,reachtime,hitdef,statetype,totaltime,power=0):        
    tempstate = state[:]
    tempstate.insert(trigger,py)
    if hitdef != None and ('-B' in hitdef or 'T' in hitdef.upper()):tempstate.insert(trigger+1,"triggerall = p2movetype != H\n")
    else:tempstate.insert(trigger+1,"triggerall = p2movetype != H || p2stateno = [120,159]\n")
    tempstate.insert(trigger+2,"triggerall = !inguarddist && !helper({aihelperID}),inguarddist && p2statetype != L\n".format(aihelperID=aihelperID))
    attack_rate = max(min(int(625/(reachtime+1+totaltime+10*('S' in hitdef or 'H' in hitdef))+13*(statetype=='A' or 'T' in hitdef)),75),1)
    if 0<power<1000:attack_rate=max(int(attack_rate*(1-power/1000)),1)
    if hitdef != None and ('-G' in hitdef and 'H' not in hitdef):
        attack_rateA = max(min(int(1250/(reachtime+1+totaltime)),75),25)
        if 0<power<1000:attack_rateA=max(int(attack_rateA*(1-power/1000)),5)
        tempstate.insert(trigger+3,"triggerall = random <= {attack_rate}*{ai_var}|| p2statetype = A && random <= {attack_rateA}*{ai_var}\n".format(attack_rate=attack_rate,attack_rateA=attack_rateA,ai_var=ai_var))
    else:
        tempstate.insert(trigger+3,"triggerall = random <= {attack_rate}*{ai_var}\n".format(attack_rate=attack_rate,ai_var=ai_var))
    if hitdef != None and 'T' in hitdef.upper():tempstate.insert(trigger+3,"triggerall = helper({aihelperID}),var(18) <= 0\n".format(aihelperID=aihelperID))
    return tempstate

def writethrow(py,hitdef,reachtime):        
    tempstate = state[:]
    tempstate.insert(trigger,py)
    tempstate.insert(trigger+1,"triggerall = p2movetype != H\n")    
    tempstate.insert(trigger+2,"triggerall = !inguarddist && p2statetype != L\n")
    attack_rate = max(min(int(150/(reachtime+1)),60),1)
    tempstate.insert(trigger+3,"triggerall = random <= {attack_rate}*{ai_var}\n".format(attack_rate=attack_rate,ai_var=ai_var))
    if 'T' in hitdef.upper():tempstate.insert(trigger+4,"triggerall = helper({aihelperID}),var(18) <= 0\n".format(aihelperID=aihelperID))
    return tempstate

def writecombo(pyh,reachtime,power=0,nothitbyflag=0):    
    tempstate = state[:]
    tempstate.insert(trigger,pyh)
    tempstate.insert(trigger+1,"triggerall = enemynear,animtime <= -{reachtime} && !enemynear,canrecover && helper({aihelperID}),var(17) = 0 || helper({aihelperID}),var(17) >= {reachtime}\n".format(aihelperID=aihelperID,reachtime=reachtime))
    tempstate.insert(trigger+2,"triggerall = (!inguarddist || !ctrl) && enemynear,alive && p2movetype = H && p2statetype != L\n")
    if power >= 1000 or nothitbyflag==1:tempstate.insert(trigger+3,"triggerall = p2stateno != [120,159]\n")
    else:tempstate.insert(trigger+3,"triggerall = random%10<9 || p2stateno != [120,159]\n")
    tempstate.insert(trigger+4,"triggerall = random <= (80+(helper({aihelperID}),var(17)={reachtime})*45)*{ai_var}\n".format(aihelperID=aihelperID,reachtime=reachtime+1,ai_var=ai_var))        
    return tempstate

def procArray(a):
     b=[]
     a.sort(key=lambda x:findstateno(x))
     for e in a:
         b=b+e     
     return b

def writestate2(state,stateno,trigger):
    tempstate=state[:]
    if stateno == 40 or stateno == 41:
#        p = re.compile(r'value\s*=\s*40\s*$',re.I)
#        for lino in range(len(tempstate)):
#            if p.search(tempstate[lino]):tempstate[lino]='value = 41\n'
        tempstate.insert(trigger,"triggerall = p2movetype = H || enemynear,hitdefattr=sca,at && helper({aihelperID}),var(1)<=1 && abs(p2bodydist x) <= 60 || p2bodydist x > 120 || random%5=0 && p2bodydist x = [40,100]\n".format(aihelperID=aihelperID,ai_var=ai_var))
        tempstate.insert(trigger+1,"triggerall = p2statetype != L || p2bodydist x > 100 || p2stateno = 5120 && enemynear,animtime = [-41,-30]\n")
        tempstate.insert(trigger+2,"triggerall = p2movetype != H || p2statetype = A || p2stateno = [120,159]\n")
        tempstate.insert(trigger+3,"triggerall = (!inguarddist || !ctrl || enemynear,hitdefattr=sca,at && helper({aihelperID}),var(1)<=1) && {ai_var} > 0 && roundstate = 2\n".format(aihelperID=aihelperID,ai_var=ai_var))
        tempstate.insert(trigger+4,"triggerall = random <= (25+50*(p2movetype = H)+100*(enemynear,hitdefattr=sca,at && helper({aihelperID}),var(1)<=1 && abs(p2bodydist x) <= 60))*{ai_var}\n".format(aihelperID=aihelperID,ai_var=ai_var))
    if stateno == 100:        
        tempstate.insert(trigger,"triggerall = p2bodydist x > 100 || p2bodydist x > 60 && enemynear,vel x < 0 && p2movetype = H && p2stateno != [120,159]\n")
        tempstate.insert(trigger+1,"triggerall = p2statetype != L || p2bodydist x > 140\n")
        tempstate.insert(trigger+2,"triggerall = !inguarddist\n")
        tempstate.insert(trigger+3,"triggerall = {ai_var} > 0 && roundstate = 2 && random <= 13*{ai_var} && stateno != [100,102]\n".format(ai_var=ai_var))
    if stateno == 110:        
        tempstate.insert(trigger,"triggerall = p2bodydist x > 100 || (p2bodydist x > 60 || !ctrl) && enemynear,vel x < 0 && p2movetype = H && p2stateno != [120,159]\n")
        tempstate.insert(trigger+1,"triggerall = p2statetype != L || p2bodydist x > 130\n")
        tempstate.insert(trigger+2,"triggerall = !inguarddist || !ctrl\n")
        tempstate.insert(trigger+3,"triggerall = {ai_var} > 0 && roundstate = 2 && random <= 13*{ai_var} && stateno != [110,111]\n".format(ai_var=ai_var))
    if stateno == 105:        
        tempstate.insert(trigger,"triggerall = p2bodydist x = [0,80]\n")
        tempstate.insert(trigger+1,"triggerall = p2statetype != L && !inguarddist\n")
        tempstate.insert(trigger+2,"triggerall = p2movetype != H || p2stateno = [120,159]\n")
        tempstate.insert(trigger+3,"triggerall = {ai_var} > 0 && roundstate = 2 && random <= 3*{ai_var} && stateno != [105,106]\n".format(ai_var=ai_var))
    if stateno == 115:        
        tempstate.insert(trigger,"triggerall = p2bodydist x = [0,80]\n")
        tempstate.insert(trigger+1,"triggerall = p2statetype != L && !inguarddist\n")
        tempstate.insert(trigger+2,"triggerall = p2movetype != H || p2stateno = [120,159]\n")
        tempstate.insert(trigger+3,"triggerall = {ai_var} > 0 && roundstate = 2 && random <= 3*{ai_var} && stateno != [115,116]\n".format(ai_var=ai_var))           
    return tempstate

workdir = os.listdir()
deffilelist=[]
deffile = None
select_num=0
for s in workdir:
    if s[-4:].lower()==".def":
        deffilelist.append(s)
if deffilelist !=[]:
    for i in range(len(deffilelist)):
            print("{0} {1}".format(i+1,deffilelist[i]))
else:
    input("Can't open def file.Press enter to exit.")
    sys.exit()
if len(deffilelist)>1:
    select_num=input("Please select a def file(1-{0}):".format(i+1))    
try:
    s = int(select_num)-1
    if s < 0:
        s=0
    elif s > i:
        s=i
    deffile=deffilelist[s]
except ValueError as err:
    print(err)
select_num2=input("Please select mugenversion 1 Winmugen(default) 2 Mugen 1.0+(use AILevel) (1-2):")
if select_num2 == "2":
    ai_var="AILevel"
    ai_var_re="AILevel"
else:
    select_num2_1=input("Input an unused var number(0-59) for ai var(default:59):")
    if select_num2_1.isdigit() and 0<=int(select_num2_1)<=59:
        ai_var="var({select_num2_1})".format(select_num2_1=select_num2_1)
        ai_var_re=r"var\({select_num2_1}\)".format(select_num2_1=select_num2_1)
    else:
        ai_var="var(59)"
        ai_var_re=r"var\(59\)"
print(ai_var)
select_num3=input("Try to find proj and helper type attack?(slow and distance is usually not corrected) 1 Yes(default) 2 No:")
if select_num3 == "2":
    helper_key=0
else:
    helper_key=1
select_num4=input("Input an unused helper ID for AIhelper id(default 33000):")
if select_num4.isdigit():
    aihelperID=int(select_num4)
else:
    aihelperID=33000
select_num5=input("Add {ai_var} <= 0 for each state in ai cmd file? 1 Yes 2 No(default):".format(ai_var=ai_var))
if select_num5 == "1":
    cmd_aiswitch=1
else:
    cmd_aiswitch=0
if os.path.isfile(deffile):
    deflist = read_unknown_encoding(deffile)
else:
    input("Can't open def file.Press enter to exit.")
    sys.exit()
st =[]
localcoord_scale = 1
for line in deflist:
        airmatch=re.search(r'anim\s*=\s*(\S+.*)',cut(line),re.I)
        if airmatch is not None:air=airmatch.group(1).strip()
        cmdmatch=re.search(r'cmd\s*=\s*(\S+.*)',cut(line),re.I)
        if cmdmatch is not None:cmd=cmdmatch.group(1).strip()
        cnsmatch=re.search(r'cns\s*=\s*(\S+.*)',cut(line),re.I)
        if cnsmatch is not None:cns=cnsmatch.group(1).strip()
        stcmatch=re.search(r'stcommon\s*=\s*(\S+.*)',cut(line),re.I)
        if stcmatch is not None:stcommon=stcmatch.group(1).strip()
        stmatch=re.search(r'st\d*\s*=\s*(\S+.*)',cut(line),re.I)
        if stmatch is not None:st.append(stmatch.group(1).strip())
        localcoord=re.search(r'localcoord\s*=\s*(\d+)\s*,\s*(\d+)?.*',cut(line),re.I)
        if localcoord is not None:
            if localcoord.group(2) != None:localcoord_scale = float(240/int(localcoord.group(2)))
            else:localcoord_scale = float(320/int(localcoord.group(1)))
if cns != None and os.path.isfile(cns):
    print("Cns file:",cns)
else:
    input("Can't find cns file.Press enter to exit")
    sys.exit()
if air != None and os.path.isfile(air):
    actionlist=read_unknown_encoding(air)
    print("Air file:",air)
else:
    input("Can't find air file.Press enter to exit")
    sys.exit()
if cmd != None and os.path.isfile(cmd):
    print("Cmd file:",cmd)
else:
    input("Can't find cmd file.Press enter to exit")
    sys.exit()
if st != None:
    print("St file:",st)
else:
    input("Can't find st file.Press enter to exit")
    sys.exit()
temp = read_unknown_encoding(cns)
xscale,yscale = None,None
for line in temp:
    XS=re.search(r'xscale\s*=\s*(\d*\.?\d+)',line,re.I)
    if XS and xscale==None:xscale=float(XS.group(1))
    YS=re.search(r'yscale\s*=\s*(\d*\.?\d+)',line,re.I)
    if YS and yscale==None:yscale=float(YS.group(1))
    GBACK=re.search(r'ground\.back\s*=\s*(\d+)',line,re.I)
    if GBACK is not None:groundback=int(GBACK.group(1))
    GFRONT=re.search(r'ground\.front\s*=\s*(\d+)',line,re.I)
    if GFRONT is not None:groundfront=int(GFRONT.group(1))
    ABACK=re.search(r'air\.back\s*=\s*(\d+)',line,re.I)
    if ABACK is not None:airback=int(ABACK.group(1))
    AFRONT=re.search(r'air\.front\s*=\s*(\d+)',line,re.I)
    if AFRONT is not None:airfront=int(AFRONT.group(1))
    HPOSY=re.search(r'head\.pos\s*=\s*\S+\s*,\s*(-\d+)',line,re.I)
    if HPOSY is not None:headposy=int(HPOSY.group(1))
    MPOSY=re.search(r'mid\.pos\s*=\s*\S+\s*,\s*(-\d+)',line,re.I)
    if MPOSY is not None:midposy=int(MPOSY.group(1))
p1=re.compile(r'\[state',re.I)
p2=re.compile(r'type\s*=\s*(change|self)state',re.I)
flag=0
statedef=[]
state=[]
chance=[]
counter=[]
fight=[]
combo=[]
throw=[]
movetext=[]
newstfiles=[]
guardtext=["[State -3,Guard]\ntype = changestate\nvalue = 120\ntriggerall = {ai_var} > 0 && roundstate=2 && random <= 250*{ai_var}\ntriggerall = ctrl || stateno = [0,20]\ntriggerall = helper({aihelperID}),var(1) <= 1 || helper({aihelperID}),var(18) >= 0 || random%6=0 || (prevstateno != [120,155]) || stateno != [120,155]\ntrigger1 = inguarddist\ntrigger2 = numhelper({aihelperID})&& helper({aihelperID}),inguarddist\n\n".format(aihelperID=aihelperID,ai_var=ai_var)]
stfiles = st[:]
if stcommon not in st and os.path.isfile(stcommon):
    stfiles = stfiles+[str(stcommon)]
if cns not in st and os.path.isfile(cns):
    stfiles = stfiles+[str(cns)]
for stfile in stfiles:
    if os.path.isfile(stfile):
        newst=read_unknown_encoding(stfile)
        newstfilename=os.path.splitext(stfile)[0]+'-AI'+os.path.splitext(stfile)[1]
        NEWSTFILE=open(newstfilename,'w',encoding='utf-8')
        NEWSTFILE.writelines(newst)
        NEWSTFILE.close()
        newstfiles.append(newstfilename)
temp = read_unknown_encoding(cmd)
i = 0
statenolist =[]
distx_reach=None
disty_reach=None
distx=None
disty=None
for line in temp:
    m1 = p1.search(line)
    m2 = p2.search(line)
    i=i+1
    if flag >= 1 and m1==None:
        if m2:flag = 2
        if cut(line)!= None:state.append(cut(line))
    if (flag == 2 and m1) or i >= len(temp):
        stateno = findstateno(state)
        attacktype,stateattr,reach,attr=state_read(stateno)
        reach=list(reach)
        nextstate=stateattr[17]
        changestatetime=stateattr[18]
        totaltime=reach[1]
        state = clearcmd(state)
        #if stateno == 1620:print(state)
        if state != None and state [-1] != None and state[-1] != '' and state[-1][-1] != '\n':state[-1] += '\n'
        else:state.append('\n')
        trigger=None
        for lineno in range(len(state)):
                if "trigger1" in state[lineno].lower() and trigger == None:
                    if"value"in state[lineno-1].lower():
                        trigger=lineno
                    else:
                        trigger=lineno-1
        if reach[0] == None and (nextstate == None or nextstate < 200):
            if trigger and (stateno == 100 or stateno == 105 or stateno == 40 or stateno == 41 or stateno == 110 or stateno == 115):
                movetext = movetext+writestate2(state,stateno,trigger)
                statenolist.append(stateno)
            state = []
            if cut(line):state.append(cut(line))
            flag = 1
        if reach[2] == None and stateno >= 200 and nextstate != None and changestatetime != None:
            while nextstate != None and nextstate >= 200 and reach[2] == None:
                attacktype,stateattr,reach,attr=state_read(nextstate)
                reach=list(reach)
                if changestatetime >= 0:
                    if reach[0] != None:reach[0]=reach[0]+changestatetime
                    if reach[1] != None:reach[1]=reach[1]+changestatetime
                elif changestatetime < 0 and totaltime != None:
                    if reach[0] != None:reach[0]=reach[0]+totaltime+changestatetime+1
                    if reach[1] != None:reach[1]=reach[1]+totaltime+changestatetime+1
                if reach[2] != None or nextstate == None or nextstate < 200 or changestatetime == None:break
                nextstate=stateattr[17]
                if stateattr[18] != None and stateattr[18] >= 0:
                    changestatetime += stateattr[18]
                elif stateattr[18] != None and stateattr[18] < 0 and totaltime != None:
                    changestatetime += totaltime+stateattr[18]+1
                totaltime=reach[1]
            #if reach[2] != None:flag = 1
        #if stateno == 1620:print(stateno,nextstate,changestatetime,reach,stateattr,attacktype,state)
        if reach[2] != None:
            p2x2=reach[3]-airfront*(stateattr[1]=='A')-groundfront*(stateattr[1]!='A')
            if reach[2] < 0 and abs(reach[2]) > airback*(stateattr[1]=='A')+groundfront*(stateattr[1]!='A'):p2x1=reach[2]+airback*(stateattr[1]=='A')+groundfront*(stateattr[1]!='A')
            elif reach[2] >= airback*(stateattr[1]=='A')+groundfront*(stateattr[1]!='A')+10:p2x1=reach[2]-airback*(stateattr[1]=='A')-groundfront*(stateattr[1]!='A')
            else:p2x1 = 0
            if stateattr[1]!='A':p2y1,p2y2=reach[4],reach[5]
            else:
                if reach[7]==None:
                    p2y1=reach[4]
                else:p2y1=reach[4]-reach[7]
                if reach[6]==None:
                    p2y2=reach[5]
                else:p2y2=reach[5]-reach[6]
            state.insert(3,"triggerall = %s > 0 && roundstate = 2\n"%(ai_var))
            if attacktype == "reversal":
                p2x1=p2x1-20
                p2x2=p2x2+20
                p2y1=p2y1-20
                p2y2=p2y2+20
            if xscale != None and xscale != 0 and xscale != 1:
                if p2x1 != None:p2x1=int(p2x1*xscale)
                if p2x2 != None:p2x2=int(p2x2*xscale)
            if yscale != None and yscale != 0 and yscale != 1:
                if p2y1 != None:p2y1=int(p2y1*yscale)
                if p2y2 != None:p2y2=int(p2y2*yscale)
            if p2x2 < p2x1:p2x1,p2x2=p2x2,p2x1
            if p2y2 < p2y1:p2y1,p2y2=p2y2,p2y1
            if trigger != None:
                if reach[0] > 0:
                    if p2x1 != 0:
                        state.insert(trigger,"triggerall = p2bodydist x = [%d,%d+%d*(vel x+enemynear,vel x)]\n"%(p2x1,p2x2,reach[0]))
                    else:
                        state.insert(trigger,"triggerall = p2dist x >= 0 && p2bodydist x <= %d+%d*(vel x+enemynear,vel x)\n"%(p2x2,reach[0]))
                else:
                    if p2x1 != 0:
                        state.insert(trigger,"triggerall = p2bodydist x = [%d,%d]\n"%(p2x1,p2x2))
                    else:
                        state.insert(trigger,"triggerall = p2dist x >= 0 && p2bodydist x <=%d\n"%(p2x2))
                if reach[0] > 6 and stateattr[1]=='A':state.insert(trigger+1,"triggerall = pos Y+%d*vel y+const(movement.yaccel)*%d*%d*0.5 < 0\n"%(reach[0],reach[0],reach[0]+1))
                p2height=p2y2
                if p2height != None and p2height < 0:p2height=int(p2height*localcoord_scale)
                if p2height < -20 and stateattr[1] !='A':state.insert(trigger+1,"triggerall = !numhelper({aihelperID}) || helper({aihelperID}),var(16) <= {p2height}\n".format(aihelperID=aihelperID,p2height=p2height))
                if stateattr[1] != 'A':
                    if reach[0] > 1:
                        py = "triggerall = p2bodydist y + %d*enemynear,vel y >= %d\n"%(reach[0],p2y1)
                        pyh = "triggerall = p2statetype != A || p2bodydist y + %d*enemynear,vel y + enemynear,gethitvar(yaccel)*%d*%d*0.5 = [%d,-1]\n"%(reach[0],reach[0],reach[0]+1,p2y1)
                    elif reach[0] == 1:
                        py = "triggerall = p2bodydist y + enemynear,vel y >= %d\n"%(p2y1)
                        pyh = "triggerall = p2statetype != A || p2bodydist y + enemynear,vel y + enemynear,gethitvar(yaccel) = [%d,-1]\n"%(p2y1)
                    else:
                        py=pyh="triggerall = p2statetype != A || p2bodydist y = [%d,%d]\n"%(p2y1,p2y2)
                    if stateattr[3] != None and '-A' in stateattr[3]: py=pyh="triggerall = p2statetype != A\n"
                else:
                    if reach[0] > 0:
                        py=pyh="triggerall = p2bodydist y - %d*(vel y - enemynear,vel y) = [%d,%d]\n"%(reach[0],p2y1,p2y2)
                    elif reach[0] == 1:
                        py=pyh="triggerall = p2bodydist y - vel y + enemynear,vel y = [%d,%d]\n"%(p2y1,p2y2)
                    else:
                        py=pyh="triggerall = p2bodydist y = [%d,%d]\n"%(p2y1,p2y2)
            #if stateno == 1620:print(p2x1,p2x2,reach[0],trigger,attr,py)
            if p2x1 != None and p2x2 != None and reach[0] != None and trigger and attr != None and (py != None or pyh != None):
                tempset=None
                if attacktype == "reversal" and reach[0]<=1:
                    tempset = writecounter2(py,attr)
                    counter.append(tempset)
                tempset=None
                if stateattr[9] ==1 and stateattr[7] <= 1:
                    tempset = writecounter3(py,reach[0],stateattr[6],stateattr[8])
                    counter.append(tempset)
                tempset=None
                if reach[0]<20 and (stateattr[9] !=1 or (stateattr[7] !=None and stateattr[7] > 1)) and attacktype != "reversal":
                    tempset = writecounter(py,reach[0],attr)
                if tempset != None:counter.append(tempset)
                tempset=None
                if reach[0]<40 and attacktype != "reversal":
                    if attacktype=="helper":
                        tempset = writechance(py,reach[0],attr,reach[1])
                    else:
                        tempset = writechance(py,reach[0],stateattr[3],reach[1])
                if tempset != None:chance.append(tempset)
                if '-B' not in attr and attacktype != "reversal":
                    tempset=None
                    tempset = writecombo(pyh,reach[0],stateattr[2],stateattr[9])
                    if tempset != None:combo.append(tempset)                
                if (stateattr[2] < 1000 and '-U' not in attr) and attacktype != "reversal":
                    tempset=None
                    tempset = writefight(py,reach[0],attr,stateattr[1],reach[1],stateattr[2])
                    if tempset != None:fight.append(tempset)
                if '-U' in attr:                    
                    throw=throw+writethrow(py,attr,reach[0])
                statenolist.append(stateno)                
        state = []       
        if cut(line):state.append(cut(line))
        flag = 1
    if m1:        
        if flag == 1:state=[]
        if cut(line):state.append(cut(line))
        if flag == 0:flag=1            
num_cmd = 0
insertpoint=0
s,s1,aistart=0,1,0
r_command = ['U','D','F','B','DF','DB','UF','UB','a','b','c','x','y','z','s']
singlecmd = ['up','fwd','back','down','start','a','b','c','x','y','z']
singlecmd2_name = []
singlecmd2_command = []
singlecmd2_time = []
#print(statenolist)
for lino in range(len(temp)):
    temp[lino]=cut(temp[lino])
    p = re.compile(r'\[Command\]',re.I)
    p1 = re.compile(r'name\s*=\s*"(up|fwd|back|down|start|[abcxyz])"',re.I)
    #p2 = re.compile(fr'{ai_var_re}\s*<?=\s*0|!\s*{ai_var_re}',re.I)    
    p3 = re.compile(r'^type\s*=\s*(change|self)state',re.I)
    p4 = re.compile(r'^value\s*=\s*(\d+)',re.I)    
    m1 = p1.search(temp[lino])
    #m2 = p2.search(temp[lino])
    m3 = p3.search(temp[lino])
    m4 = p4.search(temp[lino])    
    if s==0:insertpoint += 1        
    if p.search(temp[lino]):
        s=1
        num_cmd +=1
    if m1 and m1.group(1) in singlecmd:        
        singlecmd.remove(m1.group(1))
        singlecmd2_name.append(m1.group(1)+'2')
        singlecmd2_command.append(temp[lino+1])
        singlecmd2_time.append(temp[lino+2])
    if s1 == 1 and (m4 and int(m4.group(1)) not in statenolist) and cmd_aiswitch != 1:s1=0
    if s1==0 and m3:s1=1
    if s1==1 and ("triggerall" in temp[lino].lower() or "trigger1" in temp[lino].lower()) :
        temp.insert(lino,"triggerall = {ai_var} <= 0\n".format(ai_var=ai_var))
        s1 = 0
useable_cmd = 127-num_cmd
print(useable_cmd)
aiswitch = ['[State -3]\n','Type = varset\n','Triggerall = {ai_var} = 0 && roundstate < 3\n'.format(ai_var=ai_var)]
if ai_var=="AILevel":aiswitch=[]
if useable_cmd > len(singlecmd) and ai_var!="AILevel":
    useable_cmd -=len(singlecmd)
    for t in range(len(singlecmd)):
        temp.insert(insertpoint-1,"[Command]\n")
        temp.insert(insertpoint,'name = "'+singlecmd[t]+'"\n')
        singlecmd2_name.append(singlecmd[t]+'2')
        if singlecmd[t] in ['up','fwd','back','down']:
            temp.insert(insertpoint+1,'command = '+singlecmd[t][0].upper()+'\n')
            singlecmd2_command.append('command = '+singlecmd[t][0].upper()+'\n')
        else:
            temp.insert(insertpoint+1,'command = '+singlecmd[t]+'\n')
            singlecmd2_command.append('command = '+singlecmd[t]+'\n')
        temp.insert(insertpoint+2,'time = 1\n\n')
if useable_cmd > len(singlecmd2_name) and ai_var!="AILevel":
    useable_cmd -=len(singlecmd2_name)
    for t in range(len(singlecmd2_name)):
        temp.insert(insertpoint-1,"[Command]\n")
        temp.insert(insertpoint,'name = "'+singlecmd2_name[t]+'"\n')
        temp.insert(insertpoint+1,singlecmd2_command[t])
        temp.insert(insertpoint+2,'time = 1\n\n')
        trigger_line="trigger"+str(t+1)+' = '+'command = "%s" ^^ command = "%s"\n'%(singlecmd2_name[t][:-1],singlecmd2_name[t])
        aiswitch.append(trigger_line)
if useable_cmd-11 >= 20:useable_cmd = useable_cmd-11
if useable_cmd >= 1 and ai_var!="AILevel":
    for n in range(min(50,useable_cmd-1)):
        useable_cmd -=1
        temp.insert(insertpoint-1,"[Command]\n")
        temp.insert(insertpoint,'name = "AI'+str(n)+'"\n')
        aicommand = ','.join(random.sample(r_command,random.randint(7,15)))
        temp.insert(insertpoint+1,'command = '+str(aicommand)+'\n')
        temp.insert(insertpoint+2,'time = 0\n\n')        
        aiswitch.append("trigger"+str(n+len(singlecmd2_name)+1)+' = '+'command = "AI'+str(n)+'"\n')
if useable_cmd <= len(singlecmd) and len(singlecmd2_name)<10 and ai_var!="AILevel":aistart=1
#if aistart:
#    aiswitch.append("trigger"+str(n+len(singlecmd2_name)+2)+' = '+'numhelper(11990+id) && helper(11990+id),var(59)> 0\n')
if ai_var!="AILevel":
    aiswitch.append("{ai_var} = 8\n".format(ai_var=ai_var))
    aiswitch.append("ignorehitpause = 1\n\n")
aiswitch.append('[State -3]\ntype = helper\ntrigger1 = !numhelper({aihelperID})\nhelpertype = normal\nname = "AIconfig"\n'.format(aihelperID=aihelperID))
aiswitch.append('ID = {aihelperID}\nstateno = {aihelperID}\npostype = p1\npos = 0,0\nfacing = -1\n'.format(aihelperID=aihelperID))
aiswitch.append('ownpal = 1\nIgnorehitpause = 1\npausemovetime=2147483647\nsupermovetime=2147483647\nSprPriority = 7\npersistent = 0\n\n')
aiswitch.append('[State -3]\ntype = changestate\nTrigger1= ishelper({aihelperID})&&stateno != {aihelperID}\nvalue = {aihelperID}\n\n'.format(aihelperID=aihelperID))
#if aistart:
#    aiswitch.append('[State -3]\ntype = helper\ntriggerall = !ishelper\ntriggerall = roundstate < 2 || stateno = 0 && !ctrl\n')
#    aiswitch.append('trigger1=!numhelper(11990+id) && alive && {ai_var} = 0\nhelpertype = normal\nname = "AIstart"\n'.format(ai_var=ai_var))
#    aiswitch.append('ID = 11990+id\nstateno = 11990\nkeyctrl = 1\npos = 9999,9999\n')
#    aiswitch.append('pausemovetime=2147483647\nsupermovetime=2147483647\nSprPriority = 7\npersistent = 0\n\n')
#    aiswitch.append('[State -3]\ntype = changestate\nTrigger1 = ishelper\nTrigger1= ishelper(11990+id) && stateno != 11990\nvalue = 11990\n\n')
CMDAI=open(os.path.splitext(cmd)[0]+'-AI'+os.path.splitext(cmd)[1],'w',encoding='utf-8')
CMDAI.writelines(temp)
CMDAI.close()
print(os.path.splitext(cmd)[0]+'-AI'+os.path.splitext(cmd)[1]+' is saved')
state3 = []
state3state,guardstate = [],[]
state3file = None
guardfile = None
p = re.compile(r'\[Statedef\s*(-?\d+)',re.I)
for cnsfile in newstfiles:
    if os.path.isfile(cnsfile):
        ST=open(cnsfile,'r',encoding='utf-8')
        tempST=ST.readlines()
        ST.close()       
        for line in tempST:
            m = p.search(line)          
            if m:stateno2 = int(m.group(1))
            if m and stateno2 == 120:
                guardfile=cnsfile
                guardstate=tempST[:]
            if m and stateno2 == -3:
                state3file=cnsfile
                state3state=tempST[:]
            if state3file != None and guardfile != None and guardfile != stcommon:break
s3=None
linolist=[]
if state3file != None:
    s=0
    i=0
    start,end = 0,0    
    for line in state3state:        
        m = p.search(line)
        if m:
            stateno2 = int(m.group(1))
            if stateno2 != -3:s3=0
        if s==1:
            if m:
                s3=0
                s = 2
                break
            else:
                state3.append(line)
                linolist.append(i)                
        if stateno2 == -3 and m and s==0:
            state3.append(line)
            linolist.append(i)
            start = i
            s=1
            if s3==None:s3=1
        i +=1
if len(linolist) >= 1 and s3 == 0:
    for k in range(i-start):
        state3state.pop(start)
if len(state3) >= 1:state3[-1]=state3[-1]+'\n\n'
if state3file == guardfile !=None:
    guardstate = state3state[:]
    state3state = []
elif state3file != None and s3 == 0:
    STATE3 = open(state3file,'w',encoding='utf-8')
    STATE3.writelines(state3state)
    STATE3.close()
    print(state3file+' is saved')
if state3file == None or state3 == None or state3==[]:state3=["[Statedef -3]\n"]
counter=procArray(counter)
chance=procArray(chance)
combo=procArray(combo)
fight=procArray(fight)
aihelperdef=['[Statedef {aihelperID}]\n'.format(aihelperID=aihelperID)]
aihelper=['Ctrl = 0\n', '\n', '[State 33000]\n', 'type=selfstate\n', 'trigger1=!ishelper\n', 'value=0\n', '\n', '[State 33000]\n', 'Type = AssertSpecial\n', 'Trigger1 = IsHelper\n', 'flag = invisible\n', '\n', '[State 33000]\n', 'type = nothitby\n', 'trigger1 = 1\n', 'value = sca\n', '\n', '[STATE 超必殺判定]\n', 'type = VarSet\n', 'triggerall = Time\n', 'trigger1 = var(10)>enemy,power\n', 'var(9) = (var(10)-enemy,power)\n', '\n', '[STATE 超必殺判定(リセット)]\n', 'type = VarSet\n', 'triggerall = Time\n', 'trigger1 = enemynear,movetype=H\n', 'trigger2 = enemynear,stateno=[0,105]\n', 'trigger3 = enemynear,stateno=[120,155]\n', 'trigger4 = enemynear,stateno=[5000,5210]\n', 'var(9) = 0\n', '\n', '[STATE ENEMY,POWER]\n', 'type = VarSet\n', 'trigger1 = Time\n', 'var(10) = enemynear,power\n', '\n', ';めくりガード対応ヘルパー\n', '[State 4444]\n', 'Type = PosSet\n', 'Trigger1 = 1\n', 'X = Ceil(EnemyNear,Pos X)-10*Facing\n', 'Y = Ceil(EnemyNear,Pos Y)\n', 'IgnoreHitPause = 1\n', 'SuperMoveTime = 9999\n', 'PauseMoveTime = 9999\n', '\n', '[State 4444]\n', 'Type = Turn\n', 'Trigger1 = Facing = EnemyNear,Facing\n', 'IgnoreHitPause = 1\n', 'SuperMoveTime = 9999\n', 'PauseMoveTime = 9999\n', '\n', ';相手がAIか判別\n', '\n', '[state -2,ai]\n', 'type = varset\n', 'trigger1 = roundstate < 2\n', 'var(4) = 0\n', '\n', '[state -2,ai]\n', 'type = varset\n', 'trigger1 = abs(var(4)) > 10\n', 'var(4) = ifelse(var(4) > 0,10,-10)\n', '\n', '[state -2,ai]\n', 'type = varadd\n', 'trigger1 = (enemynear,stateno=[120,132])&&(enemynear,prevstateno!=[120,155])\n', 'trigger1 = enemynear,time <= 1\n', 'trigger1 = enemynear,command!="holdback"\n', 'var(4) = 1\n', '\n', '[state -2,ai]\n', 'type = varadd\n', 'trigger1 = (enemynear,stateno=[120,132])&&(enemynear,prevstateno!=[120,155])\n', 'trigger1 = enemynear,time <= 1\n', 'trigger1 = enemynear,command="holdback"\n', 'var(4) = -1\n', '\n', '[State -1, 直前行動]\n', 'type = VarSet\n', 'trigger1 = root,movetype = H\n', 'trigger1 = root,prevstateno != [5000,5799]\n', 'trigger1 = root,stateno != [120,159]\n', 'var(13) = root,prevstateno\n', '\n', '[State -1, 直前行動]\n', 'type = VarSet\n', 'trigger1 = root,movetype = A \n', 'var(14) = root,stateno\n', '\n', '[State -1, Preview State]\n', 'type = VarSet\n', 'trigger1 = var(14) != 0\n', 'trigger1 = enemynear,movetype != H || enemynear,stateno = [150,159]\n', 'var(14) = 0\n', '\n', '[State 32000]\n', 'type = varset\n', 'trigger1 = var(15) != 0\n', 'trigger1 = enemynear,movetype != H && root,movetype != A\n', 'var(15) = 0\n', '\n', '[State 32000]\n', 'type = varset\n', 'trigger1 = var(15) = 0\n', 'trigger1 = enemynear,movetype = H || root,hitdefattr = sca,at\n', 'var(15) = root,time\n', '\n', '[State 32000]\n', 'type = varset\n', 'trigger1 = enemynear,statetype = S || enemynear,statetype = L\n', 'var(16) = enemynear,const(size.head.pos.y)\n', '\n', '[State 32000]\n', 'type = varset\n', 'trigger1 = enemynear,statetype = C\n', 'var(16) = enemynear,const(size.mid.pos.y)\n', '\n', '[State 32000]\n', 'type = varset\n', 'trigger1 = enemynear,statetype = A\n', 'var(16) = -99\n', '\n', '[State -2,recover]\n', 'type=varadd\n', 'trigger1=var(17)>0\n', 'var(17)=-1\n', 'ignorehitpause=1\n', '\n', '[State -2,recover]\n', 'type=varset\n', 'triggerall=var(17)>0\n', 'trigger1=enemynear,movetype!=H\n', 'var(17)=0\n', '\n', '[State -2,ガード硬直]\n', 'type=varset\n', 'triggerall=enemynear,movetype=H\n', 'triggerall=enemynear,stateno<200\n', 'triggerall=enemynear,statetype=A\n', 'trigger1=!enemynear,gethitvar(fall)\n', 'trigger1=!(enemynear,hitshakeover)\n', 'trigger1=enemynear,time=1||var(17)=0\n', 'var(17)=enemynear,gethitvar(ctrltime)+enemynear,gethitvar(hitshaketime)+1\n', 'ignorehitpause=1\n', '\n', '[State -2,ガード硬直]\n', 'type=varset\n', 'triggerall=enemynear,movetype=H\n', 'triggerall=enemynear,stateno<200\n', 'triggerall=enemynear,statetype!=A\n', 'trigger1=!enemynear,gethitvar(fall)\n', 'trigger1=!(enemynear,hitshakeover)\n', 'trigger1=enemynear,time=1||var(17)=0\n', 'var(17)=ifelse(enemynear,gethitvar(ctrltime)<enemynear,gethitvar(hittime),enemynear,gethitvar(ctrltime),enemynear,gethitvar(hittime))+enemynear,gethitvar(hitshaketime)+1\n', 'ignorehitpause=1\n', '\n', '[State -2,のけぞり時間]\n', 'type=varset\n', 'triggerall=enemynear,movetype=H\n', 'triggerall=enemynear,stateno>199\n', 'trigger1=!enemynear,gethitvar(fall)\n', 'trigger1=!(enemynear,hitshakeover)\n', 'trigger1=enemynear,time=1\n', 'var(17)=enemynear,gethitvar(hittime)+enemynear,gethitvar(hitshaketime)+1\n', 'ignorehitpause=1\n', '\n', '[State -2,受身不能時間]\n', 'type=varset\n', 'triggerall=enemynear,stateno>199\n', 'triggerall=enemynear,movetype=H\n', 'triggerall=enemynear,statetype!=L\n', 'trigger1=enemynear,gethitvar(fall)\n', 'trigger1=!(enemynear,hitshakeover)\n', 'trigger1=enemynear,time=1\n', 'var(17)=enemynear,gethitvar(fall.recovertime)-1\n', 'ignorehitpause=1\n', '\n', '[State -2,受身不能時間]\n', 'type=varset\n', 'triggerall=numenemy>=2\n', 'triggerall=enemynear,stateno>199\n', 'triggerall=enemynear,movetype=H\n', 'triggerall=enemynear,statetype!=L\n', 'trigger1=enemynear,gethitvar(fall)\n', 'trigger1=var(17)<enemynear,gethitvar(fall.recovertime)-100\n', 'var(17)=enemynear,gethitvar(fall.recovertime)-100\n', 'ignorehitpause=1\n', '\n', '[State -2,受身不能時間]\n', 'type=varset\n', 'triggerall=enemynear,stateno>199\n', 'triggerall=enemynear,movetype=H\n', 'triggerall=enemynear,statetype!=L\n', 'trigger1=!enemynear,gethitvar(fall.recover)\n', 'trigger1=enemynear,gethitvar(fall)\n', 'trigger2=enemynear,stateno=5070\n', 'var(17)=999\n', 'ignorehitpause=1\n', '\n', '[State -3,up]\n', 'type = varset\n', 'trigger1 = var(18) <= 0\n', 'trigger1 = enemynear,statetype = L\n', 'var(18) = 15\n', '\n', '[State -3,up]\n', 'type = varset\n', 'trigger1 = var(18) = 0\n', 'trigger1 = root,statetype = L\n', 'var(18) = -15\n', '\n', '[State -3,up]\n', 'type = varadd\n', 'triggerall = var(18) != 0\n', 'trigger1 = var(18) > 0\n', 'trigger1 = enemynear,statetype != L\n', 'trigger2 = var(18) < 0\n', 'trigger2 = root,statetype != L\n', 'var(18) = ifelse(var(18) > 0,-1,1)\n', '\n', ';相手のヘルパー数調べ\n', '[state -1];ヘルパー数調べの準備\n', 'type=varset\n', 'trigger1 = roundstate!=2\n', 'var(19)=9999\n', 'supermove = 1\n', 'ignorehitpause = 1\n', 'pausemovetime = 99999\n', 'supermovetime = 99999\n', '\n', '\n', '[state -1];ヘルパー数を調べる\n', 'type=varset\n', 'var(19)=enemynear,numhelper\n', 'trigger1 = roundstate=2\n', 'trigger1 = enemynear,ctrl=1\n', 'trigger1 = var(19)>=enemynear,numhelper\n', 'trigger2 = enemynear,movetype != A\n', 'trigger2 = root,inguarddist = 0\n', 'trigger2 = (enemynear,stateno =[5000,5999]) || enemynear,stateno = [50,200)\n', 'trigger2 = root,stateno != [120,162]\n', 'trigger2 = root,stateno != [5000,5300]\n', 'trigger2 = root,movetype != H\n', 'trigger2 = root,hitpausetime = 0 && enemynear,hitpausetime = 0\n', 'ignorehitpause = 1\n', '\n', '[state -1]\n', 'type=varset\n', 'triggerall = var(20) != 0\n', 'trigger1 = root,movetype = A\n', 'trigger2 = root,movetype = H && root,stateno != [120,159]\n', 'var(20)=0\n', 'ignorehitpause = 1\n', '\n', '[state -1]\n', 'type=varadd\n', 'trigger1 = root,movetype = H && !root,ctrl && root,stateno = [150,159]\n', 'var(20)=1\n', 'ignorehitpause = 1\n', '\n', '[state -1]\n', 'type=varadd\n', 'trigger1 = var(20) > 0\n', 'trigger1 = root,movetype != H\n', 'var(20)=-1\n', 'ignorehitpause = 1\n', '\n', '[state -1]\n', 'type=varset\n', 'trigger1 = root,movehit = 1\n', 'var(21)=ceil(root,p2bodydist y)\n', 'ignorehitpause = 1\n', '\n', '[State -3]\n', 'Type = VarSet\n', 'Trigger1 = enemynear,movetype = A\n', 'Trigger1 = enemynear,time <= 1\n', 'trigger2 = enemynear,movetype != A\n', 'var(0) = 0\n', 'IgnoreHitPause = 1\n', '\n', '[State -2,time]\n', 'Type = VarSet\n', 'Trigger1 = enemynear,movetype = A\n', 'Trigger1 = enemynear,hitdefattr = sca,aa,ap,at\n', 'trigger1 = var(0) = 0\n', 'var(0) = enemynear,time\n', 'IgnoreHitPause = 1\n', '\n', '[State -3]\n', 'Type = VarSet\n', 'Trigger1 = enemynear,movetype = A\n', 'Trigger1 = enemynear,time <= 1\n', 'trigger2 = enemynear,movetype != A\n', 'var(8) = 0\n', 'IgnoreHitPause = 1\n', '\n', '[State -3]\n', 'Type = VarSet\n', 'Trigger1 = enemynear,movetype = A\n', 'Trigger1 = root,movetype = H\n', 'trigger1 = root,time <= 1\n', 'trigger1 = var(8) = 0\n', 'var(8) = enemynear,time\n', 'IgnoreHitPause = 1\n', '\n', '[State 7777,shield]\n', 'Type = VarSet\n', 'triggerall = var(1) != 0\n', 'Trigger1 = EnemyNear,time < 1\n', 'trigger2 = enemynear,movetype != A\n', 'trigger3 = var(7) = 1\n', 'var(1)=0\n', 'IgnoreHitPause=1\n', '\n', '[State 7777,shield]\n', 'Type = VarAdd\n', 'Trigger1 = EnemyNear,MoveType=A\n', 'Trigger1 = EnemyNear,HitDefAttr = SCA,AA,AP,AT\n', 'var(1)=1\n', 'IgnoreHitPause=1\n', '\n', '[State 7777,shield]\n', 'Type = Varset\n', 'triggerall = var(7) != 1\n', 'Trigger1 = EnemyNear,time <= 1\n', 'Trigger1 = EnemyNear,HitDefAttr = SCA,AA,AP\n', 'var(7)=1\n', 'IgnoreHitPause=1\n', '\n', '[State 7777,shield]\n', 'Type = Varset\n', 'triggerall = var(7) != 0\n', 'Trigger1 = EnemyNear,HitDefAttr = SCA,AA,AP,AT\n', 'trigger1 = root,movetype = H || enemynear,movecontact || enemynear,movereversed\n', 'trigger2 = enemynear,movetype != A\n', 'trigger3 = !enemynear,hitdefattr = sca,aa,ap\n', 'var(7)=0\n', 'IgnoreHitPause=1\n', '\n', '[State -2,stateno1]\n', 'Type = Varset\n', 'TriggerAll = Enemy,TeamMode = Single || Enemy,TeamMode = Turns\n', 'Trigger1 = enemynear,movetype != A\n', 'V = 2\n', 'value = 0\n', 'IgnoreHitPause = 1\n', '\n', '[State -2,time]\n', 'Type = VarSet\n', 'TriggerAll = Enemy,TeamMode = Single || Enemy,TeamMode = Turns\n', 'Trigger1 = enemynear,movetype != A\n', 'V = 3\n', 'value = 0\n', 'IgnoreHitPause = 1\n', '\n', '[State 33000,time]\n', 'Type = Null\n', 'TriggerAll = Enemy,TeamMode = Single || Enemy,TeamMode = Turns\n', 'TriggerAll = Var(2) != Enemynear,Stateno\n', 'Trigger1 = floor(fvar(0)) = Enemynear,Stateno\n', 'trigger1 = var(2) := floor(fvar(0)) || 1\n', 'trigger1 = var(3) := floor(1000*(fvar(0)-floor(fvar(0))))\n', 'Trigger2 = floor(fvar(1)) = Enemynear,Stateno\n', 'trigger2 = var(2) := floor(fvar(1)) || 1\n', 'trigger2 = var(3) := floor(1000*(fvar(1)-floor(fvar(1))))\n', 'Trigger3 = floor(fvar(2)) = Enemynear,Stateno\n', 'trigger3 = var(2) := floor(fvar(2)) || 1\n', 'trigger3 = var(3) := floor(1000*(fvar(2)-floor(fvar(2))))\n', 'Trigger4 = floor(fvar(3)) = Enemynear,Stateno\n', 'trigger4 = var(2) := floor(fvar(3)) || 1\n', 'trigger4 = var(3) := floor(1000*(fvar(3)-floor(fvar(3))))\n', 'Trigger5 = floor(fvar(4)) = Enemynear,Stateno\n', 'trigger5 = var(2) := floor(fvar(4)) || 1\n', 'trigger5 = var(3) := floor(1000*(fvar(4)-floor(fvar(4))))\n', 'Trigger6 = floor(fvar(5)) = Enemynear,Stateno\n', 'trigger6 = var(2) := floor(fvar(5)) || 1\n', 'trigger6 = var(3) := floor(1000*(fvar(5)-floor(fvar(5))))\n', 'Trigger7 = floor(fvar(6)) = Enemynear,Stateno\n', 'trigger7 = var(2) := floor(fvar(6)) || 1\n', 'trigger7 = var(3) := floor(1000*(fvar(6)-floor(fvar(6))))\n', 'Trigger8 = floor(fvar(7)) = Enemynear,Stateno\n', 'trigger8 = var(2) := floor(fvar(7)) || 1\n', 'trigger8 = var(3) := floor(1000*(fvar(7)-floor(fvar(7))))\n', 'Trigger9 = floor(fvar(8)) = Enemynear,Stateno\n', 'trigger9 = var(2) := floor(fvar(8)) || 1\n', 'trigger9 = var(3) := floor(1000*(fvar(8)-floor(fvar(8))))\n', 'Trigger10 = floor(fvar(9)) = Enemynear,Stateno\n', 'trigger10 = var(2) := floor(fvar(9)) || 1\n', 'trigger10 = var(3) := floor(1000*(fvar(9)-floor(fvar(9))))\n', 'Trigger11 = floor(fvar(10)) = Enemynear,Stateno\n', 'trigger11 = var(2) := floor(fvar(10)) || 1\n', 'trigger11 = var(3) := floor(1000*(fvar(10)-floor(fvar(10))))\n', 'Trigger12 = floor(fvar(11)) = Enemynear,Stateno\n', 'trigger12 = var(2) := floor(fvar(11)) || 1\n', 'trigger12 = var(3) := floor(1000*(fvar(11)-floor(fvar(11))))\n', 'Trigger13 = floor(fvar(12)) = Enemynear,Stateno\n', 'trigger13 = var(2) := floor(fvar(12)) || 1\n', 'trigger13 = var(3) := floor(1000*(fvar(12)-floor(fvar(12))))\n', 'Trigger14 = floor(fvar(13)) = Enemynear,Stateno\n', 'trigger14 = var(2) := floor(fvar(13)) || 1\n', 'trigger14 = var(3) := floor(1000*(fvar(13)-floor(fvar(13))))\n', 'Trigger15 = floor(fvar(14)) = Enemynear,Stateno\n', 'trigger15 = var(2) := floor(fvar(14)) || 1\n', 'trigger15 = var(3) := floor(1000*(fvar(14)-floor(fvar(14))))\n', 'Trigger16 = floor(fvar(15)) = Enemynear,Stateno\n', 'trigger16 = var(2) := floor(fvar(15)) || 1\n', 'trigger16 = var(3) := floor(1000*(fvar(15)-floor(fvar(15))))\n', 'Trigger17 = floor(fvar(16)) = Enemynear,Stateno\n', 'trigger17 = var(2) := floor(fvar(16)) || 1\n', 'trigger17 = var(3) := floor(1000*(fvar(16)-floor(fvar(16))))\n', 'Trigger18 = floor(fvar(17)) = Enemynear,Stateno\n', 'trigger18 = var(2) := floor(fvar(17)) || 1\n', 'trigger18 = var(3) := floor(1000*(fvar(17)-floor(fvar(17))))\n', 'Trigger19 = floor(fvar(18)) = Enemynear,Stateno\n', 'trigger19 = var(2) := floor(fvar(18)) || 1\n', 'trigger19 = var(3) := floor(1000*(fvar(18)-floor(fvar(18))))\n', 'Trigger20 = floor(fvar(19)) = Enemynear,Stateno\n', 'trigger20 = var(2) := floor(fvar(19)) || 1\n', 'trigger20 = var(3) := floor(1000*(fvar(19)-floor(fvar(19))))\n', 'Trigger21 = floor(fvar(20)) = Enemynear,Stateno\n', 'trigger21 = var(2) := floor(fvar(20)) || 1\n', 'trigger21 = var(3) := floor(1000*(fvar(20)-floor(fvar(20))))\n', 'Trigger22 = floor(fvar(21)) = Enemynear,Stateno\n', 'trigger22 = var(2) := floor(fvar(21)) || 1\n', 'trigger22 = var(3) := floor(1000*(fvar(21)-floor(fvar(21))))\n', 'Trigger23 = floor(fvar(22)) = Enemynear,Stateno\n', 'trigger23 = var(2) := floor(fvar(22)) || 1\n', 'trigger23 = var(3) := floor(1000*(fvar(22)-floor(fvar(22))))\n', 'Trigger24 = floor(fvar(23)) = Enemynear,Stateno\n', 'trigger24 = var(2) := floor(fvar(23)) || 1\n', 'trigger24 = var(3) := floor(1000*(fvar(23)-floor(fvar(23))))\n', 'Trigger25 = floor(fvar(24)) = Enemynear,Stateno\n', 'trigger25 = var(2) := floor(fvar(24)) || 1\n', 'trigger25 = var(3) := floor(1000*(fvar(24)-floor(fvar(24))))\n', 'Trigger26 = floor(fvar(25)) = Enemynear,Stateno\n', 'trigger26 = var(2) := floor(fvar(25)) || 1\n', 'trigger26 = var(3) := floor(1000*(fvar(25)-floor(fvar(25))))\n', 'Trigger27 = floor(fvar(26)) = Enemynear,Stateno\n', 'trigger27 = var(2) := floor(fvar(26)) || 1\n', 'trigger27 = var(3) := floor(1000*(fvar(26)-floor(fvar(26))))\n', 'Trigger28 = floor(fvar(27)) = Enemynear,Stateno\n', 'trigger28 = var(2) := floor(fvar(27)) || 1\n', 'trigger28 = var(3) := floor(1000*(fvar(27)-floor(fvar(27))))\n', 'Trigger29 = floor(fvar(28)) = Enemynear,Stateno\n', 'trigger29 = var(2) := floor(fvar(28)) || 1\n', 'trigger29 = var(3) := floor(1000*(fvar(28)-floor(fvar(28))))\n', 'Trigger30 = floor(fvar(29)) = Enemynear,Stateno\n', 'trigger30 = var(2) := floor(fvar(29)) || 1\n', 'trigger30 = var(3) := floor(1000*(fvar(29)-floor(fvar(29))))\n', 'Trigger31 = floor(fvar(30)) = Enemynear,Stateno\n', 'trigger31 = var(2) := floor(fvar(30)) || 1\n', 'trigger31 = var(3) := floor(1000*(fvar(30)-floor(fvar(30))))\n', 'Trigger32 = floor(fvar(31)) = Enemynear,Stateno\n', 'trigger32 = var(2) := floor(fvar(31)) || 1\n', 'trigger32 = var(3) := floor(1000*(fvar(31)-floor(fvar(31))))\n', 'Trigger33 = floor(fvar(32)) = Enemynear,Stateno\n', 'trigger33 = var(2) := floor(fvar(32)) || 1\n', 'trigger33 = var(3) := floor(1000*(fvar(32)-floor(fvar(32))))\n', 'Trigger34 = floor(fvar(33)) = Enemynear,Stateno\n', 'trigger34 = var(2) := floor(fvar(33)) || 1\n', 'trigger34 = var(3) := floor(1000*(fvar(33)-floor(fvar(33))))\n', 'Trigger35 = floor(fvar(34)) = Enemynear,Stateno\n', 'trigger35 = var(2) := floor(fvar(34)) || 1\n', 'trigger35 = var(3) := floor(1000*(fvar(34)-floor(fvar(34))))\n', 'Trigger36 = floor(fvar(35)) = Enemynear,Stateno\n', 'trigger36 = var(2) := floor(fvar(35)) || 1\n', 'trigger36 = var(3) := floor(1000*(fvar(35)-floor(fvar(35))))\n', 'Trigger37 = floor(fvar(36)) = Enemynear,Stateno\n', 'trigger37 = var(2) := floor(fvar(36)) || 1\n', 'trigger37 = var(3) := floor(1000*(fvar(36)-floor(fvar(36))))\n', 'Trigger38 = floor(fvar(37)) = Enemynear,Stateno\n', 'trigger38 = var(2) := floor(fvar(37)) || 1\n', 'trigger38 = var(3) := floor(1000*(fvar(37)-floor(fvar(37))))\n', 'Trigger39 = floor(fvar(38)) = Enemynear,Stateno\n', 'trigger39 = var(2) := floor(fvar(38)) || 1\n', 'trigger39 = var(3) := floor(1000*(fvar(38)-floor(fvar(38))))\n', 'Trigger40 = floor(fvar(39)) = Enemynear,Stateno\n', 'trigger40 = var(2) := floor(fvar(39)) || 1\n', 'trigger40 = var(3) := floor(1000*(fvar(39)-floor(fvar(39))))\n', 'IgnoreHitPause = 1\n', '\n', '\n', '[State -2,pointer]\n', 'Type = VarAdd\n', 'TriggerAll = Enemy,TeamMode = Single || Enemy,TeamMode = Turns\n', 'Trigger1 = var(5) > 0 && var(0) != 0\n', 'var(6) = 1\n', 'IgnoreHitPause = 1\n', '\n', '[State -2,reset]\n', 'Type = VarSet\n', ';TriggerAll = Root,var(59) > 0\n', 'Trigger1 = Var(5) > 0 && var(0) != 0\n', 'var(5) = 0\n', 'IgnoreHitPause = 1\n', '\n', '[State -2,stateno3]\n', 'Type = VarSet\n', 'TriggerAll = Enemy,TeamMode = Single || Enemy,TeamMode = Turns\n', 'TriggerAll = enemynear,movetype = A\n', 'TriggerAll = Var(2) != enemynear,stateno\n', 'Trigger1 = var(0) != 0\n', 'var(2) = enemynear,stateno\n', 'IgnoreHitPause = 1\n', '\n', '[State -2,time]\n', 'Type = VarSet\n', 'TriggerAll = Enemy,TeamMode = Single || Enemy,TeamMode = Turns\n', 'TriggerAll = enemynear,movetype = A\n', 'TriggerAll = Var(2) = enemynear,stateno\n', 'Trigger1 = var(0) != 0\n', 'var(3) = var(0)\n', 'IgnoreHitPause = 1\n', '\n', '[State -2,max]\n', 'Type = Varset\n', 'Trigger1 = var(3) > 999\n', 'var(3) = 999\n', 'IgnoreHitPause = 1\n', '\n', '[State -2,pointer]\n', 'Type = VarSet\n', 'TriggerAll = Enemy,TeamMode = Single || Enemy,TeamMode = Turns\n', 'TriggerAll = enemynear,movetype = A && var(0) != 0\n', 'TriggerAll = Var(6) <= 39\n', 'TriggerAll = floor(fvar(0)) != var(2)\n', 'TriggerAll = floor(fvar(1)) != var(2)\n', 'TriggerAll = floor(fvar(2)) != var(2)\n', 'TriggerAll = floor(fvar(3)) != var(2)\n', 'TriggerAll = floor(fvar(4)) != var(2)\n', 'TriggerAll = floor(fvar(5)) != var(2)\n', 'TriggerAll = floor(fvar(6)) != var(2)\n', 'TriggerAll = floor(fvar(7)) != var(2)\n', 'TriggerAll = floor(fvar(8)) != var(2)\n', 'TriggerAll = floor(fvar(9)) != var(2)\n', 'TriggerAll = floor(fvar(10)) != var(2)\n', 'TriggerAll = floor(fvar(11)) != var(2)\n', 'TriggerAll = floor(fvar(12)) != var(2)\n', 'TriggerAll = floor(fvar(13)) != var(2)\n', 'TriggerAll = floor(fvar(14)) != var(2)\n', 'TriggerAll = floor(fvar(15)) != var(2)\n', 'TriggerAll = floor(fvar(16)) != var(2)\n', 'TriggerAll = floor(fvar(17)) != var(2)\n', 'TriggerAll = floor(fvar(18)) != var(2)\n', 'TriggerAll = floor(fvar(19)) != var(2)\n', 'TriggerAll = floor(fvar(20)) != var(2)\n', 'TriggerAll = floor(fvar(21)) != var(2)\n', 'TriggerAll = floor(fvar(22)) != var(2)\n', 'TriggerAll = floor(fvar(23)) != var(2)\n', 'TriggerAll = floor(fvar(24)) != var(2)\n', 'TriggerAll = floor(fvar(25)) != var(2)\n', 'TriggerAll = floor(fvar(26)) != var(2)\n', 'TriggerAll = floor(fvar(27)) != var(2)\n', 'TriggerAll = floor(fvar(28)) != var(2)\n', 'TriggerAll = floor(fvar(29)) != var(2)\n', 'TriggerAll = floor(fvar(30)) != var(2)\n', 'TriggerAll = floor(fvar(31)) != var(2)\n', 'TriggerAll = floor(fvar(32)) != var(2)\n', 'TriggerAll = floor(fvar(33)) != var(2)\n', 'TriggerAll = floor(fvar(34)) != var(2)\n', 'TriggerAll = floor(fvar(35)) != var(2)\n', 'TriggerAll = floor(fvar(36)) != var(2)\n', 'TriggerAll = floor(fvar(37)) != var(2)\n', 'TriggerAll = floor(fvar(38)) != var(2)\n', 'TriggerAll = floor(fvar(39)) != var(2)\n', 'TriggerAll = var(5) = 0\n', 'Triggerall = Enemynear,Prevstateno != Enemynear,Stateno\n', 'trigger1 = enemynear,hitdefattr = sca,na,sa,np,sp,nt,st\n', 'var(5) = 1\n', 'IgnoreHitPause = 1\n', '\n', '[State -2,record]\n', 'Type = VarSet\n', 'TriggerAll = Enemy,TeamMode = Single || Enemy,TeamMode = Turns\n', 'Trigger1 = var(5) = 1\n', 'FV = Var(6)\n', 'Value = Var(2)+0.001*Var(3)\n', 'IgnoreHitPause = 1\n', '\n', '\n', '[State -2, 判定用Varのリセット]\n', 'Type = VarSet\n', 'TriggerAll = Enemy,TeamMode = Single || Enemy,TeamMode = Turns\n', 'triggerall = var(22)\n', 'triggerall = Root,StateNo != [120,155]\n', 'triggerall = Root,MoveType != H\n', 'trigger1 = Root,Ctrl || Root,StateNo < 200\n', 'trigger2 = Root,MoveType = A\n', 'V = 22\n', 'Value = 0\n', 'IgnoreHitPause = 1\n', '\n', '[State -2, 下段(立ちガード不可攻撃)判定]\n', 'Type = VarSet\n', 'TriggerAll = RoundState = 2 && Var(22) = 0\n', 'TriggerAll = root,StateNo != [120,155]\n', 'TriggerAll = root,prevStateNo != [5000,5099]\n', 'TriggerAll = enemynear,movetype = A\n', 'TriggerAll = EnemyNear,StateType = S\n', 'TriggerAll = root,movetype = H\n', 'triggerall = !enemynear,hitdefattr = sca,at\n', 'Trigger1 = root,PrevStateNo = 130\n', 'Trigger2 = root,PrevStateNo = [150,151]\n', 'V = 22\n', 'Value = 1\n', 'IgnoreHitPause = 1\n', '\n', '[State -2, 中段(屈みガード不可攻撃)判定]\n', 'Type = VarSet\n', 'TriggerAll = RoundState = 2 && Var(22) = 0\n', 'TriggerAll = root,StateNo != [120,155]\n', 'TriggerAll = root,prevStateNo != [5000,5099]\n', 'TriggerAll = enemynear,movetype = A\n', 'TriggerAll = EnemyNear,StateType = S\n', 'TriggerAll = root,movetype = H\n', 'triggerall = !enemynear,hitdefattr = sca,at\n', 'Trigger1 = root,PrevStateNo = 131\n', 'Trigger2 = root,PrevStateNo = [152,153]\n', 'V = 22\n', 'Value = 2\n', 'IgnoreHitPause = 1\n', '\n', '[State 60000,Reset]\n', 'type = VarSet\n', 'triggerall = var(11) != 0\n', 'trigger1 = enemynear,stateno != var(30)\n', 'trigger1 = enemynear,stateno != var(31)\n', 'trigger1 = enemynear,stateno != var(32)\n', 'trigger1 = enemynear,stateno != var(33)\n', 'trigger1 = enemynear,stateno != var(34)\n', 'trigger1 = enemynear,stateno != var(35)\n', 'trigger1 = enemynear,stateno != var(36)\n', 'trigger1 = enemynear,stateno != var(37)\n', 'trigger1 = enemynear,stateno != var(38)\n', 'trigger1 = enemynear,stateno != var(39)\n', 'trigger1 = enemynear,stateno != var(40)\n', 'trigger1 = enemynear,stateno != var(41)\n', 'trigger1 = enemynear,stateno != var(42)\n', 'trigger1 = enemynear,stateno != var(43)\n', 'trigger2 = enemynear,movetype != A\n', 'var(11) = 0\n', 'ignorehitpause = 1\n', '\n', '[State 60000,下段]\n', 'type = VarSet\n', 'triggerall = var(11) != 1\n', 'trigger1 = var(30) > 0\n', 'trigger1 = enemynear,stateno = var(30)\n', 'trigger2 = var(31) > 0\n', 'trigger2 = enemynear,stateno = var(31)\n', 'trigger3 = var(32) > 0\n', 'trigger3 = enemynear,stateno = var(32)\n', 'var(11) = 1\n', 'ignorehitpause = 1\n', '\n', '[State 60000,中段]\n', 'type = VarSet\n', 'triggerall = var(11) != 2\n', 'trigger1 = var(33) > 0\n', 'trigger1 = enemynear,stateno = var(33)\n', 'trigger2 = var(34) > 0\n', 'trigger2 = enemynear,stateno = var(34)\n', 'trigger3 = var(35) > 0\n', 'trigger3 = enemynear,stateno = var(35)\n', 'var(11) = 2\n', 'ignorehitpause = 1\n', '\n', '[State 60000,投]\n', 'type = VarSet\n', 'triggerall = var(11) != 3\n', 'trigger1 = var(36) > 0\n', 'trigger1 = enemynear,stateno = var(36)\n', 'trigger2 = var(37) > 0\n', 'trigger2 = enemynear,stateno = var(37)\n', 'trigger3 = var(38) > 0\n', 'trigger3 = enemynear,stateno = var(38)\n', 'trigger4 = var(39) > 0\n', 'trigger4 = enemynear,stateno = var(39)\n', 'trigger5 = var(40) > 0\n', 'trigger5 = enemynear,stateno = var(40)\n', 'trigger6 = var(41) > 0\n', 'trigger6 = enemynear,stateno = var(41)\n', 'var(11) = 3\n', 'ignorehitpause = 1\n', '\n', '[State 60000,不可防]\n', 'type = VarSet\n', 'triggerall = var(11) != 4\n', 'trigger1 = var(42) > 0\n', 'trigger1 = enemynear,stateno = var(42)\n', 'trigger2 = var(43) > 0\n', 'trigger2 = enemynear,stateno = var(43)\n', 'var(11) = 4\n', 'ignorehitpause = 1\n', '\n', '[State 60000,下段学習]\n', 'type = VarSet\n', 'trigger1 = enemynear,movetype = A\n', 'trigger1 = var(22) = 1\n', 'trigger1 = Enemy,TeamMode = Single || Enemy,TeamMode = Turns || Enemy,TeamMode = Simul && (Enemy(0),Alive && !Enemy(NumEnemy=2),Alive || !Enemy(0),Alive && Enemy(NumEnemy=2),Alive)\n', 'trigger1 = !var(30)\n', 'trigger1 = !var(42)||var(42)&&var(42)!=EnemyNear,StateNo\n', 'trigger1 = !var(43)||var(43)&&var(43)!=EnemyNear,StateNo\n', 'var(30) = EnemyNear,StateNo\n', 'ignorehitpause = 1\n', '\n', '[State 60000,下段学習2]\n', 'type = VarSet\n', 'trigger1 = enemynear,movetype = A\n', 'trigger1 = var(22) = 1\n', 'trigger1 = Enemy,TeamMode = Single || Enemy,TeamMode = Turns || Enemy,TeamMode = Simul && (Enemy(0),Alive && !Enemy(NumEnemy=2),Alive || !Enemy(0),Alive && Enemy(NumEnemy=2),Alive)\n', 'trigger1 = var(30)\n', 'trigger1 = !var(31)\n', 'trigger1 = !var(42)||var(42)&&var(42)!=EnemyNear,StateNo\n', 'trigger1 = !var(43)||var(43)&&var(43)!=EnemyNear,StateNo\n', 'trigger1 = enemynear,stateno != var(30)\n', 'var(31) = EnemyNear,StateNo\n', 'ignorehitpause = 1\n', '\n', '[State 60000,下段学習3]\n', 'type = VarSet\n', 'trigger1 = enemynear,movetype = A\n', 'trigger1 = var(22) = 1\n', 'trigger1 = Enemy,TeamMode = Single || Enemy,TeamMode = Turns || Enemy,TeamMode = Simul && (Enemy(0),Alive && !Enemy(NumEnemy=2),Alive || !Enemy(0),Alive && Enemy(NumEnemy=2),Alive)\n', 'trigger1 = var(31)\n', 'trigger1 = !var(32)\n', 'trigger1 = !var(42)||var(42)&&var(42)!=EnemyNear,StateNo\n', 'trigger1 = !var(43)||var(43)&&var(43)!=EnemyNear,StateNo\n', 'trigger1 = enemynear,stateno != var(30)\n', 'trigger1 = enemynear,stateno != var(31)\n', 'var(32) = EnemyNear,StateNo\n', 'ignorehitpause = 1\n', '\n', '[State 60000,中段学習]\n', 'type = VarSet\n', 'trigger1 = enemynear,movetype = A\n', 'trigger1 = var(22) = 2\n', 'trigger1 = Enemy,TeamMode = Single || Enemy,TeamMode = Turns || Enemy,TeamMode = Simul && (Enemy(0),Alive && !Enemy(NumEnemy=2),Alive || !Enemy(0),Alive && Enemy(NumEnemy=2),Alive)\n', 'trigger1 = !var(33)\n', 'trigger1 = !var(42)||var(42)&&var(42)!=EnemyNear,StateNo\n', 'trigger1 = !var(43)||var(43)&&var(43)!=EnemyNear,StateNo\n', 'var(33) = EnemyNear,StateNo\n', 'ignorehitpause = 1\n', '\n', '[State 60000,中段学習2]\n', 'type = VarSet\n', 'trigger1 = enemynear,movetype = A\n', 'trigger1 = var(22) = 2\n', 'trigger1 = Enemy,TeamMode = Single || Enemy,TeamMode = Turns || Enemy,TeamMode = Simul && (Enemy(0),Alive && !Enemy(NumEnemy=2),Alive || !Enemy(0),Alive && Enemy(NumEnemy=2),Alive)\n', 'trigger1 = var(33)\n', 'trigger1 = !var(34)\n', 'trigger1 = !var(42)||var(42)&&var(42)!=EnemyNear,StateNo\n', 'trigger1 = !var(43)||var(43)&&var(43)!=EnemyNear,StateNo\n', 'trigger1 = enemynear,stateno != var(33)\n', 'var(34) = EnemyNear,StateNo\n', 'ignorehitpause = 1\n', '\n', '[State 60000,中段学習3]\n', 'type = VarSet\n', 'trigger1 = enemynear,movetype = A\n', 'trigger1 = var(22) = 2\n', 'trigger1 = Enemy,TeamMode = Single || Enemy,TeamMode = Turns || Enemy,TeamMode = Simul && (Enemy(0),Alive && !Enemy(NumEnemy=2),Alive || !Enemy(0),Alive && Enemy(NumEnemy=2),Alive)\n', 'trigger1 = var(34)\n', 'trigger1 = !var(35)\n', 'trigger1 = !var(42)||var(42)&&var(42)!=EnemyNear,StateNo\n', 'trigger1 = !var(43)||var(43)&&var(43)!=EnemyNear,StateNo\n', 'trigger1 = enemynear,stateno != var(33)\n', 'trigger1 = enemynear,stateno != var(34)\n', 'var(35) = EnemyNear,StateNo\n', 'ignorehitpause = 1\n', '\n', '[State 60000,投]\n', 'type = VarSet\n', 'trigger1 = enemynear,movetype = A\n', 'trigger1 = Enemy,TeamMode = Single || Enemy,TeamMode = Turns || Enemy,TeamMode = Simul && (Enemy(0),Alive && !Enemy(NumEnemy=2),Alive || !Enemy(0),Alive && Enemy(NumEnemy=2),Alive)\n', 'trigger1 = enemynear,hitdefattr = sc,nt,st,ht,at\n', 'trigger1 = !var(36)\n', 'var(36) = enemynear,stateno\n', 'ignorehitpause = 1\n', '\n', '[State 60000,投2]\n', 'type = VarSet\n', 'trigger1 = enemynear,movetype = A\n', 'trigger1 = Enemy,TeamMode = Single || Enemy,TeamMode = Turns || Enemy,TeamMode = Simul && (Enemy(0),Alive && !Enemy(NumEnemy=2),Alive || !Enemy(0),Alive && Enemy(NumEnemy=2),Alive)\n', 'trigger1 = enemynear,hitdefattr = sc,nt,st,ht,at\n', 'trigger1 = !var(37) && var(36)\n', 'trigger1 = enemynear,stateno != var(36)\n', 'var(37) = enemynear,stateno\n', 'ignorehitpause = 1\n', '\n', '[State 60000,投3]\n', 'type = VarSet\n', 'trigger1 = enemynear,movetype = A\n', 'trigger1 = Enemy,TeamMode = Single || Enemy,TeamMode = Turns || Enemy,TeamMode = Simul && (Enemy(0),Alive && !Enemy(NumEnemy=2),Alive || !Enemy(0),Alive && Enemy(NumEnemy=2),Alive)\n', 'trigger1 = enemynear,hitdefattr = sc,nt,st,ht,at\n', 'trigger1 = !var(38) && var(37)\n', 'trigger1 = enemynear,stateno != var(36)\n', 'trigger1 = enemynear,stateno != var(37)\n', 'var(38) = enemynear,stateno\n', '\n', '[State 60000,投4]\n', 'type = VarSet\n', 'trigger1 = enemynear,movetype = A\n', 'trigger1 = Enemy,TeamMode = Single || Enemy,TeamMode = Turns || Enemy,TeamMode = Simul && (Enemy(0),Alive && !Enemy(NumEnemy=2),Alive || !Enemy(0),Alive && Enemy(NumEnemy=2),Alive)\n', 'trigger1 = enemynear,hitdefattr = sca,nt,st,ht,at\n', 'trigger1 = !var(39) && var(38)\n', 'trigger1 = enemynear,stateno != var(36)\n', 'trigger1 = enemynear,stateno != var(37)\n', 'trigger1 = enemynear,stateno != var(38)\n', 'var(39) = enemynear,stateno\n', '\n', '[State 60000,投5]\n', 'type = VarSet\n', 'trigger1 = enemynear,movetype = A\n', 'trigger1 = Enemy,TeamMode = Single || Enemy,TeamMode = Turns || Enemy,TeamMode = Simul && (Enemy(0),Alive && !Enemy(NumEnemy=2),Alive || !Enemy(0),Alive && Enemy(NumEnemy=2),Alive)\n', 'trigger1 = enemynear,hitdefattr = sca,nt,st,ht,at\n', 'trigger1 = !var(40) && var(39)\n', 'trigger1 = enemynear,stateno != var(36)\n', 'trigger1 = enemynear,stateno != var(37)\n', 'trigger1 = enemynear,stateno != var(38)\n', 'trigger1 = enemynear,stateno != var(39)\n', 'var(40) = enemynear,stateno\n', '\n', '[State 60000,投6]\n', 'type = VarSet\n', 'trigger1 = enemynear,movetype = A\n', 'trigger1 = Enemy,TeamMode = Single || Enemy,TeamMode = Turns || Enemy,TeamMode = Simul && (Enemy(0),Alive && !Enemy(NumEnemy=2),Alive || !Enemy(0),Alive && Enemy(NumEnemy=2),Alive)\n', 'trigger1 = enemynear,hitdefattr = sca,nt,st,ht,at\n', 'trigger1 = !var(41) && var(40)\n', 'trigger1 = enemynear,stateno != var(36)\n', 'trigger1 = enemynear,stateno != var(37)\n', 'trigger1 = enemynear,stateno != var(38)\n', 'trigger1 = enemynear,stateno != var(39)\n', 'trigger1 = enemynear,stateno != var(40)\n', 'var(41) = enemynear,stateno\n', '\n', '[State 60000,ガード不能学習]\n', 'type = VarSet\n', 'triggerall = !var(42)\n', 'trigger1 = var(30)>0\n', 'trigger1 = var(30) = var(33) || var(30) = var(34) || var(30) = var(35)\n', 'var(42) = var(10)\n', 'ignorehitpause = 1\n', '\n', '[State 60000,ガード不能学習]\n', 'type = VarSet\n', 'triggerall = !var(42)\n', 'trigger1 = var(31)>0\n', 'trigger1 = var(31) = var(33) || var(31) = var(34) || var(31) = var(35)\n', 'var(42) = var(31)\n', 'ignorehitpause = 1\n', '\n', '[State 60000,ガード不能学習]\n', 'type = VarSet\n', 'triggerall = !var(42)\n', 'trigger1 = var(32)>0\n', 'trigger1 = var(32) = var(33) || var(32) = var(34) || var(32) = var(35)\n', 'var(42) = var(32)\n', 'ignorehitpause = 1\n', '\n', '[State 60000,ガード不能学習]\n', 'type = VarSet\n', 'triggerall = var(30)\n', 'trigger1 = var(42) = var(30)\n', 'var(30) = 0\n', 'ignorehitpause = 1\n', '\n', '[State 60000,ガード不能学習]\n', 'type = VarSet\n', 'triggerall = var(31)\n', 'trigger1 = var(42) = var(31)\n', 'var(31) = 0\n', 'ignorehitpause = 1\n', '\n', '[State 60000,ガード不能学習]\n', 'type = VarSet\n', 'triggerall = var(32)\n', 'trigger1 = var(42) = var(32)\n', 'var(32) = 0\n', 'ignorehitpause = 1\n', '\n', '[State 60000,ガード不能学習]\n', 'type = VarSet\n', 'triggerall = var(33)\n', 'trigger1 = var(42) = var(33)\n', 'var(33) = 0\n', 'ignorehitpause = 1\n', '\n', '[State 60000,ガード不能学習]\n', 'type = VarSet\n', 'triggerall = var(34)\n', 'trigger1 = var(42) = var(34)\n', 'var(34) = 0\n', 'ignorehitpause = 1\n', '\n', '[State 60000,ガード不能学習]\n', 'type = VarSet\n', 'triggerall = var(35)\n', 'trigger1 = var(42) = var(35)\n', 'var(35) = 0\n', 'ignorehitpause = 1\n', '\n', '[State 60000,ガード不能学習2]\n', 'type = VarSet\n', 'triggerall = !var(43)\n', 'triggerall = var(42)\n', 'trigger1 = var(30)>0\n', 'trigger1 = var(30) = var(33) || var(30) = var(34) || var(30) = var(35)\n', 'var(43) = ifelse(var(30)!=var(42),var(30),0)\n', 'ignorehitpause = 1\n', '\n', '[State 60000,ガード不能学習2]\n', 'type = VarSet\n', 'triggerall = !var(43)\n', 'triggerall = var(42)\n', 'trigger1 = var(31)>0\n', 'trigger1 = var(31) = var(33) || var(31) = var(34) || var(31) = var(35)\n', 'var(43) = ifelse(var(30)!=var(42),var(31),0)\n', 'ignorehitpause = 1\n', '\n', '[State 60000,ガード不能学習2]\n', 'type = VarSet\n', 'triggerall = !var(43)\n', 'triggerall = var(42)\n', 'trigger1 = var(32)>0\n', 'trigger1 = var(32) = var(33) || var(32) = var(34) || var(32) = var(35)\n', 'var(43) = ifelse(var(30)!=var(42),var(32),0)\n', 'ignorehitpause = 1\n', '\n', '[State 60000,ガード不能学習]\n', 'type = VarSet\n', 'triggerall = var(30)\n', 'trigger1 = var(43) = var(30)\n', 'var(30) = 0\n', 'ignorehitpause = 1\n', '\n', '[State 60000,ガード不能学習]\n', 'type = VarSet\n', 'triggerall = var(31)\n', 'trigger1 = var(43) = var(31)\n', 'var(31) = 0\n', 'ignorehitpause = 1\n', '\n', '[State 60000,ガード不能学習]\n', 'type = VarSet\n', 'triggerall = var(32)\n', 'trigger1 = var(43) = var(32)\n', 'var(32) = 0\n', 'ignorehitpause = 1\n', '\n', '[State 60000,ガード不能学習]\n', 'type = VarSet\n', 'triggerall = var(33)\n', 'trigger1 = var(43) = var(33)\n', 'var(33) = 0\n', 'ignorehitpause = 1\n', '\n', '[State 60000,ガード不能学習]\n', 'type = VarSet\n', 'triggerall = var(34)\n', 'trigger1 = var(43) = var(34)\n', 'var(34) = 0\n', 'ignorehitpause = 1\n', '\n', '[State 60000,ガード不能学習]\n', 'type = VarSet\n', 'triggerall = var(35)\n', 'trigger1 = var(43) = var(35)\n', 'var(35) = 0\n', 'ignorehitpause = 1\n', '\n']
aihelper=aihelperdef+aihelper
tempfile = state3+aiswitch+['\n;Counter\n']+counter+['\n;Guard\n']+guardtext+['\n;Chance\n']+chance+['\n;Combo\n']+combo+['\n;Throw\n']+throw+['\n;Fight\n']+fight+['\n;Move and other\n']+movetext+['\n;AIhelper\n']+aihelper
if s3 == 1:
    AIFILE=open(state3file,'w',encoding='utf-8')
    print('aifile:'+state3file+' is saved.')
else:
    AIFILE=open("aisummary.txt",'w',encoding='utf-8')
    print('aisummary.txt is saved.')
AIFILE.writelines(tempfile)
AIFILE.close()
counter=[]
chance=[]
combo=[]
fight=[]
tempfile = []
temp = []
aiswitch = []
p = re.compile(r'\[Statedef\s*(-?\d+)',re.I)
p1 = re.compile(r'\[State',re.I)
p2 = re.compile(r'Type\s*=\s*Statetypeset',re.I)
p3 = re.compile(r'Type\s*=\s*changestate',re.I)
p4 = re.compile(r'value\s*=\s*(\d+)',re.I)
p6 = re.compile(r'(command\s*!?=\s*".*?")',re.I)
p7 = re.compile(r'(!inguarddist)',re.I)
p8 = re.compile(r'trigger(all|\d+)\s*=',re.I)
p9 = re.compile(r'hitshakeover',re.I)
p0 = re.compile(r'^statetype\s*=\s*(\w)',re.I)
p10 = re.compile(r'Type\s*=\s*Varset',re.I)
p11 = re.compile(r'sysvar\(1\)\s*=\s*(-?\d)',re.I)
p12 = re.compile(r'^type\s*=\s*(\w+)\s*$',re.I)
s,s1,s2,value_type=0,0,0,0
tempno=None
sctrltype=None
if guardfile != None:
    for lino in range(len(guardstate)):
        m=p.search(guardstate[lino])
        m1=p1.search(guardstate[lino])
        m2=p2.search(guardstate[lino])
        m3=p3.search(guardstate[lino])
        m4=p4.search(guardstate[lino])        
        m6=p6.search(guardstate[lino])
        m7=p7.search(guardstate[lino])
        m8=p8.search(guardstate[lino])
        m9=p9.search(guardstate[lino])
        m0=p0.search(guardstate[lino])
        m10=p10.search(guardstate[lino])
        m11=p11.search(guardstate[lino])
        m12=p12.search(guardstate[lino])
        if m:stateno2 = int(m.group(1))
        if m12:
            sctrltype = m12.group(1).strip().lower()
        if m4:
            value = int(m4.group(1))
            m3=p3.search(guardstate[lino-1])
            if m3:value_type=1
        if m8:
            triggerno= m8.group(1)
            if triggerno.isdigit():triggerin = int(triggerno)+1
            else:triggerin = 1
        if stateno2 == 40 or stateno2 == 41 or stateno2 == 45:
            if m1:
                s2,value_type=0,0
                sctrltype=None
            if sctrltype == "varset":
                if m6:
                    guardstate[lino] = p6.sub(fr'\1 && {ai_var} <= 0',guardstate[lino])
                    s2=1.4
                if m11 and s2==1.4:
                    sysvar1=int(m11.group(1))
                    if sysvar1==1:guardstate.insert(lino,'trigger'+str(triggerin)+' = {ai_var} > 0 && p2bodydist x >= 0 && (p2movetype = H || random <= 500 || p2bodydist x > 160)\n'.format(ai_var=ai_var))
                    elif sysvar1==-1:guardstate.insert(lino,'trigger'+str(triggerin)+' = {ai_var} > 0 && (p2dist x < 0 || p2bodydist x < 80 && random > 500 && (p2movetype != H || p2stateno = [120,159]))\n'.format(ai_var=ai_var))
                    s2=1.6
        if 100 <=stateno2< 105:
            if m1:
                s2,value_type=0,0
                sctrltype=None
            if m6 and sctrltype == "changestate":
                #if stateno2==101:print(lino,m6)
                #print(lino,guardstate[lino])
                guardstate[lino] = p6.sub(fr'\1 && {ai_var} <= 0',guardstate[lino])
                s2=1.5
            if m4 and s2==1.5 and sctrltype == "changestate":
                if 100<value<105:
                    guardstate.insert(lino,'trigger'+str(triggerin)+' = {ai_var} > 0\n'.format(ai_var=ai_var))
                    guardstate.insert(lino+1,'trigger'+str(triggerin)+' = inguarddist+helper({aihelperID}),inguarddist || p2bodydist x <= 10\n'.format(aihelperID=aihelperID))
                    s2=1.8
        if 120<=stateno2<=155:
            if m1:
                s,value_type=0,0
                triggerno=0
                tempno=0
                sctrltype=None
            if m2:s=1
            if m3:s=2            
            if 1<=s<2:                
                if m6:
                    guardstate[lino] = p6.sub(fr'\1 && {ai_var} <= 0',guardstate[lino])
                    s=1.5
                if m0 and s==1.5:                    
                    if m0.group(1).upper() == 'C' and triggerin:
                        guardstate.insert(lino,'trigger'+str(triggerin)+' = {ai_var} > 0 && statetype = S\n'.format(ai_var=ai_var))
                        guardstate.insert(lino+1,'trigger'+str(triggerin)+' = p2statetype = C || p2statetype = S && numhelper({aihelperID}) && (random%2 = 0 && helper({aihelperID}),var(11) = 0 || helper({aihelperID}),var(11) = 1)\n'.format(aihelperID=aihelperID))
                        s = 3
                    if m0.group(1).upper() == 'S' and triggerin:
                        guardstate.insert(lino,'trigger'+str(triggerin)+' = {ai_var} > 0 && statetype = C\n'.format(ai_var=ai_var))
                        guardstate.insert(lino+1,'trigger'+str(triggerin)+' = p2statetype = A || p2statetype = S && numhelper({aihelperID}) && (random%2 = 1 && helper({aihelperID}),var(11) = 0 || helper({aihelperID}),var(11) = 2)\n'.format(aihelperID=aihelperID))
                        s = 3
            if 2<=s<3:                
                if m9:
                    s=2.5
                if m6 and s:
                    if stateno2 == 132 or stateno2 == 155:
                        guardstate[lino] = p6.sub(fr'\1 && {ai_var} <= 0',guardstate[lino])
                        s=2.7
                    elif s==2.5 and value == 151:
                        guardstate[lino] = p6.sub(fr'\1 && {ai_var} <= 0 || {ai_var} && (p2statetype = C || p2statetype = S && helper({aihelperID}),var(11) = 1)',guardstate[lino])
                        s=2.6
                    else:
                        s=2.4
                        guardstate[lino] = p6.sub(fr'\1 && {ai_var} <= 0',guardstate[lino])  
                if s ==2.7 and value == 130 and triggerin and (stateno2 == 132 or stateno2 == 155):
                    if (m4 and value_type==0) or (value_type==1 and (m1 or guardstate[lino].strip()=="")):
                        guardstate.insert(lino,'trigger'+str(triggerin)+' = {ai_var} > 0\n'.format(ai_var=ai_var))
                        guardstate.insert(lino+1,'trigger'+str(triggerin)+' = sysvar(0) && inguarddist+helper({aihelperID}),inguarddist\n'.format(aihelperID=aihelperID))
                        s=3
                if value == 131 and triggerin and stateno2 == 130:
                    if (m4 and value_type==0) or (value_type==1 and (m1 or guardstate[lino].strip()=="")):
                        guardstate.insert(lino,'trigger'+str(triggerin)+' = {ai_var} > 0\n'.format(ai_var=ai_var))
                        guardstate.insert(lino+1,'trigger'+str(triggerin)+' = p2statetype = C || p2statetype = S && numhelper({aihelperID}) && (random%2 = 0 && helper({aihelperID}),var(11) = 0 || helper({aihelperID}),var(11) = 1)\n'.format(aihelperID=aihelperID))
                        s=3
                if value == 130 and triggerin and stateno2 == 131:
                    if (m4 and value_type==0) or (value_type==1 and (m1 or guardstate[lino].strip()=="")):
                        guardstate.insert(lino,'trigger'+str(triggerin)+' = {ai_var} > 0\n'.format(ai_var=ai_var))
                        guardstate.insert(lino+1,'trigger'+str(triggerin)+' = p2statetype = A || p2statetype = S && numhelper({aihelperID}) && (random%2 = 1 && helper({aihelperID}),var(11) = 0 || helper({aihelperID}),var(11) = 2)\n'.format(aihelperID=aihelperID))
                        s=3
                if m7 and 120 <= stateno2 <= 132:
                    guardstate[lino] = p7.sub(fr'\1 && !helper({aihelperID}),inguarddist',guardstate[lino])
if guardfile !=None:
    GUARD = open(guardfile,'w',encoding='utf-8')
    GUARD.writelines(guardstate)
    GUARD.close()
    print(guardfile+' is saved')
elif guardfile == None and stcommon not in stfiles:
    print("Copy the common1.cns in the RAR into the character's folder")
newcmd=os.path.splitext(cmd)[0]+'-AI'+os.path.splitext(cmd)[1]
newcns=os.path.splitext(cns)[0]+'-AI'+os.path.splitext(cns)[1]
newcommon=os.path.splitext(stcommon)[0]+'-AI'+os.path.splitext(stcommon)[1]
temp_stfiles=newstfiles
if (cns not in st) and (newcns in temp_stfiles):temp_stfiles.remove(newcns)
if newcommon in temp_stfiles:temp_stfiles.remove(newcommon)
merged_filename=""
if len(temp_stfiles) > 10+(s3==1):
    origin_length=len(temp_stfiles)
    merged_filename=os.path.splitext(temp_stfiles[-1])[0]+'_merged'+os.path.splitext(temp_stfiles[-1])[1]
    while len(temp_stfiles) >= 10+(s3==1):
        file_to_merge = temp_stfiles.pop()
        #print(len(temp_stfiles),file_to_merge,temp_stfiles)
        if os.path.isfile(file_to_merge):
            with open(file_to_merge, 'r',encoding='utf-8') as fr:
                if len(temp_stfiles) >= origin_length-1:
                    with open(merged_filename, 'w',encoding='utf-8') as fw:
                        fw.write(fr.read())
                else:
                    with open(merged_filename, 'a',encoding='utf-8') as fw:
                        fw.write(fr.read())
            os.remove(file_to_merge)
if merged_filename!="":temp_stfiles.append(merged_filename)
if newstfiles != None and deffile != None:    
    p = re.compile(r'=\s*(\S+)',re.I)
    p1 = re.compile(r'st(\d*)\s*=\s*',re.I)
    p2 = re.compile(r'mugenversion\s*=\s*(\S+)',re.I)
    p3 = re.compile(r'\[Files\]',re.I)
    s=0
    n=0
    templino=0
    mugenver_exist=0
    name=""
    for lino in range(len(deflist)):
        deflist[lino] = cut(deflist[lino])
        m = deflist[lino].split("=")
        if len(m)>1 and m[1] != None:name=m[1].lower().strip()
        m1 = p1.search(deflist[lino])
        m2 = p2.search(deflist[lino])
        m3 = p3.search(deflist[lino])
#        if m and m.group(1) in stfiles:
#           stfilename=m.group(1)
#            deflist[lino] = p.sub('= '+os.path.splitext(stfilename)[0]+'-AI'+os.path.splitext(stfilename)[1],deflist[lino])
        if name == cmd.lower().strip():deflist[lino] = "cmd = "+newcmd+'\n'
        if name == cns.lower().strip() and cns in stfiles:deflist[lino] = "cns = "+newcns+'\n'
        if name == stcommon.lower().strip() and stcommon in stfiles:deflist[lino] = "stcommon = "+newcommon+'\n'
        if m2:
            mugenver_exist=1
            if ai_var=="AILevel":
                if m2.group(1) !="1.0" and m2.group(1) != "1.1":deflist[lino]="mugenversion = 1.0\n"
        if m3 and mugenver_exist==0:
            deflist.insert(lino,"mugenversion = 1.0\n")
            mugenver_exist=1
        if m1 and s==2 and m1.group(1).isdigit() and lino>templino:deflist[lino]=""
        if m1 and s!=2 and n < len(temp_stfiles):
            if n == 0:
                deflist[lino] = "st = "+temp_stfiles[n]+"\n"
            else:
                deflist[lino] = "st"+str(n-1)+" = "+temp_stfiles[n]+"\n"
            s=1
            n=n+1
        if m1==None and s==1:
            #print(lino,n,s)
            if n < len(temp_stfiles):
                deflist.insert(lino,"st"+str(n-1)+" = "+temp_stfiles[n]+"\n")
                n=n+1
            else:
                if s3 != 1:deflist.insert(lino,"st"+str(n-1)+" = aisummary.txt\n")
                templino=lino
                s=2
    DEFNEW=open(os.path.splitext(deffile)[0]+'-AI'+os.path.splitext(deffile)[1],'w',encoding='utf-8')
    DEFNEW.writelines(deflist)
    DEFNEW.close()
    print(os.path.splitext(deffile)[0]+'-AI'+os.path.splitext(deffile)[1]+' is saved')
input('Press enter to exit.')

