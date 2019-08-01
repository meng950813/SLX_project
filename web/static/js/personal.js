// 全局变量
var SCHOOL_LIST = {};
var SCHOOL_NAME= "";
var INSTITUTION_NAME = "";
var DATA = {}; 
var CORE_NODE = [];


/**
 * 显示关系图
 */
function showGraph() {
    //默认请求的是关系图
    let school = $("#select-college").children("option:selected").text();
    let institution = $('#select-institution').children("option:selected");
    // 选中 "全部"
    if(institution.data("type")){
        getSchoolGraphData(school);
    }
    else{
        getInstitutionGraphData(school,institution.text());
    }
}

/**
 * 点击 显示/隐藏非核心节点 的事件
 */
$("#toggle-node-btn").click((e)=>{
    myChart.showLoading();
    toggle_unimportant_node(0, true);
    toggle_relation_with_core_node(-1, true);
    reloadGraph(DATA);
})

/**
 * 显示行政关系
 */
function showTree() {
    myChart.showLoading();
    $.get('static/relation_data/back_tree.json', function (data) {
        myChart.hideLoading();
        treeOption.series[0].data = [data];
        myChart.setOption(treeOption);
    });
}

// 切换学校的响应事件
$("#select-college").change(function(){
    let school = $(this).children("option:selected").text();
    // 
    if(school in SCHOOL_LIST){
        setInstitution(SCHOOL_LIST[school],school);
    }
    else{
        getInstitutions(school);
    }
})

// 切换学院的响应事件
$("#select-institution").change(showGraph);


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
            // console.log(response);
            if(response.success == false){
                toggle_alert(false, "", response.message);
                myChart.hideLoading();
                return;
            }
            setInstitution(response, school);
            // 保存数据
            SCHOOL_LIST[school] = response;
        },
        error: function(error){
            console.error(error);
            toggle_alert(false, "", "服务器连接失败,请稍后再试");
            myChart.hideLoading();
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
    let options = "<option data-type='all'>——全部——</option>";
    for (let i = 0; i < institution_list.length; i++) {
        options += `<option>${institution_list[i]}</option>`;
    }
    $("#select-institution").html(options);
    // getInstitutionGraphData(school, institution_list[0]);
    getSchoolGraphData(school);
}

/**
 * 根据学校名，获取在当前学校建立的社交关系
 * @param {String} school
 */
function getSchoolGraphData(school) {
    myChart.showLoading();
    $.ajax({
        type: "get",
        url: "/get_school_relation",
        data: {"school": school},
        dataType: "json",
        success: function (response) {
            // console.log(response);
            reloadGraph(response);
        },
        error: function(){
            toggle_alert(false, "", "服务器连接失败,请稍后再试");
            myChart.hideLoading();
        }
    });
    $("#toggle-node-btn").hide();
}


/**
 * 根据学校名及学院名，获取学院内的关系数据
 * @param {String} school 
 * @param {String} institution 
 */
function getInstitutionGraphData(school, institution){
    myChart.showLoading();
    $.ajax({
        type: "get",
        url: "/change_institution",
        data: {"school": school, "institution": institution, "relation": true},
        dataType: "json",
        success: function (response) {
            // console.log(response);
            if(response.success == false){
                toggle_alert(false, "", response.message);
                myChart.hideLoading();
                return;
            }
            SCHOOL_NAME = school;
            INSTITUTION_NAME = institution;
            DATA = response;
            toggle_unimportant_node(0, true);
            reloadGraph(DATA);
            // console.log("after load graph");
            // create_relation_with_core_node(DATA.core_node);
            // console.log("create_relation_with_core_node");
            // console.log(CORE_NODE);

        },
        error: function () {
            toggle_alert(false, "", "服务器连接失败,请稍后再试");
            myChart.hideLoading();
        }
    });
    $("#toggle-node-btn").show();
}


/**
 * 显示/隐藏统一社区的非核心节点
 * @param {int} category 
 * @param {boolean} toggle_all 若为真, 显示/隐藏全部非核心节点
 */
function toggle_unimportant_node(category, toggle_all = false){
    // 关系数据为空
    if(DATA.nodes == undefined){
        // console.log("DATA.nodes is ", DATA.nodes)
        return;
    }
    for(let i in DATA.nodes){
        let node = DATA.nodes[i];
        // 核心节点，不隐藏
        if(node.itemStyle){
            continue;
        }
        if(toggle_all || node.category == category || node.category == (category * -1)){
            // console.log("change ", node.label)
            node.category *= -1;
        }
    }
}


/**
 * 创建用户与核心节点的关系
 * @param {json} core_node_data ==> [t_id : {"visited": 123, "activity": 234},...]
 */
function create_relation_with_core_node(core_node_data){
    if(!core_node_data || core_node_data.length == 0) return;
    
    // 重置
    CORE_NODE = [];

    // for(let id in core_node_data){
    //     CORE_NODE.push({
    //         "source":"0",
    //         "target":`-${id}`,
    //         "visited": `共${core_node_data[id].visited}`,
    //         "activity": `共${core_node_data[id].activity}`,
    //         "lineStyle": {
    //             "normal": {
    //                 // TODO 根据拜访次数设定连线宽度
    //                 "width": 10
    //             }
    //         }
    //     })
    // }

    DATA.links = DATA.links.concat(CORE_NODE);
}

/**
 * 
 * @param {string} t_id 
 * @param {boolean} toggle_all 若为真, 显示/隐藏全部与核心节点的关系集合
 */
function toggle_relation_with_core_node(t_id, toggle_all = false){
    // console.log("toggle_relation_with_core_node");
    for(let i in CORE_NODE){
        let node = CORE_NODE[i];
        if(toggle_all || node.target == t_id || node.target == ("-" + t_id)){
            node.target = (parseInt(node.target) * -1).toString()
        }
    }
    // console.log(CORE_NODE);
}