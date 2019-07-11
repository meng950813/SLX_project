// 全局变量
var SCHOOL_LIST = {};
var SCHOOL_NAME= "";
var INSTITUTION_NAME = "";
var DATA = {}; 

/**
 * 阻止右键默认事件
 */
$(document).ready(function(){
    $(document).bind("contextmenu",function(e){
        return false;
    });
});


//echarts 对象
let myChart = echarts.init(document.getElementById('container'));

//关系图属性
let graphOption = {
    tooltip: {
        formatter: function (params) {
            if (params.dataType == "node") {
                if(params.data.label == "我"){
                    return "<strong>我</strong>";
                }
                //设置提示框的内容和格式 节点和边都显示name属性
                return `<strong>节点属性</strong><hr>姓名：${params.data.label}<br>所属学校：${SCHOOL_NAME}<br>所属学院：${INSTITUTION_NAME}`;
            }
            else{
                if(params.data.visited){
                    return  `<strong>关系属性</strong><hr>拜访次数：${params.data.visited}次`;
                }
                return `<strong>关系属性</strong><hr>
                论文合作：${params.data.paper}次<br>专利合作：${params.data.patent}次<br>项目合作：${params.data.project}次<br>`;
            }
        }
    },

    // 图例
    legend: [
    ],
    animation: true,
    series : [
        {
            type: 'graph',
            layout: 'force',
            data: [],
            links: [],
            categories: [],

            // // 边的长度范围
            // edgeLength: [10, 50],

            //是否开启鼠标缩放和平移漫游。默认不开启。如果只想要开启缩放或者平移，可以设置成 'scale' 或者 'move'。设置成 true 为都开启
            roam: true,

            // 当鼠标移动到节点上，突出显示节点以及节点的边和邻接节点
            focusNodeAdjacency:true,
            // 是否启用图例 hover(悬停) 时的联动高亮。
            legendHoverLink : true,

            label: {
                normal: {
                    position: 'inside',
                    show : true,

                    //回调函数，显示用户名
                    formatter: function(params){
                        return params.data.label;
                    }
                }
            },
            force: {
                repulsion : [20,100],//节点之间的斥力因子。支持数组表达斥力范围，值越大斥力越大。
                gravity : 0.05,//节点受到的向中心的引力因子。该值越大节点越往中心点靠拢。
                edgeLength :[20,100],//边的两个节点之间的距离，这个距离也会受 repulsion。[10, 50] 。值越小则长度越长
                layoutAnimation : true
            },

            lineStyle: {
                show : true,
                color: 'target',//决定边的颜色是与起点相同还是与终点相同
                curveness: 0.1//边的曲度，支持从 0 到 1 的值，值越大曲度越大。
            }
        }
    ]
};

//树属性
let treeOption = {
    tooltip: {
        trigger: 'item',
        triggerOn: 'mousemove',
        formatter: function (params) {
            //设置提示框的内容和格式 节点和边都显示name属性
            return "行政关系。。。"
        }
    },
    series:[
        {
            type: 'tree',

            data: [],

            left: '2%',
            right: '2%',
            top: '8%',
            bottom: '20%',

            symbol: 'emptyCircle',

            orient: 'vertical',

            expandAndCollapse: false,

            label: {
                normal: {
                    position: 'top',
                    rotate: -90,
                    verticalAlign: 'middle',
                    align: 'right',
                    fontSize: 9
                }
            },

            leaves: {
                label: {
                    normal: {
                        position: 'bottom',
                        rotate: -90,
                        verticalAlign: 'middle',
                        align: 'left'
                    }
                }
            },
            animationDurationUpdate: 750
        }
    ]
};


/**
 * 重新加载关系图数据，把数据赋值给graphOption中的data
 * @param data 关系图数据
 */
function reloadGraph(data){
    if(!"nodes" in data) return;
    console.log(data)
    let nodes = data.nodes, links = data.links, cates = data.community;
    // console.log(nodes.length, links.length, cates.length);
    graphOption.series[0].data = nodes;
    graphOption.series[0].links = links;

    let categories = [];
    categories[0] = {name: '我'};
    for (let i = 1; i <= cates; i++) {
        categories[i] = {
            name: '社区' + i
        };
    }
    graphOption.series[0].categories = categories;
    graphOption.legend = [{
        data: categories.map(function (a) {
            return a.name;
        })
    }];
    myChart.setOption(graphOption);
}

//添加点击跳转事件
myChart.on('click', function (params) {
    //仅限节点类型
    if (params.dataType == 'node'){
        //页面
        window.open('/scholar/'+params.data.name);
        return;
    }
    else if (params.dataType == 'main'){
        alert('点击了树的结点');
    }
});


/**
 * 添加节点双击事件，用于隐藏非重要节点
 */
myChart.on("contextmenu", function(params){
    //仅限核心节点类型
    if (params.dataType == 'node'){
        // console.log("双击节点", params);
        toggle_unimportant_node(params.data.category);
        reloadGraph(DATA);
    }
})


/**
 * 显示/隐藏统一社区的非核心节点
 * @param {int} category 
 * @param {boolean} toggle_all 若为真, 显示/隐藏全部非核心节点
 */
function toggle_unimportant_node(category, toggle_all = false){
    // 关系数据为空
    if(DATA.nodes == undefined){
        console.log("DATA.nodes is ", DATA.nodes)
        return;
    }
    for(let i in DATA.nodes){
        let node = DATA.nodes[i];
        // 核心节点，不隐藏
        if(node.itemStyle){
            continue;
        }
        if(toggle_all){
            node.category *= -1;
        }
        else if(node.category == category || node.category == (category * -1)){
            // console.log("change ", node.label)
            node.category *= -1;
        }
    }
}

/**
 * 显示关系图
 */
function showGraph() {
    //默认请求的是关系图
    let school = $("#select-college").children("option:selected").text();
    let institution = $('#select-institution').children("option:selected").text();
    getInstitutionGraphData(school,institution);
}

/**
 * 点击 显示/隐藏非核心节点 的事件
 */
$("#toggle-node-btn").click((e)=>{
    toggle_unimportant_node(0, true);
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
$("#select-institution").change(function () {
    let school = $("#select-college").children("option:selected").text();
    let institution = $(this).children("option:selected").text();
    // console.log(school,institution);
    getInstitutionGraphData(school,institution);
});


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
 * @param {array} institution_list 学院数组
 * @param {String} school 学校
 */
function setInstitution(institution_list, school){
    if(institution_list.length <= 0){
        alert("学院数据为空");
        return;
    }
    let options = "";
    for (let i = 0; i < institution_list.length; i++) {
        options += `<option>${institution_list[i]}</option>`;
    }
    $("#select-institution").html(options);
    getInstitutionGraphData(school, institution_list[0]);
}


/**
 * 根据学校名及学院名，获取学院内的关系数据
 * @param {String} school 
 * @param {String} institution 
 */
function getInstitutionGraphData(school, institution){
    $.ajax({
        type: "get",
        url: "/change_institution",
        data: {"school": school, "institution": institution},
        dataType: "json",
        success: function (response) {
            // console.log(response);
            if(response.success == false){
                toggle_alert(false, "", response.message);
                return;
            }
            SCHOOL_NAME = school;
            INSTITUTION_NAME = institution;
            DATA = response;
            reloadGraph(response);
        },
        error: function () {
            toggle_alert(false, "", "服务器连接失败,请稍后再试");
        }
    });
}