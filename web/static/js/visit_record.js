//选中项
let tds = null;
let detail = null;
let identifier = null;
//当前是在修改数据还是在添加新的拜访记录
let isModifying = true;
var SCHOOL_LIST = {};




/**
 * 点击修改按钮后的填充模态框函数
 * @param e
 */
$(".btn-modify").on("click", (e)=>{
    e = $(e.target);
    //修改模态框标题
    $(".modal-title").text("修改拜访记录");
    //选择其他的兄弟
    tds = e.parent().siblings();
    isModifying = true;
    identifier = e.parent().data("id");

    $("#date").val(tds[1].innerText);
    $("#title").val(tds[2].innerText);
    $("#teacher").attr("readonly","readonly").val(tds[5].innerText);
    
    let school = tds[3].innerText;
    let institution = tds[4].innerText;
    
    $("#select-college").attr("disabled","disabled").val(school);
    $("#select-institution").attr("disabled","disabled").empty().html(`<option>${institution}</option>`);
    
    $('#content').val(e.siblings('.detail').val().split("<br>").join("\n"));
    
    $("#exampleModal").modal();
})


/**
 * 添加新的拜访记录
 */
function wantToNewRecord() {
    isModifying = false;
    $("#select-college").attr("disabled",false);
    $("#select-institution").attr("disabled",false);
    $("#teacher").attr("readonly",false);
    getInstitutions($("#select-college").val())
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
let cur_institution = null;


/**
 * 获取所有学校的列表，用于填充模态框中的下拉框
 * @param element
 */
$.ajax({
    url:'/get_schools',
    type: 'GET',
    dataType: 'json'
}).done(function (data) {
    schools = data;
    // autocomplete(document.getElementById('school'), schools);
    // console.log("schools------------  :", schools);
    var html;
    for(var i = 0; i < schools.length; i++){
        school = schools[i];
        html += '<option>'+ school + '</option>';
    }
    $('#select-college').html(html);

    // 如果没有点击学校，则选取默认的学校进行其学院的加载
    loadInstitution();
});



if ($('#school').val()){
    // reloadInstitutions();
    loadInstitution();
}

/**
 * 点击学校之后加载学院数据
 * @param element
 */
$('#select-college').on("change", loadInstitution)

$('#select-institution').on("change", function () {
    cur_school = $('#select-college').children("option:selected").text();
    cur_institution = $(this).children("option:selected").text();

    $.ajax({
        type: "get",
        url: "change_institution",
        data: {"school": cur_school, "institution": cur_institution},
        success: function (response) {}
    });
})
/**
 * 加载当前学校的所有学院数据
 */
function loadInstitution(){
    cur_school = $('#select-college').children("option:selected").text();
    getInstitutions(cur_school);
}


/**
 * 根据学校名获取其所有学院信息
 * @param {String} school 学校名
 */
function getInstitutions(school, callback = undefined){
    if(school in SCHOOL_LIST){
        setInstitution(SCHOOL_LIST[school], school);
    }else{
        $.ajax({
            type: "get",
            url: "/change_school",
            data: {"school" : school},
            dataType: "json",
            success: function (response) {
                // console.log(response);
                if(response.success == false){
                    return toggle_alert(false, "", response.message);
                }
                setInstitution(response, school);
                // 保存数据
                SCHOOL_LIST[school] = response;

                if (callback){
                    callback();
                }
            },
            error: function(error){
                console.error(error);
                toggle_alert(false, "", "服务器连接失败,请稍后再试");
            }
        });
    }
}

/**
 * 将学院信息填充到下拉框中
 * @param {object} institution_list 学院数据 [{"name":xxx},...]
 */
function setInstitution(institution_list){
    if(institution_list.length <= 0){
        alert("学院数据为空");
        return;
    }
    let options = "";
    for (let i = 0; i < institution_list.length; i++) {
        options += `<option>${institution_list[i]}</option>`;
    }
    $("#select-institution").html(options);
}


/**
 * 删除拜访记录
 */
$(".btn-delete").on("click", (e)=>{
    if (!confirm('确定删除此条记录?'))
        return;
    e = $(e.target);
    let record_id = e.parent('.operation').data("id");
    let csrf_token = $('#csrf_token').val();
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
            e.parent().parent('tr').remove();
            $('#total').text(parseInt($('#total').text()) - 1);
        }
        else{
            toggle_alert(false, "", data.message)
        }
    });
})


/*
修改，点击保存时改变所选那一行的数据 给要修改的那一行添加一个属性，利用这个属性去选择正在
修改的那一行，然后捕捉到关闭模态框的状态，关闭模态框时将这一行的属性去掉；
 */
function saveVisitedRecord(e){
    let date = $('#date').val().trim();
    if(!date) return toggle_alert(false, "", "拜访时间不能为空");

    let title = $('#title').val().trim();
    if(!title) return toggle_alert(false, "", "标题不能为空");
    
    
    let content = $('#content').val().split("\n").join("<br>");
    if(!content) return toggle_alert(false, "", "拜访内容不能为空");
    
    let csrf_token = $('#csrf_token').val();
    send_data = {
        date: date,
        content: content,
        title: title,
        csrf_token: csrf_token
    }

    let url = '';
    //回写
    if (isModifying){
        send_data["id"] = identifier;
        url = '/visit_record/edit';
    }else{
        let teacher = $('#teacher').val().trim();
        if(!teacher) return toggle_alert(false, "", "受访对象不能为空");
        
        url = '/visit_record/new';
        cur_school = $('#select-college').children("option:selected").text();
        cur_institution = $('#select-institution').children("option:selected").text();
        send_data["school"] = cur_school;
        send_data["institution"] = cur_institution;
        send_data['teacher'] = teacher;
    }

    //发送事件
    $.ajax({
        url: url,
        type: 'POST',
        data: send_data,
        dataType: 'json'
    }).done(function (response) {
        //新的拜访记录添加成功
        if (!response.success){
            return toggle_alert(false, "exampleModal", response.message);
        }
        //显示新修改的记录
        if (!isModifying){
            let total = parseInt($('#total').text()) + 1;
            let insert_html =
                `<tr><td>${total}</td><td>${send_data.date}</td><td><a>${send_data.title}</a></td><td>${send_data.school}</td>
                <td>${send_data.institution}</td> <td>${send_data.teacher}</td> 
                <td class="operation" data-id="${send_data.record_id}">
                    <button class="btn btn-info btn-modify">修改</button>
                    <button class="btn btn-danger btn-delete">删除</button>
                    <input type="hidden" id="detail" value="${send_data.content}">
                </td></tr>`;
            let $tr=$("#tab tr").eq(-2);
            $tr.after(insert_html);
            //修改总数目
            $('#total').text(total);

            toggle_alert(true, "exampleModal", "拜访记录添加成功");
        }
        else{
            if(isModifying){
                if(tds != null){
                    tds[1].innerHTML = send_data.date;
                    tds[2].innerHTML = send_data.title;
                }
                
                $("#detail").val(send_data.content);
            }
            toggle_alert(true, "exampleModal", "修改成功");
        }
    });
}