/**
* 针对修改不同版块，修改模态框的标题
*/
$(".editor").on("click", (e)=> {
    let $target = $(e.target);
    let title = $target.siblings("legend").text();
    $("#modifiyInfoModalLabel").text(title);
    $("#modifiyInfoModal").modal('show');
});

$("#submit-btn").click((e) => { 
    e.preventDefault();
    check_model_submit();
});

/**
 * 检查提交内容
 */
function check_model_submit(){
    let target = $("#recipient-name").val();
    if(target.trim().length == 0) return;
    let content = $("#message-text").val();
    if(content.trim().length == 0) return;

    let form_data = {
        "csrf_token": $('#csrf_token').val(),
        "title": $("#modifiyInfoModalLabel").text(),
        "type" : $("input[name='add-modify-delete']:checked").val(),
        "target" : target,
        "content" : content
    }
    $.ajax({
        type: "post",
        url: "/info_modify",
        data: form_data,
        dataType: "json",
        success: function (response) {
            $("#modifiyInfoModal").modal("hide");
            toggle_alert(true);
        },
        error : function(error){
            $("#modifiyInfoModal").modal("hide");
            console.log(error);
            toggle_alert(false);
        }
    });
}

/**
 * 显示/隐藏提示框
 * @param {boolean} isSuccess 
 */
function toggle_alert(isSuccess){
    let success = $("#alert-box-success");
    let error = $("#alert-box-danger");
    // 显示操作成功的提示框
    if(isSuccess){
        error.hide();
        success.show(200);
        setTimeout(()=>{
            success.hide(200);
        }, 2000)
    }else{
        success.hide();
        error.show(200);
        setTimeout(()=>{
            error.hide(200);
        },2000);
    }
}


