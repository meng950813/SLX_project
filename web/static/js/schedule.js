/**
* 针对修改不同版块，修改模态框的标题
*/
$(".editor").on("click", (e)=> {
    let $target = $(e.target);
    // let title = $target.siblings("legend").text();
    // $("#scheduleModal").text(title);
    let $card = $target.parent().parent().parent();
    let remind_date = $card.children(".card-title").text();
    let detail = $card.children(".schedule-detail").text();
    let id = $card.children(".card-title").attr("data-id");
    
    $("#schedule-id").val(id);
    $("#remind_date").val(remind_date);
    $("#content").val(detail);
    
    $("#scheduleModal").modal('show');

});

/**
 * 添加新日程
 */
$("#new-schedule").click( (e) => {
    // clear_modal();
    $("#scheduleModal").modal('show');
});


/**
 * 提交内容
 */
$("#save-schedule").click((e) => {
    // id=-1 ==> 创建新日程  id>0 ==> 编辑已有日程
    let id = $("#schedule-id").val();

    if(id < -1){
        alert("错误代码");
        return;
    }
    let remind_date = $("#remind_date").val();
    if(remind_date.trim().length !== 10){
        alert("时间格式错误");
        return;
    }
    let content = $("#content").val();
    if(content.trim().length == 0){
        alert("内容不应为空");
        return;
    }

    let data = {"csrf_token": $("#csrf_token").val(), "date": remind_date, "content": content, "id": id}

    $.ajax({
        type: "post",
        url: "/edit_schedule",
        data: data,
        dataType: "json",
        success: function (response) {
            console.log(response);
            toggle_alert(response.success, "scheduleModal", response.message);


        },
        error: function(error){
            console.log(error);
            toggle_alert(false, "scheduleModal", "服务器连接失败，请稍后再试");
        }
    });
})


/**
 * 日程标记完成/取消
 */
$(".operate-schedule").click((e)=>{
    let id = $("#schedule-id").val();
    if(id == -1){
        clear_modal();
        return;
    }
    else{
        let status = $(e.target).attr("data-type");
        console.log(status)
        /**
         * status: 0 ==> 取消日程安排
         * status: 1 ==> 完成日程安排
         *  */
        if(status != 0 && status != 1){
            alert("错误代码");
            return;
        }

        $.ajax({
            type: "post",
            url: "/operate_schedule",
            data: {"csrf_token": $("#csrf_token").val(), "id":id, "type":status},
            dataType: "json",
            success: function (response) {
                if(response.success){
                    remove_card(id);
                }
                toggle_alert(Response.success, "scheduleModal", response.message)
            },
            error: function(error){
                console.log(error);
                toggle_alert(false, "scheduleModal", "服务器连接失败，请稍后再试");
            }
        });
    }
})


/**
 * 清空模态框中的内容
 */
function clear_modal(){
    $("#schedule-id").val(-1);
    $("#remind_date").val("");
    $("#content").val("");
}

/**
 * 在dom中移除某一card
 * @param {int} id 该日程的id
 */
function remove_card(id){
    let target = $(`.card-title[data-id=${id}]`).parent().parent();
    if(target.length){
        target.remove();
    }
}

/**
 * 更新/创建日程安排内容
 * @param {int} id 日程id
 * @param {object} data 数据
 */
function create_card(id, data){
    let target = $(`.card-title[data-id=${id}]`);
    // 新id ==> 创建
    if(target.length == 0){
        $("#card-list").insert(`
            <div class="card">
                <div class="card-body">
                <button type="button" class="close" data-toggle="modal"><span aria-hidden="true"><i class="editor mdui-icon material-icons">&#xe3c9;</i></span></button>
                <h5 class="card-title" data-id="1">2019-06-27</h5>
                <p class="card-text schedule-detail">${data.content}</p>
                <p class="text-right card-text"><small class="create-time">创建于${new Date().Format("yyyy-MM-dd")}</small></p>
                </div>
            </div>
        `)
    }else{
        let card_body = target.parent();
        $target.text(data.date);
        card_body.children(".schedule-detail").text(data.content);
        card_body.children(".create-time").text(`创建于 ${new Date().Format("yyyy-MM-dd")}`);
    }
}

// 对Date的扩展，将 Date 转化为指定格式的String
// 月(M)、日(d)、小时(h)、分(m)、秒(s)、季度(q) 可以用 1-2 个占位符，
// 年(y)可以用 1-4 个占位符，毫秒(S)只能用 1 个占位符(是 1-3 位的数字)
// 例子：
// (new Date()).Format("yyyy-MM-dd hh:mm:ss.S") ==> 2006-07-02 08:09:04.423
// (new Date()).Format("yyyy-M-d h:m:s.S") ==> 2006-7-2 8:9:4.18

Date.prototype.Format = function (fmt) { // author: meizz
    var o = {
        "M+": this.getMonth() + 1, // 月份
        "d+": this.getDate(), // 日
        "h+": this.getHours(), // 小时
        "m+": this.getMinutes(), // 分
        "s+": this.getSeconds(), // 秒
        "q+": Math.floor((this.getMonth() + 3) / 3), // 季度
        "S": this.getMilliseconds() // 毫秒
    };
    if (/(y+)/.test(fmt))
        fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
    for (var k in o)
        if (new RegExp("(" + k + ")").test(fmt)) fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
            return fmt;
}