%rebase base position='FTP服务配置'
<div class="page-body">
    <div class="row">
        <div class="col-lg-12 col-md-12 col-sm-12 col-xs-12">
            <div class="widget">
                <div class="widget-header bordered-bottom bordered-themesecondary">
                    <i class="widget-icon fa fa-tags themesecondary"></i>
                    <span class="widget-caption themesecondary">FTP服务配置</span>
                    <div class="widget-buttons">
                        <a href="#" data-toggle="maximize">
                            <i class="fa fa-expand"></i>
                        </a>
                        <a href="#" data-toggle="collapse">
                            <i class="fa fa-minus"></i>
                        </a>
                        <a href="#" data-toggle="dispose">
                            <i class="fa fa-times"></i>
                        </a>
                    </div>
                    
                </div><!--Widget Header-->
                <div style="padding:-10px 0px;" class="widget-body no-padding">
                  <form action="" method="post">
		    %if msg.get('message'):
                            <span style="color:{{msg.get('color','')}};font-weight:bold;">&emsp;{{msg.get('message','')}}</span>
                    %end
		    <div class="modal-body">
                        <div class="input-group">
                           <span class="input-group-addon">验证方式&emsp;</span>
                           <select style="width:420px" class="form-control" name="authtype">
				<option 
                                %if info.get('authtype','') == 1:
                                        selected
                                %end 
                                value="1">SSL/TLS+普通认证          
                                </option>
                                <option 
				%if info.get('authtype','') == 0:
					selected
				%end 
                                        value="0">仅普通认证
                                </option>
                                <option 
				%if info.get('authtype','') == 2:
                                        selected
                                %end 
                                        value="2">仅SSL/TLS认证
                                </option>
                            </select>
                        </div>
                   </div>
		    <div class="modal-body">
                        <div class="input-group">
                          <span class="input-group-addon">监听信息&emsp;</span>
			  <input type="text" style="width:210px" class="form-control" id="" name="listenaddr" placeholder="IP地址" aria-describedby="inputGroupSuccess4Status"
			   %if info.get('listenaddr',''): 
                                value="{{info.get('listenaddr','')}}"
                           %else :
                                value="*"
                           %end 
			  >
			  <input type="text" style="width:210px" class="form-control" id="" name="listenport" onkeyup="if(this.value.length==1){this.value=this.value.replace(/[^1-9]/g,'')}else{this.value=this.value.replace(/\D/g,'')}" onafterpaste="if(this.value.length==1){this.value=this.value.replace(/[^1-9]/g,'')}else{this.value=this.value.replace(/\D/g,'')}" placeholder="监听端口" aria-describedby="inputGroupSuccess4Status" 
			   %if info.get('listenport',''): 
			   	value="{{info.get('listenport','')}}"
			   %else :
				value="21"
			   %end 
			   readonly>
                        </div>
                    </div>
		    <div class="modal-body">
                        <div class="input-group">
                          <span class="input-group-addon">连接控制&emsp;</span>
                          <input type="text" style="width:210px" class="form-control" id="" name="maxclient" onkeyup="if(this.value.length==1){this.value=this.value.replace(/[^1-9]/g,'')}else{this.value=this.value.replace(/\D/g,'')}" onafterpaste="if(this.value.length==1){this.value=this.value.replace(/[^1-9]/g,'')}else{this.value=this.value.replace(/\D/g,'')}" placeholder="允许客户端同时登录最大值" aria-describedby="inputGroupSuccess4Status" 
			  %if info.get('maxclient',''): 
                                value="{{info.get('maxclient','')}}"
			  %else :
                                value="100"
                          %end 
			  >
			  <input type="text" style="width:210px" class="form-control" id="" name="sameipmax" placeholder="相同IP最大连接数" onkeyup="if(this.value.length==1){this.value=this.value.replace(/[^1-9]/g,'')}else{this.value=this.value.replace(/\D/g,'')}" onafterpaste="if(this.value.length==1){this.value=this.value.replace(/[^1-9]/g,'')}else{this.value=this.value.replace(/\D/g,'')}" aria-describedby="inputGroupSuccess4Status"
			  %if info.get('maxuser',''): 
                                value="{{info.get('sameipmax','')}}"
			  %else :
                                value="50"
                          %end 
			  >
                       </div>
                    </div>
		    <div class="modal-body">
                        <div class="input-group">
                          <span class="input-group-addon" >&nbsp;FTP属性&emsp;</span>
			  <input type="text" style="width:210px" class="form-control" id="" name="vdir" onkeyup="value=value.replace(/[^\w\.\/]/ig,'')" placeholder="FTP主目录" aria-describedby="inputGroupSuccess4Status" 
                          %if info.get('vdir',''): 
                                value="{{info.get('vdir','')}}"
                          %else :
                                value="/ftpdir"
                          %end 
                          >
                          <input type="text" style="width:105px" class="form-control" id="" name="vid" placeholder="用户ID:组ID" aria-describedby="inputGroupSuccess4Status" 
                          %if info.get('maxclient',''): 
                                value="{{info.get('vid','')}}"
			  %else :
                                value="1100:1100"
                          %end 
                          readonly>
                          <input type="text" style="width:105px" class="form-control" id="" name="umask" placeholder="新建权限" aria-describedby="inputGroupSuccess4Status"
                          %if info.get('maxuser',''): 
                                value="{{info.get('umask','')}}"
			  %else :
				value="133:022"
                          %end 
                          readonly>
                       </div>
                    </div>
		    <div class="modal-body">
		    	<div class="input-group">
			   <span class="input-group-addon">被动模式&emsp;</span>
			   <select style="width:210px" class="form-control" id="passiveenable" name="passiveenable">
                                <option 
                                %if info.get('passiveenable','') == 1:
                                        selected
                                %end 
                                value="1">开启
                                </option>
                                <option 
                                %if info.get('passiveenable','') == 0:
                                        selected
                                %end 
                                        value="0">关闭
                                </option>
			   </select>
			   <input type="text" style="width:105px" class="form-control" id="passiveport" name="passiveport" placeholder="被动模式端口" aria-describedby="inputGroupSuccess4Status"
			   %if info.get('passiveport',''): 
                                value="{{info.get('passiveport','')}}"
			   %else :
                                value="60000-60020"
                           %end 
                           readonly>
			   <input type="text" style="width:105px" class="form-control" id="passiveaddr" name="passiveaddr" placeholder="被动模式IP" aria-describedby="inputGroupSuccess4Status"
			   %if info.get('passiveaddr',''): 
                                value="{{info.get('passiveaddr','')}}"
			   %else :
                                value="*"
                           %end 
                           >
		    	</div>
		    </div>
                    <div class="modal-footer">
                        <button type="submit" style="float:left" class="btn btn-primary">保存</button>
                    </div>
                </div>
              </form>
            </div>
        </div>
    </div>
</div>
<script src="/assets/js/datetime/bootstrap-datepicker.js"></script> 
<script charset="utf-8" src="/assets/kindeditor/kindeditor.js"></script>
<script charset="utf-8" src="/assets/kindeditor/lang/zh_CN.js"></script>

<script language="JavaScript" type="text/javascript">
$(function() {
  $('#passiveenable').click(function() {
    if (this.value == '0') {
        //document.getElementById("passiveport").readOnly=true ;
	//document.getElementById("passiveaddr").readOnly=true ;
	$('#passiveport').hide();
	$('#passiveaddr').hide();
    }else{
	$('#passiveport').show();
        $('#passiveaddr').show();
    }
   
  });
  $('#passiveenable').click();
});
</script>
