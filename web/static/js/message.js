/**
 * 发送消息
 * @param element
 */
$("#send_message").click((e) =>{
    let receiver= $("#receiver").val();
    let content = $("#content").val();
    console.log(receiver)
    $.ajax({
        url: '/add_message',
        type: 'POST',
        data: {
            receiver: receiver,
            content: content,
            csrf_token: csrf_token,
        },
        dataType: 'json'
    }).done(function (data) {
        if(data.success){
            toggle_alert(true, "", "删除成功");
            //删除此条记录
            element.parents('tr').remove();
            $('#total').text(parseInt($('#total').text()) - 1);
        }
    });
});

