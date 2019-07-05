// 全局变量，
var SCHOOL_LIST = {};


//echarts 对象
let myChart = echarts.init(document.getElementById('container'));

//关系图属性
let graphOption = {
    tooltip: {
        formatter: function (params) {
            if (params.dataType == "node") {
                //设置提示框的内容和格式 节点和边都显示name属性
                return `<strong>节点属性</strong><hr>姓名：${params.data.label}</b><br>所属学校：${params.data.school}<br>所属学院：${params.data.institution}`;
            }
            else{
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
                    show : false,

                    //回调函数，显示用户名
                    formatter: function(params){
                        return params.data.label;
                    }
                }
            },
            force: {
                repulsion : [10,100],//节点之间的斥力因子。支持数组表达斥力范围，值越大斥力越大。
                gravity : 0.1,//节点受到的向中心的引力因子。该值越大节点越往中心点靠拢。
                edgeLength :[10,80],//边的两个节点之间的距离，这个距离也会受 repulsion。[10, 50] 。值越小则长度越长
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
    let nodes = data.nodes, links = data.links, cates = data.community;
    console.log(nodes.length, links.length, cates.length);
    graphOption.series[0].data = nodes;
    graphOption.series[0].links = links;

    let categories = [];
    for (let i = 0; i < cates.length; i++) {
        categories[i] = {
            name: '社区' + (i + 1)
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
    if (params.dataType == 'node')
    {
        //页面
        window.open('/scholar/'+params.data.teacherId);
        return;
    }
    else if (params.dataType == 'main')
    {
        alert('点击了树的结点');
    }
});

/**
 * 规格化关系图数据，使之可以生成echarts可用的数据格式
 * @param data
 * @returns {{nodes: Array, links: Array, community: *}}
 */
function formatGraph(data)
{
    let back_data = {
        "nodes" : [],
        "links" : [],
        "community" : data['community_data']
    };

    let nodes = data['nodes'];
    for(let index in nodes)
    {
        let node = nodes[index];
        node['label'] = node['name'];
        node['name'] = node['id'];
        //node['symbolSize'] = parseInt(node['centrality'] * 20 + 5);
        node['category'] = node['class'] - 1;
        node.draggable= true;
        delete node["id"];
        delete node["class"];
        back_data["nodes"].push(node);
    }
    let links = data['edges'];
    for(let index in links)
    {
        let link = links[index];
        link["value"] = link["weight"];
        delete link["weight"];
        back_data['links'].push(link)
    }

    return back_data;
}


/**
 * 显示关系图
 */
function showGraph() {
    //默认请求的是关系图
    $.get('/static/relation_data/back.json').done(function (data) {
        let graph = formatGraph(data);
        reloadGraph(graph);
    });
}
//TODO:初次调用显示关系图
showGraph();

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


$("#select-college").change(function(){
    let school = $(this).children("option:selected").text();
    // 
    if(school in SCHOOL_LIST){
        setInstitution(SCHOOL_LIST[school],school);
    }
    else{
        getInstitution(school);
    }
})


/**
 * 根据学校名获取其所有学院信息
 * @param {String} school 学校名
 */
function getInstitution(school){
    $.ajax({
        type: "get",
        // TODO
        url: "TODO",
        data: {"school" : school},
        dataType: "json",
        success: function (response) {
            let institution = JSON.parse(response);
            setInstitution(institution, school);
            // 保存数据
            SCHOOL_LIST[school] = institution;
        },
        error: function(error){
            console.error(error);
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
    getGraphData(school, institution_list[0]);
}


/**
 * 根据学校名及学院名，获取学院内的关系数据
 * @param {String} school 
 * @param {String} institution 
 */
function getGraphData(school, institution){
    let file_path = `/static/relation_data/${school}${institution}.txt`;
    $.ajax({
        type: "get",
        url: file_path,
        dataType: "json",
        success: function (response) {
            let data = JSON.stringify(response);
            console.log(data);
            reloadGraph(formatGraph(data));
        }
    });
}