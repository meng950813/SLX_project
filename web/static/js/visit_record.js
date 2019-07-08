//选中项
let tds = null;

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
    for(let i = 0;i < input_model.length;i++){
        input_model[i].value = tds[i].innerText;
        console.log(input_model[i].value, typeof(input_model[i].value));
    }
}

/*
修改，点击保存时改变所选那一行的数据 给要修改的那一行添加一个属性，利用这个属性去选择正在
修改的那一行，然后捕捉到关闭模态框的状态，关闭模态框时将这一行的属性去掉；
 */
function saveVisitedRecord(e){
    let mod_title = $(".modal-title");
    //判断当前是否是修改
    if (tds != null){
        //模态框
        let input_model = $("#exampleModal .mod");
        for(let i=0;i < input_model.length;i++){
            tds[i].textContent = input_model[i].value;
        }
        /*
        $.ajax({
            url: '/visit_record/edit',
            data: {csrf_token:}
        });
         */
        tds = null;
    }else{
        //模态框
        input_model = $("#exampleModal .mod");
        var insert_html = `<tr><td>2019-06-28</td><td>上海交融大学</td> <td>计算机学院</td> <td>罗军舟</td> <td><a href=#>关于计算机科学产学研合</a></td>
                        <td class="operation"><a class="modify-btn"  data-toggle="modal" data-target="#exampleModal"  onclick="modify_modal($(this))" >修改</a>
                        <a class="delete" href=#>删除</a></td> </tr>`

        var $tr=$("#tab tr").eq(-2);
        $tr.after(insert_html);
    }
}
