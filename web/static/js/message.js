/**
 * 发送消息
 * @param element
 */
$("#send_message").click((e) =>{
    let receiver= $("#receiver").val();
    let content = $("#content").val();
    let csrf_token = $("#csrf_token").val();
    //TODO:接收者的id已经得知
    let receiver_id = null;
    //TODO:遍历查找接收者的id 目前未处理存在重名的情况
    for (let i = 0; i < users.length; i++){
        if (users[i].name == receiver){
            receiver_id = users[i].id;
            break;
        }
    }
    if (receiver_id == null)
    {
        toggle_alert(false, "scheduleModal", "发送失败，请确定名字");
        return ;
    }
    $.ajax({
        url: '/add_message',
        type: 'POST',
        data: {
            receiver: receiver,
            receiver_id: receiver_id,
            content: content,
            csrf_token: csrf_token,
        },
        dataType: 'json'
    }).done(function (data) {
        if(data.success){
            toggle_alert(true, "scheduleModal", "发送成功");
        }
    });
});

//请求获取所有的商务名字和id
let users = null;
$.ajax({
    url: '/get_agents',
    type: 'GET',
    dataType: 'json'
}).done(function (data) {
    users = data;
    let names = [];
    //自动补全
    for (let i = 0; i < users.length; i++)
        names.push(users[i].name);
    /*传递参数*/
    autocomplete(document.getElementById("receiver"), names);
});


function showModal(element) {
    let name = element.data('name');
    //填充模态框字段
    $("#receiver").val(name);
    $('#scheduleModal').modal("show");
}

