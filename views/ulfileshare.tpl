%rebase base position='文件上传页面'
<script src="/assets/js/uploadFile.js"></script>
<style>
    .banner-block .upload-block {
      position: relative;
      width: 540px;
      height: 150px;
      padding: 15px;
      background-color: #F7F7F7;
      border: 10px solid  #fff;
      border-radius: 5px;
      outline: 1px dashed #999;
      text-align: center;
      color: #797E8E;
      margin-left: auto;
      margin-right: auto;
      margin-top: 5px;
      z-index: 10; }
    .banner-block .upload-block:after {
      content: '';
      display: block;
      overflow: hidden;
      clear: both;
      height: 0; }
    .banner-block .upload-block > .upload-desc {
      font-size: 14px;
      line-height: 14px; }
    .banner-block .upload-block > .add-file {
      position: relative;
      width: 29px;
      height: 29px;
      margin-left: auto;
      margin-right: auto;
      margin-top: 10px;
      margin-bottom: 5px; }
    .banner-block .upload-block > .add-file:after {
      content: '';
      display: block;
      overflow: hidden;
      clear: both;
      height: 0; }
    .banner-block .upload-block > .add-file:before, .banner-block .upload-block > .add-file:after {
      display: block;
      position: absolute;
      top: 50%;
      left: 0;
      margin-top: -2px;
      width: 29px;
      height: 4px;
      content: "";
      background: #C4C4C4; }
    .banner-block .upload-block > .add-file:after {
      -webkit-transform-origin: 50% 50%;
      -ms-transform-origin: 50% 50%;
      transform-origin: 50% 50%;
      -webkit-transform: rotate(90deg);
      -ms-transform: rotate(90deg);
      transform: rotate(90deg); }
    .banner-block .upload-block [type="file"] {
      position: absolute;
      left: 0;
      top: 0;
      width: 100%;
      height: 100%;
      opacity: 0; }
    .progress {
      width:100%;
      //padding:10px;
      font-size:15px;
      color:#f60;
      text-align:center;
    }
</style>
<div class="page-body">
    <div class="row">
        <div class="col-lg-12 col-md-12 col-sm-12 col-xs-12">
            <div class="widget">
                <div class="widget-header bordered-bottom bordered-themesecondary">
                    <i class="widget-icon fa fa-tags themesecondary"></i>
                    <span class="widget-caption themesecondary">文件上传</span>
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
		 <div class="banner-block">
  		   <div class="upload-block" id="selectUploadFile">
    		    <div class="upload-desc">拖拽文件到这里 或 点击+上传</div>
    		    <div class="add-file"></div>
    		    <div class="format-desc">支持文件格式：rar zip tar tgz tar.gz doc(x) xls(x) ppt(x) pdf bin</div>
                <div class="">请尽量保持文件名为纯字符或数字组合，不要出现中文/韩文描述，以免系统解码异常</div>
    		    <form id="fileForm" class="" enctype="multipart/form-data" method="post" name="fileinfo">
      		      <input id="uploadFile" type="file" draggable="true" />
      		      <input type="hidden" name="filepath" value="" />
		      <div class="progress"></div>
    		    </form>
  		   </div>
		 </div>
		</div>
		<div class="modal-footer">
                   <a style="margin-left:auto; margin-right:auto;width:100%" class="btn btn-primary" href="/fileshare">返回分享页</a>
                </div>
		<!--第一屏-->
		<div class="mt40"></div>
		<script src="https://cdn.bootcss.com/jquery/1.11.3/jquery.js"></script>
		<!--上传组件进度条-->
             </div>
        </div>
    </div>
</div>
<script src="/assets/js/datetime/bootstrap-datepicker.js"></script> 
<script charset="utf-8" src="/assets/kindeditor/kindeditor.js"></script>
<script charset="utf-8" src="/assets/kindeditor/lang/zh_CN.js"></script>
<script>
  var sUploadFile = new SgyUploadFile({
    uploadProgress: function(evt){
      if (evt.lengthComputable) {
        var percentComplete = Math.round(evt.loaded * 100 / evt.total);
        $('.progress').html("上传文件进度"+percentComplete+"%");
      }
    },
    uploadError: function( result ) {
      // 上传失败关闭进度条
      $('#uploadFile').val('');
    },
    uploadSuccess:function( result ) {
      if(result.error_code == 0) {
        $('#uploadFile').val('');
      }
    }
  });
  /**
   * 上传组件
   */
  $( function() {
    /**
     * 1、获取文件路径
     * 2、获取文件后缀名
     * 3、判断文件后缀是否正确，不正确提供格式不正确，清除input中的文件
     * 4、格式正确，开始上传文件
     */
    $( '#uploadFile' ).on( 'change', function( event ) {
      var el  = event.srcElement || event.target;
      var fileName = el.value;
      var files = el.files;
      if(files.length == 1) {
        var file = files[ 0 ];
        sUploadFile.ajaxUpload({
          formData:sUploadFile.wrapperFormDate(file, fileName),
          fileName:fileName
        });
      }
    } );
    // 当鼠标释放时
    document.addEventListener( 'drop', function( e ) {
      var file = e.dataTransfer.files[ 0 ];
      if ( file ) {
        sUploadFile.ajaxUpload({
          formData:sUploadFile.wrapperFormDate(file),
          fileName:file.name
        });
      }
    }, false );
  } );
</script>
