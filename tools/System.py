#!/usr/bin/env python
#coding=utf-8
import os,sys,json,re,time,datetime,logging,zipfile,platform
from bottle import request,route,template,static_file,abort,redirect

from MySQL import writeDb,readDb,readDb2
from Login import checkLogin,checkAccess

from Functions import AppServer,cmdhandle,writeFTPconf,GetFileMd5,is_chinese,netModule

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
    info['v4addr'] = 'Lan: '+netmod.NatIP()+'\tWan: '+netmod.NetIP()
    info['appversion'] = AppServer().getVersion()
    """管理日志"""
    sql = " SELECT id,objtext,objact,objhost,objtime FROM logrecord order by id DESC limit 7 "
    logdict = readDb(sql,)
    return template('systeminfo',session=s,info=info,logdict=logdict)

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
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

class DateEncoder(json.JSONEncoder):  
    def default(self, obj):  
        if isinstance(obj, datetime.datetime):  
            return obj.strftime('%Y-%m-%d %H:%M:%S')  
        elif isinstance(obj, date):  
            return obj.strftime("%Y-%m-%d")  
        else:  
            return json.JSONEncoder.default(self, obj) 

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
    return template('ftpservconf',session=s,msg={},info=result[0])

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
    if ( listenaddr != "*" and netmod.checkmask(listenaddr) == False ) or ( passiveaddr != "*" and netmod.checkip(passiveaddr) == False ) :  
       msg = {'color':'red','message':u'地址填写不合法，保存失败'}
       sql = " select id,authtype,listenaddr,listenport,maxuser,sameipmax,vdir,owninfo,umask,passiveenable,passiveport,passiveaddr from ftpserv where id='1'"
       result = readDb(sql,)
       return template('ftpservconf',session=s,msg=msg,info=result[0])
    #ftp根路径处理判断
    if vdir.endswith('/'):
       vdir = re.sub('/$','',vdir)
    if not vdir.startswith('/'):
       msg = {'color':'red','message':u'根路径必须绝对路径，保存失败'}
       sql = " select id,authtype,listenaddr,listenport,maxuser,sameipmax,vdir,owninfo,umask,passiveenable,passiveport,passiveaddr from ftpserv where id='1'"
       result = readDb(sql,)
       return template('ftpservconf',session=s,msg=msg,info=result[0])
    sql = " UPDATE ftpserv set authtype=%s,listenaddr=%s,listenport=%s,maxuser=%s,sameipmax=%s,vdir=%s,owninfo=%s,umask=%s,passiveenable=%s,passiveport=%s,passiveaddr=%s where id='1'"
    data = (authtype,listenaddr,listenport,maxclient,sameipmax,vdir,vid,umask,passiveenable,passiveport,passiveaddr)
    result = writeDb(sql,data)
    if result == True :
       msg = {'color':'green','message':u'配置保存成功'}
       sql = " select id,authtype,listenaddr,listenport,maxuser,sameipmax,vdir,owninfo,umask,passiveenable,passiveport,passiveaddr from ftpserv where id='1'"
       result = readDb(sql,)
       writeFTPconf(action='uptconf')
       return template('ftpservconf',session=s,msg=msg,info=result[0])
    else :
       msg = {'color':'red','message':u'配置保存失败'}
       sql = " select id,authtype,listenaddr,listenport,maxuser,sameipmax,dir,owninfo,umask,passiveenable,passiveport,passiveaddr from ftpserv where id='1'"
       result = readDb(sql,)
       return template('ftpservconf',session=s,msg=msg,info=result[0])

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


@route('/fileshare')
@checkLogin
def fileshare():
    s = request.environ.get('beaker.session')
    urladdr = dict()
    # 判断配置文件中url是否合规,合规才提交到界面替换默认url
    pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    result = re.match(pattern,AppServer().getConfValue('fileshare','urladdr'))
    if str(result) == 'None':
       urladdr['url']="1"
    else:
       urladdr['url'] = AppServer().getConfValue('fileshare','urladdr')
    return template('fileshare',session=s,msg={},urladdr=urladdr)

@route('/api/getfileshareinfo',method=['GET', 'POST'])
@checkLogin
def getfileshareinfo():
    import chardet
    s = request.environ.get('beaker.session')
    username = s['username']
    sql = " SELECT concat(D.vdir,'/',U.vdir) as vdir FROM user as U LEFT OUTER JOIN ftpserv as D ON D.id='1' WHERE U.username=%s "
    ownftpdir = readDb(sql,(username,))[0].get('vdir')
    info=[]
    status,result=cmds.gettuplerst('find %s -name \'*.*\' -exec basename {} \;|sort -u' % ownftpdir)
    for i in result.split():
        if str(i) != "":
           infos={}
           charstr=chardet.detect(str(i)).get('encoding')
           if str(charstr).lower() != "utf-8" :
              #print str(charstr).lower()
              try:
                 infos['filename']=i.decode(str(charstr)).encode('utf-8')
              except:
                 continue
              ownftpdir = ownftpdir.encode(str(charstr)).encode('utf-8')
              filepath = '%s/%s' % (ownftpdir.encode(charstr),i)
              nfilepath = filepath.decode(charstr).encode('utf-8')
           else:
              infos['filename']=i
              filepath = '%s/%s' % (ownftpdir,i)
              nfilepath = filepath
           #if chardet.detect(i).get('encoding')=="GB2312":
           #   infos['filename']=i.decode('GB2312')
           #   ownftpdir = ownftpdir.encode('GB2312')
           #   filepath = '%s/%s' % (ownftpdir.encode('GB2312'),i)
           #   nfilepath = filepath.decode('gb2312').encode('utf-8')
           #else:
           #   infos['filename']=i
           #   filepath = '%s/%s' % (ownftpdir,i)
           #   nfilepath = filepath
           if os.path.isfile(filepath) == False:
              continue
           infos['filesize']=os.path.getsize(filepath)
           cctime=os.path.getctime(filepath)
           infos['filetime']=time.strftime('%Y%m%d%H%M%S',time.localtime(cctime))
        infos['signdata']=GetFileMd5(filepath)
        sql = " INSERT INTO fileshare (filepath, signdata) VALUES (%s , %s) ON DUPLICATE KEY UPDATE filepath=%s,signdata=%s "
        data = (nfilepath,infos['signdata'],nfilepath,infos['signdata'])
        try:
           writeDb(sql,data)
        except :
           True
        info.append(infos)
    return json.dumps(info)

@route('/ulfileshare')
@checkLogin
def syscheck():
    s = request.environ.get('beaker.session')
    return template('ulfileshare',session=s)

@route('/ulfileshare', method='POST')
@checkLogin
def do_upload():
    import chardet
    s = request.environ.get('beaker.session')
    urladdr = dict()
    # 判断配置文件中url是否合规,合规才提交到界面替换默认url
    pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    result = re.match(pattern,AppServer().getConfValue('fileshare','urladdr'))
    if str(result) == 'None':
       urladdr['url']="1"
    else:
       urladdr['url'] = AppServer().getConfValue('fileshare','urladdr')
    username = s['username']
    sql = " SELECT concat(D.vdir,'/',U.vdir) as vdir FROM user as U LEFT OUTER JOIN ftpserv as D ON D.id='1' WHERE U.username=%s "
    ownftpdir = readDb(sql,(username,))[0].get('vdir')
    upload = request.files.get('cv')
    #为了兼容ftp显示字符，UTF8字符文件名转换为GB2312
    if is_chinese(upload.filename) == True:
       ownftpdir = ownftpdir.encode('GB2312','ignore')
       filename=str(upload.filename).encode('GB2312','ignore')
    else:
       filename = str(upload.filename)
       #取消判断文件格式，由JS判断
       #name, ext = os.path.splitext(upload.filename)
       #if ext not in ('.rar','.zip','.bin','.tar','.tgz','.tar.gz','.doc','.docx','.xls','.xlsx','.ppt','.pptx'):
       #        msg = {'color':'red','message':u'文件格式不被允许.请重新上传'}
       #        return template('fileshare',session=s,msg=msg,urladdr=urladdr)
    cmds.gettuplerst('%s/sbin/mkdir -p %s' % (gl.get_value('wkdir'),ownftpdir))
    try:
       upload.save('%s/%s' % (ownftpdir,filename))
       cmds.getdictrst('chown vftp:vftp %s/%s' % (ownftpdir,filename))
       msg = {'color':'green','message':u'文件上传成功'}
       return template('fileshare',session=s,msg=msg,urladdr=urladdr)
    except:
       msg = {'color':'red','message':u'文件上传失败'}
       return template('fileshare',session=s,msg=msg,urladdr=urladdr)

@route('/filesharesign/<signdata>')
def filesharesign(signdata):
    sql = " SELECT filepath from fileshare where signdata=%s "
    if signdata == "" :
       return abort(404)
    download_path = readDb(sql,(signdata,))[0].get('filepath')
    filename = os.path.basename(download_path)
    if is_chinese(filename) == True:
       filename = filename.encode('GB2312')
       filedir  = os.path.dirname(download_path).encode('GB2312')
    else :
        filedir  = os.path.dirname(download_path)
    return static_file(filename, root=filedir, download=filename)

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

if __name__ == '__main__' :
   sys.exit()
