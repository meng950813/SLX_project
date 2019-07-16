//请求获取所有的学校名称
let schools = [];
let institutions = [];
//当前选中的学校
let cur_school = null;
let timeoutID = null;

$.ajax({
    url: '/get_schools',
    type: 'GET',
    dataType: 'json'
}).done(function (data) {
    schools = data;
    /*传递参数*/
    autocomplete(document.getElementById("school"), schools);
});

//学校输入框失去焦点绑定事件
$('#school').on('blur', function () {
    if (timeoutID)
        clearTimeout(timeoutID);

    timeoutID = setTimeout(reloadInstitutions, 500);
});


function  reloadInstitutions() {
    timeoutID = null;
    //判断是否需要重新请求获取学院
    let school = $('#school').val();
    if (school != cur_school) {
        cur_school = school;
        //请求获取学院
        $.ajax({
            url: '/get_institutions/' + cur_school,
            type: 'GET',
            dataType: 'json'
        }).done(function (data) {
            institutions = data;
            /*传递参数*/
            autocomplete(document.getElementById("institution"), institutions);
        });
    }
}

$('#submit').click(function (e) {
    //TODO: 判断学校相同 niuniu
    if (cur_school == $('#school').val() && schools.indexOf(cur_school) != -1
        && institutions.indexOf($('#institution').val())){
        $('form').submit();
    }
    else{
        toggle_alert(false, "", "学校名或学院名输入有误");
        e.preventDefault();
    }
});