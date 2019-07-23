/*
*一旦页面加载，
*请求该用户的数据
 */

//用于存储后端传来的用户基本信息
let user_dict;

$.ajax({
    url: '/get_user_info',
    type:'GET',
    dataType:'json',
}).done(function (data) {
    user_dict = data;
    user_info = data;
    console.log(user_info);

    // 填充表单
    $("#user_name").val(user_info["user_name"]);
    $("#user_tel").val(user_info["user_tel"]);
    console.log(user_info["user_tel"]);
    $("#user_email").val(user_info["user_email"]);

    $("#user_type").val(user_info["user_type"]);

    var charge_school = "";
    for(var i = 0; i < user_info["charge_school"].length; i++){
        charge_school += user_info["charge_school"][i] + "  " ;
    }
    if(charge_school == "")
        charge_school = "无"
    $("#charge_school").val(charge_school);

    var related_teachers = "";
    for(var i = 0; i < user_info["related_teacher"].length; i++){
        related_teachers += user_info["related_teacher"][i]["name"]
    }
    if(related_teachers == "")
        related_teachers = "无"
    $("#related_teacher").val(related_teachers);
})


/*
*点击保存按钮，触发该函数
 */
function save_basic_info(e) {
    user_name = $("#user_name").val();
    user_tel = $("#user_tel").val();
    user_email = $("#user_email").val();

    user_dict["user_name"] = user_name;
    user_dict["user_tel"] = user_tel;
    user_dict["user_email"] = user_email;
    console.log(user_dict);
    let csrf_token = $('#csrf_token').val();
    $.ajax({
        url: '/save_basic_info',
        type: 'POST',
        data: {
            user_id: user_dict["user_id"],
            user_name: user_dict["user_name"],
            user_email: user_dict["user_email"],
            user_tel: user_dict["user_tel"],
            csrf_token: csrf_token,
        },
        dataType: 'json'
    }).done(function (data) {
        if(data.success){
            toggle_alert(true, "", "保存成功!!");
        }
    })
}

/*
 *验证输入的原密码是否与数据库中一致
 */
function save_change_pwd(e) {
    old_pwd = $("#old_pwd").val();
    console.log("old--  " + old_pwd);
    $.ajax({
        url: '/vertify_pwd/' + old_pwd,
        type: 'GET',
        dataType: 'json'
    }).done(function (data) {
        console.log(data)
        if(data.success == false){
            console.log("-----1")
            toggle_alert(false, "", "旧密码验证失败")
        }else{
            change_new_pwd();
        }
    })


}


/*
 *验证新密码两次输入是否一致
 * 若一致，将新密码入库
 */
function change_new_pwd() {
    new_pwd = $("#new_pwd").val();
    second_new_pwd = $("#second_new_pwd").val()

    if(new_pwd != second_new_pwd){
        console.log("-----2")
        toggle_alert(false, "", "重置的密码两次输入不一致！")
        return;
    }else{
        $.ajax({
            url: '/change_pwd_in_db/' + new_pwd,
            type: 'GET',
            dataType: 'json'
        }).done(function (data) {
            if(data.success){
                            console.log("-----3")

                toggle_alert(true, "", "密码修改成功");
            }
        })
    }


}