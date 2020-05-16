#coding=utf-8
import os,sys,json,re,time,datetime,logging,zipfile,platform
from bottle import request,route,template,static_file,abort,redirect

from MySQL import writeDb,readDb,readDb2
from Login import checkLogin,checkAccess
from FTP import FTPHandle
from Functions import AppServer,LoginCls,cmdhandle,writeFTPconf,GetFileMd5,is_chinese,netModule,servchk

import Global as gl

#支持中文配置读取
sys.setdefaultencoding('utf-8')

cmds=cmdhandle()
netmod=netModule()

@route('/systeminfo')
@route('/')
@checkAccess
def systeminfo():
    """系统信息项"""
    s = request.environ.get('beaker.session')
    info=dict()
    info['hostname'] = platform.node()
    info['kernel'] = platform.platform()
    info['systime'] = cmds.getdictrst('date +"%Y%m%d %H:%M:%S"').get('result')
    cmdRun='cat /proc/uptime|awk -F. \'{run_days=$1/86400;run_hour=($1%86400)/3600;run_minute=($1%3600)/60;run_second=$1%60;printf("%d天%d时%d分%d秒",run_days,run_hour,run_minute,run_second)}\''
    info['runtime'] = cmds.getdictrst(cmdRun).get('result')
    info['pyversion'] = platform.python_version()
    info['memsize'] = cmds.getdictrst('cat /proc/meminfo |grep \'MemTotal\' |awk -F: \'{printf ("%.0fM",$2/1024)}\'|sed \'s/^[ \t]*//g\'').get('result')
    info['cpumode'] = cmds.getdictrst('grep \'model name\' /proc/cpuinfo |uniq |awk -F : \'{print $2}\' |sed \'s/^[ \t]*//g\' |sed \'s/ \+/ /g\'').get('result')
    info['v4addr'] = 'Wan: '+netmod.NetIP()
    info['appversion'] = AppServer().getVersion()
    """管理日志"""
    sql = " SELECT id,objtext,objact,objhost,objtime FROM logrecord order by id DESC limit 7 "
    logdict = readDb(sql,)
    return template('systeminfo',session=s,info=info,logdict=logdict)

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)

@route('/systeminfo',method="POST")
@checkAccess
def do_systeminfo():
    s = request.environ.get('beaker.session')
    sql = " select value from sysattr where attr='resData' "
    info = readDb(sql,)
    try:
        ninfo=json.loads(info[0].get('value'))
    except:
        return False
    visitDay = ninfo.get('visitDay')
    try:
        date = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()-(int(visitDay) * 86400)))
        sql = " select info,tim from sysinfo where tim > (%s) order by id"
        resultData = readDb2(sql,(date,))
        result = [True,resultData]
    except Exception as e:
        result = [False,str(e)]
    return json.dumps({'resultCode':0,'result':result},cls=DateEncoder)

@route('/resconfig')
@checkAccess
def servtools():
    """资源配置"""
    s = request.environ.get('beaker.session')
    sql = " select value from sysattr where attr='resData' and servattr='sys' "
    result = readDb(sql,)
    try:
        info = json.loads(result[0].get('value'))
    except:
        return(template('resconfig',session=s,msg={},info={}))
    return template('resconfig',session=s,msg={},info=info)

@route('/resconfig',method="POST")
@checkAccess
def do_servtools():
    s = request.environ.get('beaker.session')
    ResState = request.forms.get("ResState")
    ResSaveDay = request.forms.get("ResSaveDay")
    ResInv = request.forms.get("ResInv")
    visitDay = request.forms.get("visitDay")
    try:
       int(ResSaveDay)
       int(visitDay)
       int(ResInv)
    except:
       msg = {'color':'red','message':'配置保存失败,参数不符合要求'}
       return redirect('/resconfig')
    if int(ResSaveDay) < 1 or int(visitDay) < 1 or int(ResInv) < 60 :
       msg = {'color':'red','message':'配置保存失败,参数不符合要求'}
       return redirect('/resconfig')
    idata = dict()
    idata['ResState'] = ResState
    idata['ResSaveDay'] = ResSaveDay
    idata['ResInv'] = ResInv
    idata['visitDay'] = visitDay
    sql = " update sysattr set value=%s where attr='resData' "
    iidata=json.dumps(idata)
    result = writeDb(sql,(iidata,))
    if result == True :
       msg = {'color':'green','message':'配置保存成功'}
    else:
       msg = {'color':'red','message':'配置保存失败'}
    return(template('resconfig',msg=msg,session=s,info=idata))

@route('/applog')
@checkAccess
def applog():
    """服务工具"""
    s = request.environ.get('beaker.session')
    return template('applog',session=s,msg={},info={})

@route('/api/getapplog',method=['GET', 'POST'])
@checkAccess
def getapplog():
    sql = """ SELECT id,objtime,objname,objtext,objact,objhost FROM logrecord order by id desc """
    item_list = readDb(sql,)
    return json.dumps(item_list, cls=DateEncoder)

@route('/ftpservconf')
@checkAccess
def addservconf():
    """新增服务配置项"""
    s = request.environ.get('beaker.session')
    sql = " select id,authtype,listenaddr,listenport,maxuser,sameipmax,vdir,owninfo,umask,passiveenable,passiveport,passiveaddr from ftpserv where id='1'"
    result = readDb(sql,)
    info=result[0]
    info['ftpstatus']=servchk(result[0].get('listenport'))
    return template('ftpservconf',session=s,msg={},info=info)

@route('/ftpservconf',method="POST")
@checkAccess
def do_addftpservconf():
    """新增服务配置项"""
    s = request.environ.get('beaker.session')
    authtype = request.forms.get("authtype")
    listenaddr = request.forms.get("listenaddr")
    listenport = request.forms.get("listenport")
    maxclient = request.forms.get("maxclient")
    sameipmax = request.forms.get("sameipmax")
    vdir = request.forms.get("vdir")
    vid = request.forms.get("vid")
    umask = request.forms.get("umask")
    passiveenable = request.forms.get("passiveenable")
    passiveport = request.forms.get("passiveport")
    passiveaddr = request.forms.get("passiveaddr")
    if (listenaddr != "*" and netmod.checkip(listenaddr) == False) or ( passiveaddr != "*" and netmod.checkip(passiveaddr) == False ) :  
       msg = {'color':'red','message':u'地址填写不合法，保存失败'}
       sql = " select id,authtype,listenaddr,listenport,maxuser,sameipmax,vdir,owninfo,umask,passiveenable,passiveport,passiveaddr from ftpserv where id='1'"
       result = readDb(sql,)
       info=result[0]
       info['ftpstatus']=servchk(result[0].get('listenport'))
       return template('ftpservconf',session=s,msg=msg,info=info)
    for port in passiveport.split('-') :
        if netmod.is_port(port) == False or passiveport.split('-')[0] >= passiveport.split('-')[1]:
           msg = {'color':'red','message':u'端口填写不合法，保存失败'}
           sql = " select id,authtype,listenaddr,listenport,maxuser,sameipmax,vdir,owninfo,umask,passiveenable,passiveport,passiveaddr from ftpserv where id='1'"
           result = readDb(sql,)
           info=result[0]
           info['ftpstatus']=servchk(result[0].get('listenport'))
           return template('ftpservconf',session=s,msg=msg,info=info) 
    if int(listenport) < 0 or int(listenport) > 65535 :
       msg = {'color':'red','message':u'端口配置错误，保存失败'}
       sql = " select id,authtype,listenaddr,listenport,maxuser,sameipmax,vdir,owninfo,umask,passiveenable,passiveport,passiveaddr from ftpserv where id='1'"
       result = readDb(sql,)
       info=result[0]
       info['ftpstatus']=servchk(result[0].get('listenport'))
       return template('ftpservconf',session=s,msg=msg,info=info)
    #ftp根路径处理判断
    if vdir.endswith('/'):
       vdir = re.sub('/$','',vdir)
    if not vdir.startswith('/'):
       msg = {'color':'red','message':u'根路径必须绝对路径，保存失败'}
       sql = " select id,authtype,listenaddr,listenport,maxuser,sameipmax,vdir,owninfo,umask,passiveenable,passiveport,passiveaddr from ftpserv where id='1'"
       result = readDb(sql,)
       info=result[0]
       info['ftpstatus']=servchk(result[0].get('listenport'))
       return template('ftpservconf',session=s,msg=msg,info=info)
    sql = " UPDATE ftpserv set authtype=%s,listenaddr=%s,listenport=%s,maxuser=%s,sameipmax=%s,vdir=%s,owninfo=%s,umask=%s,passiveenable=%s,passiveport=%s,passiveaddr=%s where id='1'"
    data = (authtype,listenaddr,listenport,maxclient,sameipmax,vdir,vid,umask,passiveenable,passiveport,passiveaddr)
    result = writeDb(sql,data)
    if result == True :
       msg = {'color':'green','message':u'配置保存成功'}
       sql = " select id,authtype,listenaddr,listenport,maxuser,sameipmax,vdir,owninfo,umask,passiveenable,passiveport,passiveaddr from ftpserv where id='1'"
       result = readDb(sql,)
       writeFTPconf(action='uptconf')
       info=result[0]
       time.sleep(1) #防止检测FTP服务状态时异常
       info['ftpstatus']=servchk(result[0].get('listenport'))
       return template('ftpservconf',session=s,msg=msg,info=info)
    else :
       msg = {'color':'red','message':u'配置保存失败'}
       sql = " select id,authtype,listenaddr,listenport,maxuser,sameipmax,dir,owninfo,umask,passiveenable,passiveport,passiveaddr from ftpserv where id='1'"
       result = readDb(sql,)
       info=result[0]
       info['ftpstatus']=servchk(result[0].get('listenport'))
       return template('ftpservconf',session=s,msg=msg,info=info)

@route('/showlog')
@checkAccess
def showservlog():
    """显示日志项"""
    s = request.environ.get('beaker.session')
    result = cmds.getdictrst('tail -300 %s/ftpd/ftpd.log|awk \'{$4="";print $0}\'' % gl.get_value('plgdir'))
    return template('showlog',session=s,msg={},info=result)

@route('/onlineusers')
@checkAccess
def showservlog():
    """显示日志项"""
    s = request.environ.get('beaker.session')
    return template('onlineuser',session=s,msg={})

@route('/syscheck')
@checkAccess
def syscheck():
    s = request.environ.get('beaker.session')
    result = cmds.envCheck()
    return template('systemcheck',session=s,info=result)

@route('/syscheck',method="POST")
@checkAccess
def do_syscheck():
    s = request.environ.get('beaker.session')
    result = cmds.envCheck()
    return(template('systemcheck',session=s,info=result))

# 备份集管理
@route('/backupset')
@checkAccess
def syscheck():
    s = request.environ.get('beaker.session')
    return template('backupset',session=s,msg={})

@route('/uploadfile')
@checkAccess
def syscheck():
    s = request.environ.get('beaker.session')
    return template('uploadfile',session=s,msg={})

@route('/uploadfile', method='POST')
@checkAccess
def do_upload():
    s = request.environ.get('beaker.session')
    category = request.forms.get('category')
    upload = request.files.get('upload')
    name, ext = os.path.splitext(upload.filename)
    if ext not in ('.bkt','.jpgsss'):
        msg = {'color':'red','message':u'文件格式不被允许.请重新上传'}
        return template('backupset',session=s,msg=msg)
    try:
        upload.save('%s/backupset' % gl.get_value('plgdir'))
        msg = {'color':'green','message':u'文件上传成功'}
        return template('backupset',session=s,msg=msg)
    except:
        msg = {'color':'red','message':u'文件上传失败'}
        return template('backupset',session=s,msg=msg)

@route('/fileshare/<path>')
@checkLogin
def fileshare(path):
    s = request.environ.get('beaker.session')
    # 获取FTP目录列表
    ftpuser = s['username']
    ftppass=LoginCls().decode(AppServer().getConfValue('keys','pkey'),s['skeyid'])
    sql = """ select listenaddr,listenport,passiveenable,passiveaddr from ftpserv """
    result = readDb(sql,)
    if int(result[0].get('passiveenable')) == 0:
       if result[0].get('listenaddr') == "*":
          servaddr="127.0.0.1"
       else:
          servaddr=result[0].get('listenaddr')
    else:
       if result[0].get('passiveaddr') == "*":
          servaddr="127.0.0.1"
       else:
          servaddr=result[0].get('passiveaddr')
    try:
       ftp = FTPHandle(servaddr,int(result[0].get('listenport')),'0','1')
    except:
       newflist=[]
       msg={'color':'red','message':u'FTP服务连接失败,请检查FTP配置'}
       return template('fileshare',session=s,msg=msg,path=path,ftpdirs=[])
    try:
       ftp.Login(ftpuser,ftppass)
    except:
       newflist=[]
       msg={'color':'red','message':u'FTP服务连接失败,请检查FTP配置'}
       return template('fileshare',session=s,msg=msg,path=path,ftpdirs=[])
    try: 
       flistdict=ftp.getdirs()
    except:
       newflist=[]
       msg={'color':'red','message':u'目录读取失败,请检查FTP配置'}
       return template('fileshare',session=s,msg=msg,path=path,ftpdirs=[])
    ftp.close()
    return template('fileshare',session=s,msg={},path=path,ftpdirs=flistdict.get('dirs'))

@route('/api/getfileshareinfo/<path>',method=['GET', 'POST'])
@checkLogin
def getfileshareinfo(path):
    import chardet
    from MySQL import readDb
    s = request.environ.get('beaker.session')
    ftpuser = s['username']
    ftppass=LoginCls().decode(AppServer().getConfValue('keys','pkey'),s['skeyid'])
    sql = """ select listenaddr,listenport,passiveenable,passiveaddr from ftpserv """
    result = readDb(sql,)
    if int(result[0].get('passiveenable')) == 0:
       if result[0].get('listenaddr') == "*":
          servaddr="127.0.0.1"
       else:
          servaddr=result[0].get('listenaddr')
    else:
       if result[0].get('passiveaddr') == "*":
          servaddr="127.0.0.1"
       else:
          servaddr=result[0].get('passiveaddr')
    try:
       ftp = FTPHandle(servaddr,int(result[0].get('listenport')),'0','1')
    except:
       newflist=[]
       return json.dumps(newflist)
    try:
       ftp.Login(ftpuser,ftppass)
    except:
       newflist=[]
       return json.dumps(newflist)
    if path == 'root':
       flistdict=ftp.getdirs()
    else:
       charstr=chardet.detect(path).get('encoding')
       if str(charstr).lower() != "gbk" :
          try:
            path=path.decode('utf-8').encode('gbk')
          except:
            path=path
       flistdict=ftp.getdirs(path)
    ftp.close()
    newflist=[]
    for i in flistdict.get('files'):
        charstr=chardet.detect(i.get('name')).get('encoding')
        if str(charstr).lower() != "utf-8" :
           try:
              i['name']=i.get('name').decode('gbk').encode('utf-8')
              newflist.append(i)
           except:
              continue
        else:
           newflist.append(i)
    return json.dumps(newflist)

@route('/addfileshare', method='POST')
@checkLogin
def do_upload():
    import chardet
    s = request.environ.get('beaker.session')
    dstdir = request.forms.get('dstdir')
    charstr=chardet.detect(dstdir).get('encoding')
    if str(charstr).lower() != "gbk" :
       try:
          dstdir=dstdir.decode('utf-8').encode('gbk')
       except:
          dstdir=dstdir
    ftpuser=s['username']
    ftppass=LoginCls().decode(AppServer().getConfValue('keys','pkey'),s['skeyid'])
    sql = """ select listenaddr,listenport,passiveenable,passiveaddr from ftpserv """
    result = readDb(sql,)
    if int(result[0].get('passiveenable')) == 0:
       if result[0].get('listenaddr') == "*":
          servaddr="127.0.0.1"
       else:
          servaddr=result[0].get('listenaddr')
    else:
       if result[0].get('passiveaddr') == "*":
          servaddr="127.0.0.1"
       else:
          servaddr=result[0].get('passiveaddr')
    try:
       ftp = FTPHandle(servaddr,int(result[0].get('listenport')),'0','1')
    except:
       return -1
    fname = request.forms.get('fname')
    if fname:
       charstr=chardet.detect(fname).get('encoding')
       if str(charstr).lower() != "gbk" :
          try:
              fname=fname.decode('utf-8').encode('gbk')
          except:
              pass
       os.system('rm -f /tmp/%s_ftpfile' % ftpuser)
       softfile = request.POST.get('fdesc')
       softfile.save('/tmp/%s_ftpfile' % ftpuser, overwrite=True)
       try:
         ftp.Login(ftpuser,ftppass)
         ftp.UpLoadFile("/tmp/%s_ftpfile" % ftpuser, fname, dstdir )
         ftp.close()
       except:
         return -1
       os.system('rm -f /tmp/%s_ftpfile' % ftpuser)
       return 0
    else:
       return -1

@route('/startbackupset')
@checkAccess
def delbackupset():
    s = request.environ.get('beaker.session')
    createtm = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
    from MySQL import db_name,db_user,db_pass,db_ip,db_port
    backupsetname='backupset_%s.bkt' % createtm
    cmd='mysqldump -u%s -p%s -h%s -P%s %s > %s/backupset/%s ' % (db_user,db_pass,db_ip,db_port,db_name,gl.get_value('plgdir'),backupsetname)
    x,y = cmds.gettuplerst(cmd)
    if x == 0:
       msg = {'color':'green','message':u'备份完成'}
    else :
       msg = {'color':'red','message':u'备份失败'}
    return template('backupset',session=s,msg=msg)


@route('/download/<vdir>/<filename:re:.*\.zip|.*\.bkt>')
def download(vdir,filename):
    if vdir == 'backupset':
       download_path = '%s/backupset' % gl.get_value('plgdir')
    return static_file(filename, root=download_path, download=filename)

@route('/restore/<filename>')
@checkAccess
def restore(filename):
    s = request.environ.get('beaker.session')
    if filename != "":
       db_name = AppServer().getConfValue('Databases','MysqlDB')
       db_user = AppServer().getConfValue('Databases','MysqlUser')
       db_pass = AppServer().getConfValue('Databases','MysqlPass')
       db_ip = AppServer().getConfValue('Databases','MysqlHost')
       db_port = AppServer().getConfValue('Databases','MysqlPort')
       x,y=cmds.gettuplerst('mysql -h%s -P%s -u%s -p%s %s < %s/backupset/%s' % (db_ip,db_port,db_user,db_pass,db_name,gl.get_value('plgdir'),filename))
       if x == 0:
          msg = {'color':'green','message':u'备份集恢复成功,请重启服务以重新加载数据.'}
       else:
          msg = {'color':'red','message':u'备份集恢复失败'}
    else:
       msg = {'color':'red','message':u'备份集恢复失败'}
    return template('backupset',session=s,msg=msg)


@route('/delbackupset/<filename>')
@checkAccess
def delbackupset(filename):
    s = request.environ.get('beaker.session')
    if filename != "":
       x,y=cmds.gettuplerst('rm -rf %s/backupset/%s' % (gl.get_value('plgdir'),filename))
       if x == 0:
          msg = {'color':'green','message':u'备份集删除成功'}
       else:
          msg = {'color':'red','message':u'备份集删除失败'}
    return template('backupset',session=s,msg=msg)

@route('/api/getbackupsetinfo',method=['GET', 'POST'])
@checkAccess
def getbackupsetinfo():
    info=[]
    status,result=cmds.gettuplerst('find %s/backupset -name \'*.bkt\' -exec basename {} \;' % gl.get_value('plgdir'))
    for i in result.split('\n'):
        if str(i) != "":
           infos={}
           infos['filename']=str(i)
           infos['filesize']=os.path.getsize('%s/backupset/%s' % (gl.get_value('plgdir'),i))
           cctime=os.path.getctime('%s/backupset/%s' % (gl.get_value('plgdir'),i))
           infos['filetime']=time.strftime('%Y%m%d%H%M%S',time.localtime(cctime))
           info.append(infos)
    return json.dumps(info)

@route('/api/getonlineusers',method=['GET', 'POST'])
@checkAccess
def getonlineusers():
    info=[]
    status,result=cmds.gettuplerst('pure-ftpwho -H -n -s')
    for i in result.split('\n'):
        if str(i) != "" and len(i.split('|')) > 5:
           infos={}
           infos['spid']=i.split('|')[0]
           infos['username']=i.split('|')[1]
           infos['ctime']=int(int(i.split('|')[2])/60)
           infos['remoteaddr']=i.split('|')[5]
           info.append(infos)
    return json.dumps(info)

@route('/disconn/<spid>')
@checkAccess
def disconn(spid):
    s = request.environ.get('beaker.session')
    x,y=cmds.gettuplerst('kill -9 %s' % (spid))
    if x == 0:
          msg = {'color':'green','message':u'强制中断完成'}
    else:
          msg = {'color':'red','message':u'中断失败请重试'}
    return template('onlineuser',session=s,msg=msg)

if __name__ == '__main__' :
   sys.exit()
