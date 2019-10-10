%rebase base position='用户管理',managetopli="active open",adduser="active"

<div class="page-body">
    <div class="row">
        <div class="col-lg-12 col-md-12 col-sm-12 col-xs-12">
            <div class="widget">
                <div class="widget-header bordered-bottom bordered-themesecondary">
                    <i class="widget-icon fa fa-tags themesecondary"></i>
                    <span class="widget-caption themesecondary">用户列表</span>
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
                    <div class="tickets-container">
                        <div class="table-toolbar" style="float:left">
                            <!--a id="adduser" href="javascript:void(0);" class="btn  btn-primary ">
                                <i class="btn-label fa fa-plus"></i>添加用户
                            </a>
                            <a id="changeuser" href="javascript:void(0);" class="btn btn-warning shiny">
                                <i class="btn-label fa fa-cog"></i>修改用户
                            </a>
                            <a id="deluser" href="javascript:void(0);" class="btn btn-darkorange">
                                <i class="btn-label fa fa-times"></i>删除用户
                            </a-->
                            %if msg.get('message'):
                      		    <span style="color:{{msg.get('color','')}};font-weight:bold;">&emsp;{{msg.get('message','')}}</span>
                    	    %end
                        </div>
                       <table id="myLoadTable" class="table table-bordered table-hover"></table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="modal fade" id="myModal" tabindex="-1" role="dialog"  aria-labelledby="myModalLabel" aria-hidden="true">
    <div class="modal-dialog" >
      <div class="modal-content" id="contentDiv">
         <div class="widget-header bordered-bottom bordered-blue ">
           <i class="widget-icon fa fa-pencil themeprimary"></i>
           <span class="widget-caption themeprimary" id="modalTitle">添加用户</span>
         </div>

         <div class="modal-body">
            <div>
            <form id="modalForm">
                <div class="form-group">
                  <label class="control-label" for="inputSuccess1">帐号：</label>
                  <input type="text" class="form-control" onkeyup="value=value.replace(/[^\w\.\/]/ig,'')" id="username" name="username" placeholder="由字母、数字组成(特殊符号除外)，至少4位以上" require>
                </div>
                <div class="form-group">
                  <label class="control-label" for="inputSuccess1">密码：</label>
                  <input type="password" class="form-control" id="password" name="password" placeholder="由字母、数字组成、符号，至少8位以上" require>
                </div>
                <div class="form-group">
                  <label class="control-label" for="inputSuccess1">允许IP：</label>
                  <input type="text" class="form-control" onkeyup="this.value=this.value.replace(/[^\d.]/g,'')" onafterpaste="this.value=this.value.replace(/[^\d.]/g,'')" id="ipaccess" name="ipaccess">
                </div>
                <div class="form-group">
                  <label class="control-label" for="inputSuccess1">上传速率：</label>
                  <input type="text" class="form-control" onkeyup="this.value=this.value.replace(/\D/g,'')" onafterpaste="this.value=this.value.replace(/\D/g,'')" id="ulbandwidth" name="ulbandwidth">
                </div>
                <div class="form-group">
                  <label class="control-label" for="inputSuccess1">下载速率：</label>
                  <input type="text" class="form-control" onkeyup="this.value=this.value.replace(/\D/g,'')" onafterpaste="this.value=this.value.replace(/\D/g,'')" id="dlbandwidth" name="dlbandwidth">
                </div>
                <div class="form-group">
                  <label class="control-label" for="inputSuccess1">空间大小：</label>
                  <input type="text" class="form-control" onkeyup="this.value=this.value.replace(/\D/g,'')" onafterpaste="this.value=this.value.replace(/\D/g,'')" id="quotasize" name="quotasize">
                </div>
                <div class="form-group">
                  <label class="control-label" for="inputSuccess1">用户路径：</label>
                  <input type="text" class="form-control" onkeyup="value=value.replace(/[^\w\.\/]/ig,'')" id="vdir" name="vdir">
                </div>
                <div class="form-group">
                  <label class="control-label" for="inputSuccess1">用户权限：</label>
                  <select id="power" style="width:100%;" name="power">
                    <option value='1'>可读写</option>
                    <option value='0'>仅读取</option>
                 </select>
                </div>
                <div class="form-group">
                  <label class="control-label" for="inputSuccess1">用户状态：</label>
                  <select id="ustatus" style="width:100%;" name="ustatus">
                    <option value='1'>启用</option>
                    <option value='0'>禁用</option>
                 </select>
               </div>
               <div class="form-group">
                  <label class="control-label" for="inputSuccess1">备注信息：</label>
                  <textarea id="comment" name="comment" style="height:70px;width:100%;" ></textarea>
              </div>
              <div class="form-group">
                  <input type="hidden" id="hidInput" value="">
                  <button type="button" id="subBtn" class="btn btn-primary  btn-sm">提交</button>
                  <button type="button" class="btn btn-warning btn-sm" data-dismiss="modal">关闭</button>
              </div>
            </form>
            </div>
         </div>
      </div>
   </div>
</div>
<script type="text/javascript">
$(function(){
    /* **表格数据 */
    var editId;        //定义全局操作数据变量
    var isEdit;
    $('#myLoadTable').bootstrapTable({
          method: 'post',
          url: '/api/getonlineusers',
          contentType: "application/json",
          datatype: "json",
          cache: false,
          checkboxHeader: true,
          striped: true,
          pagination: true,
          pageSize: 15,
          pageList: [10,20,50],
          search: true,
          showColumns: true,
          showRefresh: true,
          minimumCountColumns: 2,
          clickToSelect: true,
          smartDisplay: true,
          //sidePagination : "server",
          sortOrder: 'asc',
          sortName: 'id',
          columns: [{
              field: 'bianhao',
              title: 'checkbox',      
              checkbox: true,
          },{
              field: 'xid',
              title: '编号',
              align: 'center',
              valign: 'middle',
              width:25,
              //sortable: false,
	      formatter:function(value,row,index){
                return index+1;
              }
          },{

              field: 'spid',
              title: '系统ID',
              align: 'center',
              valign: 'middle',
              sortable: false
          },{ 
              field: 'username',
              title: '用户名',
              align: 'center',
              valign: 'middle',
              sortable: false
          },{ 
              field: 'remoteaddr',
              title: '远程地址',
              align: 'center',
              valign: 'middle',
              //visible: false,
              sortable: false
          },{
              field: 'ctime',
              title: '连接时长(min)',
              align: 'center',
              valign: 'middle',
              sortable: false,
          },{
              field: '',
              title: '操作',
              align: 'center',
              valign: 'middle',
              width:200,
              formatter:getinfo
          }]
      });
      //定义列操作
      function getinfo(value,row,index){
        eval('rowobj='+JSON.stringify(row));
        //定义编辑按钮样式，只有管理员或自己编辑的任务才有权编辑
        //if("{{session.get('username',None)}}" ){
        //    var style_del = '&nbsp;<a href="/delftpobj/'+rowobj['name']+'" class="btn-sm btn-danger" onClick="return confirm(&quot;确定删除?&quot;)"> ';
        //}else{
        //    var style_del = '&nbsp;<a class="btn-sm btn-danger" disabled>';
        //}
        //定义删除按钮样式，只有管理员或自己编辑的任务才有权删除
        if("{{session.get('username',None)}}"){
            var style_disconn = '&nbsp;<a href="/disconn/'+rowobj['spid']+'" class="btn-sm btn-danger" onClick="return confirm(&quot;确定强制断开吗?&quot;)"> ';
        }else{
            var style_disconn = '&nbsp;<a class="btn-sm btn-danger" disabled>';
        }

        return [
            //style_del,
            //    '<i class="fa fa-download"> 下载或删除</i>',
            //'</a>',

            style_disconn,
                '<i class="fa fa-times"> 断开</i>',
            '</a>'
        ].join('');
    }
})
</script>
