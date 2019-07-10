/**
* 针对修改不同版块，修改模态框的标题
*/
$("#send_message").on("click", (e)=> {
    let $receivce= $("#receiver").val();
    let $content =$("#content").val();
    

});

/**
 * 发送消息
 * @param element
 */
function send_message(element){
    let receiver= $("#receiver").val();
    let content = $("#content").val();
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
}

/**
 * 删除拜访记录
 * @param element
 */
function deleteRecord(element) {
    if (!confirm('确定删除此条记录?'))
        return;
    let record_id = element.parent().parent('.operation').find('#identifier').val();
    let csrf_token = element.parent().find('#csrf_token').val();
    //发送事件
    $.ajax({
        url: '/visit_record/delete',
        type: 'POST',
        data: {
            id: record_id,
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
}