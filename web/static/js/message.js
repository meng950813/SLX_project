/**
 * 发送消息
 * @param element
 */
$("#send_message").click((e) =>{
    let receiver= $("#receiver").val();
    let content = $("#content").val();
    let csrf_token = $("#csrf_token").val();
    //TODO:接收者的id已经得知
    let receiver_id = 100000;
    console.log(receiver);
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

