//选中项
let tds = null;
let detail = null;
let identifier = null;
//当前是在修改数据还是在添加新的拜访记录
let isModifying = true;

/**
 * 点击修改按钮后的填充模态框函数
 * @param e
 */
function fillModal(e){
    //修改模态框标题
    $(".modal-title").text("修改拜访记录");
    //选择其他的兄弟
    tds = e.parent().siblings();
    isModifying = true;
    //将表格中的内容逐个取出，然后填到表单中去
    let input_model = $("#exampleModal .mod");
    for(let i = 1;i < tds.length;i++){
        input_model[i - 1].value = tds[i].innerText;
    }
    detail = e.parent('.operation').find('#detail');
    identifier = e.siblings('form').find('#identifier');
    $('#content').val(e.parent('.operation').find('#detail').val());
}

/**
 * 添加新的拜访记录
 */
function wantToNewRecord() {
    isModifying = false;
    $(".modal-title").text("添加拜访记录");
}

/**
 * 添加新的拜访记录时自动补全，并将教师的id存下
 * @param element
 */
//请求获取所有的学校名称
let schools = [];
let institutions = [];
//当前选中的学校
let cur_school = null;
let timeoutID = null;
let res = null;

$.ajax({
    url:'/get_schools',
    type: 'GET',
    dataType: 'json'
}).done(function (data) {
    schools = data;
    //传参
    autocomplete(document.getElementById('school'), schools);
});

if ($('#school').val()){
    reloadInstitutions();
}

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
    if (school != "" && school != cur_school) {
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

$('#teacher').on('blur', function () {

    if ($('#institution').val() && $('#teacher').val()){
        console.log("________比较ins and tea")
        school = $('#school').val();
        institution = $('#institution').val();
        teacher = $('#teacher').val();
        tranferID(school, institution, teacher);
    }
})



function tranferID(school, institution, teacher) {
    teacher_info = {
        "csrf_token": $("#csrf_token").val(),
        "school": school,
        "institution": institution,
        "teacher": teacher
    }
    console.log("--------", teacher_info);
    $.ajax({
        url: '/get_teacher_id',
        type: 'POST',
        data: teacher_info,
        dataType: 'json',
        success: function (response) {
            let teacher_id = response["teacher_id"];
            res = response;
            console.log("-----teacher_id", teacher_id)
            $('#teacher').attr('teacher_id', teacher_id);
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
            toggle_alert(true, "", "删除成功!!");
            //删除此条记录
            element.parents('tr').remove();
            $('#total').text(parseInt($('#total').text()) - 1);
        }
    });
}
/*
修改，点击保存时改变所选那一行的数据 给要修改的那一行添加一个属性，利用这个属性去选择正在
修改的那一行，然后捕捉到关闭模态框的状态，关闭模态框时将这一行的属性去掉；
 */
function saveVisitedRecord(e){
    let date = $('#date').val();
    let title = $('#title').val();
    let school = $('#school').val();
    let institution = $('#institution').val();
    let teacher = $('#teacher').val();
    let content = $('#content').val();
    let csrf_token = $('#csrf_token').val();
    let id = null;
    let teacher_id = $('#teacher').val();

    let url = '';
    //回写
    if (isModifying){
        //模态框
        let input_model = $("#exampleModal .mod");
        for(let i = 1;i < tds.length;i++){
            tds[i].innerHTML = input_model[i - 1].value;
        }
        detail.val(content);
        id = identifier.val();
        url = '/visit_record/edit';
    }else{
        url = '/visit_record/new';
    }
    tds = null;
    detail = null;
    //发送事件
    $.ajax({
        url: url,
        type: 'POST',
        data: {
            id: id,
            date: date,
            school: school,
            institution: institution,
            teacher: teacher,
            content: content,
            title: title,
            csrf_token: csrf_token,
            teacher_id: teacher_id,
        },
        dataType: 'json'
    }).done(function (data) {
        console.log(data);
        //新的拜访记录添加成功
        if (!isModifying){
            if (!data.success){
                toggle_alert(false, "exampleModal", "拜访记录添加失败");
                return ;
            }
            let record_id = data.record_id;
            let total = parseInt($('#total').text()) + 1;
            let insert_html =
                `<tr><td>${total}</td><td>${date}</td><td><a>${title}</a></td><td>${school}</td> <td>${institution}</td> <td>${teacher}</td> 
                <td class="operation">
                    <button class="btn btn-info" href="#" data-toggle="modal" data-target="#exampleModal" onclick="fillModal($(this));">修改</button>
                    <form style="display: inline">
                        <input type="hidden" id="csrf_token" name="csrf_token" value="${csrf_token}"/>
                        <input type="hidden" id="identifier" name="id" value="${record_id}">
                        <button class="btn btn-danger" type="button" onclick="deleteRecord($(this));">删除</button>
                    </form>
                    <input type="hidden" id="detail" value="${content}">
                </td></tr>`;
            let $tr=$("#tab tr").eq(-2);
            $tr.after(insert_html);
            //修改总数目
            $('#total').text(total);

            toggle_alert(true, "exampleModal", "拜访记录添加成功");
        }
        else if(data.success){
            toggle_alert(true, "exampleModal", "修改成功");
        }
    });
    //隐藏模态框
    //$('#exampleModal').modal('hide');
}

