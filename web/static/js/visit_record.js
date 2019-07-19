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
function fillModal(e){
    //修改模态框标题
    $(".modal-title").text("修改拜访记录");
    //选择其他的兄弟
    tds = e.parent().siblings();
    console.log("tds    : ", tds);
    isModifying = true;
    //将表格中的内容逐个取出，然后填到表单中去
    let input_model = $("#exampleModal .mod");

    input_model[0].value = tds[1].innerText;
    input_model[1].value = tds[2].innerText;
    input_model[2].value = tds[5].innerText;


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
let cur_institution = null;
let timeoutID = null;
let res = null;


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
$('#select-college').click(function () {
    console.log("---------点击学校");
    // 如果点击了学校下拉框，则对学院进行重新加载
    if (timeoutID)
        clearTimeout(timeoutID);
    timeoutID = setTimeout(500);
    loadInstitution();
})

/**
 * 加载当前学校的所有学院数据
 * @param element
 */
function loadInstitution(){

    cur_school = $('#select-college').children("option:selected").text();

    console.log("schools   :", schools)
    console.log("????cur_school    :", cur_school);

    getInstitutions(cur_school);
}


/**
 * 根据学校名获取其所有学院信息
 * @param {String} school 学校名
 */
function getInstitutions(school){
    $.ajax({
        type: "get",
        url: "/change_school",
        data: {"school" : school},
        dataType: "json",
        success: function (response) {
            console.log(response);
            if(response.success == false){
                toggle_alert(false, "", response.message);
                return;
            }
            setInstitution(response, school);
            // 保存数据
            SCHOOL_LIST[school] = response;
        },
        error: function(error){
            console.error(error);
            toggle_alert(false, "", "服务器连接失败,请稍后再试");
        }
    });
}

/**
 * 将学院信息填充到下拉框中
 * @param {object} institution_list 学院数据 [{"name":xxx, "visited":1},...]
 * @param {String} school 学校
 */
function setInstitution(institution_list, school){
    if(institution_list.length <= 0){
        alert("学院数据为空");
        return;
    }
    let options = "";
    for (let i = 0; i < institution_list.length; i++) {
        // options += `<option>${institution_list[i]}</option>`;
        options += `<option data-times="${institution_list[i].visited}">${institution_list[i].name}</option>`;
    }
    $("#select-institution").html(options);
}


$('#select-institution').click(function () {
    // console.log("-----点击学院");
    if (timeoutID)
        clearTimeout(timeoutID);
    timeoutID = setTimeout(500);
    cur_school = $('#select-college').children("option:selected").text();
    cur_institution = $(this).children("option:selected").text();

    // console.log("school adn insi---------", cur_school, cur_institution);
})
//学校输入框失去焦点绑定事件
// $('#select-college').on('blur', function () {
//     // if (timeoutID)
//     //     clearTimeout(timeoutID);
//     // timeoutID = setTimeout(reloadInstitutions, 500);
//     console.log("schools   :", schools)
//     let school = $(this).children("option").text();
//     console.log("cur_school    :", school);
//     if(school in schools){
//         $.ajax({
//             url: '/get_institutions',
//             type: 'GET',
//             data: {"school": school},
//             dataType: 'json'
//         }).done(function (data) {
//             institutions = data;
//
//             console.log("institutions   :", institutions)
//
//             var html;
//             for(var i = 0; i < institutions.length; i++){
//                 html += '<option>' + institutions[i] + '</option>';
//             }
//             $('#select-institution').html(
//                 html
//             );
//         })
//     }
// });


// function  reloadInstitutions() {
//     timeoutID = null;
//     //判断是否需要重新请求获取学院
//     let school = $('#school').val();
//     if (school != "" && school != cur_school) {
//         cur_school = school;
//         //请求获取学院
//         $.ajax({
//             url: '/get_institutions/' + cur_school,
//             type: 'GET',
//             dataType: 'json'
//         }).done(function (data) {
//
//             console.log("----------测试");
//             institutions = data;
//             /*传递参数*/
//             // autocomplete(document.getElementById("institution"), institutions);
//         });
//     }
// }



$('#teacher').on('blur', function () {
    cur_school = $('#select-college').children("option:selected").text();
    cur_institution = $('#select-institution').children("option:selected").text();
    if (cur_school && cur_institution){

        teacher = $('#teacher').val();
        // console.log(">>>>>>>>", cur_school, cur_institution, teacher);
        tranferID(cur_school, cur_institution, teacher);
    }
})



function tranferID(school, institution, teacher) {
    teacher_info = {
        "csrf_token": $("#csrf_token").val(),
        "school": school,
        "institution": institution,
        "teacher": teacher
    }
    $.ajax({
        url: '/get_teacher_id',
        type: 'POST',
        data: teacher_info,
        dataType: 'json',
        success: function (response) {
            let teacher_id = response["teacher_id"];
            res = response;
            $('#teacher').attr('data-id', teacher_id);
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
let teacher_id
function saveVisitedRecord(e){
    let date = $('#date').val();
    let title = $('#title').val();
    // let school = $('#school').val();
    // let institution = $('#institution').val();
    let school = $('#select-college').children("option:selected").text();
    let institution = $('#select-institution').children("option:selected").text();

    let teacher = $('#teacher').val();
    let content = $('#content').val();
    let csrf_token = $('#csrf_token').val();
    let id = null;
    teacher_id = $('#teacher').attr("data-id");

    let url = '';
    //回写
    if (isModifying){

        id = identifier.val();
        url = '/visit_record/edit';
    }else{
        url = '/visit_record/new';
    }

    //发送事件
    $.ajax({
        url: url,
        type: 'POST',
        data: {
            id: id,
            date: date,
            school: cur_school,
            institution: cur_institution,
            teacher: teacher,
            content: content,
            title: title,
            csrf_token: csrf_token,
            teacher_id: teacher_id,
        },
        dataType: 'json'
    }).done(function (data) {
        //显示新修改的记录

        //新的拜访记录添加成功
        if (!isModifying){
            console.log("------------- teacher_id  :"+teacher_id)
            if (!data.success || typeof(teacher_id) == undefined){
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
            if(isModifying){
                //模态框
                let input_model = $("#exampleModal .mod");
                // console.log("---tds   :", tds)
                if(tds != null){
                    // for(let i = 1;i < tds.length;i++){
                    //     tds[i].innerHTML = input_model[i - 1].value;
                    // }
                    tds[1].innerHTML = input_model[0].value;
                    tds[2].innerHTML = input_model[1].value;
                    tds[3].innerHTML = cur_school;
                    tds[4].innerHTML = cur_institution;
                    tds[5].innerHTML = input_model[2].value;
                }
                console.log(">>>>>>>>", school, institution, teacher);

                // console.log("--detail  :", detail);
                // console.log("--content  :", content);
                if(detail != null)
                    detail.val(content);
            }
            toggle_alert(true, "exampleModal", "修改成功");
        }else if(!data.success ||  typeof(teacher_id) == undefined){
            toggle_alert(false, "exampleModal", "修改记录添加失败");
            return ;
        }
    });

    //隐藏模态框
    $('#exampleModal').modal('hide');
}

