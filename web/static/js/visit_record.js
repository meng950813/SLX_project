//选中项
let tds = null;
let detail = null;

function modify_modal(e){
    //修改模态框标题
    $(".modal-title").text("修改拜访记录");
    //将表格中的内容添加在表单中
    //选择修改a标签所在的单元格
    let target = $(e.target);
    //选择其他的兄弟
    tds = e.parent().siblings();
    //将表格中的内容逐个取出，然后填到表单中去
    let input_model = $("#exampleModal .mod");
    for(let i = 0;i < tds.length;i++){
        input_model[i].value = tds[i].innerText;
    }
    detail = e.parent('.operation').find('#detail');
    $('#content').val(e.parent('.operation').find('#detail').val());
}

/*
修改，点击保存时改变所选那一行的数据 给要修改的那一行添加一个属性，利用这个属性去选择正在
修改的那一行，然后捕捉到关闭模态框的状态，关闭模态框时将这一行的属性去掉；
 */
function saveVisitedRecord(e){
    let mod_title = $(".modal-title");

    let date = $('#date').val();
    let title = $('#title').val();
    let school = $('#school').val();
    let institution = $('#institution').val();
    let teacher = $('#teacher').val();
    let content = $('#content').val();
    let url = '';
    //回写
    if (tds != null){
        //模态框
        let input_model = $("#exampleModal .mod");
        for(let i=0;i < tds.length;i++){
            tds[i].innerHTML = input_model[i].value;
        }
        detail.val(content);

        url = '/visit_record/edit';
        tds = null;
        detail = null;
    }else{
        //模态框
        let input_model = $("#exampleModal .mod");
        var insert_html =
            `<tr><td>${date}</td><td>${school}</td> <td>${institution}</td> <td>${teacher}</td> <td><a href=#>${title}</a></td>
                <td class="operation">
                    <a class="btn btn-info" href="#" data-toggle="modal" data-target="#exampleModal" onclick="modify_modal($(this));">修改</a>
                    <a class="btn btn-danger" href=#>删除</a>
                </td></tr>`;

        var $tr=$("#tab tr").eq(-2);
        $tr.after(insert_html);
        url = '/visit_record/new';
    }
    $.ajax({
        url: url,
        type: 'POST',
        data: {
            date: date,
            school: school,
            institution: institution,
            teacher: teacher,
            content: content,
            csrf_token: $('#csrf_token').val(),
        },
        dataType: 'json'
    }).done(function (data) {
        console.log(data);
    });
}
