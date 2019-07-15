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
    if(target.trim().length == 0){
        toggle_alert(false, "", "修改项不能为空");
        return;
    }
    let content = $("#message-text").val();
    if(content.trim().length == 0){
        toggle_alert(false, "", "请输入具体内容");
        return;
    } 

    let form_data = {
        "csrf_token": $('#csrf_token').val(),
        "title": $("#modifiyInfoModalLabel").text(),
        "type" : $("input[name='add-modify-delete']:checked").val(),
        "target" : target,
        "content" : content
    }
    $.ajax({
        type: "post",
        url: "/feedback",
        data: form_data,
        dataType: "json",
        success: function (response) {
            toggle_alert(response.success, "modifiyInfoModal");
        },
        error : function(error){
            $("#").modal("hide");
            console.log(error);
            toggle_alert(false, "modifiyInfoModal");
        }
    });
}